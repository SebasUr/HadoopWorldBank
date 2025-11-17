#!/usr/bin/env bash
set -euo pipefail

# Script para descargar el ZIP de WDI y extraer WDICSV.csv en data_raw/
# Usa la URL indicada en data_raw/data.txt

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_RAW_DIR="${SCRIPT_DIR}"
DATA_TXT="${DATA_RAW_DIR}/data.txt"

# Leer URL de data.txt (primera línea que contenga http)
URL="$(grep -Eo 'https?://[^ ]+' "${DATA_TXT}" | head -n 1)"

if [[ -z "${URL:-}" ]]; then
  echo "No se encontró una URL en ${DATA_TXT}" >&2
  exit 1
fi

ZIP_PATH="${DATA_RAW_DIR}/WDI_CSV_10_08.zip"
TMP_DIR="${DATA_RAW_DIR}/wdi_tmp_extract"

echo "Descargando ZIP desde: ${URL}" 
curl -L "${URL}" -o "${ZIP_PATH}"

echo "Eliminando carpeta temporal anterior (si existe): ${TMP_DIR}" 
rm -rf "${TMP_DIR}"
mkdir -p "${TMP_DIR}"

echo "Descomprimiendo ZIP en: ${TMP_DIR}" 
unzip -o "${ZIP_PATH}" -d "${TMP_DIR}"

# Buscar el archivo WDICSV.csv dentro de lo descomprimido
CSV_SRC="$(find "${TMP_DIR}" -maxdepth 2 -type f -name 'WDICSV.csv' | head -n 1)"

if [[ -z "${CSV_SRC:-}" ]]; then
  echo "No se encontró WDICSV.csv dentro del ZIP" >&2
  exit 1
fi

echo "Moviendo ${CSV_SRC} a ${DATA_RAW_DIR}/WDICSV.csv" 
mv "${CSV_SRC}" "${DATA_RAW_DIR}/WDICSV.csv"

echo "Limpieza de carpeta temporal" 
rm -rf "${TMP_DIR}"

echo "Hecho. WDICSV.csv está en ${DATA_RAW_DIR}" 
