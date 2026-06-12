# -*- coding: utf-8 -*-

# Internal Imports
import os
# from distutils.version import StrictVersion
from fnmatch import fnmatch

# External Imports
import requests

# Personal Imports
from lib import constants
from lib import local
from lib import remote
import time
# import subprocess
import shutil

print(constants.USER_AGENT)

# This block will only be read if e621dl.py is directly executed by python. Not if it is imported.
if __name__ == '__main__':
    # Create the requests session that will be used throughout the run and set the user-agent.
    # The user-agent requirements are specified at (https://e621.net/help/show/api#basics).
    with requests.Session() as session:
        session.headers['User-Agent'] = constants.USER_AGENT

    local.init_log()

    # Check if a new version is released on github. If so, notify the user.
    # Not required because we're running headless
    # if StrictVersion(constants.VERSION) < StrictVersion(remote.get_github_release(session)):
    # local.print_log('e621dl', 'info', 'A NEW VERSION OF E621DL IS AVAILABLE ON GITHUB: (https://github.com/Wulfre/e621dl/releases/latest).')

    local.print_log('e621dl', 'info', 'Running e621dl version ' + constants.VERSION + '.')
    local.print_log('e621dl', 'info', 'Checking for partial downloads.')
    remote.finish_partial_downloads(session)
    local.print_log('e621dl', 'info', 'Parsing config.')
    config = local.get_config()

    # Initialize the lists that will be used to filter posts.
    blacklist = []
    searches = []

    # Initialize user configured options in case any are missing.
    include_md5 = False  # The md5 checksum is not appended to file names.
    default_date = local.get_date(1)  # Get posts from one day before execution.
    default_score = -0x7FFFFFFF  # Allow posts of any score to be downloaded.
    default_ratings = ['e']  # Allow only explicit posts to be downloaded.

    # Iterate through all sections (lines enclosed in brackets: []).
    for section in config.sections():

        # Get values from the "Other" section. Currently only used for file name appending.
        if section.lower() == 'other':
            for option, value in config.items(section):
                if option.lower() == 'include_md5':
                    if value.lower() == 'true':
                        include_md5 = True

        # Get values from the "Defaults" section. This overwrites the initialized default_* variables.
        elif section.lower() == 'defaults':
            for option, value in config.items(section):
                if option.lower() in {'days_to_check', 'days'}:
                    default_date = local.get_date(int(value))
                elif option.lower() in {'min_score', 'score'}:
                    default_score = int(value)
                elif option.lower() in {'ratings', 'rating'}:
                    default_ratings = value.replace(',', ' ').lower().strip().split()

        # Get values from the "Blacklist" section. Tags are aliased to their acknowledged names.
        elif section.lower() == 'blacklist':
            blacklist = [remote.get_tag_alias(tag.lower(), session) for tag in
                         config.get(section, 'tags').replace(',', ' ').lower().strip().split()]

        # If the section name is not one of the above, it is assumed to be the values for a search.
        else:

            # Initialize the list of tags that will be searched.
            section_tags = []

            # Default options are set in case the user did not declare any for the specific section.
            section_date = default_date
            section_score = default_score
            section_ratings = default_ratings

            # Go through each option within the section to find search related values.
            for option, value in config.items(section):

                # Get the tags that will be searched for. Tags are aliased to their acknowledged names.
                if option.lower() in {'tags', 'tag'}:
                    section_tags = [remote.get_tag_alias(tag.lower(), session) for tag in
                                    value.replace(',', ' ').lower().strip().split()]

                # Overwrite default options if the user has a specific value for the section
                elif option.lower() in {'days_to_check', 'days'}:
                    section_date = local.get_date(int(value))
                elif option.lower() in {'min_score', 'score'}:
                    section_score = int(value)
                elif option.lower() in {'ratings', 'rating'}:
                    section_ratings = value.replace(',', ' ').lower().strip().split()

            # Append the final values that will be used for the specific section to the list of searches.
            # Note section_tags is a list within a list.
            searches.append([section, section_tags, section_ratings, section_score, section_date])

    for search in searches:
        print('')

        # Re-assign each element of the search list to an easier to remember name. There is probably a better way.
        directory = '.'  # I want everything in a single folder
        tags = search[1]
        ratings = search[2]
        min_score = search[3]
        earliest_date = search[4]

        # Create the list that holds the title of each column in the search result table.
        # Keeping the titles in a list allows the use of list comprehension and the sum function.
        col_titles = ['downloaded', 'duplicate', 'rating conflict', 'blacklisted', 'missing tag']

        # Calculates the length of a row in the search results table including spacers so that text can be centered.
        row_len = sum(len(x) for x in col_titles) + ((len(col_titles) * 3) - 1)

        # Prints the title of the search, the titles of the results columns, and the table around it.
        print('┌' + '─' * row_len + '┐')
        print('│{:^{width}}│'.format(tags[0], width=row_len))
        print('├─' + '─' * len(col_titles[0]) + '─┬─' + '─' * len(col_titles[1]) + '─┬─' + '─' * len(
            col_titles[2]) + '─┬─' + '─' * len(col_titles[3]) + '─┬─' + '─' * len(col_titles[4]) + '─┤')
        print('│ ' + ' │ '.join(col_titles) + ' │')
        print('├─' + '─' * len(col_titles[0]) + '─┼─' + '─' * len(col_titles[1]) + '─┼─' + '─' * len(
            col_titles[2]) + '─┼─' + '─' * len(col_titles[3]) + '─┼─' + '─' * len(col_titles[4]) + '─┤')

        # Initializes the results of each post in the search.
        in_storage = 0
        bad_rating = 0
        blacklisted = 0
        bad_tag = 0
        downloaded = 0

        # Creates the string to be sent to the API.
        # Currently only 4 items can be sent directly so the rest are discarded to be filtered out later.
        if len(tags) > 4:
            search_string = ' '.join(tags[:4])
        else:
            search_string = ' '.join(tags)

        # Initializes last_id (the last post found in a search) to an enormous number so that the newest post will be found.
        # This number is hard-coded because on 64-bit archs, sys.maxsize() will return a number too big for e621 to use.
        last_id = 0x7FFFFFFF

        # Sets up a loop that will continue indefinitely until the last post of a search has been found.
        while True:
            if search_string == "dnp_flagged":
                results = remote.get_dnp_flagged_posts(last_id, session)
            else:
                results = remote.get_posts(search_string, min_score, earliest_date, last_id, session)

            # Gets the id of the last post found in the search so that the search can continue.
            # If the number of results is less than the max, the next searches will always return 0 results.
            # Because of this, the last id is set to 0 which is the base case for exiting the while loop.
            if len(results) < constants.MAX_RESULTS:
                last_id = 0
            else:
                last_id = results[-1]['id']

            # This dummy result makes sure that the for loop is always executed even for 0 real results.
            # This is so the table will print 0.
            dummy_id = 'There is no way this dummy will ever break as a long string. Probably.'
            results['posts'].append({'id': dummy_id, 'file': {'md5': dummy_id, 'ext': dummy_id}})

            for post in results['posts']:
                isotime = time.strftime("%Y%m%d_%H%M%S_", time.localtime())
                if post['id'] is not dummy_id:
                    post_tags = [item for sublist in post['tags'].values() for item in sublist]
                if include_md5:
                    path = local.make_path(directory, isotime + str(post['file']['md5']), post['file']['ext'])
                else:
                    path = local.make_path(directory, isotime + str(post['id']), post['file']['ext'])

                if post['id'] == dummy_id:
                    pass
                elif str(post['id']) in open('database.txt', 'r').read():
                    in_storage += 1
                elif post['rating'] not in ratings:
                    bad_rating += 1

                # Using fnmatch allows for wildcards to be properly filtered.
                elif [x for x in post_tags if any(fnmatch(x, y) for y in blacklist)]:
                    blacklisted += 1
                elif not set(tags[4:]).issubset(post_tags):
                    bad_tag += 1
                else:
                    # so apparently the new e621 can just decide to return a null file URL for no reason. Fun!
                    # attempt to guess the proper URL and hope that it works
                    if post['file']['url'] == None:
                        post['file']['url'] = f"https://static1.e621.net/data/{post['file']['md5'][:2]}/{post['file']['md5'][2:4]}/{post['file']['md5']}.{post['file']['ext']}"
                    downloaded += 1
                    if search_string != "dnp_flagged":
                        open('database.txt', 'a').write(str(post['id']) + '\n')
                    remote.download_post(local.make_url(post['file']['md5'], post['file']['ext']), path, session)

                    # FFmpeg transcode webm to mp4
                    # if str(path[-4:]) == "webm":
                    #     ffmpeg = subprocess.Popen(["/usr/local/bin/ffmpeg", "-i", path, "-tune", "animation", "-preset", "fast", path[:-4] + 'mp4'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    #     ffmpeg.wait()
                    #     (stdout, stderr) = ffmpeg.communicate()

                    # oldpath = path
                    # path = path[:-4] + 'mp4'

                    # if ffmpeg.returncode != 0:
                    #     print(stderr)
                    #     path = oldpath
                    # else:
                    #     os.remove(oldpath)

                # Prints the numerical values of the search results.
                print('│ {:^{width0}} │ {:^{width1}} │ {:^{width2}} │ {:^{width3}} │ {:^{width4}} │'.format(
                    str(downloaded), str(in_storage), str(bad_rating), str(blacklisted), str(bad_tag),
                    width0=len(col_titles[0]), width1=len(col_titles[1]), width2=len(col_titles[2]),
                    width3=len(col_titles[3]), width4=len(col_titles[4])
                ), end='\r', flush=True)

            # Print bottom of table. Break while loop. End program.
            if last_id == 0:
                print('')
                print('└─' + '─' * len(col_titles[0]) + '─┴─' + '─' * len(col_titles[1]) + '─┴─' + '─' * len(
                    col_titles[2]) + '─┴─' + '─' * len(col_titles[3]) + '─┴─' + '─' * len(col_titles[4]) + '─┘')

                break

# OneDrive integration
# onedrive = subprocess.Popen(["/usr/bin/rclone", "move", "/home/manual/e621dl/downloads", "onedrive:downloads"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# onedrive.wait()
# (stdout, stderr) = onedrive.communicate()

# Local FS integration
# source_dir = '/Users/ixion/Projects/e621dl/downloads'
# target_dir = '/Users/ixion/Yiff/downloads'

# file_names = os.listdir(source_dir)

# for file_name in file_names:
#     if file_name.startswith("."):
#         continue
#     shutil.move(os.path.join(source_dir, file_name), target_dir)

print('')
print('All searches complete.')
raise SystemExit
