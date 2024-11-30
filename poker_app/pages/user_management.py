import sqlite3
import streamlit as st

# データベース操作用関数
def execute_query(query, params=()):
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def fetch_query(query, params=()):
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()
    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results

def update_user_name(user_id, new_name):
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()
    c.execute("UPDATE Users SET name = ? WHERE id = ?", (new_name, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect("poker_tool.db")
    c = conn.cursor()
    # ユーザー戦績の削除
    c.execute("DELETE FROM Records WHERE user_id = ?", (user_id,))
    # ユーザーの削除
    c.execute("DELETE FROM Users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# ユーザー管理ページ
st.title("ユーザー管理")

# ユーザー登録タブ
st.header("ユーザー登録")
new_user = st.text_input("ユーザー名を入力してください")
if st.button("登録する"):
    if new_user:
        try:
            execute_query("INSERT INTO Users (name) VALUES (?)", (new_user,))
            st.success(f"ユーザー '{new_user}' を登録しました。")
        except sqlite3.IntegrityError:
            st.error("このユーザー名は既に登録されています。")
    else:
        st.error("ユーザー名を入力してください。")

# 登録済みユーザーの表示
st.header("登録済みユーザー")
users = fetch_query("SELECT id, name, created_at FROM Users")
for user in users:
    st.write(f"ID: {user[0]} / 名前: {user[1]} / 登録日: {user[2]}")

# ユーザーリストの取得
user_options = fetch_query("SELECT id, name FROM Users")
if user_options:
    # ユーザー編集
    selected_user = st.selectbox("ユーザーを選択してください", user_options, format_func=lambda x: x[1])
    
    # 編集ボタン
    st.subheader("ユーザー名の編集")
    new_name = st.text_input("新しいユーザー名", value=selected_user[1])
    if st.button("ユーザー名を更新"):
        update_user_name(selected_user[0], new_name)
        st.success(f"{selected_user[1]} の名前が {new_name} に変更されました。")
    
    # 削除ボタン
    st.subheader("ユーザー削除")
    delete_confirm = st.radio(
        "本当にこのユーザーを削除してもよろしいですか？",
        ("いいえ", "はい")
    )
    
    if delete_confirm == "はい" and st.button(f"{selected_user[1]} を削除"):
        delete_user(selected_user[0])
        st.success(f"{selected_user[1]} を削除しました。")
else:
    st.error("ユーザーが登録されていません。")
