my_dir="$(dirname "$0")"
source $my_dir/vars.sh

ROOT=$(dirname "$mydir")

docker build -t "$DOCKER_REPO" -f $ROOT/docker/full_test.Dockerfile $ROOT
docker push $DOCKER_REPO
