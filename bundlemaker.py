#!/usr/bin/python

# This script creates bundles for charms.

import os
import stat
import sys
import yaml

charm_series = ['precise', 'trusty']
bundle_readme_text = """
# An automatically generated bundle for the {0} charm.

This bundle was automatically generated from {1}.

# Usage

You can deploy the bundle with the following command:

    juju-deployer -c {2}/bundles.yaml

This bundle makes use of local charm URIs and will not work with quickstart.
"""
bundle_test_python = """#!/usr/bin/env python3

# This file was automatically generated to test the {0} charm in a bundle.

import os
import unittest
import yaml
import amulet

seconds_to_wait = 600


class BundleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = amulet.Deployment()
        bundle_path = os.path.join(
            os.path.dirname(__file__), '../bundles.yaml')
        with open(bundle_path, 'r') as bundle_file:
            contents = yaml.safe_load(bundle_file)
            d.load(contents)
        d.setup(seconds_to_wait)
        d.sentry.wait(seconds_to_wait)
        cls.d = d

    def test_deployed(self):
        self.assertTrue(self.d.deployed)


if __name__ == '__main__':
    unittest.main()
"""
bundle_yaml = """
  services:
  relations: []
  series: trusty
"""
script_name = sys.argv[0]


def create_bundles(charm_paths, bundle_directory):
    """ Create the bundles for the charm paths in the list. """
    for path in charm_paths:
        metadata = get_charm_metadata(path)
        # Get the charm name from metatdata not the path!
        charm_name = metadata['name']
        # Get the charm series from the path.
        series = get_series(path)
        # Create the charm bundle directory path.
        charm_bundle_directory = os.path.join(bundle_directory,
                                              series,
                                              charm_name)
        if not os.path.isdir(charm_bundle_directory):
            os.makedirs(charm_bundle_directory)

        # Create the charm README.md file path.
        bundle_readme = os.path.join(charm_bundle_directory, 'README.md')
        if not os.path.isfile(bundle_readme):
            with open(bundle_readme, 'w') as readme_file:
                # Format the readme text with the variables.
                readme_text = bundle_readme_text.format(charm_name,
                                                        script_name,
                                                        charm_bundle_directory)
                # Write the bundle README.md file.
                readme_file.write(readme_text)

        # Create the bundle test directory path.
        bundle_tests_directory = os.path.join(charm_bundle_directory, 'tests')
        if not os.path.isdir(bundle_tests_directory):
            os.mkdir(bundle_tests_directory)
            # Create the bundle python test file path.
            bundle_test = os.path.join(bundle_tests_directory,
                                       '10-automated-test.py')
            with open(bundle_test, 'w') as test_file:
                # Write the bundle python test file.
                test_file.write(bundle_test_python.format(charm_name))
            st = os.stat(bundle_test)
            # Make sure the file is executable.
            os.chmod(bundle_test, st.st_mode | stat.S_IXUSR | stat.S_IXOTH)

        # Create the bundles.yaml file path.
        bundle_file = os.path.join(charm_bundle_directory, 'bundles.yaml')
        if not os.path.exists(bundle_file):
            # Write the bundles.yaml file.
            write_bundles_yaml(bundle_file, path, metadata)
            print('Created bundle in {0} for the charm {1}'.format(
                charm_bundle_directory, path))
    print('{0} bundles created.'.format(len(charm_paths)))


def create_bundles_from_directory(charm_directory, bundle_directory):
    """ Create the bundles based on the charm directory. """
    # Get charm path list from the base charm directory
    charm_paths = get_charms(charm_directory)
    # Create bundles from the charm path list.
    create_bundles(charm_paths, bundle_directory)


def get_charm_metadata(charm_path):
    """ Get the metadata of the charm. """
    # Create the path to the metadata.yaml file.
    yaml_file = os.path.join(charm_path, 'metadata.yaml')
    with open(yaml_file) as meta_file:
        # Read the metadata file in the yaml format.
        metadata = yaml.load(meta_file)
    return metadata


def get_charms(charm_directory):
    """ Create a list of paths to charms that do not have tests. """
    charm_paths = []
    charm_number = 0
    # Is the directory already a charm directory?
    if is_charm_dir(charm_directory):
        charm_paths.append(charm_directory)
        charm_number += 1
    else:
        # Go through the charms directory to find the charm directories.
        for series in charm_series:
            directory = os.path.join(charm_directory, series)
            if os.path.isdir(directory):
                for file_or_dir in os.listdir(directory):
                    charm = os.path.join(directory, file_or_dir)
                    if is_charm_dir(charm):
                        charm_number += 1
                        # Add the charm directory to the list of paths.
                        charm_paths.append(charm)

                        tests = os.path.join(charm, 'tests')
                        # Does the test directory not exist, or is it empty?
                        if not os.path.isdir(tests) or len(os.listdir(tests)) == 0:
                            print('{0} does not have tests.'.format(charm))
                        else:
                            print('{0} has tests.'.format(charm))

    print('{0} charms evaluated'.format(charm_number))
    return charm_paths


def get_series(charm_path):
    """ Get the series from a charm path. """
    series = None
    series = os.path.split(os.path.split(charm_path)[0])[1]
    return series


def is_charm_dir(path):
    """ Return True if the path is a charm directory. """
    is_charm = False
    if os.path.isdir(path):
        # The metadata file defines a charm, it must exist.
        metadata_file = os.path.join(path, 'metadata.yaml')
        if os.path.isfile(metadata_file):
            is_charm = True
    return is_charm


def write_bundles_yaml(bundle_file_name, charm_path, metadata_yaml):
    """ Create the bundles.yaml file. """
    # Grab the charm name from the metadata yaml.
    name = metadata_yaml['name']
    # The charm uri is how deployer will find the bundle.
    if (os.path.isabs(charm_path)):
        charm_uri = charm_path
    else:
        # Use a relative path.
        series = get_series(charm_path)
        index = charm_path.find(series)
        if index == -1:
            index = 0
        charm_uri = charm_path[series:]

    # Note that some of the charm URIs show up as:
    #     local:trusty/ubuntu
    #     cs:trusty/hadoop-14
    # charm_uri = 'local:trusty/' + name

    # Create the minimal number of charm parts.
    charm_parts = {'charm': str(charm_uri), 'num_units': 1}
    charm = {name: charm_parts}
    # Load the base bundle yaml data.
    base_bundle = yaml.load(bundle_yaml)
    # Set the services to the single charm.
    base_bundle['services'] = charm
    bundles_yaml = {name + '-automated-bundle': base_bundle}
    with open(bundle_file_name, 'w') as bundle_file:
        # Write the bundle file out.
        bundle_file.write(yaml.dump(bundles_yaml, default_flow_style=False))


if __name__ == '__main__':
    # The first argument is the charm directory.
    charm_directory = sys.argv[1]
    if not os.path.isabs(charm_directory):
        charm_directory = os.path.abspath(charm_directory)
    # The second argument is the bundle directory.
    bundle_directory = sys.argv[2]
    if not os.path.exists(bundle_directory):
        os.makedirs(bundle_directory)
    # Create the bundles using this charm directory, and bundle directory.
    create_bundles_from_directory(charm_directory, bundle_directory)
