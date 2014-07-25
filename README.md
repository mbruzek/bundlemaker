bundlemaker
===========

Automatically create Juju bundles for charms without tests. 

This is a utility that creates a bundles.yaml file, a README.md file, and a 
bundle test directory and file for charms that do not already have tests.

# Usage

Run the script by the following command:

    python bundlemaker.py <charm directory> <bundle directory>

The series will be added to the charm directory (currently only precise 
and trusty) followed by a charm directory name.  

A bundle will be written if the charm directory does not contain a tests
directory or it is empty.

    python bundlemaker.py /home/mbruzek/workspace/charms /tmp/bundles/

This example will inspect the charms at /home/mbruzek/workspace/charms and
write the bundle files to /tmp/bundles/ creating the directories if necessary.
