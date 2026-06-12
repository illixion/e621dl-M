# -*- coding: utf-8 -*-

# Internal Imports
import os
from time import sleep
from timeit import default_timer

# Personal Imports
from . import constants
from . import local

def delayed_post(url, payload, session):
    # Take time before and after getting the requests response.
    start = default_timer()
    response = session.get(url, data = payload)
    elapsed = default_timer() - start

    # If the response took less than 0.5 seconds (only 2 requests are allowed per second as per the e621 API)
    # Wait for the rest of the 0.5 seconds.
    if elapsed < 0.5:
        sleep(0.5)

    return response

def get_github_release(session):
    url = 'https://api.github.com/repos/wulfre/e621dl/releases/latest'

    response = session.get(url)
    response.raise_for_status()

    return response.json()['tag_name'].strip('v')

def get_posts(search_string, min_score, earliest_date, last_id, session):
    url = 'https://e621.net/posts.json'
    payload = {
        'limit': constants.MAX_RESULTS,
        'tags': 'id:<' + str(last_id) + ' ' + 'score:>=' + str(min_score) + ' ' + 'date:>=' + str(earliest_date) + ' ' + search_string
    }

    response = delayed_post(url, payload, session)
    response.raise_for_status()

    return response.json()

# Custom function accessed by searching for "dnp_flagged"
# Assembles a custom search of DNP flagged posts
def get_dnp_flagged_posts(last_id, session):
    faux_search_results = {
        "posts": []
    }
    flags_url = "https://e621.net/post_flags.json"
    flags_response = delayed_post(flags_url, {}, session)
    flags_response.raise_for_status()

    for item in flags_response.json():
        if "paysite" in item['reason'].lower() and item['is_deletion'] is False and str(item['post_id']) not in open('database.txt', 'r').read():
            posts = get_known_post(item['post_id'], session)['posts']
            if len(posts) == 1:
                faux_search_results['posts'].append(posts[0])

            open('database.txt', 'a').write(str(item['post_id']) + '\n')

    return faux_search_results

def get_known_post(post_id, session):
    url = 'https://e621.net/posts.json'
    payload = {'tags': f"id:{post_id}"}

    response = delayed_post(url, payload, session)
    response.raise_for_status()

    return response.json()

def get_tag_alias(user_tag, session):
    prefix = ''

    if ':' in user_tag:
        return user_tag

    if user_tag[0] == '~':
        prefix = '~'
        user_tag = user_tag[1:]

    if user_tag[0] == '-':
        prefix = '-'
        user_tag = user_tag[1:]

    url = 'https://e621.net/tags.json'
    payload = {'search[name_matches]': user_tag}

    response = delayed_post(url, payload, session)
    response.raise_for_status()

    results = response.json()

    if '*' in user_tag and results:
        return user_tag

    if user_tag == 'dnp_flagged':
        return user_tag

    if 'tags' not in results:
        for tag in results:
            if user_tag == tag['name']:
                return prefix + user_tag

    url = 'https://e621.net/tag_aliases.json'
    payload = {'search[antecedent_name]': user_tag}

    response = delayed_post(url, payload, session)
    response.raise_for_status()

    results = response.json()

    # check if tag exists
    if 'tag_aliases' in results:
        local.print_log('remote', 'error', 'The tag ' + prefix + user_tag + ' is spelled incorrectly or does not exist.')
        raise SystemExit

    for tag in results:
        if user_tag == tag['consequent_name']:
            url = 'https://e621.net/tags.json'
            payload = {'id': str(tag['alias_id'])}

            response = delayed_post(url, payload, session)
            response.raise_for_status()

            results = response.json()

            local.print_log('remote', 'info', 'Tag aliased: ' + prefix + user_tag + ' -> ' + prefix + results['name'])

            return prefix + results['name']

    local.print_log('remote', 'error', 'The tag ' + prefix + user_tag + ' is spelled incorrectly or does not exist.')
    raise SystemExit

def download_post(url, path, session):
    # print(url, path, session)
    if '.' + constants.PARTIAL_DOWNLOAD_EXT not in path:
        path += '.' + constants.PARTIAL_DOWNLOAD_EXT

    try:
        open(path, 'x')
    except FileExistsError:
        pass

    header = {'Range': 'bytes=' + str(os.path.getsize(path)) + '-'}
    response = session.get(url, stream = True, headers = header)
    response.raise_for_status()

    with open(path, 'ab') as outfile:
        for chunk in response.iter_content(chunk_size = 8192):
            outfile.write(chunk)

    os.rename(path, path.replace('.' + constants.PARTIAL_DOWNLOAD_EXT, ''))

def finish_partial_downloads(session):
    for root, dirs, files in os.walk('/Users/ixion/Projects/e621dl/downloads'):
        for file in files:
            if file.endswith(constants.PARTIAL_DOWNLOAD_EXT):
                local.print_log('remote', 'info', 'Partial download found: ' + file + '.')

                #path = os.path.join(root, file)
                #url = get_known_post(file.split('.')[0], session)['file_url']

                # download_post(url, path, session)
