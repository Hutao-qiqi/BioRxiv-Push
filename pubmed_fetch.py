# pubmed_fetch.py
"""
PubMed 文章获取模块
用于获取 Nature、Science、Cell 等顶级期刊的最新文章
"""

import requests
import time
import logging
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

# PubMed E-utilities API
PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
ESEARCH_URL = PUBMED_BASE_URL + "esearch.fcgi"
EFETCH_URL = PUBMED_BASE_URL + "efetch.fcgi"

# 顶级期刊列表
TOP_JOURNALS = {
    "Nature": "Nature[Journal]",
    "Science": "Science[Journal]",
    "Cell": "Cell[Journal]",
    "Nature Medicine": "Nature Medicine[Journal]",
    "Nature Biotechnology": "Nature Biotechnology[Journal]",
    "Nature Cancer": "Nature Cancer[Journal]",
    "Nature Cell Biology": "Nature Cell Biology[Journal]",
    "Nature Genetics": "Nature Genetics[Journal]",
    "Nature Immunology": "Nature Immunology[Journal]",
    "Nature Methods": "Nature Methods[Journal]",
    "Cell Stem Cell": "Cell Stem Cell[Journal]",
    "Cancer Cell": "Cancer Cell[Journal]",
    "Cancer Discovery": "Cancer Discovery[Journal]",
    "Immunity": "Immunity[Journal]",
    "Molecular Cell": "Molecular Cell[Journal]",
    "Developmental Cell": "Developmental Cell[Journal]",
}


def search_pubmed(query, days=7, max_results=100):
    """
    在 PubMed 搜索文章
    
    Args:
        query: 搜索查询字符串
        days: 获取最近几天的文章
        max_results: 最大结果数
        
    Returns:
        list: PubMed ID 列表
    """
    # 计算日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 格式化日期 (YYYY/MM/DD)
    date_range = f"{start_date.strftime('%Y/%m/%d')}:{end_date.strftime('%Y/%m/%d')}[dp]"
    
    # 构建查询
    full_query = f"{query} AND {date_range}"
    
    params = {
        "db": "pubmed",
        "term": full_query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "pub_date",
    }
    
    try:
        logger.info(f"正在搜索 PubMed: {query}")
        response = requests.get(ESEARCH_URL, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])
        
        logger.info(f"找到 {len(id_list)} 篇 PubMed 文章")
        return id_list
        
    except Exception as e:
        logger.error(f"PubMed 搜索失败: {e}")
        return []


def fetch_pubmed_details(pmid_list):
    """
    获取 PubMed 文章详细信息
    
    Args:
        pmid_list: PubMed ID 列表
        
    Returns:
        list: 文章详情列表
    """
    if not pmid_list:
        return []
    
    articles = []
    
    # 分批获取（每次最多200个）
    batch_size = 200
    for i in range(0, len(pmid_list), batch_size):
        batch = pmid_list[i:i + batch_size]
        batch_str = ",".join(batch)
        
        params = {
            "db": "pubmed",
            "id": batch_str,
            "retmode": "xml",
        }
        
        try:
            logger.info(f"正在获取 {len(batch)} 篇文章详情...")
            response = requests.get(EFETCH_URL, params=params, timeout=60)
            response.raise_for_status()
            
            # 解析 XML
            root = ET.fromstring(response.content)
            
            for article_elem in root.findall(".//PubmedArticle"):
                article = parse_pubmed_article(article_elem)
                if article:
                    articles.append(article)
            
            time.sleep(0.5)  # 避免请求过快
            
        except Exception as e:
            logger.error(f"获取 PubMed 详情失败: {e}")
            continue
    
    return articles


