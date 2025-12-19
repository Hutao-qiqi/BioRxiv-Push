# biorxiv_bot.py
"""
BioRxiv 肿瘤学文章自动阅读与邮件推送系统
- 定时获取 BioRxiv 最新文章
- 使用 AI 生成研究简报
- 通过邮件发送给用户
"""

import os
import json
import yaml
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dateutil import tz
import logging

from utils import now_in_tz, last_window_start, fmt_period
from biorxiv_fetch import fetch_window, pack_papers
from pubmed_fetch import fetch_pubmed_articles
from summarizer_api import run_ollama
from state import PeriodState
from email_sender import send_digest_email, send_error_notification

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(SCRIPT_DIR, 'biorxiv_push.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载环境变量（使用绝对路径）
env_path = os.path.join(SCRIPT_DIR, '.env')
load_dotenv(dotenv_path=env_path)
logger.info(f"从 {env_path} 加载环境变量")

# 加载配置
config_path = os.path.join(SCRIPT_DIR, "config.yaml")
try:
    with open(config_path, "r", encoding="utf-8") as f:
        CFG = yaml.safe_load(f)
    logger.info(f"✅ 配置文件加载成功: {config_path}")
except FileNotFoundError:
    logger.error(f"❌ 未找到配置文件: {config_path}")
    exit(1)

TZNAME = CFG.get("timezone", "Asia/Shanghai")
WINDOW_H = int(CFG.get("time_window_hours", 24))

# 全局状态
BOT_STATUS = {
    "running": True,
    "start_time": datetime.now(),
    "last_fetch": None,
    "last_report": None,
    "total_reports": 0,
    "total_papers": 0,
    "errors": []
}

# 创建调度器
scheduler = AsyncIOScheduler(timezone=TZNAME)


async def generate_and_send_digest(period_label: str, manual=False):
    """
    生成并发送研究简报
    
    Args:
        period_label: 期别标签（如：早报、晚报）
        manual: 是否为手动触发
    """
    try:
        logger.info("=" * 80)
        logger.info(f"🚀 开始生成{period_label}")
        logger.info("=" * 80)
        
        # 计算时间窗口
        now_local = now_in_tz(TZNAME)
        since_local = last_window_start(TZNAME, WINDOW_H)
        
        logger.info(f"📅 时间窗口: {since_local} ~ {now_local}")
        
        # 获取文章
        logger.info("📥 正在从 BioRxiv 获取文章...")
        biorxiv_articles = fetch_window(CFG, since_local, now_local)
        biorxiv_data = pack_papers(CFG, biorxiv_articles)
        
        logger.info(f"✅ BioRxiv: {len(biorxiv_data)} 篇文章")
        
        # 获取 PubMed 文章（Nature/Science/Cell等）
        logger.info("📥 正在从 PubMed 获取顶级期刊文章...")
        try:
            pubmed_articles = fetch_pubmed_articles(CFG, days=3)
            pubmed_data = pack_papers(CFG, pubmed_articles)
            logger.info(f"✅ PubMed: {len(pubmed_data)} 篇文章")
        except Exception as e:
            logger.warning(f"⚠️ PubMed 获取失败: {e}")
            pubmed_data = []
        
        # 合并数据
        data = biorxiv_data + pubmed_data
        logger.info(f"📊 合并后总计: {len(data)} 篇文章")
        
        BOT_STATUS["last_fetch"] = now_local
        BOT_STATUS["total_papers"] += len(data)
        
        logger.info(f"✅ 获取到 {len(data)} 篇文章")
        
        # 如果没有文章
        if len(data) == 0:
            logger.warning("⚠️ 本次时间窗口内没有新文章")
            # 可选：发送无文章通知邮件
            # send_digest_email(period_label, "# 本次时间窗口内没有新的肿瘤学相关文章\n\n请稍后再试。")
            return True
        
        # 保存原始数据
        period = fmt_period(now_local)
        st = PeriodState(period)
        st.save_raw(data)
        logger.info(f"💾 原始数据已保存: {period}")
        
        # 使用 AI 生成摘要
        logger.info("🤖 正在使用 AI 生成研究简报...")

        
        summary_md = run_ollama(
            CFG,
            period_label,
            since_local.isoformat(),
            now_local.isoformat(),
            json.dumps(data, ensure_ascii=False)
        )
        
        st.save_report(summary_md)
        logger.info(f"💾 简报已保存")
        
        # 生成上下文（用于后续对话）
        prompt_ctx = (
            "# 原始条目 (JSON)\n" +
            json.dumps(data, ensure_ascii=False, indent=2) +
            "\n\n# 研究简报 (Markdown)\n" +
            summary_md
        )
        st.save_prompt(prompt_ctx)
        
        # 发送邮件
        logger.info("📧 正在发送邮件...")
        email_success = send_digest_email(period_label, summary_md)
        
        if email_success:
            logger.info(f"✅ {period_label}生成并发送成功！")
            BOT_STATUS["last_report"] = now_local
            BOT_STATUS["total_reports"] += 1
        else:
            logger.error(f"❌ 邮件发送失败")
            return False
        
        logger.info("=" * 80)
        logger.info(f"✨ {period_label}完成")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        error_msg = f"生成{period_label}失败: {str(e)}"
        logger.error(f"❌ {error_msg}", exc_info=True)
        
        BOT_STATUS["errors"].append({
            "time": datetime.now(),
            "error": error_msg
        })
        
        # 发送错误通知邮件
        try:
            send_error_notification(error_msg)
        except:
            pass
        
        return False


def start_scheduler():
    """启动定时调度器"""
    if scheduler.running:
        logger.warning("调度器已在运行中")
        return
    
    # 清除现有任务
    scheduler.remove_all_jobs()
    
    # 添加定时任务
    report_times = CFG.get("report_times", ["09:00", "21:00"])
    
    for report_time in report_times:
        try:
            hour, minute = map(int, report_time.split(":"))
            label = "早报" if hour < 12 else "晚报"
            
            scheduler.add_job(
                generate_and_send_digest,
                CronTrigger(hour=hour, minute=minute, timezone=TZNAME),
                args=[label],
                id=f"daily_{label}_{report_time}",
                name=f"{label}({report_time})",
                replace_existing=True
            )
            
            logger.info(f"✅ 已添加定时任务: {label} - 每天 {report_time}")
            
        except Exception as e:
            logger.error(f"❌ 添加定时任务失败 ({report_time}): {e}")
    
    # 启动调度器
    scheduler.start()
    logger.info("🚀 调度器已启动")
    
    # 打印下次执行时间
    jobs = scheduler.get_jobs()
    for job in jobs:
        next_run = job.next_run_time
        logger.info(f"   📅 {job.name} 下次执行: {next_run}")


def stop_scheduler():
    """停止调度器"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("⏸️ 调度器已停止")


def show_status():
    """显示系统状态"""
    print("\n" + "=" * 80)
    print("📊 BioRxiv 肿瘤学研究推送系统 - 状态监控")
    print("=" * 80)
    
    uptime = datetime.now() - BOT_STATUS["start_time"]
    uptime_str = str(uptime).split('.')[0]
    
    print(f"\n🟢 运行状态: {'运行中' if BOT_STATUS['running'] else '已停止'}")
    print(f"⏱️  运行时长: {uptime_str}")
    print(f"📈 已生成报告: {BOT_STATUS['total_reports']} 份")
    print(f"📄 已处理文章: {BOT_STATUS['total_papers']} 篇")
    print(f"🌐 时区: {TZNAME}")
    print(f"⏰ 报送时间: {', '.join(CFG.get('report_times', []))}")
    print(f"⌛ 时间窗口: {WINDOW_H} 小时")
    
    if BOT_STATUS["last_fetch"]:
        print(f"📥 最后获取: {BOT_STATUS['last_fetch'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    if BOT_STATUS["last_report"]:
        print(f"📧 最后报告: {BOT_STATUS['last_report'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 显示定时任务
    if scheduler.running:
        jobs = scheduler.get_jobs()
        print(f"\n📅 定时任务 ({len(jobs)} 个):")
        for job in jobs:
            next_run = job.next_run_time
            print(f"   • {job.name}: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 显示错误
    if BOT_STATUS["errors"]:
        recent_errors = BOT_STATUS["errors"][-3:]
        print(f"\n⚠️  最近错误 ({len(BOT_STATUS['errors'])} 个):")
        for err in recent_errors:
            print(f"   • {err['time'].strftime('%H:%M:%S')}: {err['error']}")
    
    print("\n" + "=" * 80 + "\n")


async def manual_run(period_type="auto"):
    """
    手动运行一次报告生成
    
    Args:
        period_type: 报告类型 (am/pm/auto)
    """
    if period_type == "auto":
        # 根据当前时间自动判断
        now_local = now_in_tz(TZNAME)
        period_type = "am" if now_local.hour < 12 else "pm"
    
    label = "早报" if period_type.lower() == "am" else "晚报"
    
    logger.info(f"🎯 手动触发: {label}")
    success = await generate_and_send_digest(label, manual=True)
    
    if success:
        logger.info(f"✅ 手动生成{label}成功")
    else:
        logger.error(f"❌ 手动生成{label}失败")
    
    return success


async def main_loop():
    """主循环"""
    logger.info("\n" + "=" * 80)
    logger.info("🚀 BioRxiv 肿瘤学研究推送系统启动")
    logger.info("=" * 80)
    logger.info(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🌐 时区: {TZNAME}")
    logger.info(f"⏰ 报送时间: {', '.join(CFG.get('report_times', []))}")
    logger.info(f"📧 收件人: {os.getenv('EMAIL_RECIPIENT', '未配置')}")
    logger.info("=" * 80 + "\n")
    
    # 启动调度器
    start_scheduler()
    
    try:
        # 保持运行
        while True:
            await asyncio.sleep(60)  # 每分钟检查一次
            
    except KeyboardInterrupt:
        logger.info("\n收到退出信号...")
    finally:
        stop_scheduler()
        logger.info("👋 系统已停止")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status" or command == "smi":
            # 显示状态
            show_status()
            
        elif command == "run" or command == "rn":
            # 手动运行一次
            period = sys.argv[2] if len(sys.argv) > 2 else "auto"
            asyncio.run(manual_run(period))
            
        elif command == "test":
            # 测试模式：立即运行一次
            logger.info("🧪 测试模式：立即生成一次报告")
            asyncio.run(manual_run("auto"))
            
        else:
            print(f"未知命令: {command}")
            print("\n可用命令:")
            print("  python biorxiv_bot.py              - 启动服务")
            print("  python biorxiv_bot.py status       - 显示状态")
            print("  python biorxiv_bot.py run [am|pm]  - 手动运行一次")
            print("  python biorxiv_bot.py test         - 测试模式")
    else:
        # 默认：启动服务
        asyncio.run(main_loop())

