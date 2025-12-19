# 🧬 ArXivPush: 肿瘤学研究智能追踪与 AI 摘要推送系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE.md)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

## 📖 项目简介

**ArXivPush** 是一个专为肿瘤学（Oncology）研究人员设计的**全自动化文献追踪与 AI 摘要系统**。它能够定时从 **BioRxiv**、**PubMed**（涵盖 Nature/Science/Cell 等顶级期刊）以及 **arXiv** 抓取最新研究成果，利用先进的大语言模型（**DeepSeek-R1**）生成中英双语的**高质量深度摘要**，并以精美的 HTML 邮件形式推送至您的邮箱。

### 💡 为什么选择 ArXivPush？

- 📚 **节省时间**：每天为您节省至少 30 分钟的文献检索时间
- 🎯 **精准过滤**：智能关键词匹配，只推送您关注领域的高质量论文
- 🤖 **AI 赋能**：深度摘要提炼核心发现、创新点、临床意义与研究局限
- 📧 **即时获取**：定时推送到邮箱，随时随地掌握前沿动态
- 🔧 **高度定制**：灵活配置数据源、关键词、推送时间等参数

### ✨ 核心特性

#### 🔍 多源实时获取
- **BioRxiv**：通过 RSS 订阅获取生物医学预印本，覆盖肿瘤学、免疫学等领域
- **PubMed**：精准锁定 Nature、Science、Cell、NEJM、Lancet 等顶级期刊的最新研究
- **arXiv**（可选）：支持时间感知（Time-Aware）的迭代搜索，确保不漏掉任何重要文章

#### 🤖 深度 AI 摘要（S1-S5 质量标准）
系统采用 **DeepSeek-R1** 大语言模型，生成的摘要严格遵循五大质量维度：
- **S1 - 准确性**：忠实原文，避免过度解读
- **S2 - 创新点**：提炼研究的独特贡献与突破
- **S3 - 定量数据**：保留关键实验数据与统计结果
- **S4 - 肿瘤学语境**：结合领域知识进行深度解读
- **S5 - 行动力**：提示临床应用价值与研究方向

每篇论文摘要包含：
- 📌 研究方向与背景
- 🔬 核心发现与创新点
- 📊 关键实验数据
- 💊 临床意义与转化价值
- ⚠️ 研究局限与未来方向

#### 🧫 领域深度定制
内置针对前沿技术的关键词库：
- **单细胞测序**：scRNA-seq、single-cell transcriptomics、CyTOF
- **空间组学**：spatial transcriptomics、spatial proteomics
- **免疫治疗**：CAR-T、checkpoint inhibitor、PD-1/PD-L1、CTLA-4
- **肿瘤机制**：metastasis、tumor microenvironment (TME)、immune evasion
- **精准医疗**：liquid biopsy、ctDNA、biomarker

#### 📧 精美邮件推送
- ✉️ 响应式 HTML 设计，完美适配桌面端与移动端
- 📋 结构化展示：研究热点分析 → 重点文章解读 → 趋势洞察
- 🔗 一键直达原文链接（DOI/PubMed/BioRxiv）
- 🎨 Markdown 源文件同步保存，方便二次整理

#### ⏰ 全自动化运行
- 🕘 基于 APScheduler 的定时任务引擎
- 📅 支持自定义早报/晚报推送时间（默认 09:00 & 21:00）
- 🔄 自动去重，避免重复推送相同论文
- 💾 本地存储历史报告，按日期自动归档

#### 📊 智能状态监控
- 📈 实时查看系统运行状态、已生成报告数、已处理文章数
- ⏱️ 显示下次推送时间与任务排程
- 📝 详细日志记录，方便调试与优化

### 🎯 适用场景

| 用户群体 | 应用价值 |
|---------|---------|
| 🔬 **肿瘤学研究人员** | 跟踪前沿研究进展，发现潜在合作方向 |
| 🎓 **医学院学生/博士** | 学习最新研究方法，积累文献阅读经验 |
| 💊 **制药公司研发团队** | 关注药物靶点、临床试验与市场动态 |
| 🏥 **医院科室医生** | 了解肿瘤治疗新方法，优化诊疗方案 |
| 📰 **科技媒体/编辑** | 发掘热点话题，撰写科普文章 |

---

## 🚀 快速开始

### 前置要求

