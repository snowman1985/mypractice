#!/bin/bash

mkdir /cgroup
mkdir /cgroup/memory
mkdir /cgroup/blkio

mem_limit=3
mongod_pid=$1
mongod_write_io=4194304  #4MB/s
dbpath_major=104 #disk major using ls -lL /mongodb
dbpath_minor=16 #disk minor using ls -lL /mongodb
tasks="/cgroup/blkio/kuaiji/tasks"


mount -t cgroup -o memory memcg /cgroup/memory
mount -t cgroup -o blkio blkiocg /cgroup/blkio

mkdir /cgroup/memory/kuaiji
mkdir /cgroup/blkio/kuaiji

echo ${mem_limit}G > /cgroup/memory/kuaiji/memory.limit_in_bytes
echo $mongod_pid > /cgroup/memory/kuaiji/tasks

echo "${dbpath_major}:${dbpath_minor}  $mongod_write_io"  > /cgroup/blkio/kuaiji/blkio.throttle.write_bps_device
echo $mongod_pid > /cgroup/blkio/kuaiji/tasks

mongodpids=`pstree -p ${mongod_pid} | sed 's/(/\n(/g' | grep '(' | sed 's/(\(.*\)).*/\1/'`

arr=$(echo $mongodpids | tr " " "\n")


for element in $arr; do
  echo $element > /cgroup/blkio/kuaiji/tasks
done



 
