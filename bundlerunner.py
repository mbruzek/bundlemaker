#!/usr/bin/python

# This script runs all the bundle tests in a subdirectory.

import os
import subprocess
import sys


# The first argument to this script must be the bundle directory.
bundle_directory = sys.argv[1]
# The second argument to this script must be the output directory.
output = sys.argv[2]

charm_series = ['precise', 'trusty']
command = ['juju', 'test', '-v', '--timeout', '9m', '--on-timeout', 'skip']

for series in charm_series:
    directory = os.path.join(bundle_directory, series)
    if os.path.isdir(directory):
        for file_or_dir in os.listdir(directory):
            bundle = os.path.join(directory, file_or_dir)
            if os.path.isdir(bundle):
                print(bundle)
                # Change the directory to the bundle root.
                os.chdir(bundle)
                print(command)
                try:
                    # Run the juju test command in this directory.
                    results = subprocess.check_output(command,
                                                      stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as cpe:
                    results = "{0} returned {1} with output {2}".format(cpe.cmd,
                        cpe.returncode, cpe.output)
                print(results)
                result_path = os.path.join(output, bundle.replace('/', '_'))
                with open(result_path, 'w') as result_file:
                    result_file.write(str(results))
                print("Results written to {0}".format(result_path))
