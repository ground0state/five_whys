import streamlit as st
import openai
from streamlit_local_storage import LocalStorage


# システムプロンプト
SYSTEM_PROMPT = """
あなたは、Five whysに関するコンサルタントです。
あなたの目標は、私が抱えている課題に合わせて、課題の深堀をし、課題の解決策を探っていくことです。

次のプロセスに従ってください。

1. まず最初に、抱えている課題について私に確認してください。
私が質問の答えを提供するので、次のステップを経て、継続的な反復を通じて改善してください。

2. 私の入力に基づいて、次のように応答してください。
・確認（課題の内容について反復して確認してください。私に共感するような文章にしてください。）
・N回目の深堀り質問をしますと言います。
・課題の深堀質問（課題の内容を深堀するために、なぜその課題が生じているのか質問をしてくだい。このとき、あなたからなぜその課題が生じているのかの理由候補を水平思考で5つ挙げてください。）

3. 2のプロセスは、私があなたに追加情報を提供し、あなたが課題の深堀を「5回」まで反復して続けます。「5回」まで反復したら、必ず次のステップ4に移ってください。

4. 3の反復プロセスが終了したら5のプロセスに移ってください。

5. 深堀した課題に対して対策を水平思考で候補を5つ挙げてください（私は候補外の答えをするかもしれません）。

6. 5のプロセスは、私があなたに追加情報を提供し、あなたが課題の深堀を「私から終了と言うまで反復して繰り返してください」。

7. 6のプロセスが終了したら、今まで深堀した課題点と対策案を要約してまとめて出力してください。

※全体的に次の事項を遵守してください。
・私が出力を読みやすいように、適切に改行してください。
・私は課題の深堀や対策の深堀をしていき、疲れていきます。そこであなたは、私を励ますように優しい文章にすることを心がけてください。
"""


def LocalStorageManager():
    return LocalStorage()


local_storage = LocalStorageManager()

with st.sidebar:
    openai_api_key = local_storage.getItem("openai-api-key")
    if openai_api_key is None:
        openai_api_key = ""

    openai_api_key = st.text_input(
        "OpenAI API Key", key="chatbot_api_key", type="password", value=openai_api_key
    )
    st.write("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")
    local_storage.setItem("openai-api-key", openai_api_key)


# 過去のチャット履歴を保持する関数
def get_chat_history():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    return st.session_state["chat_history"]


# チャット履歴を更新する関数
def update_chat_history(role, content):
    st.session_state["chat_history"].append({"role": role, "content": content})


# Streamlitアプリ
def main():
    st.title("Five why analysis AI")

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    else:
        # OpenAI API keyを設定
        openai.api_key = openai_api_key

    # チャット履歴を取得
    chat_history = get_chat_history()

    if len(chat_history) == 0:
        st.chat_message("assistant").write("困っていることを入力してください！")

    # 過去のチャットを表示
    if chat_history:
        st.subheader("Chat History")
        for message in chat_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])

    # ユーザーの入力を受け取る
    if "is_processing" not in st.session_state:
        st.session_state["is_processing"] = False

    user_input = st.chat_input(key="user_input")

    if user_input:
        if user_input.strip():
            # ユーザーの入力をチャット履歴に追加
            update_chat_history("user", user_input)

            # OpenAI APIに送信するメッセージリストを準備
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history

            try:
                # OpenAI APIを呼び出し
                response = openai.chat.completions.create(
                    model="gpt-4o",  # gpt-4o-miniだとプロンプトの内容をあまり理解できない
                    messages=messages,
                )
                # APIの応答を取得
                assistant_message = response.choices[0].message.content

                # 応答をチャット履歴に追加
                update_chat_history("assistant", assistant_message)

            except Exception as e:
                st.error(f"An error occurred: {e}")

            # 最新のチャット履歴を表示
            st.rerun()


if __name__ == "__main__":
    main()
