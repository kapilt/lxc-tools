Juju Alternate LXC Provider
---------------------------

This package provides a cli plugin for juju that allows for fast
provisioning of lxc containers as machines with the juju environment.

Juju already has a local provider that can create lxc (or kvm) machines,
but at the time of this plugin writing those are suboptimal as they
consume extraneous network/disk/cpu resources per container creation.

Instead this provider relies on cloning container images with
snapshots, and minimal extraneous software installation. 

Its expected that these features will be merged into the local provider
implementation so that juju's out of the box developer experience is 
awesome.

Installation
------------

 If your using the aufs containers, you need to use lxc 1.0, if your
 not on trusty, this can be gotten from the lxc stable ppa.
 https://launchpad.net/~ubuntu-lxc/+archive/stable


 There's not much automation in jlxc at the moment, so there are a few manual steps.

 There's an ansible playbook available as ec2.yml that will automate
 the setup of an instance in ec2 with ebs volume setup for btrfs.

 First you'll need to decide if your using btrfs or aufs, if your using
 btrfs, you'll need to mount /var/lib/lxc via btrfs. This can be done
 using additional drives or loopback devices. For aufs no additional
 setup is needed.

 Next, you'll need to setup your base/template container::

  $ lxc-create -t ubuntu-cloud -n precise-base -- -r precise -S ~/.ssh/id_dsa.pub
  $ lxc-create


Usage
-----

Creating containers::

  $ jlxc-add -h

  usage: jlxc-add [-h] [-b BASE_NAME] [-f {btrfs,aufs}] [-c COUNT] [-s OFFSET] [-e ENV_NAME]
  Add container to environment

  optional arguments:
    -h, --help            show this help message and exit
    -b BASE_NAME, --base BASE_NAME
                        Base container to clone
    -f {btrfs,aufs}, --fs {btrfs,aufs}
                        Filesystem type
    -c COUNT, --count COUNT
                        Number of containers to create
    -s OFFSET, --offset OFFSET
                        Name index offset
    -e ENV_NAME, --environment ENV_NAME
                        Juju environment

For example to add 5 containers to the 'foobar' environment using aufs::

  $ jlxc-add -c 5 -e foobar -b precise-subvol

Removing containers, by default removes all manual containers::

  $ jlxc-remove -e foobar

TODO
----

 - Make proper juju plugin
 - Document usage.
 - Automate environment configuration

