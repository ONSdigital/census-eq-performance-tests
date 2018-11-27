my_dir="$(dirname "$0")"
source $my_dir/vars.sh

gcloud beta container \
--project "$PROJECT_ID" clusters delete "$CLUSTER_NAME" \
--zone "$ZONE" \
--quiet