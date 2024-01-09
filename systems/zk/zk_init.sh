#!/bin/bash

# This script just initializes a cluster of ZooKeeper nodes with just one key value pair
# Kill all ZooKeeper instances
pkill -f 'java.*zoo*'
ZK_HOME=$HOME'/legolas-target-systems/zookeeper/3.6.2'
CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#Delete all the CORDS trace files
#Delete ZooKeeper workload directories
rm -rf cordslog*
rm -rf trace*
rm -rf store*

# Create workload directories for 3 nodes
# Create the required files for ZooKeeper
mkdir store-1
mkdir store-2
mkdir store-3

touch store-1/myid
touch store-2/myid
touch store-3/myid

echo '1' > store-1/myid
echo '2' > store-2/myid
echo '3' > store-3/myid

#Start the 3 nodes in the Zookeeper Cluster.
#$CURR_DIR/start-cluster.sh

#sleep 2

# Insert key value pairs to ZooKeeper
#value=$(printf 'a%.s' {1..8192})
#echo 'create /zookeeper0 '$value > script
#$ZK_HOME"/bin/zkCli.sh" -server localhost:10712 < script


# Kill all ZooKeeper instances
#rm -rf script
#pkill -f 'java.*zoo*'
#sleep 1
#ps aux | grep zoo
#rm -rf zookeeper.out
