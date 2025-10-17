# summarizer_api.py
"""
使用 SiliconFlow API (DeepSeek V3.2) 生成文章摘要
"""

import os
import requests
import json
import logging

logger = logging.getLogger(__name__)


PROMPT_TEMPLATE = """
你是一位世界顶尖的生物医学研究专家，专注于肿瘤学（Oncology）、癌症生物学（Cancer Biology）和单细胞组学（Single-cell Omics）领域。

**【关键要求】**：
你必须严格遵守以下五个核心标准（Quality Standards）：

**S1 - 极高准确性 (High Fidelity)**：
- 禁止出现任何"幻觉"（Hallucination）
- 所有数值、基因名、实验对象必须来自原文
- 如果原文没有明确数据，说明"未提供具体数值"

**S2 - 关注核心创新点 (Novelty Focus)**：
- 明确指出：新靶点？新模型？新机制？新策略？
- 避免大篇幅描述背景知识

**S3 - 关键定量数据提取 (Quantitative Data)**：
- 每篇文章必须提取至少1-2个关键数值
- 例如：准确率95.2%、肿瘤体积抑制率75%、P值、样本量等

**S4 - 肿瘤学相关性 (Oncology Context)**：
- 明确癌症类型（NSCLC、胶质母细胞瘤等）
- 明确分子靶点（EGFR、PD-L1、KRAS等）
- 明确技术平台（scRNA-seq、CRISPR等）

**S5 - 行动力 (Actionability)**：
- 读者能立即判断：是否与我的研究相关？
- 是否需要深入阅读？

---

# 🧬 肿瘤学与单细胞生物学研究深度报告

## 【期别】{period_label}
## 【时间范围】{since} ~ {now}
## 【文章数量】共 {total_papers} 篇

---

## 📊 一、研究全景概览

### 1.1 研究热点分布
请详细分析本期文章涵盖的主要研究领域和热点分布（200-300字）：
- 肿瘤类型分布（乳腺癌、肺癌、结直肠癌等）
- 研究技术分布（单细胞测序、空间转录组、CRISPR等）
- 研究主题分布（免疫治疗、肿瘤微环境、耐药机制等）

### 1.2 技术方法趋势
分析本期文章使用的主要技术方法和创新点：
- 单细胞/空间组学技术的应用情况
- 多组学整合分析的趋势
- 新兴技术平台和工具

### 1.3 研究范式演变
总结当前肿瘤研究的范式转变和未来方向

---

## 🔬 二、重点文章深度解析

请对**每篇文章**严格按照以下模板生成摘要：

---

### 📄 文章 [编号]

**【结构 A：文章元数据】**

**标题**：[完整文章标题]

**作者及单位**：[第一作者]（[单位]）、[通讯作者]（[单位]）

**来源**：[BioRxiv/PubMed/期刊名] | **DOI/链接**：[链接]

**发布日期**：[YYYY-MM-DD]

---

**【结构 B：核心摘要区】** *(由 DeepSeek V3.2 生成)*

**1️⃣ 研究痛点 (Background & Gap)** [1-2句话]
> 当前肿瘤治疗/认知中存在什么核心问题？
[基于原文的简洁描述]

**2️⃣ 核心创新 (Novel Contribution)** [2句话，最重要]
> 本文提出了什么新概念/新模型/新机制/新靶点？
- **创新类型**：[新靶点/新模型/新机制/新策略]
- **具体描述**：[详细说明创新点]

**3️⃣ 关键发现 (Key Findings & Data)** [2-3句话，必须含数值]
> 最重要的1-2个结果是什么？
- **发现1**：[描述] + **数据**：[具体数值，如 P<0.001, 准确率92%]
- **发现2**：[描述] + **数据**：[具体数值]
- **关键机制**：[如果有，描述生物学机制]

**4️⃣ 技术细节 (Methodology & Tech)** [1句话]
> 使用了哪些高通量/AI/计算方法？
[如：scRNA-seq + 深度学习模型 / CRISPR筛选 / 空间转录组]

**5️⃣ 结论与意义 (Conclusion & Impact)** [1句话]
> 对临床转化/未来研究的意义？
[简洁明确的价值陈述]

---

**【结构 C：AI 辅助标签与评分】**

**🏷️ 关键实体标签 (Entities)**：
- **癌症类型**：[具体癌种，如：非小细胞肺癌、胰腺癌]
- **关键基因/靶点**：[如：KRAS G12C、PD-L1、EGFR]
- **核心技术**：[如：scRNA-seq、空间转录组、GNN模型]

**🎯 AI 主题分类 (Topic)**：
- [主要分类：如 计算药理学/肿瘤微环境/免疫治疗/单细胞组学]
- [次要分类：如 耐药机制/生物标志物发现]

**⭐ 评估得分 (LLM Assessment)**：
- **相关性得分**：[1-10分，基于肿瘤学和单细胞技术的相关性]
- **创新性得分**：[1-10分，基于方法和发现的新颖性]
- **临床转化潜力**：[高/中/低]
- **阅读优先级**：[极高/高/中/低] + [推荐理由1句话]

**⚠️ 局限性提示**：
[简要指出1-2个研究局限，如：样本量较小/需要临床验证/机制尚不完全清楚]

---

## 🎓 三、学科交叉与技术整合分析

### 3.1 单细胞技术的应用深度
- 单细胞转录组学（scRNA-seq）的最新应用
- 空间转录组学（Spatial Transcriptomics）的突破
- 单细胞多组学（Multi-omics）整合策略
- 细胞异质性分析的新见解

### 3.2 肿瘤微环境研究进展
- TME细胞组成的新认识
- 细胞-细胞相互作用网络
- 免疫抑制机制
- 代谢重编程

### 3.3 精准医学与个体化治疗
- 基于组学的患者分层策略
- 耐药机制与克服策略
- 免疫治疗响应预测
- 联合治疗的理论基础

---

## 🔮 四、前沿趋势与未来展望

### 4.1 当前研究热点
详细分析3-5个最热门的研究方向，包括：
- 研究现状
- 技术瓶颈
- 突破方向

### 4.2 新兴技术展望
- 空间多组学的发展方向
- AI/机器学习在肿瘤研究中的应用
- 单细胞CRISPR筛选技术
- 活细胞成像技术

### 4.3 临床转化路径
- 从基础到临床的转化策略
- 监管与伦理考虑
- 商业化前景

### 4.4 学科融合趋势
- 系统生物学与网络医学
- 计算生物学的角色
- 工程学与生物学的交叉

---

## 💎 五、关键见解与启示

请总结本期最重要的3-5个**take-home message**：
1. [关键见解1：深入阐述]
2. [关键见解2：深入阐述]
3. [关键见解3：深入阐述]

---

## 📚 六、推荐阅读与延伸

### 必读文章（按重要性排序）
1. [文章标题] - 推荐理由
2. [文章标题] - 推荐理由
3. [文章标题] - 推荐理由

### 相关领域拓展
- 建议关注的相关研究方向
- 值得深入学习的技术方法
- 推荐的综述文章主题

---

## 🔗 七、完整文章列表

[按研究类型/重要性分类列出所有文章标题和链接]

---

## 📎 附录：原始数据

```json
{items_json}
```

---

**【严格要求】**：

1. ✅ **禁止幻觉**：所有数据必须来自原文，不得编造
2. ✅ **必须提取数值**：每篇文章至少1-2个关键数值
3. ✅ **明确癌症类型**：必须指出具体癌种（如果原文涉及）
4. ✅ **突出创新点**：用"新靶点/新模型/新机制"明确标注
5. ✅ **可操作性**：读者能立即判断是否需要深入阅读
6. ✅ **使用专业术语**：NSCLC、scRNA-seq、TME、PDX等标准缩写
7. ✅ **结构化输出**：严格按照上述模板格式输出

---

**请开始生成符合上述标准的深度分析报告**：
""".strip()


