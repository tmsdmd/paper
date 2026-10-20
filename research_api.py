import re
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


def clean_text(value):
    if not value:
        return ""
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def summarize_text(text, max_chars=600):
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    cleaned = [s.strip() for s in sentences if len(s.strip()) > 25]
    summary = " ".join(cleaned[:4])
    if len(summary) > max_chars:
        return summary[:max_chars].rsplit(" ", 1)[0] + "..."
    return summary


def search_arxiv(topic, max_results=5):
    query = quote(topic)
    url = f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "xml")
    results = []
    for entry in soup.find_all("entry"):
        title = clean_text(entry.find("title").get_text()) if entry.find("title") else ""
        summary = clean_text(entry.find("summary").get_text()) if entry.find("summary") else ""
        published = clean_text(entry.find("published").get_text()) if entry.find("published") else ""
        arxiv_id = clean_text(entry.find("id").get_text()) if entry.find("id") else ""
        authors = ", ".join([clean_text(a.get_text()) for a in entry.find_all("name")]) if entry.find_all("name") else ""
        results.append(
            {
                "title": title,
                "authors": authors,
                "year": published[:4] if published else "",
                "source_name": "arXiv",
                "source_url": arxiv_id,
                "source_type": "arXiv",
                "abstract": summary,
                "summary": summarize_text(summary),
                "keywords": "",
                "language": "English",
            }
        )
    return results


def search_crossref(topic, max_results=5):
    url = "https://api.crossref.org/works"
    params = {
        "query.title": topic,
        "rows": max_results,
        "select": "title,author,issued,DOI,URL,abstract",
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
    except Exception:
        return []

    payload = response.json()
    items = []
    for item in payload.get("message", {}).get("items", []):
        title = item.get("title", [""])[0]
        abstract = item.get("abstract", "")
        abstract = re.sub(r"<.*?>", " ", abstract)
        abstract = clean_text(abstract)
        authors = ", ".join([a.get("family", "") for a in item.get("author", [])])
        issued = item.get("issued", {}).get("date-parts", [[None]])[0][0]
        doi = item.get("DOI", "")
        url_value = item.get("URL", "")
        items.append(
            {
                "title": clean_text(title),
                "authors": authors,
                "year": str(issued) if issued else "",
                "source_name": "Crossref",
                "source_url": url_value or doi,
                "source_type": "Crossref",
                "abstract": abstract,
                "summary": summarize_text(abstract),
                "keywords": "",
                "language": "English",
            }
        )
    return items


def fetch_research(topic, max_results=5):
    results = []
    seen = set()
    for source in (search_arxiv(topic, max_results=max_results), search_crossref(topic, max_results=max_results)):
        for item in source:
            title = item.get("title", "").strip()
            if not title or title in seen:
                continue
            seen.add(title)
            results.append(item)
    return results
