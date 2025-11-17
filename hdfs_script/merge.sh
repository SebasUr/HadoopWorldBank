cd ~/HadoopWorldBank  

hdfs dfs -cat /user/hadoop/HadoopWorldBank/output/job2/part-* > job2_output_raw.txt

head job2_output_raw.txt
