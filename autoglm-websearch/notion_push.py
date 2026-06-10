# -*- coding: utf-8 -*-
import sys
import io

# 强制 UTF-8 编码
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import httpx
import json
import os
from datetime import datetime

TOKEN       = "ntn_"  
DATABASE_ID = "37b7bac517208072901df527af0eb5f9"

def get_proxy():
    """获取系统代理"""
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    if http_proxy or https_proxy:
        return http_proxy or https_proxy
    return None

def push_topic(topic: dict):
    proxy = get_proxy()
    client = httpx.Client(proxy=proxy) if proxy else httpx.Client()
    
    # 确保数据是 UTF-8 编码
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "选题标题": {
                "title": [{"text": {"content": topic.get("title", "")}}]
            },
            "热度评级": {
                "select": {"name": topic.get("heat", "中")}
            },
            "来源平台": {
                "rich_text": [{"text": {"content": topic.get("source", "")}}]
            },
            "AI摘要": {
                "rich_text": [{"text": {"content": topic.get("summary", "")}}]
            },
            "参考链接": {
                "url": topic.get("url") or None
            },
            "日期": {
                "date": {"start": datetime.today().strftime("%Y-%m-%d")}
            }
        }
    }
    
    resp = client.post(
        "https://api.notion.com/v1/pages",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json; charset=utf-8"
        },
        json=payload,
        timeout=10
    )
    result = resp.json()
    if result.get("object") == "page":
        print("[OK] " + topic['title'])
    else:
        print("[FAIL] " + str(result))

if __name__ == "__main__":
    # 支持从文件路径参数读取
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            raw = f.read().strip()
    else:
        raw = sys.stdin.read().strip()
    topics = json.loads(raw)
    for t in topics:
        push_topic(t)
