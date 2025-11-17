from mrjob.job import MRJob
import csv
from io import StringIO

GDP = "NY.GDP.PCAP.CD"
NET = "IT.NET.USER.P2"
CO2 = "EN.ATM.CO2E.PC"

class WDIJob2Classification(MRJob):

    def mapper(self, _, line):
        # Formato: "null<TAB>COUNTRY,INDICATOR,DECADE,AVG"
        parts = line.split("\t", 1)
        if len(parts) != 2:
            return
        value_part = parts[1].strip()

        f = StringIO(value_part)
        reader = csv.reader(f)
        try:
            country_code, indicator_code, decade, avg_str = next(reader)
        except ValueError:
            return

        try:
            avg = float(avg_str)
        except ValueError:
            return

        yield country_code, (indicator_code, decade, avg)

    def reducer(self, country_code, records):
        # Estructura: data[indicator_code][decade] = avg
        data = {}
        for ind, dec, avg in records:
            data.setdefault(ind, {})[dec] = avg

        def ratio(ind, d1, d2):
            v1 = data.get(ind, {}).get(d1)
            v2 = data.get(ind, {}).get(d2)
            if v1 is None or v2 is None or v1 == 0:
                return None
            return (v2 - v1) / v1

        gdp_growth = ratio(GDP, "1990s", "2010s")
        net_growth = ratio(NET, "1990s", "2010s")
        co2_change = ratio(CO2, "1990s", "2010s")

        if gdp_growth is None or net_growth is None or co2_change is None:
            return

        # Clasificación sencilla
        if gdp_growth >= 1.0 and net_growth >= 5.0 and co2_change <= 0.1:
            label = "verde_digital"
        elif gdp_growth >= 1.0 and net_growth >= 5.0 and co2_change > 0.1:
            label = "digital_con_mas_emisiones"
        else:
            label = "crecimiento_bajo_o_mixto"

        # Score (puedes mostrarlo en el paper)
        score = gdp_growth + net_growth - max(co2_change, 0)

        yield None, f"{country_code},{gdp_growth:.3f},{net_growth:.3f},{co2_change:.3f},{score:.3f},{label}"

if __name__ == "__main__":
    WDIJob2Classification.run()
