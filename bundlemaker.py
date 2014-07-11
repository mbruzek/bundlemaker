#!/usr/bin/python

# This script writes bundles for charms that do not have amulet tests.

import os
import sys
import yaml

charm_series = ['precise', 'trusty']
bundle_readme_text = """
# An automatically generated bundle for the {0} charm.

This bundle was automatically generated from the {1} script.

# Usage

You can deploy the bundle with the following command:

    juju-deployer -c {2}/bundles.yaml

This bundle makes use of local charm URIs and will not work with quickstart.
"""
bundle_test_python = """#!/usr/bin/env python3

# This test file was automatically generated to stand up the {0} charm on its own.

import os
import unittest
import yaml

import amulet
import requests


class BundleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        d = amulet.Deployment()
        bundle_file = os.path.join(
            os.path.dirname(__file__), '../bundles.yaml')
        with open(bundle_file, 'r') as f:
            d.load(yaml.safe_load(f))
        d.setup()
        d.sentry.wait()
        cls.d = d

if __name__ == '__main__':
    b = BundleTest()
    b.setupClass()

"""
bundle_yaml = """
  services:
  relations: []
  series: trusty
"""


def charms_without_tests(charm_directory):
    """ Create a list of paths to charms that do not have tests. """
    charm_paths = []
    # Iterate over each series.
    for series in charm_series:
        directory = os.path.join(charm_directory, series)
        for file_or_dir in os.listdir(directory):
            charm = os.path.join(directory, file_or_dir)
            if os.path.isdir(charm):
                # The metadata file defines a charm, it must exist.
                metadata_file = os.path.join(charm, 'metadata.yaml')
                if os.path.isfile(metadata_file):
                    tests = os.path.join(charm, 'tests')
                    # Does the tests directory exist and is not empty?
                    if not os.path.isdir(tests) or len(os.listdir(tests)) == 0:
                        # Add the charm directory to the path.
                        charm_paths.append(charm)
    return charm_paths


def get_series(charm_path):
    """ Get the series from a charm path. """
    series = None
    series = os.path.split(os.path.split(charm_path)[0])[1]
    return series


def get_charm_metadata(charm_path):
    """ Get the metadata of the charm. """
    # Create the path to the metadata.yaml file.
    yaml_file = os.path.join(charm_path, 'metadata.yaml')
    with open(yaml_file) as meta_file:
        # Read the metadata file in the yaml format.
        metadata = yaml.load(meta_file)
    return metadata


def write_bundles_yaml(bundle_file_name, metadata_yaml):
    """ Create the bundles.yaml file. """
    # Grab the charm name from the metadata yaml.
    name = metadata_yaml['name']

    # The charm uri is how deployer will find the bundle.
    charm_uri = name
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


def create_bundles(bundle_directory, charm_paths):
    """ Create the bundles for the charm paths in the list. """
    if not os.path.exists(bundle_directory):
        os.makedirs(bundle_directory)
    for path in charm_paths:
        metadata = get_charm_metadata(path)
        # Get the charm name from metatdata not the path!
        charm_name = metadata['name']
        # Get the charm series from the path.
        series = get_series(path)
        # Create the charm bundle directory path.
        charm_bundle_directory = os.path.join(bundle_directory, series, charm_name)
        if not os.path.isdir(charm_bundle_directory):
            os.makedirs(charm_bundle_directory)

        # Create the charm README.md file path.
        bundle_readme = os.path.join(charm_bundle_directory, 'README.md')
        if not os.path.isfile(bundle_readme):
            # Write the bundle README.md file.
            with open(bundle_readme, 'w') as readme_file:
                readme_file.write(bundle_readme_text.format(charm_name,
                                                            sys.argv[0],
                                                            charm_bundle_directory))

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
            os.chmod(bundle_test, 0755)

        # Create the bundles.yaml file path.
        bundle_file = os.path.join(charm_bundle_directory, 'bundles.yaml')
        if not os.path.exists(bundle_file):
            # Write the bundles.yaml file.
            write_bundles_yaml(bundle_file, metadata)

        print('Created bundle in {0} for the charm {1}'.format(
            charm_bundle_directory, path))


if __name__ == '__main__':
    # The first argument is the charm directory.
    directory = sys.argv[1]
    # Get a list of paths to charms without tests.
    charm_paths = charms_without_tests(directory)
    # The second argument is the bundle directory.
    create_bundles(sys.argv[2], charm_paths)
