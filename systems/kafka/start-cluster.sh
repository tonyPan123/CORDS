#!/bin/bash
#if [ $# -eq 0 ]; then
#  trial=0
#else
#  trial=$1
#fi
for i in 1 2 3; do
  /home/tonypan/CORDS/systems/kafka/start-broker.sh $i /home/tonypan/legolas-target-systems/kafka/2.8.0 /home/tonypan/CORDS/systems/kafka/output-$i
done

