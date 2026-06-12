[![Github All Releases](https://img.shields.io/github/downloads/wulfre/e621dl/total.svg)](https://github.com/Wulfre/e621dl/releases/latest)

# What is **e621dl**?

**e621dl** is an automated script, originally by [**@wwyaiykycnf**](https://github.com/wwyaiykycnf), which downloads images from e621.net. It can be used to create a local mirror of your favorite searches, and keep these searches up to date as new posts are uploaded.

# How does **e621dl** work?

Put very simply, when **e621dl** starts, it determines the following based on the `config.ini` file:

- Which tags you would like to avoid seeing by reading the blacklist section.
- Which searches you would like to perform by reading your search group sections.

Once it knows these things, it goes through the searches one by one, and downloads _only_ content that matches your search request, and has passed through all specified filters.

# Installing and Setting Up **e621dl**

- Download [the latest executable release of **e621dl**](https://github.com/wulfre/e621dl/releases).

*or*

- Download and install [the latest release of Python 3](https://www.python.org/downloads/).
- Download [the latest *source* release of **e621dl**](https://github.com/wulfre/e621dl/releases).
    - Decompress the archive into any directory you would like.

# Running **e621dl**
## Running **e621dl** from the Windows executable.

- Double click the e621dl.exe icon to run the program. It will close immediately on completion.
    - If you would like to read the output after the execution is complete, run the program through the command prompt in the directory that you placed the .exe file.

## Running **e621dl** from source.

You must install all of this program's python dependencies for it to run properly from source. They can be installed by running the following command in your command shell: `pip install [package name]`.
*You must run your command shell with admin/sudo permissions for the installation of new packages to be successful.*

The required packages for **e621dl** are currently:
- [requests](https://python-requests.org)

Open your command shell in the directory you decompressed e621dl into, and run the command `py e621dl.py`. Depending on your system, the command `py` may default to Python 2. In this case you should run `py -3 e621dl.py`. Sometimes, your system may not recognize the `py` command at all. In this case you should run `python3 e621dl.py`. In some cases where Python 3 was the first installed version of Python, the command `python e621dl.py` will be used.
    - The most common error that occurs when running a Python 3 program in Python 2 is `SyntaxError: Missing parentheses in call to 'print'`.

## First Run

The first time you run **e621dl**, you will see the following errors:

```
e621dl      INFO     Running e621dl version X.X.X -- Forked from 2.4.6.
local       ERROR    No config file found.
local       INFO     New default config file created. Please add tag groups to this file.
```

These errors are normal behavior for a first run, and should not raise any alarm. **e621dl** is telling you that it was unable to find a `config.ini` file, so a generic one was created.

## Add search groups to the config file.

Create sections in the `config.ini` to specify which posts you would like to download. In the default config file, an example is provided for you. This example is replecated below. Each section will have its own directory inside the downloads folder.

```
;;;;;;;;;;;;;;;;;;;
;; SEARCH GROUPS ;;
;;;;;;;;;;;;;;;;;;;

; New search groups can be created by writing the following. (Do not include semicolons.):
; [Directory Name]
; days = 1
; ratings = s, q, e
; min_score = -100
; tags = tag1, tag2, tag3, ...

; Example:
; [Cute Cats]
; days = 30
; ratings = s
; min_score = 5
; tags = cat, cute
```

The following characters are not allowed in search group names: `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`, and ` ` as they can cause issues in windows file directories. If any of these characters are used, they will be replaced with the `_` character. The `/` character _is_ allowed to be used in section names, but it will be understood as a sub-directory. This may be useful to some users for organization. For example: separating `[Canine/Fox]` and `[Canine/Wolf]`, and separating `[Feline/Tiger]` and `[Feline/Lion]`

Commas should be used to separate tags and ratings, but this is not strictly enforced in current versions of **e621dl**.

One side effect of the workaround used to search an unlimited number tags is that you may only use up to 4 meta tags `:`, negative tags `-`, operational tags `~`, or wildcard tags `*` per group, and they must be the first 4 items in the group. See [the e621 cheatsheet](https://e621.net/help/show/cheatsheet) for more information on these special types of tags.

### Search Group Keys, Values, and Descriptions

Key                   | Acceptable Values               | Description
--------------------- | ------------------------------- | --------------------------------------------------------------------------------------------------------------------------
[]                    | Nearly Anything                 | The search group name which will be used to title console output and name folders. See above for restrictions.
days                  | Integer from `1` to ∞           | How many days into the past to check for new posts.
ratings               | Characters `s`, `q`, and/or `e` | Acceptable explicitness ratings for downloaded posts. Characters stand for safe, questionable, and explicit, respectively.
min_score             | Integer from -∞ to ∞            | Lowest acceptable score for downloaded posts. Posts with higher scores than this number will also be downloaded.
tags                  | Nearly Anything                 | Tags which will be used to perform the post search. See above for restrictions

## [Optional] Add blacklisted tags to the config file.

Add any tags for posts you would like to avoid downloading to the blacklist section of the `config.ini` file. Meta tags `:`, negative tags `-`, operational tags `~`, will potentially break the script, as they are currently not filtered out of the blacklist, so do not use them in this section. Wildcard tags `*` *are* supported in the blacklist, though it is easy for a misspelled wildcard to match an artist's name, for example, and the program will not give any errors.

## [Optional] Modify the defaults in the config file.

The defaults section of the `config.ini` is the primary fallback for any missing lines in a search group. This section uses the same keys as search groups.

There is also a hard-coded secondary fallback if any lines are missing in the defaults section. They are as follows:

```
days = 1
ratings = s
score = -9999999
```

## Normal Operation

Once you have added at least one group to the tags file, you should see something similar to this when you run **e621dl**:

```
e621dl      INFO     Running e621dl version X.X.X.

e621dl      INFO     Checking for partial downloads.
remote      INFO     Partial download found: id.ext.request. Finishing download.

e621dl      INFO     Parsing config.
remote      INFO     Tag aliased: bad_tag -> good_tag

┌──────────────────────────────────────────────────────────────────────┐
│                               Example                                │
├────────────┬───────────┬─────────────────┬─────────────┬─────────────┤
│ downloaded │ duplicate │ rating conflict │ blacklisted │ missing tag │
├────────────┼───────────┼─────────────────┼─────────────┼─────────────┤
│     X      │     X     │        X        │      X      │      X      │
└────────────┴───────────┴─────────────────┴─────────────┴─────────────┘
```

My intent was to make the column titles as easy to understand as possible, but here is briefly what each column represents.

- The `new` column represents the number of posts that have matched all search group criteria, and have been downloaded during the current run.
- The `duplicate` column represents the number of posts that have matched all search group criteria, but are already stored in your downloads folder from a previous run. They will not be downloaded.
- The `rating conflict` column represents the number of posts that were found during the initial search, but do not match the explicitness rating for the search group. They will not be downloaded.
- The `blacklisted` column represents the number of posts that were found during the initial search, but contain a blacklisted tag. They will not be downloaded.
- The `missing tag` column represents the number of posts that were found during the initial search, but do not contain all tags for the search group. This is due to API limitations. They will not be downloaded.

# Automation of **e621dl**

It should be recognized that **e621dl**, as a script, can be scheduled to run as often as you like, keeping the your local collections always up-to-date, however, the methods for doing this are dependent on your platform, and are outside the scope of this quick-guide.

# Feedback and Requests

If you have any ideas on how to make this script run better, or for features you would like to see in the future, [open an issue](https://github.com/Wulfre/e621dl/issues) and I will try to read it as soon as possible.
