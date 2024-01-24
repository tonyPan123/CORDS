#!/usr/bin/env bash

workspace=$(cd "$(dirname "${BASH_SOURCE-$0}")"; pwd)

KAFKA_SRC=$2
JMX_PORT_BASE=8989

if [ -z "$NON_MC_MODE" ]; then
  for jar in `ls $KAFKA_SRC/*/build/libs/**.jar 2>/dev/null`; do
    mv $jar $jar.backup_jar
  done
fi


CLASSPATH=""
for i in `ls -d $KAFKA_SRC/*/build/classes/**/main`; do
  CLASSPATH="$CLASSPATH:$i"
done


CLASSPATH=$CLASSPATH \
LOG_DIR=$3 \
JMX_PORT=$(($JMX_PORT_BASE + $1)) \
KAFKA_LOG4J_OPTS="-Dlog4j.configuration=file:$workspace/conf-$1/log4j.properties" \
KAFKA_OPTS="$KAFKA_OPTS -noverify" \
$KAFKA_SRC/bin/kafka-server-start.sh -daemon $workspace/conf-$1/server.properties &
PID=$!

wait $PID

OSNAME=$(uname -s)
if [[ "$OSNAME" == "OS/390" ]]; then
    if [ -z $JOBNAME ]; then
        JOBNAME="KAFKSTRT"
    fi
    PID=$(ps -A -o pid,jobname,comm | grep -i $JOBNAME | grep java | grep -v grep | grep conf-$1 | awk '{print $1}')
elif [[ "$OSNAME" == "OS400" ]]; then
    PID=$(ps -Af | grep -i 'kafka\.Kafka' | grep java | grep -v grep | grep conf-$1 | awk '{print $2}')
else
    PID=$(ps ax | grep ' kafka\.Kafka ' | grep java | grep -v grep | grep conf-$1 | awk '{print $1}')
fi

echo $PID >$3/broker.pid
