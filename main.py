# main.py

import streamlit as st
import os
from datetime import datetime
from notion_client import Client
from openai import OpenAI

# --- 環境変数からキー取得 ---
openai_key = os.getenv("OPENAI_API_KEY")
notion_token = os.getenv("NOTION_API_KEY")
notion_db_id = os.getenv("NOTION_DATABASE_ID")

# --- OpenAIクライアント初期化 ---
client = OpenAI(api_key=openai_key)

# --- Notionに保存する関数 ---
def create_notion_page(token, database_id, question, answer, user, rating):
    notion = Client(auth=token)
    now = datetime.now().isoformat()

    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Title": {"title": [{"text": {"content": question}}]},
            "Answer": {"rich_text": [{"text": {"content": answer}}]},
            "Date": {"date": {"start": now}},
            "User": {"rich_text": [{"text": {"content": user}}]},
            "Rating": {"multi_select": [{"name": rating}]}
        }
    )

# --- Streamlit UI設定 ---
st.set_page_config(page_title="ChatGPTメモ帳", page_icon="📝")
st.title("💬 ChatGPT + Notion メモ帳")

# --- セッションステート初期化 ---
if "question" not in st.session_state:
    st.session_state.question = ""
if "answer" not in st.session_state:
    st.session_state.answer = ""
if "answered" not in st.session_state:
    st.session_state.answered = False

# --- ユーザー入力 ---
user_name = st.text_input("👤 ユーザー名", value="あなたの名前")
question_input = st.text_area("📌 質問を入力", height=100)

# --- ChatGPTへ質問するボタン ---
if st.button("🚀 ChatGPTに聞く"):
    if question_input.strip():
        with st.spinner("ChatGPTに問い合わせ中..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": question_input}]
            )
            st.session_state.answer = response.choices[0].message.content
            st.session_state.question = question_input
            st.session_state.answered = True
    else:
        st.warning("質問を入力してください。")

# --- 回答があるときだけ表示 ---
if st.session_state.answered:
    st.markdown("---")
    st.subheader("📤 あなたの質問")
    st.markdown(f"> {st.session_state.question}")

    st.subheader("🤖 ChatGPTの回答")
    # ここで回答を黒文字ではっきり表示
    st.markdown(st.session_state.answer)


    st.markdown("---")
    st.subheader("⭐ 回答の評価を選んでください")

    # 3つのボタンを横並びに表示
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("👍 Good"):
            create_notion_page(
                notion_token,
                notion_db_id,
                st.session_state.question,
                st.session_state.answer,
                user_name,
                "Good"
            )
            st.success("✅ Good評価でNotionに保存しました！")
            st.session_state.question = ""
            st.session_state.answer = ""
            st.session_state.answered = False
            st.rerun()

    with col2:
        if st.button("👎 Bad"):
            create_notion_page(
                notion_token,
                notion_db_id,
                st.session_state.question,
                st.session_state.answer,
                user_name,
                "Bad"
            )
            st.success("✅ Bad評価でNotionに保存しました！")
            st.session_state.question = ""
            st.session_state.answer = ""
            st.session_state.answered = False
            st.rerun()

    with col3:
        if st.button("⏳ Pending"):
            create_notion_page(
                notion_token,
                notion_db_id,
                st.session_state.question,
                st.session_state.answer,
                user_name,
                "Pending"
            )
            st.success("✅ Pending評価でNotionに保存しました！")
            st.session_state.question = ""
            st.session_state.answer = ""
            st.session_state.answered = False
            st.rerun()
