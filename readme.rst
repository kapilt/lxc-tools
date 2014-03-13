Juju Alternate LXC Provider
---------------------------

This package provides a cli plugin for juju that allows for fast
provisioning of lxc containers as machines with the juju environment.

Juju already has a local provider that can create lxc (or kvm) machines,
but at the time of this plugin writing those are suboptimal as they
consume extraneous network/disk/cpu resources per container creation.

Instead this provider relies on cloning container images with
snapshots, and minimal extraneous software installation. It can use
either aufs or btrfs for snapshot cloning.

Its expected that these features will be merged into the local provider
implementation so that juju's out of the box developer experience is
awesome.


Installation
============

**This plugin requires a development version of juju (>= 1.17.2)**

A usable dev version of juju is available via the dev ppa::

  $ sudo add-apt-repository ppa:juju/devel
  $ apt-get update && apt-get install juju
  $ juju version
  1.17.2-saucy-amd64

Plugin installation is done via pip/easy_install which is the python language
package managers, its available by default on ubuntu. Also recommended
is virtualenv to sandbox this install from your system packages::

  $ pip install -U juju-lxc


Setup
=====

A one-time host installation is needed of the required packages::

  $ juju lxc init-host

This will download the stable ppa version of lxc 1.0, and additional
packages needed. It will also setup an apt cache on the host for the
containers, if the host doesn't already have one configured, else the
host configuration will be used.

For each ubuntu release series you want to use, the relevant cloud
image must be downloaded, and a template container must be
created. These images are about 220Mb in size.

Let's continue by setting up a precise container with::

  $ juju lxc init-series precise

Additional series can be passed (space separated) or downloaded later.


Juju config
+++++++++++

Next let's configure a juju environment for jlxc, add a manual/null
provider environment to 'environments.yaml' for example::

  enviroments:
    jlxc:
      type: manual
      bootstrap-host: null
      bootstrap-user: ubuntu

Usage
=====

We need to tell juju which environment we want to use, there are
several ways to do this, either of the following will do the trick::

  $ juju switch jlxc
  $ export JUJU_ENV=jlxc

Now we can bootstrap our digital ocean environment::

  $ juju jlxc bootstrap -v

Which will create a container and configure it as the enviroment
state server. We can see the container running by using the lxc
command

  $ sudo lxc-ls --running --fancy
  NAME        STATE    IPV4        IPV6  AUTOSTART
  ------------------------------------------------
  jlxc-state  RUNNING  10.0.3.132  -     NO


The bootstrap machine can take a few minutes longer than a workload
container to start due to the mongodb package installation. Other
containers have all juju dependencies pre-installed.


After our environment is bootstrapped we can add additional machines
to it via the the add-machine command, for example the following will
add 5 containers in a few seconds::

  $ juju lxc add-machine -n 5
  $ juju status


We can now use standard juju commands for deploying service workloads aka
charms::

  $ juju deploy mediawiki

Without specifying the machine to place the workload on, the machine
will automatically go to an unused machine within the environment.

There are hundreds of available charms ready to be used, you can
find out more about what's out there from http://jujucharms.com
Or alternatively the 'plain' html version at
http://manage.jujucharms.com/charms/precise

We can use manual placement to deploy target particular machines::

  $ juju deploy mysql --to=2

And of course the real magic of juju comes in its ability to assemble
these workloads together via relations like lego blocks::

  $ juju add-relation mediawiki mysql
