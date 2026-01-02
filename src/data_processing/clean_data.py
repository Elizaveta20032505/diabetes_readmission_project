import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.replace("?", pd.NA, inplace=True)

    df.drop_duplicates(subset=["encounter_id"], inplace=True)

    df = df[df["discharge_disposition_id"] != 11]

    df = df[~df["readmitted"].isna()]

    df["readmitted"] = df["readmitted"].replace("?", pd.NA)

    df = df.dropna(subset=["readmitted"])

    return df
