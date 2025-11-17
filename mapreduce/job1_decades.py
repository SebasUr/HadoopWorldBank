from mrjob.job import MRJob
import csv
from io import StringIO

class WDIJob1Decades(MRJob):

    def mapper(self, _, line):
        # saltar encabezado
        if line.startswith("CountryName,"):
            return

        f = StringIO(line)
        reader = csv.reader(f)
        try:
            country_name, country_code, indicator_code, year_str, value_str = next(reader)
        except ValueError:
            return

        try:
            year = int(year_str)
            value = float(value_str)
        except ValueError:
            return

        # década
        if 1990 <= year <= 1999:
            decade = "1990s"
        elif 2000 <= year <= 2009:
            decade = "2000s"
        elif 2010 <= year <= 2020:
            decade = "2010s"
        else:
            return

        key = (country_code, indicator_code, decade)
        # (valor, contador)
        yield key, (value, 1)

    def reducer(self, key, values):
        total = 0.0
        count = 0
        for v, c in values:
            total += v
            count += c
        avg = total / count if count > 0 else 0.0

        country_code, indicator_code, decade = key
        # formateamos como CSV para el siguiente job
        yield None, f"{country_code},{indicator_code},{decade},{avg}"

if __name__ == "__main__":
    WDIJob1Decades.run()
