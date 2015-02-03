#!/bin/bash
# Simple script to run the full gamut of Logeion prep:
#   1) Update shortdefs in lemmastoknow
#   2) Extract lemmastoknow data and store in $LOGEION_ROOT/dictionaries
#   3) Run `logeion_parse.py --all`
#
# If appropriate arguments are provided, then the script will also
# do the following:
#   4) Copy GreekLexiconNov2011, LatinLexiconDiderot, and new_dvlg-wheel
#      to the provided endpoint
#   5) Backup current copies on endpoint and replace them with newly-copied
#      versions.
#
# The locations of various files/directories are taken from build.config,
# which should be located in the same directory as this script.

function print_header () {
    echo "######################################"
    echo "$1"
    echo "######################################"
}

prog=$(basename "$0")
scripts_dir=$(dirname "$0")
. "$scripts_dir/build.config"
if [ "x$lemmastoknow" == "x" ]; then
    echo "$prog: error: lemmastoknow not defined" >&2
    exit -1
elif [ "x$greek_lexicon" == "x" ]; then
    echo "$prog: error: greek_lexicon not defined" >&2
    exit -1
elif [ "x$latin_lexicon" == "x" ]; then
    echo "$prog: error: latin_lexicon not defined" >&2
    exit -1
fi

logeion_staging=/tmp/logeion_staging
print_header "1) Updating shortdefs"
"$scripts_dir/update_shortdefs.py" "$lemmastoknow" "$greek_lexicon"

print_header "2) Grabbing contents of lemmastoknow"
if [ -d "$logeion_staging" ]; then
    rm -r "$logeion_staging"
fi
mkdir "$logeion_staging"
"$scripts_dir/grab_lemmastoknow.py" --lemmastoknow "$lemmastoknow" \
    --outdir "$logeion_staging" all
mv "$logeion_staging/mastro.dat" "$dico_root/Mastronarde"
mv "$logeion_staging/hq.dat" "$dico_root/HansenQuinn"
mv "$logeion_staging/jact.dat" "$dico_root/JACT"
mv "$logeion_staging/ltrg.dat" "$dico_root/LTRG"
mv "$logeion_staging/shortdefs.dat" "$dico_root/GreekShortDefs"
rm -r "$logeion_staging"

print_header "3) Running logeion_parse.py $logeion_args"
cd "$logeion_root"
"$logeion_root/logeion_parse.py" $logeion_args
cd -
