# -*- coding: utf-8 -*-

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd

cred = credentials.Certificate(
    {
        "type": "service_account",
        "project_id": "htqltttt",
        "private_key_id": "b68aa79af62aa7728672b3615eecac0cd5002577",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCr7enz9/fG7ZO4\nJ4WjI/lpz0cBEd7rnDGgU/mV4Hetfvl285cpZJkNB0YaDNIL4OCOlEKol5Jpnkl4\nYlFqV1HvE5l6WuxditCjB0k+l/m+KalavZLebnhrG/8St47ZsRUcyyxA22yD/3NK\nK9yGZ05hpig+iVkONrFwtkN3508MNW2o9R4KJiyb2i5pPrHlGmtZ37uprh86N8JL\nYAjo5bHzCHTJzzXSSF6qfgcsyUMowdnRsmZ6ozpYSAKV9zSPspf4oq6xhbX24a8Q\nnqaTFlgaQkzTu8HQJmd75oHzuCfD/rvZGHs26Qe9rNNWbFWSp/DL4c5H1cSwJZ4H\nDwtxLbVNAgMBAAECggEAB9GTDQoqTqywM7TMaPAW8l72ir2OPXkqlN6ae5NQm7CX\nw4lt63gxMVf7+zaUeMjRKzGY/98J3//g2i2XA4kVMG+lGVzcvVZH9tDfpulr9k2z\nuJGcTysZpPTA6Ct/PqQgdOEd5Eu/YmENOMvs1snjwtfJEAZq1rnZ3qBlkzbYL+4W\nGjU5Ad3MxSQLf0E+K8OihW+hG6h4pzeL+E4KtWLiv0wwswJvO8/sv2oCRYt/k+jw\nGk9J2vMWuWyQ9AwxvIJ15i/cssKbnzm2aNZfVwkLjcSF1dxxEvYYJCwQOKnbxwEd\nb4ceaEDb3863VAVNzm+RVWLXvzvM5XA2XsI6HsgmmwKBgQDgWgw8yNfwKsNvof75\n6XB7gdzyId+/anwBl2K5bt2YQAAidS4ZpF+qY0/hRcgT7xfYinYJ2W93edva+Wo+\n6eyVMZ5TeO2IoQ5G5jIInPjoPfAIhqO4gaINHM3qnjMhST0NcjWBPvq1hOPyXplE\neM2IhN+50OVhrSozs5l+mTVZwwKBgQDELsAouypQVn1Es2rD1HaEGyTVwIiRyvFg\n6uNc1vNSD9eTdyEo5S9EwAgtrv7tqfvTY3+qVrkeKaLU7ufkgyJq/81mJ/jLnl3g\nreZ7UpkG8ux717yLZ3YdvjVArr1znZ7/LkOuph3u6w202K0JNWsIWqzlkKq200z1\niOowRyazrwKBgQCm5hZIedk6j3WIbGj0nZbSKo+liVGcYqkRvf7xl+o9ww7Wk3nS\nFZgdd3gLTBBF1A5XRtn9BcaIiRznT7icSQV5D8qKqmF6zOWEFOePxMbeboVMsmzF\na5qUSqNdMIc08fj7McVf+uwjcVLqETnP2FZ+guq0nxSlj17fy3Ia3fr0ZQKBgA+/\npQNgCwSJ/OJf+MkhrCXsu+dA3nW9seTS1k+kncHPrcGTxaCvzTyaoc1xB9vyUlnk\n2eHFtnSaaQzo5MquUDwAru9tdAZ8fxLDQwZRWiF5rMxARE14j73RgBriLCk01Qet\nIhfKFAsS6XXEExfzJtVz2f9PvrSQf9QSGqKng47XAoGABzK/dnBZakBgKFaF9+Xd\nhIgj9TH+SLGpsDcs3RcXhiNYi5Ja9TD+IVRB1wBbeUIJy5E9L+l2p0CTWHXf0x3t\nXShvmVyBkSfVrh21OnZ0bglLa0yFg9Xq+9L5JRmSA3BKxnSKJ8O2kEzm+Qu7RHJZ\nr4IByG1nX1M0WwIokRUeqkI=\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-4phbm@htqltttt.iam.gserviceaccount.com",
        "client_id": "111518443833287423565",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-4phbm%40htqltttt.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    }
)
firebase_admin.initialize_app(cred)

db = firestore.client()


def getTraineesData():
    trainee_ref = db.collection("trainees").stream()
    trainees = []
    for trainee in trainee_ref:
        formattedData = trainee.to_dict()
        trainees.append(formattedData)
    return trainees


getTraineesData()


def getCVData(userId):
    from google.cloud.firestore_v1.base_query import FieldFilter

    cv_ref = db.collection("cvs").where(filter=FieldFilter("uid", "==", userId)).get()
    cvs = []
    for cv in cv_ref:
        formattedData = cv.to_dict()
        cvs.append(formattedData)
    return cvs[0]


getCVData("b1913331")


def getCVsData():
    cv_ref = db.collection("cvs").stream()
    cvs = []
    for cv in cv_ref:
        formattedData = cv.to_dict()
        cvs.append(formattedData)
    return cvs


getCVsData()


def getFirmsData():
    firm_ref = db.collection("firms").stream()
    firms = []
    for firm in firm_ref:
        formattedData = firm.to_dict()
        firms.append(formattedData)
    return firms


getFirmsData()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Tiền xử lý dữ liệu
def preprocess_text(text):
    # Chuyển về chữ thường và loại bỏ ký tự đặc biệt và dấu câu không cần thiết
    text = text.lower()
    text = "".join(char for char in text if char.isalnum() or char.isspace())
    return text


# Tạo ma trận TF-IDF cho công ty
tfidf_vectorizer = TfidfVectorizer()
firm_fields = [preprocess_text(firm["describe"]) for firm in getFirmsData()]
tfidf_matrix_firms = tfidf_vectorizer.fit_transform(firm_fields)

# Tính độ tương đồng


def calculate_similarity(firm_tfidf, userId):
    cv_skills = preprocess_text(getCVData(userId)["skill"])
    tfidf_matrix_cv = tfidf_vectorizer.transform([cv_skills])
    similarity = cosine_similarity(tfidf_matrix_cv, firm_tfidf)
    return similarity[0]


# Tìm công ty phù hợp
def suggest_firms_user(userId):
    similarity_scores = calculate_similarity(tfidf_matrix_firms, userId)
    suggested_firms = [
        {
            "firmId": getFirmsData()[i]["firmId"],
            "firmName": getFirmsData()[i]["firmName"],
            "similarityScore": similarity_scores[i],
        }
        for i in range(len(getFirmsData()))
    ]
    suggested_firms.sort(key=lambda x: x["similarityScore"], reverse=True)
    return suggested_firms


from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok

# Intialise the app
app = Flask(__name__)


#  Create a route on our localmachine
@app.route("/suggest", methods=["POST"])
def recommendations():
    userId = request.args.get("userId")
    recommended_firms = []
    for sgf in suggest_firms_user(userId):
        recommended_firms.append(sgf)
    return jsonify(recommended_firms)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
