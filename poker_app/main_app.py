import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

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

# Firebase Admin SDKの初期化
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Firestoreのインスタンスを取得
db = firestore.client()

# Counters Collection to keep track of IDs
def get_next_id(collection_name):
    counter_ref = db.collection('Counters').document(collection_name)
    counter_doc = counter_ref.get()

    if counter_doc.exists:
        current_value = counter_doc.to_dict()['current']
        next_value = current_value + 1
        counter_ref.update({'current': next_value})
    else:
        next_value = 1
        counter_ref.set({'current': next_value})

    return next_value

# ユーザーの追加
def add_user(name):
    user_id = get_next_id('Users')  # Get next user ID
    doc_ref = db.collection('Users').document(str(user_id))
    doc_ref.set({
        'name': name,
        'created_at': firestore.SERVER_TIMESTAMP
    })
    return user_id

# ゲームの追加
def add_game(date, rate):
    game_id = get_next_id('Games')  # Get next game ID
    doc_ref = db.collection('Games').document(str(game_id))
    doc_ref.set({
        'date': date,
        'rate': rate
    })
    return game_id

# 戦績の追加
def add_record(user_id, game_id, date, result):
    user_ref = db.collection('Users').document(str(user_id))
    game_ref = db.collection('Games').document(str(game_id))
    
    db.collection('Records').add({
        'user_id': user_ref,  # user reference
        'game_id': game_ref,  # game reference
        'date': date,
        'result': result,
        'created_at': firestore.SERVER_TIMESTAMP
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
