# 🧬 BioRxiv 肿瘤学文章自动阅读系统(个人自用)

## 📖 项目简介

这是一个基于 AI 的自动化系统，专注于获取、分析和推送 BioRxiv ,pubmed平台上的肿瘤学（Oncology）相关最新研究文章。

### ✨ 主要特性

- 🔍 **多数据源获取**：BioRxiv RSS + PubMed 顶刊（Nature/Science/Cell 系）
- 🤖 **深度AI摘要（S1-S5 质量标准）**：严格遵循准确性、创新点、定量数据、肿瘤学语境与行动力五大标准
- 🧫 **单细胞/空间组学友好**：内置 scRNA-seq、Spatial、ATAC-seq 等关键词
- 📧 **邮件推送**：美观的 HTML 邮件格式
- ⏰ **定时任务**：每天自动运行，无需人工干预
- 🎯 **关键词过滤**：精准匹配肿瘤相关研究
- 📊 **实时监控**：随时查看系统运行状态

### 🎯 适用场景

- 肿瘤学研究人员跟踪最新研究进展
- 医学院学生学习最新肿瘤学知识
- 制药公司关注肿瘤药物研发动态
- 医院科室了解肿瘤治疗新方法

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
cd ./arXivPush
pip install -r requirements.txt
```

### 2️⃣ 配置环境变量

```bash
# 复制模板
cp env_template.txt .env

# 编辑配置（填写邮箱信息）
nano .env
```

**必须配置的项目**：
- `SMTP_SENDER_EMAIL`: 发件人邮箱
- `SMTP_PASSWORD`: 邮箱授权码（不是登录密码！）
- `EMAIL_RECIPIENT`: 收件人邮箱

AI 服务（已在模板中提供示例）：
- `SILICONFLOW_API_KEY`: SiliconFlow API 密钥

> 💡 **如何获取 QQ 邮箱授权码**：见 [部署指南.md](./部署指南.md#邮箱配置详解)

### 3️⃣ 测试运行

```bash
# 立即生成一次报告（测试用）
python3 biorxiv_bot.py test
```

### 4️⃣ 启动服务

```bash
# 后台运行
nohup python3 biorxiv_bot.py > biorxiv_push.log 2>&1 &
```

**就这么简单！**现在系统将在每天 09:00 和 21:00 自动发送研究简报到您的邮箱。

---

## 📋 常用命令

| 命令 | 说明 |
|------|------|
| `python3 biorxiv_bot.py` | 启动服务（前台运行） |
| `python3 biorxiv_bot.py status` | 查看系统状态 |
| `python3 biorxiv_bot.py run` | 手动运行一次 |
| `python3 biorxiv_bot.py test` | 测试模式 |
| `tail -f biorxiv_push.log` | 实时查看日志 |

---

## ⚙️ 配置说明

### 修改报告时间

编辑 `config.yaml`：

```yaml
report_times:
  - '09:00'  # 早报
  - '21:00'  # 晚报
```

### 自定义关键词

编辑 `config.yaml` 的 `queries` 部分：

```yaml
queries:
  - any:  # 任意匹配
      - breast cancer
      - lung cancer
      - immunotherapy
```

### 核心配置项

编辑 `config.yaml`：

```yaml
# 时间窗口（推荐 48 小时，避免遗漏每日 00:00 发布的文章）
time_window_hours: 48

# 报告时间
report_times:
  - '09:00'
  - '21:00'

# 文章数量与摘要长度
digest_max_items: 30        # 每次报告最多 30 篇（含顶刊）
abstract_max_chars: 1200    # 单文摘要截断上限

# 数据源开关
data_sources:
  biorxiv:
    enabled: true
    max_items: 20
  pubmed:
    enabled: true   # Nature / Science / Cell 等
    max_items: 15
    days: 3

