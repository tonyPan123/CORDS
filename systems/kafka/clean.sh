#!/bin/bash
/home/tonypan/CORDS/systems/zk/stop-cluster.sh
rm -rf /home/tonypan/CORDS/systems/zk/logs-*
rm -rf /home/tonypan/CORDS/systems/zk/store-*
mkdir /home/tonypan/CORDS/systems/zk/store-1
mkdir /home/tonypan/CORDS/systems/zk/store-2
mkdir /home/tonypan/CORDS/systems/zk/store-3

touch /home/tonypan/CORDS/systems/zk/store-1/myid 
touch /home/tonypan/CORDS/systems/zk/store-2/myid 
touch /home/tonypan/CORDS/systems/zk/store-3/myid

echo '1' > /home/tonypan/CORDS/systems/zk/store-1/myid 
echo '2' > /home/tonypan/CORDS/systems/zk/store-2/myid
echo '3' > /home/tonypan/CORDS/systems/zk/store-3/myid

/home/tonypan/CORDS/systems/zk/start-cluster.sh

rm -rf /home/tonypan/CORDS/systems/kafka/output-*
