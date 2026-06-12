# -*- coding: utf-8 -*-

# Internal Imports
import argparse
import configparser
import datetime
import logging
import os

# Personal Imports
from . import constants

def get_verbosity():
    parser = argparse.ArgumentParser(prog = 'e621dl', description = 'An automated e621 downloader.')
    verbosity = parser.add_mutually_exclusive_group(required = False)

    verbosity.add_argument('-v', '--verbose', action = 'store_true', help = 'Display full debug information while running.')
    verbosity.add_argument('-q', '--quiet', action = 'store_true', help = 'Display no output while running, except for errors.')

    args = parser.parse_args()

    if args.quiet:
        return logging.ERROR
    elif args.verbose:
        return logging.DEBUG

    return logging.INFO

def init_log():
    logging.basicConfig(level = get_verbosity(), format = constants.LOGGER_FORMAT)
    logging.getLogger('requests').setLevel(logging.CRITICAL)
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)

def print_log(module, log_level, log_message):
    log = logging.getLogger(module)
    getattr(log, log_level)(log_message)

def make_config():
    with open('config.ini', 'wt', encoding = 'utf_8_sig') as outfile:
        outfile.write(constants.DEFAULT_CONFIG_TEXT)
        print_log('local', 'info', 'New default config file created. Please add tag groups to this file.')

    raise SystemExit

def get_config():
    config = configparser.ConfigParser()

    if not os.path.isfile('config.ini'):
        print_log('local', 'error', 'No config file found.')
        make_config()

    with open('config.ini', 'rt', encoding = 'utf_8_sig') as infile:
        config.read_file(infile)

    return config

def get_date(days_to_check):
    ordinal_check_date = datetime.date.today().toordinal() - (days_to_check - 1)

    if ordinal_check_date < 1:
        ordinal_check_date = 1
    elif ordinal_check_date > datetime.date.today().toordinal():
        ordinal_check_date = datetime.date.today().toordinal()

    return datetime.date.fromordinal(ordinal_check_date).strftime(constants.DATE_FORMAT)

def substitute_illegals(char):
    illegals = ['\\', ':', '*', '?', '\"', '<', '>', '|', ' ']

    return '_' if char in illegals else char

def make_path(dir_name, filename, ext):
    clean_dir_name = ''.join([substitute_illegals(char) for char in dir_name]).lower()

    if not os.path.isdir('/Users/ixion/Projects/e621dl/downloads/' + clean_dir_name):
        os.makedirs('/Users/ixion/Projects/e621dl/downloads/' + clean_dir_name)

    return '/Users/ixion/Projects/e621dl/downloads/' + clean_dir_name + '/' + filename + '.' + ext

def make_url(md5, ext):
    return 'https://static1.e621.net/data/' + md5[0:2] + '/' + md5[2:4] + '/' + md5 + '.' + ext
