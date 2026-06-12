# 🤖 AI 日报

每日自动推送 GitHub 高分项目 & AI 资讯到 Issues。

## 数据源

| 来源 | 内容 |
|------|------|
| 🔥 GitHub Search API | 近 7 日创建的 AI/Agent/Skill 高分仓库（4 组关键词搜索） |
| 📰 Hacker News | 技术热榜 |
| 📄 ArXiv AI | AI 新论文 |
| 💰 TechCrunch AI | AI 行业资讯 |

## 工作原理

1. **GitHub Actions** 每天 UTC 00:00（北京时间 08:00）自动触发
2. **Python 脚本** (`scripts/daily_digest.py`) 抓取并整理数据
3. **创建 Issue** — 格式整洁的日报直接推送到仓库 Issues 页面

## 手动触发

在 GitHub 仓库 → Actions → **Daily AI Digest** → **Run workflow** 可随时手动运行。

## 本地测试

```bash
pip install -r scripts/requirements.txt
python scripts/daily_digest.py
```
