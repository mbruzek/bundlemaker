#!/usr/bin/python

# This script looks for bundles and runs them with juju-deployer.
# The JUJU_REPOSITORY must be set for juju-deployer to find the local charms.

import glob
import os
import shutil
import subprocess
import sys


bundle_series = ['precise', 'trusty']


def deploy_bundles(bundles, output):
    """ Deploy the bundle tests in the list of bundles.  """

    bootstrap = ['juju', 'bootstrap', '-v', '-e', 'local', '--debug']
    run_command(bootstrap, os.path.join(output, 'bootstrap.log'))

    for bundle in bundles:
        # Create a unique name for the result file.
        bundle_name = os.path.split(bundle)[1]
        # Create the path to the bundle file.
        bundle_file_name = os.path.join(bundle, 'bundles.yaml')
        series = get_series(bundle)
        if series:
            result_file_name = '{0}_{1}'.format(series, bundle_name)
        else:
            result_file_name = bundle_name
        result_path = os.path.join(output, result_file_name)
        # Create a place to put the output log files from charmtools.
        logs_directory = result_path + "_logs"
        if not os.path.isdir(logs_directory):
            os.mkdir(logs_directory)

        # Create the command to run the deployer.
        deployer = ['juju-deployer',
                    '-c', bundle_file_name,  # The config file.
                    '-L',                    # Allow locally modified charms.
                    '-t', '540',             # Timeout in seconds.
                    '-s', '1'                # Seconds to delay deploy commands.
                    ]
        run_command(deployer, result_path)

        # Expand the relative path.
        log_path = os.path.expanduser('~/.juju/local/log')
        if os.path.islink(log_path):
            log_path = os.path.realpath(log_path)
        unit_files = os.path.join(log_path, 'unit*.log')
        unit_log_files = glob.glob(unit_files)
        for unit_file in unit_log_files:
            shutil.copy2(unit_file, logs_directory)

        # Create the command to cleanup the juju environment.
        terminator = ['juju-deployer',
                      '-T'              # Terminate machines.
                      ]
        run_command(terminator, os.path.join(output, "terminate-machines.log"))
    # Destroy the juju environment now that we are done.
    destroy = ['juju', 'destroy-environment', '-y', 'local']
    run_command(destroy, os.path.join(output, 'destroy-environment.txt'))


def deploy_bundles_path(bundle_directory, output):
    """ Deploy the bundle tests given a bundle directory. """
    # Find the bundles to test.
    bundles = get_bundles(bundle_directory)
    print("{0} bundles found running tests.".format(len(bundles)))
    # Run the bundle tests.
    deploy_bundles(bundles, output)


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


def get_series(bundle_path):
    """ Get the series from a bundle path. """
    series = None
    series = os.path.split(os.path.split(bundle_path)[0])[1]
    return series


def is_bundle_dir(path):
    """ Return true if the path is a bundle. """
    is_bundle = False
    # A bundle in this sense must be a directory.
    if os.path.isdir(path):
        files_and_dirs = os.listdir(path)
        # A bundle must contain bundles.yaml.
        if 'bundles.yaml' in files_and_dirs:
            is_bundle = True
    return is_bundle


def run_command(command, output=None):
    """ Run a command and capture the output to a file. """
    print(command)
    try:
        # Run the command.
        results = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as cpe:
        results = "{0} returned {1} with output {2}".format(
            cpe.cmd, cpe.returncode, str(cpe.output))
    print(results)
    if output:
        # Write the results to a file.
        with open(output, 'w') as result_file:
            result_file.write(str(results))
        print("Results written to {0}".format(output))


if __name__ == '__main__':
    # The first argument to this script must be the bundle directory.
    bundle_directory = sys.argv[1]
    # The second argument to this script must be the output directory.
    output = sys.argv[2]
    # Create the output directory if it does not exist.
    if not os.path.isdir(output):
        os.mkdir(output)
    # Run the bundles at this path.
    deploy_bundles_path(bundle_directory, output)
