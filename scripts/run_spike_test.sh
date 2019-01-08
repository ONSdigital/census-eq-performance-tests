# TODO: re-implement

my_dir="$(dirname "$0")"
source $my_dir/vars.sh

USER_COUNT=$1
if [ -z "$USER_COUNT" ]; then
    USER_COUNT=$(expr $USERS_PER_WORKER / $SPIKE_MAX_USER_MULTIPLIER)
fi
STEP_RUN_TIME=$SPIKE_STEP_RUN_TIME

source $my_dir/deploy.sh $USER_COUNT

# Run progressively larger spikes up to 16 times larger than $USER_COUNT
exp=2
while [ $exp -le $SPIKE_MAX_USER_MULTIPLIER ]
do
    echo "Running $USER_COUNT users for $STEP_RUN_TIME seconds"

    WORKERS=$(expr $(expr $USER_COUNT + $USERS_PER_WORKER - 1) / $USERS_PER_WORKER)

    kubectl scale deployment worker --replicas=$WORKERS
    kubectl rollout status deployment/worker

    sleep $STEP_RUN_TIME

    spike_user_count=$[$USER_COUNT*$exp]

    echo "Running $spike_user_count users for $STEP_RUN_TIME seconds"
    WORKERS=$(expr $(expr $USER_COUNT + $USERS_PER_WORKER - 1) / $USERS_PER_WORKER)

    kubectl scale deployment worker --replicas=$WORKERS
    kubectl rollout status deployment/worker

    sleep $STEP_RUN_TIME

    exp=$[$exp*2]
done

kubectl scale deployment worker --replicas=$WORKERS
kubectl rollout status deployment/worker

echo "\n##############################################################################################"
echo "#                                                                                             #"
echo "# Make sure you run scripts/delete_cluster.sh to tear down your cluster when you're finished! #"
echo "#                                                                                             #"
echo "###############################################################################################"
