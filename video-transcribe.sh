#!/bin/bash

: '
title           : video-transcript.sh
description     : This script transcribes videos listed in a text file and generated a zip file containing the video transcription in markdown format.
author          : Elvis Dowson <elvis.dowson@gmail.com>
date            : 202611221700
version         : 1.0
license         : MIT
usage           : video-transcript.sh <local-video-filepath-list.txt>
notes           :
'

set -e

# common variables
CURRENT_DIR=`pwd`
SCRIPT_DIR=`dirname $0`

red=$(tput setaf 1)
green=$(tput setaf 2)
yellow=$(tput setaf 3)
blue=$(tput setaf 4)
reset=$(tput sgr0)

# script variables
VIDEO_LIST=${1:-""}

# check arguments
if [[ -z $VIDEO_LIST ]]; then
  echo "${red}error:${reset} please specify the full path to a text file containing a list of videos file paths as the first argument to this script";
  exit 1
fi

# transcribe videos
python video-transcribe.py "$VIDEO_LIST" --output-dir video-transcription --force

