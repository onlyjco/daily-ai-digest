#!/usr/bin/env python3
"""Daily AI Digest — GitHub trending projects + AI news, delivered as a GitHub Issue."""

import datetime
import os
import re
import sys
import textwrap

import feedparser
import requests

# ── Config ──────────────────────────────────────────────────────────────

GH_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
GH_HEADERS = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"} if GH_TOKEN else {
    "Accept": "application/vnd.github.v3+json"}
GH_API = "https://api.github.com"

TODAY = datetime.date.today()
# Search window: last 7 days so we always have enough results
SINCE = TODAY - datetime.timedelta(days=7)
DATE_STR = TODAY.strftime("%Y-%m-%d")
SINCE_STR = SINCE.strftime("%Y-%m-%d")

RSS_FEEDS = [
    ("Hacker News", "https://hnrss.org/frontpage"),
    ("ArXiv AI", "https://rss.arxiv.org/rss/cs.AI"),
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
]
# ── GitHub Search ───────────────────────────────────────────────────────

def search_github(query, sort="stars", order="desc", per_page=15):
    """Search GitHub repos and return list of items."""
    url = f"{GH_API}/search/repositories"
    params = {"q": query, "sort": sort, "order": order, "per_page": per_page}
    try:
        resp = requests.get(url, headers=GH_HEADERS, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("items", [])
    except requests.RequestException as e:
        print(f"  <!-- GitHub Search error: {e} -->", file=sys.stderr)
        return []


def fetch_trending_projects():
    """Fetch trending repos across AI / Agent / Skill categories."""
    created_filter = f"created:>={SINCE_STR}"

    all_items = []

    # Query 1: AI / LLM
    q1 = f"{created_filter} ai llm gpt chatgpt openai claude llama mistral gemini stars:>5"
    all_items.extend(search_github(q1, per_page=10))

    # Query 2: Agent / Tool ecosystem
    q2 = f"{created_filter} agent langchain autogpt rag mcp a2a vector embedding stars:>5"
    all_items.extend(search_github(q2, per_page=10))

    # Query 3: Skills / plugins / templates
    q3 = f"{created_filter} skill plugin extension template workflow pipeline stars:>10"
    all_items.extend(search_github(q3, per_page=10))

    # Query 4: Catch-all for repos with very high stars
    q4 = f"{created_filter} stars:>50"
    all_items.extend(search_github(q4, per_page=8))

    # Deduplicate by repo id
    seen_ids = set()
    unique = []
    for item in all_items:
        if item["id"] not in seen_ids:
            seen_ids.add(item["id"])
            unique.append(item)

    # Sort by stars descending
    unique.sort(key=lambda x: x["stargazers_count"], reverse=True)
    return unique[:25]


def format_repo(item):
    """Format a single repo item as compact markdown."""
    name = item["full_name"]
    desc = (item["description"] or "").strip()
    stars = item["stargazers_count"]
    lang = item.get("language") or ""
    url = item["html_url"]
    topics = item.get("topics") or []
    today = item.get("stars_today", 0)

    # Build the line
    line = f"- **[{name}]({url})** ⭐{stars}"
    if lang:
        line += f"  `{lang}`"

    lines = [line]
    if desc:
        # Truncate long descriptions
        short_desc = textwrap.shorten(desc, width=140, placeholder="...")
        lines.append(f"  {short_desc}")
    if topics:
        topic_tags = " ".join(f"`{t}`" for t in topics[:5])
        lines.append(f"  {topic_tags}")
    return "\n".join(lines)


# ── RSS News ────────────────────────────────────────────────────────────

def fetch_news():
    """Fetch and parse RSS feeds, return list of (source, title, link, summary)."""
    entries = []
    session = requests.Session()
    session.headers.update({
        "User-Agent": "DailyDigest/1.0 (GitHub Action; daily AI news aggregator)"
    })
    for source_name, url in RSS_FEEDS:
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            feed = feedparser.parse(resp.text)
            for entry in feed.entries[:5]:
                title = (entry.get("title") or "").strip()
                link = entry.get("link") or ""
                summary_html = entry.get("summary") or entry.get("description") or ""
                # Strip HTML tags
                plain = re.sub(r"<[^>]+>", "", summary_html)
                plain = plain.replace("\n", " ").strip()
                summary = textwrap.shorten(plain, width=200, placeholder="...") if plain else ""
                entries.append((source_name, title, link, summary))
        except Exception as e:
            entries.append((source_name, f"[Feed error: {e}]", "", ""))
    return entries


# ── Formatter ───────────────────────────────────────────────────────────

def build_digest(projects, news):
    """Assemble the full markdown digest."""
    lines = []
    lines.append(f"# 🌅 AI 日报 · {DATE_STR}")
    lines.append("")
    lines.append(f"> 自动汇总 GitHub 高分项目 & AI 资讯  |  数据范围: {SINCE_STR} ~ {DATE_STR}")
    lines.append("")

    # ── Section 1: GitHub Projects ──
    lines.append("---")
    lines.append("## 🔥 今日高分项目")
    lines.append("")

    ai_count = agent_count = skill_count = other_count = 0
    for repo in projects:
        desc = (repo.get("description") or "").lower()
        topics = " ".join(repo.get("topics") or []).lower()
        text = desc + " " + topics
        if any(w in text for w in ["ai", "llm", "gpt", "chatgpt", "openai", "claude", "llama", "mistral"]):
            ai_count += 1
        elif any(w in text for w in ["agent", "langchain", "autogpt", "rag", "mcp", "a2a", "vector", "embedding"]):
            agent_count += 1
        elif any(w in text for w in ["skill", "plugin", "extension", "template", "workflow", "pipeline", "action", "hook"]):
            skill_count += 1
        else:
            other_count += 1

    categories = []
    if ai_count:
        categories.append(f"🤖 AI × {ai_count}")
    if agent_count:
        categories.append(f"⚡ Agent × {agent_count}")
    if skill_count:
        categories.append(f"🧩 Skill × {skill_count}")
    if other_count:
        categories.append(f"📦 其他 × {other_count}")
    lines.append(f"> {' ｜ '.join(categories)}")
    lines.append("")

    for i, repo in enumerate(projects, 1):
        lines.append(format_repo(repo))
        lines.append("")

    # ── Section 2: AI News ──
    lines.append("---")
    lines.append("## 📰 AI 资讯")
    lines.append("")

    current_source = None
    for source, title, link, summary in news:
        if source != current_source:
            lines.append(f"### {source}")
            lines.append("")
            current_source = source
        if link:
            lines.append(f"- **[{title}]({link})**")
        else:
            lines.append(f"- **{title}**")
        if summary:
            lines.append(f"  > {summary}")
        lines.append("")

    # ── Footer ──
    lines.append("---")
    lines.append(f"> 🤖 由 GitHub Actions 自动生成 · {DATE_STR}")
    lines.append("")

    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────────

def main():
    projects = fetch_trending_projects()
    news = fetch_news()
    digest = build_digest(projects, news)
    print(digest)

    # Report stats to stderr so stdout stays clean
    print(f"[Digest] {len(projects)} projects, {len(news)} news items", file=sys.stderr)


if __name__ == "__main__":
    main()