# 关键词（示例，含单细胞/空间组学）
queries:
  - any:
      - oncology
      - cancer
      - tumor
  - any:
      - single-cell
      - scRNA-seq
      - spatial transcriptomics
      - ATAC-seq
  - any:
      - immunotherapy
      - CAR-T
      - PD-1
      - PD-L1
```

---

## 📂 项目结构

```
arXivPush/
├── biorxiv_bot.py          # 主程序（定时任务+邮件）
├── biorxiv_fetch.py        # BioRxiv RSS 文章获取
├── pubmed_fetch.py         # PubMed 顶刊（Nature/Science/Cell 等）
├── summarizer_api.py       # AI 摘要生成（DeepSeek V3.2）
├── email_sender.py         # SMTP 邮件发送
├── config.yaml             # 配置文件（关键词、时间等）
├── .env                    # 环境变量（API密钥、邮箱配置）
├── requirements.txt        # Python 依赖
├── test_email.py           # 邮件诊断脚本
├── 快速启动.sh             # 一键启动脚本
├── 部署指南.md             # 详细部署文档
└── README.md               # 本文件
```

---

## 🔧 技术栈

- **Python 3.8+**
- **SiliconFlow API**  - AI 摘要生成
- **BioRxiv RSS Feed** - 文章数据源
- **APScheduler** - 定时任务调度
- **SMTP** - 邮件发送
- **Markdown → HTML** - 邮件格式转换

---

## 📊 系统监控示例

```bash
$ python3 biorxiv_bot.py status

================================================================================
📊 BioRxiv 肿瘤学研究推送系统 - 状态监控
================================================================================

🟢 运行状态: 运行中
⏱️  运行时长: 3:24:15
📈 已生成报告: 8 份
📄 已处理文章: 142 篇
🌐 时区: Asia/Shanghai
⏰ 报送时间: 09:00, 21:00
⌛ 时间窗口: 48 小时

📅 定时任务 (2 个):
   • 早报(09:00): 2025-10-18 09:00:00
   • 晚报(21:00): 2025-10-18 21:00:00
```

---

## 📧 邮件样例

系统会发送格式精美的 HTML 邮件，包含：

1. **研究热点分析** - 本期文章的整体趋势
2. **重点文章解读** - 每篇文章的详细分析
   - 标题、作者
   - 研究方向
   - 核心发现
   - 创新点
   - 临床意义
3. **研究趋势洞察** - 热门方向、新兴技术
4. **文章链接** - 直达 BioRxiv 原文

---

## 🛠️ 常见问题

### Q: 邮件发送失败？

**A:** 检查以下几点：
1. 确认使用的是**授权码**而不是登录密码
2. 确认已在邮箱设置中开启 IMAP/SMTP 服务
3. 查看日志：`tail -f biorxiv_push.log`

### Q: 获取不到文章？

**A:** 
1. 检查网络连接
2. 测试 RSS Feed：`curl https://connect.biorxiv.org/biorxiv_xml.php?subject=cancer_biology`
3. 适当放宽关键词限制（修改 `config.yaml`）

### Q: API 调用失败？

**A:**
1. 确认 API 密钥正确
2. 检查 API 配额是否充足
3. 查看错误日志定位问题

更多问题请参考 [部署指南.md](./部署指南.md#常见问题)

---

## 📜 开源协议

本项目基于原 [arXivPush](https://github.com/Steven-ZN/arXivPush) 项目改造。

---

## 🙏 致谢

- 原项目：[arXivPush](https://github.com/Steven-ZN/arXivPush) by Steven-ZN
- AI 服务：[SiliconFlow](https://siliconflow.cn/)
- 数据来源：[BioRxiv](https://www.biorxiv.org/)

---

## 📞 联系方式

如有问题或建议，请：
1. 查看 [部署指南.md](./部署指南.md)
2. 查看日志文件：`biorxiv_push.log`
3. 提交 Issue 到原项目仓库
4.邮箱联系liushuye@whu.edu.cn
---

**🎉 祝您科研顺利！**

