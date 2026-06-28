#!/usr/bin/env python3
"""每日必读 — 选取2篇 + 生成 daily_read.json"""
import json, os, random
from datetime import datetime, date

WIKI = "/home/admin/wiki-info-sec"
STATE = os.path.join(WIKI, "daily_read.json")

pages = []
pl = os.path.join(WIKI, "page_list.json")
if os.path.exists(pl):
    with open(pl) as f:
        pages = json.load(f)

if not pages:
    print("No pages")
    exit(1)

today = date.today().isoformat()

# 加载历史
history = {}
if os.path.exists(STATE):
    with open(STATE) as f:
        old = json.load(f)
        if old.get("date") == today and old.get("articles"):
            print(f"Already picked for {today}")
            exit(0)
        history = old.get("history", {})

# 按未读优先 + 最久未读排序
def sort_key(p):
    h = history.get(p["path"], {})
    return (h.get("times", 0), h.get("last_read", "2000-01-01"))

pages.sort(key=sort_key)
selected = pages[:2]

# 更新历史
for p in selected:
    path = p["path"]
    history.setdefault(path, {"times": 0, "last_read": ""})
    history[path]["times"] += 1

state = {
    "date": today,
    "articles": [{"path": p["path"], "title": p["title"], "domain": p["domain"], "type": p["type"]} for p in selected],
    "history": history
}

with open(STATE, 'w') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)

print(f"📖 {today}:")
for i, a in enumerate(state["articles"]):
    print(f"  {i+1}. {a['title']}")
