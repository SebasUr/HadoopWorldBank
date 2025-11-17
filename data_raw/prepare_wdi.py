import csv

INPUT_FILE = "WDICSV.csv"
OUTPUT_FILE = "WDICSV_PREPARED.csv"

# Indicadores seleccionados
GDP_CODE = "NY.GDP.PCAP.CD"      # PIB per cápita (US$ corrientes)
NET_CODE = "IT.NET.USER.ZS"      # Individuos usando Internet (% de la población)
CO2_CODE = "NY.ADJ.DCO2.GN.ZS"   # Daño por CO2 (% del GNI)

INDICATORS = {GDP_CODE, NET_CODE, CO2_CODE}

# Rango temporal de interés
YEAR_MIN = 1990
YEAR_MAX = 2020

def main():
    with open(INPUT_FILE, newline="", encoding="utf-8-sig") as fin, \
         open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as fout:

        reader = csv.reader(fin)
        writer = csv.writer(fout)

        header = next(reader)
        # header: [0]Country Name, [1]Country Code, [2]Indicator Name,
        #         [3]Indicator Code, [4]1960, [5]1961, ...
        year_cols = header[4:]

        # Nuevo formato "long":
        writer.writerow(["CountryName", "CountryCode", "IndicatorCode", "Year", "Value"])

        for row in reader:
            country_name = row[0]
            country_code = row[1]
            indicator_code = row[3]

            # Solo nos quedamos con los 3 indicadores seleccionados
            if indicator_code not in INDICATORS:
                continue

            for idx, year_str in enumerate(year_cols, start=4):
                value_str = row[idx].strip()
                if not value_str:
                    continue

                try:
                    year = int(year_str)
                    value = float(value_str)
                except ValueError:
                    continue

                if YEAR_MIN <= year <= YEAR_MAX:
                    writer.writerow([
                        country_name,
                        country_code,
                        indicator_code,
                        year,
                        value,
                    ])

if __name__ == "__main__":
    main()
