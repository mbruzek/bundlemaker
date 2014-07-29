#!/usr/bin/python

# This script goes into a bundle directory and runs all the bundle tests.

import os
import subprocess
import sys


bundle_series = ['precise', 'trusty']


def is_bundle_dir(path):
    """ Return true if the path is a bundle. """
    is_bundle = False
    # A bundle in this sense must be a directory.
    if os.path.isdir(path):
        files_and_dirs = os.listdir(path)
        # A bundle must contain bundles.yaml and a tests directory.
        if 'bundles.yaml' in files_and_dirs and 'tests' in files_and_dirs:
            is_bundle = True
    return is_bundle


def get_bundles(bundle_directory):
    """ Return a list of bundles to run tests for. """
    bundle_paths = []
    # Is the directory already a bundle directory?
    if is_bundle_dir(bundle_directory):
        bundle_paths.append(bundle_directory)
    else:
        # Go through the directories to find the bundle directories.
        for series in bundle_series:
            directory = os.path.join(bundle_directory, series)
            if os.path.isdir(directory):
                for file_or_dir in os.listdir(directory):
                    bundle = os.path.join(directory, file_or_dir)
                    if is_bundle_dir(bundle):
                        bundle_paths.append(bundle)

    return bundle_paths


def run_bundles_path(bundle_directory, output):
    """ Run the bundle tests given a bundle directory. """
    # Find the bundles to test.
    bundles = get_bundles(bundle_directory)
    print("{0} bundles found running tests.".format(len(bundles)))
    # Run the bundle tests.
    run_bundles(bundles, output)


def run_bundles(bundles, output):
    """ Run the bundle tests in the list of bundles.  """
    for bundle in bundles:
        # Create a command that needs an output directory appended.
        command = ['juju', 'test', '-v', '--timeout', '9m',
                   '--on-timeout', 'fail', '-o']
        print(bundle)
        # Change the directory to the bundle root.
        os.chdir(bundle)
        command.append(os.path.join(output, bundle))
        print(command)
        try:
            # Run the juju test command in this directory.
            results = subprocess.check_output(
                command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as cpe:
            results = "{0} returned {1} with output {2}".format(
                cpe.cmd, cpe.returncode, cpe.output)
        print(results)
        # Create a unique name for the result file.
        result_file_name = bundle.replace('/', '_')
        result_path = os.path.join(output, result_file_name)
        # Write the results of the bundle test.
        with open(result_path, 'w') as result_file:
            result_file.write(str(results))
        print("Results written to {0}".format(result_path))


if __name__ == '__main__':
    # The first argument to this script must be the bundle directory.
    bundle_directory = sys.argv[1]
    # The second argument to this script must be the output directory.
    output = sys.argv[2]
    # Create the output directory if it does not exist.
    if not os.path.isdir(output):
        os.mkdir(output)
    # Run the bundles at this path.
    run_bundles_path(bundle_directory, output)
