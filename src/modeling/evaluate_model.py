import joblib
import pandas as pd
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
from diabetes_readmission_project.src.data_processing.load_data import load_processed

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "best_model.pkl"


def evaluate():
    df = load_processed()

    X = df.drop(columns=["readmitted"])
    y = df["readmitted"]

    model = joblib.load(MODEL_PATH)

    preds = model.predict(X)

    print("\n=== Оценка модели ===")
    print(classification_report(y, preds))
    print("\nConfusion matrix:")
    print(confusion_matrix(y, preds))


if __name__ == "__main__":
    evaluate()
