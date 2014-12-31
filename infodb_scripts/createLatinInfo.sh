#!/bin/bash
# Just run all four scripts using standard options; passing in
# vars on the command line would be a bit unruly, so just modify
# the options here; the only one you should pass in is the info db. 
#       - MS

./createLatinAuthorFreqs.py --infodb "$1"
./createLatinFrequencies.py "$1"
./createLatinCollocations.py --infodb "$1"
./createLatinSamples.py --infodb "$1"
