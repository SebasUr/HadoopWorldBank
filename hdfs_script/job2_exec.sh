hdfs dfs -rm -r -f /user/hadoop/HadoopWorldBank/output/job2

python mapreduce/job2_classification.py \
  -r hadoop \
  hdfs:///user/hadoop/HadoopWorldBank/output/job1 \
  --output-dir hdfs:///user/hadoop/HadoopWorldBank/output/job2

hdfs dfs -cat /user/hadoop/HadoopWorldBank/output/job2/part-* | head
