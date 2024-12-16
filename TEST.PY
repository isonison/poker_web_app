import firebase_admin
from firebase_admin import credentials, firestore

# Firebase Admin SDKの初期化（サービスアカウント情報をハードコーディング）
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "mypokerapp-48ad1",
    "private_key_id": "fcecb780a0aa42f923199c7c18c3b612d3481776",
    "private_key": """
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCdZBFdc+Py9dLk
Xnv5MGflwRotwymHs9n1OBah5GBiofU8kqJUTU/18szaIyQaFwF7oiciInCG9qMU
PNJ76wWf/e9+gu6spBlIpY48A3yjspUIS+8zxeOEPT7nsmMgtdVdojR1EeLqneD2
g9HWKtxoSS8UbQeQLN1doSzkq11Zj+UBL/30xpzqkxkOP4Vm09p4OWZpujYUrhGy
WdXCO9r5ClfP+GhEKMQQwyqdia33hmhj0Lgi8Cf6YFDqPSZxiKVfpsG2wP520PX0
RJd+2F1FEn8fTy6W7NWxBZWdgmv+kwehUlsBhJczmL4wAD1WXrz8uAj33e95PH0N
pidJ4nI1AgMBAAECggEATh7KI7mPDhwH1kQzgqcNGtPy+33gEjQp3fY9/ZMOaEZ9
I9iga/mH08r09Nz2YWDD4qrEg8PWWJb4sOXTj6BCxXvUMNYqQ1ScHBvYcl9EsTfF
kz2ld+wkFpITtAst+qFmSzhkkysSl2NPsuwQ7h2OEtEoZhoL4/rw0TVbxBBuoDHt
rxOoj8k0hDD8btnaSl5lLOFYx0Zvq8nt+1qTNx94dXJ4Mo6d9y7EWTLImj+1OUoM
rGSn3hFUEbglozLLRUJlB9XJ1/tL0rG4bRIbjoCwcYiP15nSlGN9AT7tWuDt2Zuu
SiET1st3WE4POzH+carGrHvhGyWQGXZOPU0YTraOzQKBgQDLj470MnRgBC1+WEMk
uMpRx+42gvVW2HuZag71wqHmFJW/nJgL0qMZi3LPA2xjZUoIJv92aPAFiiJAjdZx
9oscUXPGQUddAOfY4rg09164sV6HGI0y6/fnSVMZubu8QblaQDn7MIUMmSx28FNz
eWMEJr31F10dXaVrQ5608HSTMwKBgQDF77G9q1vUNB23O5E6U/wEXKn9mZpb9qNj
lRMgxSVwKswUQvfYPxYHAhMLhIRYC2YQJmS6kC2nJ/SolfFISuBeA18ghyZaWyoW
JQm1RsJQYAl89KLRHRPhZ/UbFWjK9px3Sntqz8ip2zx88Ww6CRurzyIxmfPANh/N
satLEHXk9wKBgBGD1bIPUVIdqehwIb7cI5Rr1oRcOk3xrJjjtkvRJmsMpGHrUG3b
/uqoxAUp7z6SLY+MA3klyFlBrHbPfX8qzoduPr71SPWoqUpRH7Z2/nB32oFXTHbw
NNFyzrKs94lYQmGQmyyQ3THbUCcfwJ5z+GAYEUowa3OmZiBXniVFd1JfAoGBAJDP
gz8bfixrEI58owyEYy2hybBCz36WnAUADKV99pzwgqwULpVj2i64YsybX+O2Oy53
mFwxnWTcw48PXB4iwbGmT9NRbUrPxaO75zVbllANYwOrSu8okeHoF5d/+1H6SJCx
ykdjyxAR2FgknKR9A2SYPxEA7CbksjHf2U0qtsYTAoGAMkizTl2hPUp7qpj7F6nB
3KyX6yrlBrwP5R1CeKI9xZeQGpmR3Qo2djlIJhoj8msCm3X+kM/wK3eoLE6q1BwM
JbqfA7sOoxoSvTzyFqnVuc2D5C0NZWS7/9a4w0m/993nD7ZZZNfdwiCov7c8KZM5
DEualio3zo3zpmYIEXn1Pfk=
-----END PRIVATE KEY-----
    """,
    "client_email": "firebase-adminsdk-4sudi@mypokerapp-48ad1.iam.gserviceaccount.com",
    "client_id": "112512610072579085133",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-4sudi%40mypokerapp-48ad1.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})

# Firestoreのインスタンスを取得
firebase_admin.initialize_app(cred)
db = firestore.client()

# サンプルデータの追加
def test_firestore_connection():
    try:
        # `users` コレクションにサンプルデータを追加
        doc_ref = db.collection("users").document("test_user")
        doc_ref.set({
            "name": "Test User",
            "email": "test@example.com"
        })

        # データを取得して確認
        user_doc = doc_ref.get()
        if user_doc.exists:
            print("Firestoreにデータが正常に追加されました。")
            print(user_doc.to_dict())
        else:
            print("Firestoreにデータが存在しません。")
    except Exception as e:
        print(f"Firestoreへの接続に失敗しました: {e}")

# 関数を実行して接続確認
test_firestore_connection()