def generate_summary_with_api(cfg, period_label, since_str, now_str, items_json):
    """
    使用 SiliconFlow API 生成摘要
    
    Args:
        cfg: 配置字典
        period_label: 期别标签（早报/晚报）
        since_str: 开始时间字符串
        now_str: 结束时间字符串
        items_json: 文章数据的 JSON 字符串
        
    Returns:
        str: 生成的摘要文本
    """
    # 获取 API 配置
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        raise ValueError("未设置 SILICONFLOW_API_KEY 环境变量")
    
    api_url = "https://api.siliconflow.cn/v1/chat/completions"
    model = "deepseek-ai/DeepSeek-V3.2-Exp"
    
    # 解析文章数据
    papers = json.loads(items_json)
    
    # 生成提示词
    prompt = PROMPT_TEMPLATE.format(
        period_label=period_label,
        since=since_str,
        now=now_str,
        total_papers=len(papers),
        items_json=items_json
    )
    
    # 构建 API 请求
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一位世界顶尖的生物医学研究专家，拥有肿瘤学、单细胞生物学和精准医学的深厚背景。你擅长深度分析科研文献，能够洞察研究的创新点、技术细节和临床转化价值。你的分析既专业严谨又富有洞察力。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.8,  # 提高温度以获得更有创造性的分析
        "max_tokens": 16000,  # 大幅增加token限制以支持深度分析
        "top_p": 0.95,
    }
    
    try:
        logger.info(f"正在调用 SiliconFlow API 生成摘要...")
        logger.info(f"使用模型: {model}")
        logger.info(f"处理文章数: {len(papers)}")
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        summary = result['choices'][0]['message']['content'].strip()
        
        logger.info(f"摘要生成成功，长度: {len(summary)} 字符")
        
        # 添加原始数据链接
        summary += f"\n\n---\n\n## 原始数据\n\n```json\n{items_json}\n```"
        
        return summary
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API 调用失败: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"响应内容: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"生成摘要时发生错误: {e}")
        raise


def run_ollama(cfg, period_label, since_str, now_str, items_json):
    """
    兼容性函数：保持与原代码的接口一致
    实际调用 SiliconFlow API
    """
    return generate_summary_with_api(cfg, period_label, since_str, now_str, items_json)

