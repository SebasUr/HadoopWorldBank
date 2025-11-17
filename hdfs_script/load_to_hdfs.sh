#!/bin/bash
set -e

sudo yum install git -y
hdfs dfs -rm -r -f /user/hadoop/HadoopWorldBank
git clone https://github.com/SebasUr/HadoopWorldBank

LOCAL_INPUT="/home/hadoop/HadoopWorldBank/data_prepared/WDICSV_PREPARED.csv"
HDFS_INPUT="/user/hadoop/HadoopWorldBank/input"

hdfs dfs -mkdir -p "$HDFS_INPUT"
hdfs dfs -put -f "$LOCAL_INPUT" "$HDFS_INPUT/WDICSV_PREPARED.csv"
hdfs dfs -ls "$HDFS_INPUT"
