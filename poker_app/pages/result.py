import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# Firebase認証情報のロード
cred = credentials.Certificate({
    "type": st.secrets["type"],
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "auth_uri": st.secrets["auth_uri"],
    "token_uri": st.secrets["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["client_x509_cert_url"],
    "universe_domain": st.secrets["universe_domain"]
})

firebase_admin.initialize_app(cred)
db = firestore.client()

# Firestore操作用の関数
def execute_query(collection, data):
    db.collection(collection).add(data)

def fetch_query(collection):
    docs = db.collection(collection).stream()
    return [doc.to_dict() for doc in docs]

# Streamlitアプリ
st.title("ポーカーツール: ユーザー戦績管理")

# タブ
tab1, tab2 = st.tabs(["戦績登録", "戦績確認"])

# タブ1: 戦績登録
with tab1:
    st.header("戦績を登録する")
    
    # ユーザー選択
    user_options = fetch_query("Users")
    if user_options:
        user_names = [(user["id"], user["name"]) for user in user_options]
        selected_user = st.selectbox("ユーザーを選択してください", user_names, format_func=lambda x: x[1], key="user_selectbox")
        
        # ゲーム選択
        games = fetch_query("Games")
        game_options = [(game["game_id"], game["date"]) for game in games]
        
        if game_options:
            selected_game = st.selectbox("ゲームを選択してください", game_options, format_func=lambda x: f"ゲームID: {x[0]} - 日付: {x[1]}", key="game_selectbox")
            
            # 日付と収支の入力
            date = st.date_input("日付を選択してください", datetime.now().date())
            result = st.number_input("収支を入力してください", value=0.0, step=0.1)
            
            # 戦績登録
            if st.button("戦績を登録する"):
                record = {
                    "user_id": selected_user[0],
                    "game_id": selected_game[0],
                    "date": date,
                    "result": result
                }
                execute_query("Records", record)
                st.success(f"戦績を登録しました: ユーザー: {selected_user[1]}, ゲームID: {selected_game[0]}, 日付: {date}, 収支: {result}")

        else:
            st.error("登録されたゲームがありません。")
    else:
        st.error("まずはユーザーを登録してください。")

# タブ2: 戦績確認
with tab2:
    st.header("戦績確認")

    # 横軸の選択肢
    axis_option = st.radio("横軸を選択してください", ("日付", "ゲームID"))

    # ユーザー選択
    user_options = fetch_query("Users")
    if user_options:
        user_names = [(user["id"], user["name"]) for user in user_options]
        selected_user = st.selectbox("ユーザーを選択してください", user_names, format_func=lambda x: x[1], key="user_select_for_graph")
        records = fetch_query("Records")
        user_records = [record for record in records if record["user_id"] == selected_user[0]]

        if user_records:
            # データをDataFrameに変換
            df = pd.DataFrame(user_records)
            df["日付"] = pd.to_datetime(df["date"])  # 日付をDatetime型に変換
            df = df.sort_values(["日付"])  # 日付順に並び替え

            # 横軸が「日付」の場合
            if axis_option == "日付":
                # 同じ日の収支を合計
                df_grouped = df.groupby(["日付"]).agg({"result": "sum"}).reset_index()

                # トータル収支を計算
                total_profit = df_grouped["result"].sum()

                # グラフ表示
                st.subheader(f"{selected_user[1]} の収支合計（横軸: 日付）")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(df_grouped["日付"], df_grouped["result"], marker='o', color="skyblue", linestyle='-', label="収支")
                ax.set_title(f"{selected_user[1]} Total Results(By:Date)", fontsize=16)
                ax.set_xlabel("Date", fontsize=12)
                ax.set_ylabel("Income", fontsize=12)
                ax.legend()
                plt.grid()
                plt.xticks(rotation=45)
                st.pyplot(fig)

                # トータル収支を表示
                st.subheader(f"トータル収支: {total_profit:.2f}")

            # 横軸が「ゲームID」の場合
            elif axis_option == "ゲームID":
                # ゲームごとの収支
                df_grouped = df.groupby(["game_id"]).agg({"result": "sum"}).reset_index()

                # トータル収支を計算
                total_profit = df_grouped["result"].sum()

                # グラフ表示
                st.subheader(f"{selected_user[1]} の収支合計（横軸: ゲームID）")
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(df_grouped["game_id"], df_grouped["result"], marker='o', color="skyblue", linestyle='-', label="収支")
                ax.set_title(f"{selected_user[1]} Total Results(By:GameID)", fontsize=16)
                ax.set_xlabel("ゲームID", fontsize=12)
                ax.set_ylabel("収支", fontsize=12)
                ax.legend()
                plt.grid()
                st.pyplot(fig)

                # トータル収支を表示
                st.subheader(f"トータル収支: {total_profit:.2f}")

        else:
            st.info("このユーザーの戦績はまだありません。")
    else:
        st.error("まずはユーザーを登録してください。")
