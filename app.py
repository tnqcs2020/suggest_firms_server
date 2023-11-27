import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask import Flask, request, jsonify
from underthesea import word_tokenize
import string
from nltk.stem.porter import PorterStemmer
import numpy as np

app = Flask(__name__)

cred = credentials.Certificate("htqltttt-key.json")

firebase_admin.initialize_app(cred)

tfidf = TfidfVectorizer(stop_words="english")


def readStopWords(fileName):
    with open(fileName, "r", encoding="utf-8") as file:
        stopWords = file.read().splitlines()
    return stopWords


stopWords = readStopWords("vietnamese-stopwords.txt")


def getCVsData(cvs_ref):
    cvs = []
    for cv in cvs_ref:
        formattedData = cv.to_dict()
        cvs.append(formattedData)
    return cvs


def getFirmsData(firm_ref):
    firms = []
    for firm in firm_ref:
        formattedData = firm.to_dict()
        firms.append(formattedData)
    return firms


def preprocess_text(text):
    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)
    # text = text.translate(translator).lower().split()

    text = word_tokenize(text, format="text").lower().split()

    noneStopWords = [word for word in text if word not in stopWords]
    text = ' '.join(noneStopWords)
    return text


def preprocess_dataframe(df, column_name):
    df[column_name] = df[column_name].apply(preprocess_text)
    return df


ps = PorterStemmer()


def stem(text):
    y= []
    for i in text.split():
        y.append(ps.stem(i))
    return ' '.join(y)


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/suggest", methods=["POST"])
def recommendations():
    userId = request.args.get("userId")

    db = firestore.client()

    cvs_ref = db.collection("cvs").stream()
    cvs = getCVsData(cvs_ref)

    firm_ref = db.collection("firms").stream()
    firms = getFirmsData(firm_ref)

    tags = []
    for firm in firms:
        temp = []
        for job in firm["listJob"]:
            temp.append(job["jobName"])
        tags.append(" ".join([firm["describe"], " ".join(temp)]))

    firm_data = pd.DataFrame(
        {
            "firmId": [firm["firmId"] for firm in firms],
            "firmName": [firm["firmName"] for firm in firms],
            "tags": tags,
        }
    )
    firms_df = preprocess_dataframe(firm_data, "tags")
    firms_df["tags"] = firms_df["tags"].apply(stem)

    cvs_df = pd.DataFrame(
        {
            "userId": [cv["userId"] for cv in cvs],
            "tags": [stem(" ".join([cv["skill"], cv["wish"]])) for cv in cvs],
        }
    )
    cvs_df = preprocess_dataframe(cvs_df, "tags")

    firms_matrix = tfidf.fit_transform(firms_df["tags"])
    cvs_matrix = tfidf.transform(cvs_df["tags"])

    user_item_matrix = linear_kernel(cvs_matrix, firms_matrix)

    firms_sugggest = []
    if len(cvs_df.index[cvs_df['userId'] == userId]) == 1:
        new_user_index = cvs_df.index[cvs_df['userId'] == userId][0]
        firms_matrix = tfidf.fit_transform(firms_df['tags'])
        new_user_matrix = tfidf.transform([cvs_df['tags'][new_user_index]])
        new_user_item_matrix = linear_kernel(new_user_matrix ,firms_matrix)

        new_user_similarity = linear_kernel(new_user_item_matrix, user_item_matrix )

        predicted_new_user = np.dot(new_user_similarity, user_item_matrix) / np.sum(
            np.abs(new_user_similarity), axis=1
        ).reshape(-1, 1)

        recommended_index = np.argsort(predicted_new_user[0])[::-1]

        for i in recommended_index:
            firms_sugggest.append(
                {
                    "firmId": firms[i]["firmId"],
                    "firmName": firms[i]["firmName"],
                    "similarityScore": predicted_new_user[0][i],
                }
            )
    return jsonify(firms_sugggest), {"Access-Control-Allow-Origin": "*"}


if __name__ == "__main__":
    app.run()

# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore
# import pandas as pd
# from google.cloud.firestore_v1.base_query import FieldFilter
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from flask import Flask, request, jsonify
# from underthesea import word_tokenize

# app = Flask(__name__)

# cred = credentials.Certificate("htqltttt-key.json")

# firebase_admin.initialize_app(cred)


# tfidf_vectorizer = TfidfVectorizer()


# def getCVData(cv_ref):
#     cvs = []
#     for cv in cv_ref:
#         formattedData = cv.to_dict()
#         cvs.append(formattedData)
#     return cvs


# def getCVsData(cvs_ref):
#     cvs = []
#     for cv in cvs_ref:
#         formattedData = cv.to_dict()
#         cvs.append(formattedData)
#     return cvs


# def getFirmsData(firm_ref):
#     firms = []
#     for firm in firm_ref:
#         formattedData = firm.to_dict()
#         firms.append(formattedData)
#     return firms


# def readStopWords(fileName):
#     with open(fileName, "r", encoding="utf-8") as file:
#         stopWords = file.read().splitlines()
#     return stopWords


# stopWords = readStopWords("vietnamese-stopwords.txt")


# def preprocess_text(text):
#     import string

#     translator = str.maketrans("", "", string.punctuation)
#     text = text.translate(translator)

#     text = word_tokenize(text, format="text").lower().split()

#     noneStopWords = [word for word in text if word not in stopWords]
#     text = " ".join(noneStopWords)

#     print(text)
#     return text


# @app.route("/")
# def hello_world():
#     return "Hello World!"


# @app.route("/suggest", methods=["POST"])
# def recommendations():
#     userId = request.args.get("userId")

#     db = firestore.client()

#     cvs_ref = db.collection("cvs").stream()
#     cvs = getCVsData(cvs_ref)

#     firm_ref = db.collection("firms").stream()
#     firms = getFirmsData(firm_ref)

#     suggested_firms = []

#     for cv in cvs:
#         if cv["userId"] == userId:
#             for firm in firms:
#                 for job in firm["listJob"]:
#                     firm["describe"] = " ".join([firm["describe"], job["jobName"]])
#             firm_fields = [preprocess_text(firm["describe"]) for firm in firms]
#             tfidf_matrix_firms = tfidf_vectorizer.fit_transform(firm_fields)

#             cv_skills = preprocess_text(" ".join([cv["skill"], cv["wish"]]))
#             tfidf_matrix_cv = tfidf_vectorizer.transform([cv_skills])
#             similarity = cosine_similarity(tfidf_matrix_cv, tfidf_matrix_firms)

#             similarity_scores = similarity[0]
#             suggested_firms = [
#                 {
#                     "firmId": firms[i]["firmId"],
#                     "firmName": firms[i]["firmName"],
#                     "similarityScore": similarity_scores[i],
#                 }
#                 for i in range(len(firms))
#             ]
#             suggested_firms.sort(key=lambda x: x["similarityScore"], reverse=True)

#     return jsonify(suggested_firms), {"Access-Control-Allow-Origin": "*"}


# if __name__ == "__main__":
#     app.run()
