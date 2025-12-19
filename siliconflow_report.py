import datetime
import json
from typing import Any, Tuple

import requests

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
DEFAULT_MODEL = "moonshotai/Kimi-K2-Instruct-0905"

# NOTE: 不建议把真实 API Key 写进代码/仓库；优先通过工作流入参 `api_key` 传入。
# 如果你的平台确实无法注入密钥，可在此处手动填写（风险自担，且务必避免提交到公开仓库）。
HARDCODED_API_KEY = "sk-oohbwbqzhiyxxrbixkzlmsyzrddhkfpiuntblsvborattxxm"

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

## 🔬 二、重点文章深度解析

请对**每篇文章**严格按照以下模板生成摘要,要美观，好看（禁止幻觉；数值/基因/癌种/靶点需来自原文；若无明确数据写“未提供具体数值”）：

---

## 📎 附录：原始数据

```json
{items_json}
```

---

**请开始生成符合上述标准的深度分析报告**：
""".strip()


def _normalize_items(items_value: Any) -> Tuple[str, list]:
    if items_value is None:
        return "[]", []
    if isinstance(items_value, (list, dict)):
        items_json = json.dumps(items_value, ensure_ascii=False)
        papers = items_value if isinstance(items_value, list) else [items_value]
        return items_json, papers

    items_str = str(items_value).strip()
    if not items_str:
        return "[]", []
    items_str = items_str.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(items_str)
    except Exception:
        return "[]", []

    if isinstance(parsed, str):
        try:
            parsed = json.loads(parsed)
        except Exception:
            return "[]", []

    if isinstance(parsed, list):
        return json.dumps(parsed, ensure_ascii=False), parsed
    if isinstance(parsed, dict):
        if "items" in parsed:
            return _normalize_items(parsed.get("items"))
        if "input" in parsed:
            return _normalize_items(parsed.get("input"))
        return json.dumps([parsed], ensure_ascii=False), [parsed]

    return "[]", []


def _call_siliconflow(
    *,
    api_key: str,
    model: str,
    prompt: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    timeout_seconds: int,
) -> str:
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是一位世界顶尖的生物医学研究专家，专注肿瘤学、癌症生物学与单细胞组学；输出需高保真、低幻觉、强调创新与定量数据。",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": float(temperature),
        "top_p": float(top_p),
        "max_tokens": int(max_tokens),
    }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=int(timeout_seconds))
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        detail = ""
        try:
            detail = resp.text[:2000]
        except Exception:
            detail = ""
        raise requests.HTTPError(f"{e}\n{detail}") from e

    data = resp.json()
    return (data["choices"][0]["message"]["content"] or "").strip()


def generate_report(
    *,
    api_key: str,
    items_value: Any,
    period_label: str,
    since: str,
    now: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    top_p: float = 0.95,
    max_tokens: int = 2048,
    timeout_seconds: int = 600,
    truncate_items_chars: int = 20000,
) -> str:
    items_json, papers = _normalize_items(items_value)
    if truncate_items_chars and len(items_json) > truncate_items_chars:
        items_json = items_json[:truncate_items_chars] + "\n...TRUNCATED..."

    prompt = PROMPT_TEMPLATE.format(
        period_label=period_label,
        since=since,
        now=now,
        total_papers=len(papers),
        items_json=items_json,
    ).strip()
    if not prompt:
        raise ValueError("Prompt is empty; check PROMPT_TEMPLATE.")

    return _call_siliconflow(
        api_key=api_key,
        model=model,
        prompt=prompt,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        timeout_seconds=timeout_seconds,
    )


def handler(params):
    """
    Workflow entrypoint:
      - input: JSON string / list / dict (papers)
      - api_key: SiliconFlow API key (bind via platform secret)
    Output:
      - output: generated report string
    """
    api_key = params.get("api_key") or HARDCODED_API_KEY
    if not api_key:
        return {"output": "❌ 缺少 api_key：优先通过工作流入参 api_key 传入；若平台不支持，请在代码顶部设置 HARDCODED_API_KEY（不推荐）"}

    items_value = params.get("input")
    if items_value is None:
        items_value = params.get("items")

    today = datetime.date.today().strftime("%Y-%m-%d")
    period_label = params.get("period_label", "日报")
    since = params.get("since", today)
    now = params.get("now", today)

    model = params.get("model", DEFAULT_MODEL)
    temperature = float(params.get("temperature", 0.7))
    top_p = float(params.get("top_p", 0.95))
    max_tokens = int(params.get("max_tokens", 2048))
    timeout_seconds = int(params.get("timeout_seconds", 600))
    truncate_items_chars = int(params.get("truncate_items_chars", 20000))

    try:
        text = generate_report(
            api_key=api_key,
            items_value=items_value,
            period_label=period_label,
            since=since,
            now=now,
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
            truncate_items_chars=truncate_items_chars,
        )
        return {"output": text}
    except Exception as e:
        return {"output": f"❌ 生成失败: {e}"}
