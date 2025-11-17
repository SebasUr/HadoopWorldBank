hdfs dfs -rm -r -f /user/hadoop/HadoopWorldBank/output/job1

python mapreduce/job1_decades.py \
  -r hadoop \
  hdfs:///user/hadoop/HadoopWorldBank/input/WDICSV_PREPARED.csv \
  --output-dir hdfs:///user/hadoop/HadoopWorldBank/output/job1
