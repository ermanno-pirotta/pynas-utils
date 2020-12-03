!/usr/bin/env python3
# encoding: utf-8
""" This file is part of pynas-utils.

pynas-utils is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pynas-utils is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pynas-utils.  If not, see <http://www.gnu.org/licenses/>.

"""

# This is the python mover utility shipped with the pynas-utils.

import os
import argparse
import shutil
import json
import logging

def move_file(origin, target):
    logging.info("moving file %s to %s", origin, target)
    target_directory, _ = os.path.split(target)
    os.makedirs(target_directory,exist_ok=True)

    try:
        if not os.path.exists(target):
            shutil.move(origin, target)
            logging.info("file %s moved to directory %s", origin, target)
        else:
            logging.info("file %s was already present in directory %s",origin, target)

    except shutil.Error as err:
        logging.error("moving the file error: %s", err)

def main(args):
    log_file = args.log_file
    json_file = args.json_file

    if log_file is None:
        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO, filename=log_file)

    try:
        with open(json_file) as f:
            data = json.load(f)

        for entry in data['entries']:
            move_file(entry['origin_file'], entry['destination_file'])

    except KeyboardInterrupt:
        print('\ncanceled.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handles changes json file created by savebydate")

    parser.add_argument('--json_file', "-j", required=False, default='changes.json', type=str,
        help='A JSON output of savebydate to handle'
    )

    parser.add_argument("--log_file", "-l", default=None, required=False, type=str,
                        help="output file log, by default it logs to console.")

    args = parser.parse_args()
    main(args)
