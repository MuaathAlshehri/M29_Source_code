from fastapi import FastAPI
import pandas as pd
import joblib
from pathlib import Path
from pydantic import BaseModel , Field
import json

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
model_path = BASE_DIR / "deployment_package" / "model.joblib"
model = joblib.load(model_path)

with open(BASE_DIR / "deployment_package" / "top_categories.json") as f:
    top_categories_dict = json.load(f)

with open(BASE_DIR / "deployment_package" / "freq_maps.json") as f:
    freq_maps = json.load(f)

def group_rare_categories(df):
    for col in ["Receiving Currency", "Payment Currency", "Payment Format"]:
        if col in df.columns:
            top_categories = top_categories_dict[col]
            df[col] = df[col].where(df[col].isin(top_categories),"Others")
    return df

def freq_columns(df):
    for col in ["From Bank", "To Bank", "Account", "Account.1"]:
        if col in df.columns:
            mapping = freq_maps[col]
            df[col + "_freq"] = df[col].map(mapping).fillna(0)
    
    df = df.drop(columns=["From Bank", "To Bank", "Account", "Account.1"])
    return df



class InputData(BaseModel):
    Timestamp: str
    From_Bank: int = Field(alias="From Bank")
    Account: str
    To_Bank: int = Field(alias="To Bank")
    Account_1: str = Field(alias="Account.1")
    Amount_Received: float = Field(alias="Amount Received")
    Receiving_Currency: str = Field(alias="Receiving Currency")
    Amount_Paid: float = Field(alias="Amount Paid")
    Payment_Currency: str = Field(alias="Payment Currency")
    Payment_Format: str = Field(alias="Payment Format")




@app.post("/predict")
def predict(data: InputData):
    
    df = pd.DataFrame([data.model_dump(by_alias=True)])

    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    df["year"] = df["Timestamp"].dt.year.fillna(0)
    df["month"] = df["Timestamp"].dt.month.fillna(0)
    df["day"] = df["Timestamp"].dt.day.fillna(0)
    df["hour"] = df["Timestamp"].dt.hour.fillna(0)

    df = group_rare_categories(df)
    df = freq_columns(df)

    prediction = model.predict(df)
    
    return {"prediction": int(prediction[0])}
    