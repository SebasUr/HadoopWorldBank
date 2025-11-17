import csv

INPUT_FILE = "job2_output_raw.txt"
OUTPUT_FILE = "results_final.csv"

def main():
    with open(INPUT_FILE, encoding="utf-8") as fin, \
         open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as fout:

        writer = csv.writer(fout)

        # Cabecera para lo que generamos en job2:
        # country_code,
        # gdp_start, gdp_end, gdp_growth,
        # net_start, net_end, net_growth,
        # co2_change, score, label
        writer.writerow([
            "CountryCode",
            "GDP_Decade_Start",
            "GDP_Decade_End",
            "GDP_Growth",
            "Net_Decade_Start",
            "Net_Decade_End",
            "Net_Growth",
            "CO2_Change",
            "Score",
            "Label",
        ])

        for line in fin:
            line = line.strip()
            if not line:
                continue

            # Separar la key (null) del valor
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue

            value_part = parts[1].strip()

            # Quitar comillas externas si existen
            if value_part.startswith('"') and value_part.endswith('"'):
                value_part = value_part[1:-1]

            # Parsear como CSV (por si acaso, aunque no hay comas raras)
            row = next(csv.reader([value_part]))
            if len(row) != 10:
                # COUNTRY, gdp_start, gdp_end, gdp_growth,
                #         net_start, net_end, net_growth,
                #         co2_change, score, label
                continue

            writer.writerow(row)

if __name__ == "__main__":
    main()

