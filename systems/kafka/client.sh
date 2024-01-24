#!/bin/bash
java -Dlog4j.configuration=file:/home/tonypan/CORDS/systems/kafka/conf-1/tools-log4j.properties -cp /home/tonypan/Legolas/driver/kafka/2.8.0/target/ka_2_8_0-1.0-jar-with-dependencies.jar edu.jhu.order.mcgray.ka_2_8_0.KafkaGrayClientMain $@

