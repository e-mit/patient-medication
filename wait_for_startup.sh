#!/bin/bash

host=$1
port=$2
timeout=$3

echo "Waiting for $host:$port to be available..."

start_time=$(date +%s)
while true; do
    (echo > /dev/tcp/$host/$port) >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "$host:$port is up and running"
        break
    fi

    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    if [ $elapsed -gt $timeout ]; then
        echo "Timed out waiting for $host:$port"
        exit 1
    fi

    sleep 1
done
