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


TODO / Document usage.
TODO / Automate environment configuration

