#!/bin/bash

set -x
DIRNAME=`dirname "$(realpath $0)"`
. "$DIRNAME/setup-lib.sh"

# Remove existing ssh key
rm -f ~/.ssh/"${KEY_NAME}" ~/.ssh/"${KEY_NAME}.pub"

if [ ! -f ~/.ssh/"${KEY_NAME}" ]; then
    ssh-keygen -t "${KEY_TYPE}" -f ~/.ssh/"${KEY_NAME}" -N ""
fi

# Scan worker nodes
touch ~/.ssh/known_hosts
chmod 600 ~/.ssh/known_hosts
for node in "${NODES[@]}" ; do
    node_ip=$(get_node_ip "$node")
    echo "$node_ip" | ssh-keyscan -4 -f - >> ~/.ssh/known_hosts
done

# Copy public ssh key to worker nodes
for node in "${NODES[@]}" ; do
    ip=$(get_node_ip "$node")
    user=$(get_node_user "$node")
    ssh-copy-id -i ~/.ssh/"${KEY_NAME}.pub" "$user"@"$ip"
done