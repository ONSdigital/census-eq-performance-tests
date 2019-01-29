my_dir="$(dirname "$0")"
source $my_dir/vars.sh

INTENDED_USER_LOAD=$1

if [ -z "$INTENDED_USER_LOAD" ]; then
    echo "Intended user count must be passed"
    exit 2
fi

if [ `expr $INTENDED_USER_LOAD % $USERS_PER_WORKER` != 0 ]; then
    echo "Intended user count must be divisible by $USERS_PER_WORKER"
    exit 2
fi 

WORKERS=$(expr $(expr $INTENDED_USER_LOAD + $USERS_PER_WORKER - 1) / $USERS_PER_WORKER)

echo "Creating cluster..."
gcloud beta container \
--project "$PROJECT_ID" clusters create "$CLUSTER_NAME" \
--region "$REGION" \
--machine-type "custom-1-4096" \
--num-nodes "3" \
--enable-ip-alias \
--enable-autoscaling \
--min-nodes "1" \
--max-nodes "500" \
--quiet


echo "\nGetting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION --project $PROJECT_ID
if [ "$?" = "1" ]; then
    exit 1
fi

set -e

DEFAULT_NAMESPACE_UID=`kubectl get namespace default -o jsonpath='{.metadata.uid}'`

kubectl create configmap cluster-details \
  --from-literal="gcp_project_id=$PROJECT_ID" \
  --from-literal="cluster_name=$CLUSTER_NAME" \
  --from-literal="default_namespace_uid=$DEFAULT_NAMESPACE_UID"

echo "\nCreating deployment..."
kubectl apply -f kubernetes-config
kubectl rollout status deployment/worker

# TODO: scale up gradually
echo "\nScaling to $WORKERS workers..."
kubectl scale deployment worker --replicas=$WORKERS
kubectl rollout status deployment/worker
