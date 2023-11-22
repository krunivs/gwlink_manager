docker run -d \
--name rabbitmq -p 15671:15671/tcp -p 15672:15672/tcp \
-p 15674:15674/tcp -p 15675:15675/tcp -p 1883:1883/tcp -p 25672:25672/tcp \
-p 4369:4369/tcp -p 5671:5671/tcp -p 5672:5672/tcp -p 61613:61613/tcp \
krunivs/rabbitmq-custom:3.7-management
