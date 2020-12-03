from PIL import Image
from PIL import UnidentifiedImageError
import datetime
import argparse
import os
import re
import shutil
import platform
import uuid
import hashlib
import logging
import json

year_from = 2000
year_to = datetime.datetime.now().year + 1

def is_valid_date(date):
    return date is not None and date > year_from and date < year_to

def get_create_year_from_exif(path_to_file):
    try:
        im = Image.open(path_to_file)
        exif = im.getexif()
        creation_time = exif.get(36867)
        date_time_obj = datetime.datetime.strptime(creation_time, "%Y:%m:%d %H:%M:%S")
        create_year = date_time_obj.year
        return create_year
    except ValueError:
        logging.error("exception while converting the date")
        return None
    except UnidentifiedImageError:
        logging.error("exception while reading the file, skipping it")
        return None

def get_create_year_from_filename(path_to_file):
    filename_with_extension = os.path.basename(path_to_file)
    filename = os.path.splitext(filename_with_extension)[0]
    try:
        create_year = int(filename[0 : 4])
        return create_year
    except ValueError:
        return None

def get_create_year_from_file_info(path_to_file):
    stat = os.stat(path_to_file)
    try:
        last_modification_year = datetime.datetime.fromtimestamp(stat.st_mtime)
        return last_modification_year.year
    except AttributeError:
        # We"re probably on Linux. No easy way to get creation dates here,
        # so we"ll settle for when its content was last modified.
        logger.info("exception while getting the last last_modification_year from file information")
        return None

def process_file(type, path_to_file):
    change_entry = {}
    change_entry['type'] = type
    change_entry['origin_file'] = path_to_file

    if(type == "image"):
        try:
            create_year = get_create_year_from_exif(path_to_file)
            change_entry['date_source'] = 'exif_info'

            if not is_valid_date(create_year):
                create_year = get_create_year_from_file_info(path_to_file)
                change_entry['date_source'] = 'file_creation_date'

            if not is_valid_date(create_year):
                create_year = get_create_year_from_filename(path_to_file)
                change_entry['date_source'] = 'file_name'

            if not is_valid_date(create_year):
                return None

        except TypeError:
            create_year = get_create_year_from_file_info(path_to_file)
            change_entry['date_source'] = 'file_creation_date'
    else:
        create_year = get_create_year_from_filename(path_to_file)
        change_entry['date_source'] = 'file_name'

        if not is_valid_date(create_year):
            create_year = get_create_year_from_file_info(path_to_file)
            change_entry['date_source'] = 'file_creation_date'

    change_entry['year'] = create_year
    return change_entry


def get_dest_file_name(origin_file, target_directory):
    origin_file_extension = os.path.splitext(origin_file)[1]
    return os.path.join(target_directory,str(uuid.uuid4()) + origin_file_extension)

def main(args):
    start_time = datetime.datetime.now()
    log_file = args.log_file

    year_from = args.year_from

    if log_file is None:
        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO)
    else:
        logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.INFO, filename=log_file)

    image_ext = [".jpg"]
    video_ext = [".mp4", ".avi"]

    input_directory = args.input
    output_directory = args.output

    changes = {}
    changes['entries'] = []
    changes['skipped'] = []
    move_count = 0
    skip_count = 0

    logging.info("processing files from %s to %s subdirectories, by file creation date", input_directory, output_directory)

    for root, dirs, files in os.walk(input_directory):
        for file in files:
            type = ""

            if file.lower().endswith(tuple(image_ext)):
                type = "image"
            elif file.lower().endswith(tuple(video_ext)):
                type = "video"

            if type == "image" or type == "video":
                path_to_file = os.path.join(root, file)
                logging.info("processing file %s", path_to_file)
                change_entry = process_file(type, path_to_file)

                if change_entry is None:
                    changes['skipped'].append({'origin_file' : path_to_file})
                    skip_count += 1
                else:
                    target_directory = os.path.join(output_directory, str(change_entry['year']))
                    change_entry['destination_file'] = get_dest_file_name(path_to_file, target_directory)
                    logging.info('%s -> %s (%s : %s)', change_entry['origin_file'], change_entry['destination_file'], change_entry['year'], change_entry['date_source'])
                    changes['entries'].append(change_entry)
                    move_count += 1

    execution_time = datetime.datetime.now() - start_time
    summary = {'moved' : move_count, 'skipped': skip_count, 'execution_time': str(execution_time)}
    changes['summary'] = summary

    with open('changes.json', 'w') as json_file:
        json.dump(changes, json_file)

    logging.info("processed a total of %s files, %s skipped due to errors", move_count + skip_count, skip_count)
    logging.info("to move the files, please review changes.json with the command python3 -m json.tool changes.json")
    logging.info("and then run mover.py")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Saves images and videos by creation date")

    parser.add_argument("--input", "-i", default=None, required=True,type=str,
                        help="input directory.")

    parser.add_argument("--output", "-o", default=None, required=True,type=str,
                        help="output directory.")

    parser.add_argument("--log_file", "-l", default=None, required=False,type=str,
                        help="output file log, by default it logs to console.")

    parser.add_argument("--year_from", "-f", default=2000, required=False,type=int,
                        help="output file log, by default it logs to console.")


    args = parser.parse_args()
    main(args)
