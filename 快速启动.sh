#!/bin/bash
# BioRxiv 肿瘤学文章推送系统 - 快速启动脚本

set -e

echo "=================================="
echo "🧬 BioRxiv 肿瘤学文章推送系统"
echo "=================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查 Python 版本
check_python() {
    echo "📌 检查 Python 版本..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        echo -e "${GREEN}✅ Python 版本: $PYTHON_VERSION${NC}"
    else
        echo -e "${RED}❌ 未找到 Python3，请先安装 Python 3.8+${NC}"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    echo ""
    echo "📌 检查依赖..."
    
    if [ -f "requirements.txt" ]; then
        echo -e "${GREEN}✅ requirements.txt 存在${NC}"
    else
        echo -e "${RED}❌ requirements.txt 不存在${NC}"
        exit 1
    fi
}

# 安装依赖
install_dependencies() {
    echo ""
    echo "📌 安装 Python 依赖..."
    
    if [ -d "venv" ]; then
        echo -e "${YELLOW}⚠️  虚拟环境已存在，跳过创建${NC}"
    else
        echo "创建虚拟环境..."
        python3 -m venv venv
        echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
    fi
    
    echo "激活虚拟环境..."
    source venv/bin/activate
    
    echo "安装依赖包..."
    pip install -r requirements.txt -q
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
}

# 检查配置文件
check_config() {
    echo ""
    echo "📌 检查配置文件..."
    
    # 检查 config.yaml
    if [ -f "config.yaml" ]; then
        echo -e "${GREEN}✅ config.yaml 存在${NC}"
    else
        echo -e "${RED}❌ config.yaml 不存在${NC}"
        exit 1
    fi
    
    # 检查 .env
    if [ -f ".env" ]; then
        echo -e "${GREEN}✅ .env 存在${NC}"
        
        # 检查必要的环境变量
        if grep -q "SMTP_SENDER_EMAIL=your_email" .env || grep -q "SMTP_PASSWORD=your_authorization" .env; then
            echo -e "${YELLOW}⚠️  警告: .env 文件似乎未正确配置${NC}"
            echo -e "${YELLOW}   请编辑 .env 文件，填写正确的邮箱配置${NC}"
            read -p "是否继续？(y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  .env 文件不存在${NC}"
        
        if [ -f "env_template.txt" ]; then
            echo "正在从模板创建 .env 文件..."
            cp env_template.txt .env
            echo -e "${GREEN}✅ .env 文件已创建${NC}"
            echo -e "${YELLOW}⚠️  请编辑 .env 文件，填写您的邮箱配置${NC}"
            echo -e "${YELLOW}   命令: nano .env${NC}"
            exit 0
        else
            echo -e "${RED}❌ env_template.txt 不存在${NC}"
            exit 1
        fi
    fi
}

# 显示菜单
show_menu() {
    echo ""
    echo "=================================="
    echo "请选择操作："
    echo "=================================="
    echo "1) 安装依赖"
    echo "2) 测试运行（立即生成一次报告）"
    echo "3) 启动服务（前台运行）"
    echo "4) 启动服务（后台运行）"
    echo "5) 查看状态"
    echo "6) 查看日志"
    echo "7) 停止服务"
    echo "8) 退出"
    echo "=================================="
    read -p "请输入选项 (1-8): " choice
}

# 执行选择
execute_choice() {
    case $choice in
        1)
            install_dependencies
            echo ""
            echo -e "${GREEN}🎉 依赖安装完成！${NC}"
            ;;
        2)
            echo ""
            echo "🧪 测试模式：立即生成一次报告..."
            if [ -d "venv" ]; then
                source venv/bin/activate
            fi
            python3 biorxiv_bot.py test
            ;;
        3)
            echo ""
            echo "🚀 启动服务（前台运行）..."
            if [ -d "venv" ]; then
                source venv/bin/activate
            fi
            python3 biorxiv_bot.py
            ;;
        4)
            echo ""
            echo "🚀 启动服务（后台运行）..."
            if [ -d "venv" ]; then
                source venv/bin/activate
            fi
            nohup python3 biorxiv_bot.py > biorxiv_push.log 2>&1 &
            PID=$!
            echo -e "${GREEN}✅ 服务已启动，进程 ID: $PID${NC}"
            echo "日志文件: biorxiv_push.log"
            echo "查看日志: tail -f biorxiv_push.log"
            ;;
        5)
            echo ""
            if [ -d "venv" ]; then
                source venv/bin/activate
            fi
            python3 biorxiv_bot.py status
            ;;
        6)
            echo ""
            echo "📋 最近 50 行日志："
            echo "=================================="
            if [ -f "biorxiv_push.log" ]; then
                tail -n 50 biorxiv_push.log
            else
                echo -e "${YELLOW}⚠️  日志文件不存在${NC}"
            fi
            ;;
        7)
            echo ""
            echo "⏸️  停止服务..."
            PID=$(ps aux | grep "biorxiv_bot.py" | grep -v grep | awk '{print $2}')
            if [ -z "$PID" ]; then
                echo -e "${YELLOW}⚠️  未找到运行中的服务${NC}"
            else
                kill $PID
                echo -e "${GREEN}✅ 服务已停止（进程 ID: $PID）${NC}"
            fi
            ;;
        8)
            echo ""
            echo "👋 再见！"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 无效选项${NC}"
            ;;
    esac
}

# 主流程
main() {
    check_python
    check_dependencies
    check_config
    
    # 如果没有参数，显示菜单
    if [ $# -eq 0 ]; then
        while true; do
            show_menu
            execute_choice
            echo ""
            read -p "按 Enter 继续..."
        done
    else
        # 如果有参数，直接执行命令
        case $1 in
            install)
                install_dependencies
                ;;
            test)
                if [ -d "venv" ]; then
                    source venv/bin/activate
                fi
                python3 biorxiv_bot.py test
                ;;
            start)
                if [ -d "venv" ]; then
                    source venv/bin/activate
                fi
                python3 biorxiv_bot.py
                ;;
            start-bg)
                if [ -d "venv" ]; then
                    source venv/bin/activate
                fi
                nohup python3 biorxiv_bot.py > biorxiv_push.log 2>&1 &
                echo "服务已后台启动"
                ;;
            status)
                if [ -d "venv" ]; then
                    source venv/bin/activate
                fi
                python3 biorxiv_bot.py status
                ;;
            stop)
                PID=$(ps aux | grep "biorxiv_bot.py" | grep -v grep | awk '{print $2}')
                if [ -z "$PID" ]; then
                    echo "未找到运行中的服务"
                else
                    kill $PID
                    echo "服务已停止"
                fi
                ;;
            *)
                echo "用法: $0 [install|test|start|start-bg|status|stop]"
                exit 1
                ;;
        esac
    fi
}

# 执行主流程
main "$@"

