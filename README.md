## Trabajo 3 – Procesamiento distribuido con MapReduce
**Pregunta:** ¿Qué países han logrado entre 1990 y 2020 combinar crecimiento económico y expansión del acceso a internet sin aumentar (o incluso reduciendo) sus emisiones de CO₂ por habitante? Es decir, ¿qué países están logrando un desarrollo digital verde? 

## Datos Utilizados
- Fuente: **World Bank – World Development Indicators (WDI)** (`WDI_CSV_10_08`). https://datacatalogfiles.worldbank.org/ddh-published/0037712/DR0095335/WDI_CSV_10_08.zip
- Archivos originales relevantes:
	- `WDICSV.csv` (datos de indicadores por país y año)
	- `WDICountry.csv`, `WDISeries.csv` (para consultar metadatos/indicadores)

| Dimensión      | Indicador WDI                                   | Código WDI          |
| -------------- | ----------------------------------------------- | ------------------- |
| Economía       | **PIB per cápita (US$ corrientes)**             | `NY.GDP.PCAP.CD`    |
| Digitalización | **Usuarios de Internet (% de la población)**    | `IT.NET.USER.ZSS`   |
| Ambiente       | **Daño por CO₂ (% del Ingreso Nacional Bruto)** | `NY.ADJ.DCO2.GN.ZS` |
Rango temporal analizado: **1990–2020**, según disponibilidad por indicador y país.


### Preparación de los datos (data_raw/prepare_wdi.py)
- Se lee el archivo original WDICSV.csv que se puede descargar y setear automáticamente con el script `download_wdi.sh`.
- Filtra los indicadores: `TARGETS = {"NY.GDP.PCAP.CD", "IT.NET.USER.ZS", "NY.ADJ.DCO2.GN.ZS"}`
- Lo convierte a un formato largo 
```
CountryName,CountryCode,IndicatorCode,Year,Value
Africa Eastern and Southern,AFE,NY.GDP.PCAP.CD,1990,822.7938...
Africa Eastern and Southern,AFE,NY.GDP.PCAP.CD,1991,864.5638...
...
Africa Eastern and Southern,AFE,IT.NET.USER.ZS,2005,1.8
...
Africa Eastern and Southern,AFE,NY.ADJ.DCO2.GN.ZS,1990,1.61...

```

- Queda WDICSV_PREPARED.csv
- Se cargan los datos a la máquina descargando el repositorio automáticamente con los scripts (`copy_script.sh`) y se **cargan al HDFS** (`load_to_hdfs.sh`).


### Visión general

## **JOB 1 – Agregación por década e indicador**  

**Objetivo**: Calcular el **promedio por década** de cada indicador seleccionado, para cada país.
#### Implementación (`WDIJob1Decades` con MRJob)
- **Mapper**:
    - Lee cada línea de `WDICSV_PREPARED.csv` (ignorando el header).
    - Parsea como CSV:  
        `CountryName, CountryCode, IndicatorCode, Year, Value`
    - Agrupa años por décadas:
        - `1990–1999` → `"1990s"`
        - `2000–2009` → `"2000s"`
        - `2010–2020` → `"2010s"`
            
    - Emite:
```
    `null "COL,NY.GDP.PCAP.CD,2010s,12024.31..."`
```

**Ejecución**: Se puede ejecutar hdfs_script/job1_exec.sh


## **JOB 2 – Clasificación de países**  
**Entrada**: salida del Job 1  
**Salida**: para cada país, métricas de cambio 1990→2010 y una **etiqueta**: 

Usando los promedios por década del Job 1:
- Calcular el **crecimiento relativo del PIB per cápita** por país.
- Calcular el **crecimiento relativo del uso de Internet** por país.
- Calcular el **cambio relativo del daño por CO₂** por país.
- Clasificar cada país en categorías:
    - `verde_digital`
    - `digital_con_mas_emisiones`
    - `crecimiento_bajo_o_mixto`
    - `digital_sin_datos_co2` (cuando falta información ambiental)


