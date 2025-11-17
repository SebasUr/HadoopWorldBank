hdfs dfs -rm -r -f /user/hadoop/HadoopWorldBank/output/job1
# Desde la raíz del repo
python mapreduce/job1_decades.py \
  -r hadoop \
  hdfs:///user/hadoop/HadoopWorldBank/input/WDICSV_PREPARED.csv \
  --output-dir hdfs:///user/hadoop/HadoopWorldBank/output/job1

# Verificar
hdfs dfs -ls /user/hadoop/HadoopWorldBank/output/job1
hdfs dfs -cat /user/hadoop/HadoopWorldBank/output/job1/part-* | head