from mrjob.job import MRJob
import csv
from io import StringIO

# Indicadores
GDP = "NY.GDP.PCAP.CD"      # PIB per cápita
NET = "IT.NET.USER.ZS"      # Individuos usando Internet (% población)
CO2 = "NY.ADJ.DCO2.GN.ZS"   # Daño por CO2 (% del GNI)

DECADES_ORDER = ["1990s", "2000s", "2010s"]

class WDIJob2Classification(MRJob):

    def mapper(self, _, line):
        # Formato de línea de job1:
        # null<TAB>"COUNTRY,INDICATOR,DECADE,AVG"
        parts = line.split("\t", 1)
        if len(parts) != 2:
            return

        value_part = parts[1].strip()

        # Quitar comillas externas si están
        if value_part.startswith('"') and value_part.endswith('"'):
            value_part = value_part[1:-1]

        # value_part: COUNTRY,INDICATOR,DECADE,AVG
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

        # clave: país; valor: (indicador, década, promedio)
        yield country_code, (indicator_code, decade, avg)

    def reducer(self, country_code, records):
        # data[indicador][decada] = avg
        data = {}
        for ind, dec, avg in records:
            data.setdefault(ind, {})[dec] = avg

        def growth_for_indicator(ind):
            """Devuelve (growth, decade_start, decade_end) usando
            la década más antigua y la más reciente disponibles."""
            decs = list(data.get(ind, {}).keys())
            if len(decs) < 2:
                return None, None, None

            # Orden según 1990s -> 2000s -> 2010s
            decs_sorted = sorted(
                decs,
                key=lambda d: DECADES_ORDER.index(d) if d in DECADES_ORDER else 999
            )

            d_start = decs_sorted[0]
            d_end = decs_sorted[-1]

            v1 = data[ind][d_start]
            v2 = data[ind][d_end]

            if v1 == 0:
                return None, d_start, d_end

            g = (v2 - v1) / v1
            return g, d_start, d_end

        # Crecimientos por indicador
        gdp_growth, gdp_start, gdp_end = growth_for_indicator(GDP)
        net_growth, net_start, net_end = growth_for_indicator(NET)
        co2_change, co2_start, co2_end = growth_for_indicator(CO2)

        # Necesitamos al menos PIB + Internet para hablar de "desarrollo digital"
        if gdp_growth is None or net_growth is None:
            return

        # Clasificación según CO2 si existe
        if co2_change is None:
            label = "digital_sin_datos_co2"
        else:
            if gdp_growth >= 1.0 and net_growth >= 5.0 and co2_change <= 0.1:
                label = "verde_digital"
            elif gdp_growth >= 1.0 and net_growth >= 5.0 and co2_change > 0.1:
                label = "digital_con_mas_emisiones"
            else:
                label = "crecimiento_bajo_o_mixto"

        # Score para ordenar: premiar crecimiento en PIB e Internet, penalizar CO2
        score = gdp_growth + net_growth
        if co2_change is not None and co2_change > 0:
            score -= co2_change

        co2_str = f"{co2_change:.3f}" if co2_change is not None else "NA"

        # Formato salida:
        # COUNTRY, gdp_start, gdp_end, gdp_growth,
        #         net_start, net_end, net_growth,
        #         co2_change|NA, score, label
        yield None, (
            f"{country_code},"
            f"{gdp_start},{gdp_end},{gdp_growth:.3f},"
            f"{net_start},{net_end},{net_growth:.3f},"
            f"{co2_str},{score:.3f},{label}"
        )

if __name__ == "__main__":
    WDIJob2Classification.run()