El reducer contruye el diccionario `data[indicator][decade] = avg` y calcula el growth:
<img width="338" height="74" alt="image-17" src="https://github.com/user-attachments/assets/a7181728-9f7f-4575-8ac9-58f73a56245a" />

Obtiene:
- `gdp_growth`
- `net_growth`
- `co2_change`

Clasificación:

- Si no hay datos de PIB o Internet → no se clasifica.
- Si no hay CO₂ → `digital_sin_datos_co2`.
- Si:
    - `gdp_growth ≥ 1.0` (PIB se duplica o más), y
    - `net_growth ≥ 5.0` (Internet crece al menos 500%), y
    - `co2_change ≤ 0.1` (daño por CO₂ se mantiene o casi no crece)  
        → **`verde_digital`**
        
- Si `gdp_growth ≥ 1.0`, `net_growth ≥ 5.0`, pero `co2_change > 0.1`  
    → **`digital_con_mas_emisiones`**
- En otros casos  
    → **`crecimiento_bajo_o_mixto`**

También define el score = gdp_growth + net_growth - max(co2_change, 0)

**Ejecución**: Se puede ejecutar automáticamente desde el master con `hdfs_script/job1_exec.sh`.


## Exportación de resultados
`cd ~/HadoopWorldBank`
hdfs dfs -cat /user/hadoop/HadoopWorldBank/output/job2/part-* > data_processed/job2_output_raw.txt

Luego utilizar un script Python (`prepare_results_final.py`) para:

1. Eliminar la key `null` y el tabulador.
2. Quitar comillas externas.
3. Parsear el string como CSV.
4. Escribir un archivo limpio con encabezado.

Finalmente queda todo en `results_final.csv`

## API de visualización
Finalmente, se construyó una **API REST** sencilla usando **FastAPI** y **pandas** para exponer los resultados:
#### Endpoints expuestos

- `GET /countries`  
    Devuelve la lista de códigos de país disponibles en el análisis.
- `GET /results`  
    Devuelve todas las filas con la clasificación completa de cada país.
- `GET /results/{country_code}`  
    Devuelve la información detallada para un país específico (por ejemplo `COL`, `BRA`, `ARE`).

**Ejecución:** 
```
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Despliegue con IaaS

Basta con entrar a la carpeta `EMR/`, llenar el archivo `terraform.tfvars` según el `.example`; primero se deben verificar los roles para EMR.
```
$ aws iam list-roles --query "Roles[*].[RoleName, Arn]" --output table
```
y ejecutar los siguientes comandos con las credenciales de AWS configuradas:
```
$ terraform init
$ terraform apply
```


# Estructura del proyecto 
```
HadoopWorldBank/
├─ data_raw/
│  ├─ WDICSV.csv                  # archivo original del World Bank
│  ├─ WDI_CSV_10_08.zip           # ZIP original descargado
│  ├─ data.txt                    # URL de descarga del ZIP
│  ├─ download_wdi.sh             # script para descargar y extraer WDICSV.csv
│  └─ prepare_wdi.py              # sólo 3 indicadores en formato “largo”
├─ data_prepared/
│  └─ WDICSV_PREPARED.csv         # indicadores filtrados y normalizados
├─ data_processed/
│  ├─ job2_output_raw.txt         # salida cruda de HDFS
│  ├─ prepare_results_final.py    # script de limpieza de la salida del job2
│  └─ results_final.csv           # CSV limpio para la API
├─ mapreduce/
│  ├─ job1_decades.py             # MRJob 1
│  └─ job2_classification.py      # MRJob 2
├─ hdfs_script/
│  ├─ job1_exec.sh
│  ├─ job2_exec.sh
│  ├─ load_to_hdfs.sh             # carga datos a HDFS
│  └─ merge.sh
├─ results/
│  └─ (vacío por ahora)
├─ api/
│  ├─ main.py                     # API FastAPI
│  └─ requirements.txt            # dependencias de la API
├─ EMR/
│  ├─ main.tf                     # definición de infraestructura EMR
│  ├─ variables.tf
│  ├─ terraform.tfvars.example
│  └─ otros archivos de Terraform
└─ README.MD
```
