import streamlit as st
import openai
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="AI選書チャットボット",
    page_icon="📚",
    layout="wide"
)

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは！AI選書チャットボットです。\n\nあなたにぴったりの本を選ぶお手伝いをします。\n\n・最近興味があることは何ですか？\n・どんなジャンルの本が読みたいですか？\n・最近読んで面白かった本はありますか？\n\n教えてください！"}
    ]

# サイドバー設定
with st.sidebar:
    st.title("📚 AI選書チャットボット")
    st.write("---")
    
    # APIキーの入力
    if "OPENAI_API_KEY" in os.environ:
        st.success("OpenAI APIキーが設定されています", icon="✅")
        openai.api_key = os.environ["OPENAI_API_KEY"]
    else:
        openai.api_key = st.text_input("OpenAI APIキーを入力してください", type="password")
        if not openai.api_key.startswith('sk-'):
            st.warning('OpenAIのAPIキーを入力してください', icon='⚠')
            st.stop()
        else:
            st.success('APIキーが設定されました！', icon='👉')
    
    st.write("---")
    if st.button("会話をリセット"):
        st.session_state.messages = [
            {"role": "assistant", "content": "会話をリセットしました。\n\n改めて、どんな本をお探しですか？"}
        ]
        st.rerun()

# チャットメッセージの表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力
if prompt := st.chat_input("メッセージを入力..."):
    # ユーザーメッセージを表示
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # セッションにユーザーメッセージを追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # アシスタントの応答を生成
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # OpenAI APIを呼び出し
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたはプロの司書です。ユーザーの興味や好みに基づいて本を推薦してください。会話を通じてユーザーの好みを深掘りし、適切な本を3〜5冊推薦してください。推薦する際は、本のタイトル、著者名、簡単な説明、そしてなぜその本を推薦するのかの理由を述べてください。"}
                ] + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            # ストリーミングでレスポンスを表示
            for chunk in response:
                if "content" in chunk.choices[0].delta:
                    chunk_content = chunk.choices[0].delta["content"]
                    full_response += chunk_content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            error_msg = f"申し訳ありません、エラーが発生しました: {str(e)}"
            st.error(error_msg)
            full_response = error_msg
    
    # セッションにアシスタントの応答を追加
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# フッター
st.sidebar.markdown("---")
st.sidebar.caption("© 2025 AI選書チャットボット")
