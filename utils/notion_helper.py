from notion_client import Client
from datetime import datetime
import os

def create_notion_page(notion_token, database_id, question, answer, user="ユーザー名"):
    notion = Client(auth=notion_token)
    now = datetime.now().astimezone().isoformat()  # 日本時間も考慮

    return notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Title": {"title": [{"text": {"content": question}}]},
            "Answer": {"rich_text": [{"text": {"content": answer}}]},
            "Date": {"date": {"start": now}},
            "User": {"rich_text": [{"text": {"content": user}}]}
        }
    )
