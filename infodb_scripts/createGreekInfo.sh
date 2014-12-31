#!/bin/bash
# Just run all four scripts using standard options; passing in
# vars on the command line would be a bit unruly, so just modify
# the options here; the only one you should pass in is the info db. 
#       - MS

./createGreekAuthorFreqs.py --infodb "$1"
./createGreekFrequencies.py "$1"
./createGreekCollocations.py --infodb "$1"
./createGreekSamples.py --infodb "$1"
