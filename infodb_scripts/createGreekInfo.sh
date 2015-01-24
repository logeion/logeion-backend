#!/bin/bash
# Just runs all four scripts using standard options; passing in
# vars on the command line would be a bit unruly, so just modify
# the options here; the only one you should pass in is the info db. 
#       - MS

prog=$(basename "$0")
if [ $# -ne 1 ]
then
    test $# -gt 1 && echo "$prog: error: need exactly 1 argument" >&2
    echo "Usage: $prog [infodb]" >&2
    exit $(test $# -eq 0)   # = 0 if no args, 1 if too many args

    # FUN FACT: If you don't care about precise exit codes, then you can
    # just do `exit $#`. Amaze your friends! Confound your enemies!
    # Debase the art of programming!

fi
# Either the target infodb file exists and is writeable,
# or it doesn't exist but we can write to the directory
if [ -f "$1" -a ! -w "$1" ] || [ ! -f "$1" -a ! -w "$(dirname '$1')" ]
then
    echo "$prog: error: cannot write to file $1" >&2
    exit 1
fi

function print_header {
    echo "##############################################"
    echo "Starting $0"
    echo "##############################################"
}

print_header createGreekAuthorFreqs && \
    ./createGreekAuthorFreqs.py --infodb "$1"
test $? -eq 0 && print_header createGreekFrequencies && \
    ./createGreekFrequencies.py "$1"
test $? -eq 0 && print_header createGreekCollocations && \
    ./createGreekCollocations.py --infodb "$1"
test $? -eq 0 && print_header createGreekSamples && \
    ./createGreekSamples.py --infodb "$1"
