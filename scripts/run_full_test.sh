my_dir="$(dirname "$0")"
source $my_dir/vars.sh

USER_COUNT=$1
if [ -z "$USER_COUNT" ]; then
    USER_COUNT=$USERS_PER_WORKER
fi
HATCH_RATE=$(expr $(expr $USER_COUNT + $RAMP_UP_TIME - 1) / $RAMP_UP_TIME)

source $my_dir/deploy.sh $USER_COUNT

# slightly arbitrary wait time as Locust doesn't seem to honour the swarming call if it's called too quickly
sleep 5

echo "\nSwarming application with $USER_COUNT users"
curl -XPOST -d "hatch_rate=$HATCH_RATE&locust_count=$USER_COUNT" $LOCUST_URL/swarm

echo "Go to $LOCUST_URL to view the locust UI"
echo "\n##############################################################################################"
echo "#                                                                                             #"
echo "# Make sure you run scripts/delete_cluster.sh to tear down your cluster when you're finished! #"
echo "# Alternatively run kubectl scale deployment locust-worker --replicas=0 to scale down your    #"
echo "# workers                                                                                     #"
echo "#                                                                                             #"
echo "###############################################################################################"
