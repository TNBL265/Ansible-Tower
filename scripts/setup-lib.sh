#!/bin/bash

##
## Main attributes
##
NODES=( "ansible-lockdown-ubuntu20" ) #"ansible-lockdown-amazon2" ) #"ansible-lockdown-rhel8")
NODES_USER=( "Ubuntu-20p04" ) #"AmazonLinux-2" ) #"RHatELinux-8")
NODES_IP=( "10.244.33.199" ) #"10.244.33.200" ) #"10.244.33.201" )

##
## Config
##
REPO_DIR=/home/CCCS-audit22/Ansible-Tower

KEY_NAME=id_rsa
KEY_TYPE=rsa

ANSIBLE_VENV=$REPO_DIR/ansible_venv
INV_DIR=$REPO_DIR/ansible/inventories
INV=$INV_DIR/inventory.ini
OVERRIDES=$INV_DIR/overrides.yml
PLAYBOOK_DIR=$REPO_DIR/ansible

PYTHON=python3.9
PIP="python3.9 -m pip"
ANSIBLE="python3.9 -m ansible"

##
## Node attribute getters
##
get_node_idx() {
    DONE=0
    if [ -z "$1" ]; then
      echo ""
      return
    fi
    i=0
    for node in "${NODES[@]}" ; do
        if [ "$node" = "$1" ]; then
            DONE=1
            break
        else
            (( i++ ))
        fi
    done
    if [ $DONE -eq 0 ]; then
        echo "Fail to get node idx"
        exit 1
    fi
    echo $i;
}

get_node_ip() {
    idx=$(get_node_idx "$1")
    ip=${NODES_IP[$idx]}
	echo "$ip"
}

get_node_user() {
    idx=$(get_node_idx "$1")
    user=${NODES_USER[$idx]}
	echo "$user"
}

##
## Package installation utils
##
if [ -z "$UID" ]; then
    UID=$(id -u)
fi
SUDO=
if [ ! "$UID" -eq 0 ] ; then
    SUDO=sudo
fi

export DEBIAN_FRONTEND=noninteractive
DPKG_OPTS=""
APT_GET_INSTALL_OPTS="-y"
APT_GET_INSTALL="$SUDO apt-get $DPKG_OPTS install $APT_GET_INSTALL_OPTS"
if [ "${DO_APT_INSTALL}" = "0" ]; then
    APT_GET_INSTALL="/bin/true ${APT_GET_INSTALL}"
fi

do_apt_update() {
    if [ ! -f "$OURDIR"/apt-updated -a "${DO_APT_UPDATE}" = "1" ]; then
	$SUDO apt-get update
	touch "$OURDIR"/apt-updated
    fi
}

are_packages_installed() {
    ret_val=1
    while [ ! -z "$1" ] ; do
	dpkg -s "$1" >/dev/null 2>&1
	if [ ! $? -eq 0 ] ; then
	    ret_val=0
	fi
	shift
    done
    return $ret_val
}

maybe_install_packages() {
    if [ ! "${DO_APT_UPGRADE}" -eq 0 ] ; then
        # Just do an install/upgrade to make sure the package(s) are installed
	# and upgraded; we want to try to upgrade the package.
	$APT_GET_INSTALL "$@"
	return $?
    else
	# Ok, check if the package is installed; if it is, don't install.
	# Otherwise, install (and maybe upgrade, due to dependency side effects).
	# Also, optimize so that we try to install or not install all the
	# packages at once if none are installed.
	are_packages_installed $@
	if [ $? -eq 1 ]; then
	    return 0
	fi

	ret_val=0
	while [ -n "$1" ] ; do
	    are_packages_installed "$1"
	    if [ $? -eq 0 ]; then
		$APT_GET_INSTALL $1
		ret_val=$($ret_val \| $?)
	    fi
	    shift
	done
	return "$ret_val"
    fi
}