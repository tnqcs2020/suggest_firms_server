import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from flask import Flask, request, jsonify
from underthesea import word_tokenize
from sklearn.neighbors import NearestNeighbors
import string
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download("wordnet")

app = Flask(__name__)

cred = credentials.Certificate("htqltttt-key.json")

firebase_admin.initialize_app(cred)

tfidf = TfidfVectorizer(stop_words="english")


def readStopWords(fileName):
    with open(fileName, "r", encoding="utf-8") as file:
        stopWords = file.read().splitlines()
    return stopWords


stopWords = readStopWords("vietnamese-stopwords.txt")


def getProfilesData(profile_ref):
    profiles = []
    for profile in profile_ref:
        formattedData = profile.to_dict()
        profiles.append(formattedData)
    return profiles


def getFirmsData(firm_ref):
    firms = []
    for firm in firm_ref:
        formattedData = firm.to_dict()
        firms.append(formattedData)
    return firms


def preprocess_text(text):
    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)

    text = lemmatizer(text)

    text = word_tokenize(text, format="text").lower().split()

    noneStopWords = [word for word in text if word not in stopWords]
    text = " ".join(noneStopWords)
    return text


def preprocess_dataFrame(df, column_name):
    df[column_name] = df[column_name].apply(preprocess_text)
    return df


def lemmatizer(text):
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in text.split()]
    return " ".join(lemmatized_tokens)


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/suggest-tfidf", methods=["POST"])
def recommendationsTFIDF():
    userId = request.args.get("userId")

    db = firestore.client()

    profile_ref = db.collection("profiles").stream()
    profiles = getProfilesData(profile_ref)

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
            "firm_id": [firm["firmId"] for firm in firms],
            "firm_name": [firm["firmName"] for firm in firms],
            "tags": tags,
            "rate": [firm["tieuChi"] for firm in firms],
        }
    )

    firms_df = preprocess_dataFrame(firm_data, "tags")

    profiles_df = pd.DataFrame(
        {
            "user_id": [profile["userId"] for profile in profiles],
            "tags": [profile["description"] for profile in profiles],
            "rate": [
                [
                    profile["language"],
                    profile["programming"],
                    profile["skillGroup"],
                    profile["machineAI"],
                    profile["website"],
                    profile["mobile"],
                ]
                for profile in profiles
            ],
        }
    )

    profiles_df = preprocess_dataFrame(profiles_df, "tags")

    tfidf = TfidfVectorizer(stop_words="english")

    firms_matrix = tfidf.fit_transform(firms_df["tags"])
    users_matrix = tfidf.transform(
        profiles_df.index[profiles_df["user_id"] == userId][0]["tags"]
    )
    users_firms_similarity = linear_kernel(users_matrix, firms_matrix)

    suggested_firms = [
        {
            "firmId": firms[j]["firmId"],
            "firmName": firms[j]["firmName"],
            "similarityScore": users_firms_similarity[0][j],
        }
        for j in range(len(firms))
    ]
    suggested_firms.sort(key=lambda x: x["similarityScore"], reverse=True)

    return jsonify(suggested_firms[0:5]), {"Access-Control-Allow-Origin": "*"}


@app.route("/suggest-knn", methods=["POST"])
def recommendationsKNN():
    userId = request.args.get("userId")

    db = firestore.client()

    profile_ref = db.collection("profiles").stream()
    profiles = getProfilesData(profile_ref)

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
            "firm_id": [firm["firmId"] for firm in firms],
            "firm_name": [firm["firmName"] for firm in firms],
            "tags": tags,
            "rate": [firm["tieuChi"] for firm in firms],
        }
    )

    firms_df = preprocess_dataFrame(firm_data, "tags")

    profiles_df = pd.DataFrame(
        {
            "user_id": [profile["userId"] for profile in profiles],
            "tags": [profile["description"] for profile in profiles],
            "rate": [
                [
                    profile["language"],
                    profile["programming"],
                    profile["skillGroup"],
                    profile["machineAI"],
                    profile["website"],
                    profile["mobile"],
                ]
                for profile in profiles
            ],
        }
    )

    profiles_df = preprocess_dataFrame(profiles_df, "tags")

    firms_rate = pd.DataFrame(
        {
            "language": [(firms_df["rate"][i])[0] for i in range(len(firms_df))],
            "programming": [(firms_df["rate"][i])[1] for i in range(len(firms_df))],
            "skil_group": [(firms_df["rate"][i])[2] for i in range(len(firms_df))],
            "machine_ai": [(firms_df["rate"][i])[3] for i in range(len(firms_df))],
            "website": [(firms_df["rate"][i])[4] for i in range(len(firms_df))],
            "mobile": [(firms_df["rate"][i])[5] for i in range(len(firms_df))],
        }
    )

    list_rate_suggest_5 = []
    list_rate_user = []

    for i in range(len(profiles_df)):
        if profiles_df["user_id"][i] == userId:
            user_in = pd.DataFrame(
                {
                    "language": [profiles_df["rate"][i][0]],
                    "programming": [profiles_df["rate"][i][1]],
                    "skil_group": [profiles_df["rate"][i][2]],
                    "machine_ai": [profiles_df["rate"][i][3]],
                    "website": [profiles_df["rate"][i][4]],
                    "mobile": [profiles_df["rate"][i][5]],
                }
            )

            knn5 = NearestNeighbors(n_neighbors=5, algorithm="brute")
            knn5.fit(firms_rate)
            distances, indices = knn5.kneighbors(X=user_in)

            suggested_firms = [
                {
                    "firmId": firms_df["firm_id"].iloc[indices.flatten()[j]],
                    "firmName": firms_df["firm_name"].iloc[indices.flatten()[j]],
                    "similarityScore": distances.flatten()[j],
                }
                for j in range(len(distances.flatten()))
            ]
            suggested_firms.sort(key=lambda x: x["similarityScore"])

    return jsonify(suggested_firms), {"Access-Control-Allow-Origin": "*"}


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