def parse_pubmed_article(article_elem):
    """
    解析单篇 PubMed 文章
    
    Args:
        article_elem: XML Element
        
    Returns:
        dict: 文章信息
    """
    try:
        # PMID
        pmid = article_elem.findtext(".//PMID")
        
        # 标题
        title = article_elem.findtext(".//ArticleTitle", "")
        
        # 摘要
        abstract_parts = article_elem.findall(".//AbstractText")
        abstract = " ".join([p.text or "" for p in abstract_parts if p.text])
        
        # 作者
        authors = []
        for author in article_elem.findall(".//Author"):
            last_name = author.findtext("LastName", "")
            fore_name = author.findtext("ForeName", "")
            if last_name:
                authors.append(f"{fore_name} {last_name}".strip())
        
        # 期刊
        journal = article_elem.findtext(".//Journal/Title", "")
        
        # 发布日期
        pub_date_elem = article_elem.find(".//PubDate")
        pub_date = None
        if pub_date_elem is not None:
            year = pub_date_elem.findtext("Year")
            month = pub_date_elem.findtext("Month", "1")
            day = pub_date_elem.findtext("Day", "1")
            
            try:
                # 尝试解析月份名称
                month_map = {
                    "Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4",
                    "May": "5", "Jun": "6", "Jul": "7", "Aug": "8",
                    "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"
                }
                month = month_map.get(month, month)
                
                date_str = f"{year}-{month}-{day}"
                pub_date = datetime.strptime(date_str, "%Y-%m-%d")
            except:
                pub_date = datetime.now()
        
        # DOI
        doi = ""
        for article_id in article_elem.findall(".//ArticleId"):
            if article_id.get("IdType") == "doi":
                doi = article_id.text
                break
        
        # 构建链接
        link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        if doi:
            link = f"https://doi.org/{doi}"
        
        return {
            "id": f"PMID:{pmid}",
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "journal": journal,
            "published": pub_date,
            "link": link,
            "doi": doi,
            "source": "PubMed",
        }
        
    except Exception as e:
        logger.error(f"解析文章失败: {e}")
        return None


def fetch_top_journals(keywords, days=7, max_per_journal=10):
    """
    从顶级期刊获取文章
    
    Args:
        keywords: 关键词列表
        days: 最近几天
        max_per_journal: 每个期刊最多获取文章数
        
    Returns:
        list: 文章列表
    """
    all_articles = []
    seen_pmids = set()
    
    # 构建关键词查询
    keyword_query = " OR ".join([f'"{kw}"' for kw in keywords[:5]])  # 只用前5个关键词
    
    for journal_name, journal_query in TOP_JOURNALS.items():
        try:
            logger.info(f"正在搜索 {journal_name}...")
            
            # 组合查询：期刊 + 关键词
            query = f"({journal_query}) AND ({keyword_query})"
            
            # 搜索文章
            pmid_list = search_pubmed(query, days=days, max_results=max_per_journal)
            
            if not pmid_list:
                continue
            
            # 获取详情
            articles = fetch_pubmed_details(pmid_list)
            
            # 去重并添加
            for article in articles:
                pmid = article.get("pmid")
                if pmid and pmid not in seen_pmids:
                    seen_pmids.add(pmid)
                    all_articles.append(article)
            
            logger.info(f"从 {journal_name} 获取到 {len(articles)} 篇文章")
            
            time.sleep(1)  # 避免请求过快
            
        except Exception as e:
            logger.error(f"从 {journal_name} 获取文章失败: {e}")
            continue
    
    logger.info(f"总共从顶级期刊获取到 {len(all_articles)} 篇文章")
    return all_articles


def filter_by_keywords(articles, keywords):
    """
    根据关键词过滤文章
    
    Args:
        articles: 文章列表
        keywords: 关键词列表
        
    Returns:
        list: 过滤后的文章
    """
    filtered = []
    
    for article in articles:
        title = article.get("title", "").lower()
        abstract = article.get("abstract", "").lower()
        text = title + " " + abstract
        
        # 检查是否包含任意关键词
        if any(kw.lower() in text for kw in keywords):
            filtered.append(article)
    
    return filtered


def fetch_pubmed_articles(cfg, days=7):
    """
    获取 PubMed 文章（主入口）
    
    Args:
        cfg: 配置字典
        days: 最近几天
        
    Returns:
        list: 文章列表
    """
    # 从配置中提取关键词
    keywords = []
    for query_block in cfg.get("queries", []):
        if "any" in query_block:
            keywords.extend(query_block["any"])
    
    # 去重
    keywords = list(set(keywords))
    
    logger.info(f"使用 {len(keywords)} 个关键词搜索 PubMed")
    logger.info(f"关键词: {', '.join(keywords[:10])}...")
    
    # 从顶级期刊获取文章
    articles = fetch_top_journals(keywords, days=days, max_per_journal=10)
    
    # 关键词过滤（二次筛选）
    articles = filter_by_keywords(articles, keywords)
    
    logger.info(f"关键词过滤后剩余 {len(articles)} 篇文章")
    
    return articles

