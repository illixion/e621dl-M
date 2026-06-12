# -*- coding: utf-8 -*-

VERSION = '4.4.2'
VERSION_NOTE = 'Forked from 2.4.6'

LOGGER_FORMAT = '%(name)-11s %(levelname)-8s %(message)s'
DATE_FORMAT = '%Y-%m-%d'

USER_AGENT = 'e621dl-M/' + VERSION + ' (+Manual on e621)'
MAX_RESULTS = 320
PARTIAL_DOWNLOAD_EXT = 'request'

DEFAULT_CONFIG_TEXT = ''';;;;;;;;;;;;;;
;; GENERAL  ;;
;;;;;;;;;;;;;;

[Other]
include_md5 = false

[Defaults]
days = 1
ratings = s
min_score = 0

[Blacklist]
tags =

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
; tags = cat, cute'''
