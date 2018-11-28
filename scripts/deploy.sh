my_dir="$(dirname "$0")"
source $my_dir/vars.sh

INTENDED_USER_LOAD=$1

if [ -z "$INTENDED_USER_LOAD" ]; then
    echo "Intended user count must be passed"
    exit 2
fi

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


echo "\nGetting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE --project $PROJECT_ID
if [ "$?" = "1" ]; then
    exit 1
fi

echo "\nRemoving any existing locust deployment"
kubectl delete deployment locust-master locust-worker

set -e

echo "\nCreating locust master deployment..."
kubectl apply -f kubernetes-config
kubectl rollout status deployment/locust-master

echo "\nScaling to $WORKERS locust workers..."
kubectl scale deployment locust-worker --replicas=$WORKERS
kubectl rollout status deployment/locust-worker

# get locust IP
EXTERNAL_IP=$(kubectl get service locust-master --template="{{range .status.loadBalancer.ingress}}{{.ip}}{{end}}")
export LOCUST_URL=http://$EXTERNAL_IP:8089