- ✅ Python 3.8 或更高版本
- ✅ 稳定的网络连接（需访问 arXiv、BioRxiv、PubMed API）
- ✅ SMTP 邮箱账号（推荐使用 QQ 邮箱或网易邮箱）
- ✅ SiliconFlow API Key（[免费注册](https://siliconflow.cn/)，赠送额度足够使用）

### 1️⃣ 克隆项目与安装依赖

```bash
# 克隆项目（或下载 ZIP 解压）
git clone https://github.com/Steven-ZN/arXivPush.git
cd arXivPush

# 安装 Python 依赖
pip install -r requirements.txt
```

**主要依赖包：**
- `feedparser`: RSS 订阅解析
- `APScheduler`: 定时任务调度
- `requests`: HTTP 请求
- `python-dotenv`: 环境变量管理
- `markdown`: Markdown 转 HTML

### 2️⃣ 配置环境变量

```bash
# 复制模板文件
cp env_template.txt .env

# 使用您喜欢的编辑器打开（Windows 用 notepad，Linux/Mac 用 nano 或 vim）
nano .env
```

**必须配置的项目：**

```ini
# SMTP 邮箱配置
SMTP_SENDER_EMAIL=your_email@qq.com          # 发件人邮箱
SMTP_PASSWORD=your_authorization_code        # 邮箱授权码（不是登录密码！）
EMAIL_RECIPIENT=recipient@example.com        # 收件人邮箱（可以是自己）

# AI 服务配置
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxxxx     # SiliconFlow API 密钥
```

> 💡 **如何获取 QQ 邮箱授权码？**
> 1. 登录 [QQ 邮箱网页版](https://mail.qq.com/)
> 2. 进入「设置」→「账户」→「POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务」
> 3. 开启「IMAP/SMTP 服务」
> 4. 按照提示发送短信，获取 16 位授权码（形如：`abcdabcdabcdabcd`）
> 
> 详细步骤见 [部署指南.md](./部署指南.md#邮箱配置详解)

> 💡 **如何获取 SiliconFlow API Key？**
> 1. 访问 [https://siliconflow.cn/](https://siliconflow.cn/) 注册账号
> 2. 进入控制台 → API Keys → 创建新的 API Key
> 3. 新用户赠送免费额度，足够日常使用

### 3️⃣ 自定义配置（可选但推荐）

编辑 `config.yaml` 文件，根据您的研究方向调整关键词：

```yaml
# 示例：如果您专注于免疫治疗研究
queries:
  - any:
      - immunotherapy
      - CAR-T
      - checkpoint inhibitor
      - PD-1
      - PD-L1
      - tumor microenvironment

# 设置推送时间
report_times:
  - '09:00'  # 早报
  - '21:00'  # 晚报
```

### 4️⃣ 测试运行

```bash
# 测试邮件发送功能
python3 test_email.py

# 手动生成一次报告（测试完整流程）
python3 biorxiv_bot.py run
```

如果成功，您将收到一封包含最新论文摘要的邮件！📧

### 5️⃣ 启动生产服务

```bash
# 方法 1：使用一键启动脚本（Linux/Mac）
chmod +x 快速启动.sh
./快速启动.sh

# 方法 2：手动后台启动（Linux/Mac）
nohup python3 biorxiv_bot.py > biorxiv_push.log 2>&1 &

# 方法 3：Windows 后台运行
start /B python biorxiv_bot.py > biorxiv_push.log 2>&1
```

**🎉 完成！** 系统现在将在每天 09:00 和 21:00 自动发送研究简报到您的邮箱。

---

## 📋 常用命令

### 服务管理

| 命令 | 说明 | 使用场景 |
|------|------|---------|
| `python3 biorxiv_bot.py` | 启动服务（前台运行） | 初次测试或调试 |
| `python3 biorxiv_bot.py status` | 查看系统状态 | 检查服务是否正常运行 |
| `python3 biorxiv_bot.py run` | 立即生成并发送一次报告 | 测试完整流程 |
| `python3 biorxiv_bot.py test` | 测试模式（不发送邮件） | 调试配置 |

### 日志管理

```bash
# 实时查看日志（Linux/Mac）
tail -f biorxiv_push.log

# 查看最近 50 行日志
tail -n 50 biorxiv_push.log

# Windows 查看日志
type biorxiv_push.log
```

### 进程管理

```bash
# 查看运行中的进程
ps aux | grep biorxiv_bot.py

# 停止服务
pkill -f biorxiv_bot.py

# 重启服务
pkill -f biorxiv_bot.py && nohup python3 biorxiv_bot.py > biorxiv_push.log 2>&1 &
```

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

