#!/bin/bash

# Redirect copy of stdout/stderr to log file
# See http://goo.gl/WWd6BN
exec > >(tee install.log)
exec 2>&1

# Update and upgrade
sudo apt-get update
sudo apt-get -y upgrade

## Server Install ##
# Install hwe kernel
#sudo apt-get -y install linux-generic-lts-raring
# Install Go
#wget https://godeb.s3.amazonaws.com/godeb-amd64.tar.gz
#tar xzvf godeb-amd64.tar.gz
#./godeb install 1.1.2

# Install Juju branch
#sudo apt-get install git mercurial bzr
#export GOPATH=$HOME
#go get install -u -v launchpad.net/juju-core/...

# Install Dependencies.
#sudo apt-get -y install python-virtualenv python-software-properties
#sudo add-apt-repository -y cloud-archive:tools
#sudo apt-get update
#sudo apt-get -y install python-mongo python-yaml lxc


# Saucy and Raring
sudo apt-get -y install python-yaml lxc python-virtualenv cloud-image-tools

# Seed lxc while manually being controlled
sudo mkdir -p /var/cache/lxc/cloud-precise
if [ -f ubuntu-12.04-server-cloudimg-amd64-root.tar.gz ]
    cd /var/cache/lxc/cloud-precise && sudo wget `ubuntu-cloudimg-query precise -f "%{url}"`
then

# Create a key for lxc container usage
#ssh-keygen  -q -b 2048 -t rsa -f ~/.ssh/id_containers_rsa -N ""

# Create seed container
#sudo lxc-create -n precise-base -t ubuntu-cloud -- -S ~/.ssh/id_containers_rsa.pub


#
