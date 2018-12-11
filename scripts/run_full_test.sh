my_dir="$(dirname "$0")"
source $my_dir/vars.sh

USER_COUNT=$1
if [ -z "$USER_COUNT" ]; then
    USER_COUNT=$USERS_PER_WORKER
fi
HATCH_RATE=$(expr $(expr $USER_COUNT + $RAMP_UP_TIME - 1) / $RAMP_UP_TIME)

source $my_dir/deploy.sh $USER_COUNT


echo "\n##############################################################################################"
echo "#                                                                                             #"
echo "# Make sure you run scripts/delete_cluster.sh to tear down your cluster when you're finished! #"
echo "# Alternatively run kubectl scale deployment worker --replicas=0 to scale down your workers   #"
echo "#                                                                                             #"
echo "###############################################################################################"
