import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase認証情報のロード
cred = credentials.Certificate({
    "type": st.secrets["firebase"]["type"],
    "project_id": st.secrets["firebase"]["project_id"],
    "private_key_id": st.secrets["firebase"]["private_key_id"],
    "private_key": st.secrets["firebase"]["private_key"],
    "client_email": st.secrets["firebase"]["client_email"],
    "client_id": st.secrets["firebase"]["client_id"],
    "auth_uri": st.secrets["firebase"]["auth_uri"],
    "token_uri": st.secrets["firebase"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
    "universe_domain": st.secrets["firebase"]["universe_domain"]
})

# Firebase Admin SDKの初期化
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Firestoreのインスタンスを取得
db = firestore.client()

# Firestoreにデータを挿入
def add_user(name):
    doc_ref = db.collection('Users').add({
        'name': name,
        'created_at': firestore.SERVER_TIMESTAMP
    })

def add_record(user_id, game_id, date, result):
    db.collection('Records').add({
        'user_id': user_id,
        'game_id': game_id,
        'date': date,
        'result': result,
        'created_at': firestore.SERVER_TIMESTAMP
    })

def add_game(date, rate):
    db.collection('game').add({
        'date': date,
        'rate': rate
    })

# Streamlitアプリ
st.title("全プレイヤー収支比較")

# 横軸の選択
axis_option = st.radio("横軸を選択してください", ("日付", "ゲームID"))

# Firestoreからユーザーを取得
users_ref = db.collection("Users")
users = users_ref.stream()

if users:
    all_records = []
    for user in users:
        records_ref = db.collection("Records").where("user_id", "==", user.id)
        records = records_ref.stream()
        for record in records:
            all_records.append((user.to_dict()['name'], record.to_dict()['date'], record.to_dict()['result'], record.to_dict()['game_id']))

    if all_records:
        # データをDataFrameに変換
        df = pd.DataFrame(all_records, columns=["ユーザー", "日付", "収支", "ゲームID"])
        df["日付"] = pd.to_datetime(df["日付"])  # 日付をDatetime型に変換
        df = df.sort_values(["ユーザー", "日付"])  # ユーザーごとに並び替え

        # 横軸が「日付」の場合
        if axis_option == "日付":
            # 同じ日の収支を合計
            df_grouped = df.groupby(["ユーザー", "日付"]).agg({"収支": "sum"}).reset_index()

            # トータル収支の計算
            total_profit = df_grouped.groupby("ユーザー")["収支"].sum().reset_index()
            total_profit = total_profit.rename(columns={"収支": "トータル収支"})

            # 折れ線グラフ作成
            st.subheader("全プレイヤーの収支折れ線グラフ（横軸: 日付）")
            fig, ax = plt.subplots(figsize=(12, 6))

            for user in df_grouped["ユーザー"].unique():
                user_data = df_grouped[df_grouped["ユーザー"] == user]
                ax.plot(user_data["日付"], user_data["収支"], marker='o', linestyle='-', label=user)

            ax.set_title("ALL USER RESULTS(BY: DATE)", fontsize=16)
            ax.set_xlabel("DATE", fontsize=12)
            ax.set_ylabel("RESULTS", fontsize=12)
            ax.legend(title="USER")
            plt.grid()
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # トータル収支を表示
            st.subheader("ユーザーごとのトータル収支")
            st.table(total_profit)

        # 横軸が「ゲームID」の場合
        elif axis_option == "ゲームID":
            # ゲームごとの収支を合計
            df_grouped = df.groupby(["ユーザー", "ゲームID"]).agg({"収支": "sum"}).reset_index()

            # トータル収支の計算
            total_profit = df_grouped.groupby("ユーザー")["収支"].sum().reset_index()
            total_profit = total_profit.rename(columns={"収支": "トータル収支"})

            # 折れ線グラフ作成
            st.subheader("全プレイヤーの収支折れ線グラフ（横軸: ゲームID）")
            fig, ax = plt.subplots(figsize=(12, 6))

            for user in df_grouped["ユーザー"].unique():
                user_data = df_grouped[df_grouped["ユーザー"] == user]
                ax.plot(user_data["ゲームID"], user_data["収支"], marker='o', linestyle='-', label=user)

            ax.set_title("ALL USER RESULTS(BY: GAME ID)", fontsize=16)
            ax.set_xlabel("GAME ID", fontsize=12)
            ax.set_ylabel("RESULTS", fontsize=12)
            ax.legend(title="USER")
            plt.grid()
            st.pyplot(fig)

            # トータル収支を表示
            st.subheader("ユーザーごとのトータル収支")
            st.table(total_profit)

    else:
        st.info("戦績が登録されていません。")
else:
    st.error("まずはユーザーを登録してください。")
