#!/bin/bash
for i in 1 2 3; do
  ZOOCFGDIR=/home/tonypan/CORDS/systems/zk/conf-$i ZOO_LOG_DIR=/home/tonypan/CORDS/systems/zk/trials/0/logs-$i /home/tonypan/legolas-target-systems/zookeeper/3.6.2/bin/zkServer.sh stop
done

