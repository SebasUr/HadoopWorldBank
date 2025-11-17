import csv

INPUT_FILE = "./WDICSV.csv"
OUTPUT_FILE = "./WWDICSV_PREPARED.csv"

INDICATORS = {
    "NY.GDP.PCAP.CD",  # PIB per cápita
    "IT.NET.USER.P2",  # Internet users
    "EN.ATM.CO2E.PC",  # CO2 per cápita
}

YEAR_START = 1990
YEAR_END = 2020

with open(INPUT_FILE, "r", encoding="utf-8-sig") as fin, open(
    OUTPUT_FILE, "w", newline="", encoding="utf-8"
) as fout:

    reader = csv.DictReader(fin)
    fieldnames = ["CountryName", "CountryCode", "IndicatorCode", "Year", "Value"]
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        code = row["Indicator Code"]
        if code not in INDICATORS:
            continue

        country_name = row["Country Name"]
        country_code = row["Country Code"]

        for year in range(YEAR_START, YEAR_END + 1):
            col = str(year)
            val = row.get(col, "")
            if val is None or val == "":
                continue
            try:
                val_f = float(val)
            except ValueError:
                continue

            writer.writerow(
                {
                    "CountryName": country_name,
                    "CountryCode": country_code,
                    "IndicatorCode": code,
                    "Year": year,
                    "Value": val_f,
                }
            )
