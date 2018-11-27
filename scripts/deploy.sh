my_dir="$(dirname "$0")"
source $my_dir/vars.sh

INTENDED_USER_LOAD=$1
if [ -z "$INTENDED_USER_LOAD" ]; then
    INTENDED_USER_LOAD=800 # default to 1 worker
fi

USERS_PER_WORKER=800
WORKERS=$(expr $(expr $INTENDED_USER_LOAD + $USERS_PER_WORKER - 1) / $USERS_PER_WORKER)

echo "Creating cluster..."
gcloud beta container \
--project "$PROJECT_ID" clusters create "$CLUSTER_NAME" \
--zone "$ZONE" \
--machine-type "n1-standard-1" \
--num-nodes "3" \
--enable-ip-alias \
--enable-autoscaling \
--min-nodes "1" \
--max-nodes "500" \
--quiet

# everything after this point needs to pass
set -e

echo "\nGetting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE --project $PROJECT_ID

echo "\nCreating deployment..."
kubectl apply -f kubernetes-config --wait
kubectl rollout status deployment/locust-master

echo "\nCreating $WORKERS locust workers..."
kubectl scale deployment locust-worker --replicas=$WORKERS
kubectl rollout status deployment/locust-worker

# get locust IP
EXTERNAL_IP=$(kubectl get service locust-master --template="{{range .status.loadBalancer.ingress}}{{.ip}}{{end}}")

echo "\nLocust setup completed."
echo "Go to http://$EXTERNAL_IP:8089 to start your load test"
echo "\n##############################################################################################"
echo "#                                                                                             #"
echo "# Make sure you run scripts/delete_cluster.sh to tear down your cluster when you're finished! #"
echo "#                                                                                             #"
echo "###############################################################################################"
