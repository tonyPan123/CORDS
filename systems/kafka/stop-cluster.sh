#!/bin/bash
if [ $# -eq 0 ]; then
  trial=0
else
  trial=$1
fi
SIGNAL=${SIGNAL:-TERM}
for i in 1 2 3; do
  pids=$(cat /home/tonypan/CORDS/systems/kafka/output-$i/broker.pid 2>/dev/null)
  for j in $pids; do  
    kill -9 $j
  done
done

