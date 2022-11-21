#!/bin/bash

set -x
DIRNAME=$(dirname "$(realpath "$0")")
. "$DIRNAME/setup-lib.sh"


#
# Install Python and Ansible
#
do_apt_update
maybe_install_packages software-properties-common
$SUDO add-apt-repository ppa:deadsnakes/ppa -y
maybe_install_packages python3.9
maybe_install_packages python3-pip python3.9-distutils python3-setuptools python3.9-venv
$PYTHON -m pip install pip
$PYTHON -m venv "$ANSIBLE_VENV"
. "$ANSIBLE_VENV"/bin/activate
$PIP install --upgrade ansible

#
# Ansible config
#
if [ -e "$INV_DIR" ]; then
    rm -rf "$INV_DIR"
fi

if [ -e "$OVERRIDES" ]; then
    rm -rf "$OVERRIDES"
fi

mkdir -p "$INV_DIR"

echo "[all]" > "$INV"
for node in "${NODES[@]}" ; do
    ip=$(get_node_ip "$node")
    user=$(get_node_user "$node")
    echo "$node ansible_user=$user ansible_host=$ip ip=$ip access_ip=$ip" >> "$INV"
done

cat <<EOF >> "$OVERRIDES"
override_system_hostname: false
disable_swap: true
ansible_python_interpreter: /usr/bin/python3
EOF

$ANSIBLE playbook -K -i "$INV_DIR/inventory.ini" \
    -e @"${OVERRIDES}" -b -v "$PLAYBOOK_DIR/site.yaml" \
    --flush-cache \
    --extra-vars "key_name=$KEY_NAME"
