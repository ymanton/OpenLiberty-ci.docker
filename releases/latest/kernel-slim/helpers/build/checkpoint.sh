#!/bin/bash

#if [ "$VERBOSE" != "true" ]; then
#  exec &>/dev/null
#fi

set -Eeox pipefail

if [ $# -gt 0 ]
then
    image="$1"
    containername="checkpoint.$$"
    docker run --name="$containername" --privileged --user=root --tmpfs=/run -v /lib/modules:/lib/modules "$image" checkpoint.sh
    docker commit --change='CMD ["criu", "restore", "-D", "/output/checkpoint", "--shell-job", "--tcp-established", "--file-locks"]' "$containername" "checkpoint:$$"
    docker container rm "$containername"
else
    #server start
    #serverPID="$( cat /opt/ol/wlp/output/.pid/defaultServer.pid )"
    server run &
    serverPID=$!
    sleep 10

    mkdir /output/checkpoint
    criu dump -t "$serverPID" -D /output/checkpoint --shell-job --tcp-established --file-locks
fi
