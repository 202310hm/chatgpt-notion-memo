import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
from notion_client import Client

# --- ヘルパー関数（Notionに保存） ---
def create_notion_page(token, database_id, question, answer, user, rating):
    notion = Client(auth=token)
    now = datetime.now().isoformat()

    try:
        notion.databases.retrieve(database_id=database_id)
    except Exception as e:
        raise RuntimeError(f"❌ データベースが見つかりません: {str(e)}")

    try:
        notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Title": {
                    "title": [{"text": {"content": question}}]
                },
                "Answer": {
                    "rich_text": [{"text": {"content": answer}}]
                },
                "Date": {
                    "date": {"start": now}
                },
                "User": {
                    "rich_text": [{"text": {"content": user}}]
                },
                "Rating": {
                    "multi_select": [{"name": rating}]
                }
            }
        )
    except Exception as e:
        raise RuntimeError(f"❌ Notionへの保存に失敗しました: {str(e)}")

# --- 環境変数の読み込み ---
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
notion_token = os.getenv("NOTION_API_KEY")
notion_db_id = os.getenv("NOTION_DATABASE_ID")

# 環境変数チェック
if not all([openai_key, notion_token, notion_db_id]):
    st.error("⚠️ 環境変数が正しく設定されていません。.envファイルを確認してください。")
    st.stop()

# --- OpenAIクライアント初期化 ---
client = OpenAI(api_key=openai_key)

# --- Streamlit UI設定 ---
st.set_page_config(page_title="ChatGPTメモ帳", page_icon="📝")
st.title("💬 ChatGPT + Notion メモ帳")
st.caption("質問を送ると、ChatGPTが答えてくれて、Notionに記録されます。")

# --- セッション初期化 ---
if "question" not in st.session_state:
    st.session_state.question = ""
if "answer" not in st.session_state:
    st.session_state.answer = ""
if "answered" not in st.session_state:
    st.session_state.answered = False

# --- 入力エリア ---
user_name = st.text_input("👤 ユーザー名", value="あなたの名前")
question_input = st.text_area("📌 質問を入力", height=100)

# --- ChatGPTに問い合わせるボタン ---
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
    st.text_area("回答", value=st.session_state.answer, height=300, disabled=True)

    rating = st.selectbox("⭐ 回答の評価を選んでください", ["Good", "Bad", "Pending"])

    if st.button("💾 Notionに保存"):
        try:
            create_notion_page(
                notion_token,
                notion_db_id,
                st.session_state.question,
                st.session_state.answer,
                user_name,
                rating
            )
            st.success("✅ Notionに保存されました！")
            # セッション初期化
            st.session_state.question = ""
            st.session_state.answer = ""
            st.session_state.answered = False
            st.rerun()
        except Exception as e:
            st.error(str(e))
            st.stop()
