from fastapi import FastAPI
import pandas as pd

app = FastAPI(title="Desarrollo Digital Verde - WDI")

df = pd.read_csv("../results/results_final.csv")

@app.get("/countries")
def list_countries():
    return df["CountryCode"].unique().tolist()

@app.get("/results")
def all_results():
    return df.to_dict(orient="records")

@app.get("/results/{country_code}")
def result_by_country(country_code: str):
    sub = df[df["CountryCode"] == country_code.upper()]
    if sub.empty:
        return {"detail": "Country not found"}
    return sub.to_dict(orient="records")[0]
