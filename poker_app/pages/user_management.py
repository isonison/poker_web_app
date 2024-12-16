import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

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

# Firestore操作用関数
def execute_query(collection, data):
    try:
        db.collection(collection).add(data)
    except Exception as e:
        st.error(f"Firestoreエラー: {e}")

def fetch_query(collection):
    try:
        docs = db.collection(collection).stream()
        return [(doc.id, doc.to_dict()) for doc in docs]
    except Exception as e:
        st.error(f"Firestoreエラー: {e}")
        return []

def update_user_name(user_id, new_name):
    try:
        user_ref = db.collection("Users").document(user_id)
        user_ref.update({"name": new_name})
    except Exception as e:
        st.error(f"Firestoreエラー: {e}")

def delete_user(user_id):
    try:
        # ユーザー戦績の削除
        records_ref = db.collection("Records").where("user_id", "==", user_id).stream()
        for record in records_ref:
            db.collection("Records").document(record.id).delete()

        # ユーザーの削除
        db.collection("Users").document(user_id).delete()
    except Exception as e:
        st.error(f"Firestoreエラー: {e}")

# ユーザー管理ページ
st.title("ユーザー管理")

# ユーザー登録タブ
st.header("ユーザー登録")
new_user = st.text_input("ユーザー名を入力してください")
if st.button("登録する"):
    if new_user:
        try:
            data = {"name": new_user, "created_at": firestore.SERVER_TIMESTAMP}
            execute_query("Users", data)
            st.success(f"ユーザー '{new_user}' を登録しました。")
        except Exception as e:
            st.error(f"ユーザー登録エラー: {e}")
    else:
        st.error("ユーザー名を入力してください。")

# 登録済みユーザーの表示
st.header("登録済みユーザー")
users = fetch_query("Users")
for user in users:
    st.write(f"ID: {user[0]} / 名前: {user[1]['name']} / 登録日: {user[1]['created_at']}")

# ユーザーリストの取得
user_options = fetch_query("Users")
if user_options:
    # ユーザー編集
    selected_user = st.selectbox("ユーザーを選択してください", user_options, format_func=lambda x: x[1]['name'])
    
    # 編集ボタン
    st.subheader("ユーザー名の編集")
    new_name = st.text_input("新しいユーザー名", value=selected_user[1]['name'])
    if st.button("ユーザー名を更新"):
        update_user_name(selected_user[0], new_name)
        st.success(f"{selected_user[1]['name']} の名前が {new_name} に変更されました。")
    
    # 削除ボタン
    st.subheader("ユーザー削除")
    delete_confirm = st.radio(
        "本当にこのユーザーを削除してもよろしいですか？",
        ("いいえ", "はい")
    )
    
    if delete_confirm == "はい" and st.button(f"{selected_user[1]['name']} を削除"):
        delete_user(selected_user[0])
        st.success(f"{selected_user[1]['name']} を削除しました。")
else:
    st.error("ユーザーが登録されていません。")
