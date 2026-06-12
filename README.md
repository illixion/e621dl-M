# e621dl

A small automated downloader for [e621](https://e621.net). It runs the searches
defined in `config.ini` and saves every matching post into a destination
folder such as the macOS Drop Box (`~/Public/Drop Box`). Uses the v2 post
API (`v2=true`).

## Usage

```sh
pip install -r requirements.txt
python3 e621dl.py
```

On first run a default `config.ini` is created next to the script.

## Configuration (`config.ini`)

```ini
[Settings]
download_directory = ~/Public/Drop Box

[Defaults]
days = 1            ; how far back to search
ratings = s, q, e   ; allowed ratings
min_score = -100

[Blacklist]
tags = tag1, tag2   ; posts with these tags are skipped (wildcards allowed)

[my search]         ; every other section is a search group
tags = fav:SomeUser
```

Each search group may override `days`, `ratings`, and `min_score`.

## Re-download behavior

Every downloaded post ID is appended to `database.txt`. Files you delete from
the download folder are **not** downloaded again — remove the corresponding ID
from `database.txt` if you ever want a post re-fetched.
