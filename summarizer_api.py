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
你是一位专业的生物医学研究助手，专注于肿瘤学（Oncology）和癌症生物学（Cancer Biology）领域。

请基于以下 BioRxiv 文章数据，生成一份专业的中文研究简报。

要求：
1. 使用简洁专业的中文撰写
2. 重点关注肿瘤相关的研究进展
3. 对每篇文章进行精准的学术总结
4. 标注研究的创新点和临床意义
5. 使用清晰的层次结构

---

# 📊 BioRxiv 肿瘤学研究简报

## 【期别】{period_label}
## 【时间范围】{since} ~ {now}
## 【文章数量】共 {total_papers} 篇

---

## 一、研究热点分析

请根据文章内容，总结本期的主要研究热点和趋势（100-150字）。

---

## 二、重点文章解读

请对每篇文章进行深入解读，包括：
- **标题**：[文章标题]
- **作者**：[前3位作者]
- **研究方向**：[肿瘤类型/研究领域]
- **核心发现**：[3-4句话总结主要发现]
- **创新点**：[1-2句话说明创新之处]
- **临床意义**：[如何应用于临床或未来研究方向]

（请为所有文章生成以上格式的解读）

---

## 三、研究趋势洞察

根据本期文章，总结以下内容：
- **热门研究方向**：[总结最受关注的研究方向]
- **新兴技术**：[提及的新技术、新方法]
- **潜在突破**：[可能带来突破的研究]

---

## 四、文章链接

（请列出所有文章的标题和链接）

---

【数据来源】
以下是本期收录的所有文章详细信息（JSON格式）：

{items_json}

---

**重要提示**：
1. 必须严格基于提供的真实文章数据生成内容，不能编造
2. 使用专业的生物医学术语
3. 保持客观、准确、简洁的学术风格
4. 如果某篇文章不是肿瘤相关，也要进行总结但注明领域

请开始生成简报：
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
                "content": "你是一位专业的生物医学研究助手，擅长分析和总结肿瘤学领域的最新研究进展。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
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

