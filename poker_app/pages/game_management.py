import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

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

# ゲーム登録ページ
st.title("ゲーム登録")

# ゲーム登録フォーム
game_date = st.date_input("ゲームの日付")
game_rate = st.number_input("レート（100bbあたりの円）", min_value=0.0, step=0.1)

def insert_game(date, rate):
    # Firestoreにゲームを追加
    db.collection("games").add({
        "date": date,
        "rate": rate
    })

def update_game(game_id, new_date, new_rate):
    # Firestoreのゲームを更新
    db.collection("games").document(game_id).update({
        "date": new_date,
        "rate": new_rate
    })

def delete_game(game_id):
    # Firestoreのゲームを削除
    db.collection("games").document(game_id).delete()

if st.button("ゲームを登録"):
    if game_date and game_rate > 0:
        insert_game(game_date, game_rate)
        st.success("ゲームが登録されました！")
    else:
        st.error("すべてのフィールドに入力してください。")

# 登録済みゲームの表示と編集・削除
st.header("登録済みゲームの管理")

# 登録されたゲームを取得
games_ref = db.collection("games")
games = [game.to_dict() for game in games_ref.stream()]

if games:
    # ゲームを選択
    selected_game_id = st.selectbox("編集・削除するゲームを選択", 
                                    [f"ゲームID: {game['game_id']} - 日付: {game['date']} - レート: {game['rate']}" for game in games])

    selected_game = next(game for game in games if f"ゲームID: {game['game_id']}" in selected_game_id)

    # 編集フォーム
    st.subheader("ゲーム編集")
    new_game_date = st.date_input("新しいゲームの日付", selected_game["date"])
    new_game_rate = st.number_input("新しいレート（100bbあたりの円）", min_value=0.0, value=float(selected_game["rate"]), step=0.1)

    if st.button("ゲームを更新"):
        update_game(selected_game["game_id"], new_game_date, new_game_rate)
        st.success(f"ゲームID: {selected_game['game_id']} が更新されました！")

    # 削除ボタン
    if st.button("ゲームを削除"):
        delete_game(selected_game["game_id"])
        st.success(f"ゲームID: {selected_game['game_id']} が削除されました！")
else:
    st.info("登録されているゲームはありません。")
