# biorxiv_fetch.py
"""
BioRxiv 文章获取模块
支持通过 RSS Feed 获取最新的肿瘤学相关论文
"""

import feedparser
import re
from datetime import datetime, timedelta
from dateutil.tz import gettz
import time
import logging

logger = logging.getLogger(__name__)


def fetch_biorxiv_rss(category="cancer-biology", days=3):
    """
    从 BioRxiv RSS Feed 获取文章
    
    Args:
        category: BioRxiv 分类 (cancer-biology, cell-biology, etc.)
        days: 获取最近几天的文章
        
    Returns:
        list: 文章列表
    """
    # BioRxiv RSS Feed URLs
    rss_urls = [
        "https://connect.biorxiv.org/biorxiv_xml.php?subject=cancer_biology",
        "https://connect.biorxiv.org/biorxiv_xml.php?subject=cell_biology",
        "https://connect.biorxiv.org/biorxiv_xml.php?subject=immunology",
    ]
    
    all_articles = []
    seen_ids = set()
    
    for rss_url in rss_urls:
        try:
            logger.info(f"正在获取 RSS Feed: {rss_url}")
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries:
                # 提取文章ID（避免重复）
                article_id = entry.get('id', entry.get('link', ''))
                if article_id in seen_ids:
                    continue
                seen_ids.add(article_id)
                
                # 解析发布时间
                published_str = entry.get('published', entry.get('updated', ''))
                try:
                    # BioRxiv 时间格式: "Tue, 15 Oct 2024 00:00:00 GMT"
                    published_dt = datetime.strptime(published_str, "%a, %d %b %Y %H:%M:%S %Z")
                except:
                    published_dt = datetime.now()
                
                # 只获取最近几天的文章
                if (datetime.now() - published_dt).days > days:
                    continue
                
                all_articles.append({
                    'id': article_id,
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'authors': entry.get('author', 'Unknown'),
                    'published': published_dt,
                    'category': entry.get('category', category),
                })
                
            logger.info(f"从 {rss_url} 获取到 {len(feed.entries)} 篇文章")
            time.sleep(1)  # 避免请求过快
            
        except Exception as e:
            logger.error(f"获取 RSS Feed 失败: {e}")
            continue
    
    logger.info(f"总共获取到 {len(all_articles)} 篇文章")
    return all_articles


def filter_by_keywords(articles, queries, exclude_keywords=None):
    """
    根据关键词过滤文章
    
    Args:
        articles: 文章列表
        queries: 查询配置（any/all）
        exclude_keywords: 排除关键词列表
        
    Returns:
        list: 过滤后的文章列表
    """
    filtered = []
    exclude_keywords = exclude_keywords or []
    exclude_keywords = [k.lower() for k in exclude_keywords]
    
    for article in articles:
        title = article['title'].lower()
        abstract = article['summary'].lower()
        text = title + " " + abstract
        
        # 排除关键词检查
        if any(exc in text for exc in exclude_keywords if exc):
            continue
        
        # 关键词匹配检查
        matched = False
        
        for query_block in queries:
            if 'any' in query_block:
                # 任意一个关键词匹配即可
                any_keywords = [k.lower() for k in query_block['any']]
                if any(keyword in text for keyword in any_keywords):
                    matched = True
                    break
            
            if 'all' in query_block:
                # 所有关键词都必须匹配
                all_keywords = [k.lower() for k in query_block['all']]
                if all(keyword in text for keyword in all_keywords):
                    matched = True
                    break
        
        if matched:
            filtered.append(article)
    
    logger.info(f"关键词过滤后剩余 {len(filtered)} 篇文章")
    return filtered


def fetch_window(cfg, since_dt_local, now_local):
    """
    获取指定时间窗口内的 BioRxiv 文章
    
    Args:
        cfg: 配置字典
        since_dt_local: 开始时间
        now_local: 结束时间
        
    Returns:
        list: 文章列表
    """
    # 计算天数差
    days = (now_local - since_dt_local).days + 1
    days = max(1, min(days, 7))  # 限制在1-7天
    
    logger.info(f"开始获取 BioRxiv 文章: {since_dt_local} ~ {now_local} ({days}天)")
    
    # 获取 RSS 文章
    articles = fetch_biorxiv_rss(days=days)
    
    # 关键词过滤
    queries = cfg.get("queries", [])
    exclude = cfg.get("exclude", [])
    
    if queries:
        articles = filter_by_keywords(articles, queries, exclude)
    
    # 时间过滤（确保在时间窗口内）
    filtered_articles = []
    for article in articles:
        pub_dt = article['published']
        if since_dt_local <= pub_dt <= now_local:
            filtered_articles.append(article)
    
    # 按发布时间降序排序
    filtered_articles.sort(key=lambda x: x['published'], reverse=True)
    
    # 限制数量
    max_items = cfg.get("digest_max_items", 20)
    result = filtered_articles[:max_items]
    
    logger.info(f"最终获取到 {len(result)} 篇符合条件的文章")
    return result


def pack_papers(cfg, articles):
    """
    将文章转换为统一的 JSON 格式
    
    Args:
        cfg: 配置字典
        articles: 文章列表
        
    Returns:
        list: JSON 格式的文章列表
    """
    data = []
    max_abs = int(cfg.get("abstract_max_chars", 500))
    
    for article in articles:
        # 处理摘要长度
        abs_text = re.sub(r"\s+", " ", article.get('summary', '')).strip()
        if len(abs_text) > max_abs:
            abs_text = abs_text[:max_abs] + "…"
        
        # 处理作者（如果是字符串则分割）
        authors = article.get('authors', 'Unknown')
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(',')]
        
        data.append({
            "id": article.get('id', ''),
            "title": article.get('title', '').strip().replace("\n", " "),
            "authors": authors,
            "primary_category": article.get('category', 'cancer-biology'),
            "published": article.get('published').isoformat() if isinstance(article.get('published'), datetime) else str(article.get('published')),
            "link": article.get('link', ''),
            "abstract": abs_text,
        })
    
    logger.info(f"打包完成: {len(data)} 篇文章")
    return data

