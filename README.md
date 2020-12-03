# Overview

pynas-utils is a collection of utility for making a rasperry pi powered nas a bit more useful.
The utilities are written in python and can therefore be reused also on desktop or laptops.

# Utils

## savebydate

As the name suggests, this utility moves images and videos from a directory, to a target sub-directory that represents the creation year of the file. The year is taken either from exif information, or file create / modify timestamp. This utility was inspired by [rmlint](https://rmlint.readthedocs.io/en/latest/index.html).

The savebydate script does not move the files by its own, it generates a json file with all the possible changes. The mover.py script is then responsible to move the files.

### requirements
* python3
* pip

To install other requirements, please run `pip install -r requirements.txt`

### Usage

* generate the list of files to be moved: `python savebydate.py -i "INPUT-DIRECTORY" -o "OUTPUT-DIRECTORY"`
* move the files: `python mover.py`

# Disclaimer

This project is a hobbyist project; the code was tested on mac OS and linux manually (test automation is completely missing). There is no guarantee that the files are moved to the correct directory.
