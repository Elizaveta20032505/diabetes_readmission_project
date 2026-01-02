import pandas as pd
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import label_binarize
import joblib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Пути к файлам
TOP10_CAT_PATH = PROJECT_ROOT / "data" / "processed" / "diabetic_data_top10.csv"
FULL_CAT_PATH = PROJECT_ROOT / "data" / "processed" / "diabetic_data_processed.csv"

MODELS_PATH = PROJECT_ROOT / "models"
MODELS_PATH.mkdir(exist_ok=True)

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_test_bin = label_binarize(y_test, classes=list(sorted(set(y_test))))
    y_prob = model.predict_proba(X_test)
    roc_auc = roc_auc_score(y_test_bin, y_prob, average="macro", multi_class="ovr")

    print(f"\nМодель: {model.__class__.__name__}")
    print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
    print(f"Recall:    {recall_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
    print(f"F1-score:  {f1_score(y_test, y_pred, average='weighted', zero_division=0):.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")


def train():
    target = "readmitted"

    # ===== CatBoost топ-10 признаков =====
    print("=== CatBoost (10 топ-признаков с категориями) ===")
    df_cb = pd.read_csv(TOP10_CAT_PATH)
    X_cb = df_cb.drop(columns=[target])
    y_cb = df_cb[target].astype(str)
    cat_features = X_cb.select_dtypes(include="object").columns.tolist()

    X_train_cb, X_test_cb, y_train_cb, y_test_cb = train_test_split(
        X_cb, y_cb, test_size=0.2, random_state=42, stratify=y_cb
    )

    cb_model = CatBoostClassifier(
        iterations=300,
        depth=6,
        learning_rate=0.1,
        loss_function="MultiClass",
        verbose=0
    )
    cb_model.fit(X_train_cb, y_train_cb, cat_features=cat_features)
    evaluate_model(cb_model, X_test_cb, y_test_cb)

    # Сохраняем модель
    joblib.dump(cb_model, MODELS_PATH / "catboost_top10.pkl")

    print("✔ Модели сохранены в:", MODELS_PATH)


if __name__ == "__main__":
    train()
