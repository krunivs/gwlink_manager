kubectl delete -n etri service/rabbitmq-nodeport
kubectl delete -n etri service/rabbitmq-clusterip
kubectl delete -n etri statefulset.apps/rabbitmq
