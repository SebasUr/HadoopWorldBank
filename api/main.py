from fastapi import FastAPI
import pandas as pd
import math

app = FastAPI(title="Desarrollo Digital Verde - WDI")

# Cargar resultados
df = pd.read_csv("../data_processed/results_final.csv")


def sanitize_record(record: dict) -> dict:
    """Reemplaza NaN, +inf, -inf por None para que JSON los soporte."""
    clean = {}
    for k, v in record.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            clean[k] = None
        else:
            clean[k] = v
    return clean


@app.get("/countries")
def list_countries():
    return sorted(df["CountryCode"].unique().tolist())


@app.get("/results")
def all_results():
    records = df.to_dict(orient="records")
    return [sanitize_record(r) for r in records]


@app.get("/results/{country_code}")
def result_by_country(country_code: str):
    sub = df[df["CountryCode"] == country_code.upper()]
    if sub.empty:
        return {"detail": "Country not found"}
    record = sub.to_dict(orient="records")[0]
    return sanitize_record(record)