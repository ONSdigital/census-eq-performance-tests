my_dir="$(dirname "$0")"
source $my_dir/vars.sh

USER_COUNT=$1
if [ -z "$USER_COUNT" ]; then
    USER_COUNT=$(expr $USERS_PER_WORKER / $SPIKE_MAX_USER_MULTIPLIER)
fi
STEP_RUN_TIME=$SPIKE_STEP_RUN_TIME
HATCH_RATE=$(expr $(expr $USER_COUNT + $RAMP_UP_TIME - 1) / $RAMP_UP_TIME)

source $my_dir/deploy.sh $USER_COUNT
echo "Go to $LOCUST_URL to view the locust UI"

# slightly arbitrary wait time as Locust doesn't seem to honour the swarming call if it's called too quickly
sleep 5

# Run progressively larger spikes up to 16 times larger than $USER_COUNT
exp=2
while [ $exp -le $SPIKE_MAX_USER_MULTIPLIER ]
do
    echo "Running $USER_COUNT for $STEP_RUN_TIME hatching at $HATCH_RATE/s"
    curl -XPOST -d "hatch_rate=$HATCH_RATE&locust_count=$USER_COUNT" $LOCUST_URL/swarm
    sleep $STEP_RUN_TIME
    
    spike_user_count=$[$USER_COUNT*$exp]
    spike_hatch_rate=$(expr $(expr $spike_user_count + $RAMP_UP_TIME - 1) / $RAMP_UP_TIME)

    echo "Running $spike_user_count for $STEP_RUN_TIME hatching at $spike_hatch_rate/s"
    curl -XPOST -d "hatch_rate=$spike_hatch_rate&locust_count=$spike_user_count" $LOCUST_URL/swarm
    sleep $STEP_RUN_TIME

    exp=$[$exp*2]
done

curl $LOCUST_URL/stop

echo "\n##############################################################################################"
echo "#                                                                                             #"
echo "# Make sure you run scripts/delete_cluster.sh to tear down your cluster when you're finished! #"
echo "# Alternatively run kubectl scale deployment locust-worker --replicas=0 to scale down your    #"
echo "# workers                                                                                     #"
echo "#                                                                                             #"
echo "###############################################################################################"
