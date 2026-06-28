#!/usr/bin/env python3
"""每日必读 API — 处理 mark_read 请求"""
import json, os, sys
from datetime import date

WIKI = "/home/admin/wiki-info-sec"
STATE_FILE = os.path.join(WIKI, "daily_read.json")

def json_response(data, code=200):
    body = json.dumps(data, ensure_ascii=False)
    print(f"Status: {code}")
    print("Content-Type: application/json")
    print(f"Content-Length: {len(body.encode())}")
    print()
    print(body)

def handle_mark_read():
    """POST /api/mark_read?index=0"""
    qs = os.environ.get("QUERY_STRING", "")
    params = {}
    for p in qs.split("&"):
        if "=" in p:
            k, v = p.split("=", 1)
            params[k] = v
    
    idx = int(params.get("index", "0"))
    
    if not os.path.exists(STATE_FILE):
        json_response({"error": "no daily_read state"}, 404)
        return
    
    with open(STATE_FILE) as f:
        state = json.load(f)
    
    if idx >= len(state.get("read", [])):
        json_response({"error": "invalid index"}, 400)
        return
    
    state["read"][idx] = True
    # Update history
    if "history" in state and idx < len(state["articles"]):
        path = state["articles"][idx]["path"]
        if path in state["history"]:
            state["history"][path]["last_read"] = date.today().isoformat()
    
    if all(state["read"]):
        from datetime import datetime
        state["completed"] = True
        state["completed_at"] = datetime.now().isoformat()
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    json_response({"ok": True, "read": state["read"], "completed": state["completed"]})

def handle_status():
    """GET /api/daily_status"""
    if not os.path.exists(STATE_FILE):
        json_response({"date": date.today().isoformat(), "needs_refresh": True, "articles": [], "read": [], "completed": False})
        return
    
    with open(STATE_FILE) as f:
        state = json.load(f)
    
    today = date.today().isoformat()
    if state.get("date") != today:
        json_response({"date": today, "needs_refresh": True, "articles": [], "read": [], "completed": False})
        return
    
    json_response(state)

if __name__ == "__main__":
    method = os.environ.get("REQUEST_METHOD", "GET")
    path = os.environ.get("SCRIPT_NAME", "")
    
    if method == "POST" and "mark_read" in path:
        handle_mark_read()
    else:
        handle_status()
