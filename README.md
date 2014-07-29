bundlemaker
===========

Automatically create Juju bundles for charms without tests. 

This is a utility that creates a bundles.yaml file, a README.md file, and a 
bundle test directory and file for charms.

# Usage: bundlemaker

Run the script by the following command:

    python bundlemaker.py <charm directory> <bundle directory>

If the charm directory is a path to an existing charm the script will
create the bundle for that one charm.

Otherwise the series will be added to the charm directory (currently only 
precise and trusty) followed by a charm directory name.  

A bundle will be written if the charm directory does not contain a tests
directory or it is empty.

    python bundlemaker.py /home/mbruzek/workspace/charms /tmp/bundles/

This example will inspect the charms at /home/mbruzek/workspace/charms and
write the bundle files to /tmp/bundles/ creating the directories if necessary.


# Usage: bundlerunner

The bundlerunner script runs the "juju test" command within the bundles that 
were created with bundlemaker.  

Run the script by issuing the following command:

    python bundlerunner.py <bundle directory> <output directory>

The script will find the bundles at the given directory and execute the 
"juju test" command running the bundle test for each bundle.

If the bundle directory is a path to an existing bundle it will just run
the test in the one bundle and store the output in the desired location.

Otherwise the series will be added to the bundle directory and the subtree
will be examined looking for bundles to run.

The directory structure that will be searched for a bundles.yaml is:

    bundle_directory/series/bundle_name/

To run the bundle tests that were created by the bundlemaker example above
run the following command:

    python bundlerunner.py /tmp/bundles /tmp/bundle_test_output

