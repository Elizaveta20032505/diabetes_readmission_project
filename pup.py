import joblib

model = joblib.load("models/catboost_top10.pkl")
print(model.feature_names_)