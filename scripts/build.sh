#!/bin/bash
# Simple script to run the full gamut of Logeion prep:
#   1) Update shortdefs in lemmastoknow
#   2) Extract lemmastoknow data and store in $LOGEION_ROOT/dictionaries
#   3) Run `logeion_parse.py` + any arguments
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

print_header () {
    echo "######################################"
    echo "$1"
    echo "######################################"
}

log_and_move () {
    echo "Moving $1 -> $2"
    mv "$1" "$2"
}

usage () {
    cat << EOF
Usage: $prog [-s|--scriptdir <dir>] [-c|--config <file>] [-d|--dump]
    -s|--scriptdir <dir>    Directory containing Logeion utility scripts. Defaults to
                            the parent of $prog $(dirname $0)
    -c|--config <file>      Config file containing options for Logeion build; check the
                            README for required entries. Defaults to the build.config
                            in <scriptdir>.
    -d|--dump               Dump the value of all config variables and exit
EOF
exit 0
}

prog=$(basename "$0")
scriptdir=$(dirname "$0")
config="$scriptdir/build.config"
dump=false
while [ "$#" -gt 0 ]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -s|--scriptdir)
            if [ "$#" -gt 1 ]; then
                scriptdir=$2
                shift 2
                continue
            else
                echo "$prog: error: must have argument following scriptdir option" >&2
                exit -1
            fi
            ;;
        -c|--config)
            if [ "$#" -gt 1 ]; then
                config=$2
                shift 2
                continue
            else
                echo "$prog: error: must have argument following config option" >&2
                exit -1
            fi
            ;;
        -d|--dump)
            dump=true
            ;;
        -?*)
            echo "$prog: warning: ignoring unknown option: $1" >&2
            ;;
        *)
            break
    esac

    shift
done

# If we're just dumping out the config values, we don't necessary need
# to check if scriptdir already exist; however, we DO need to check if
# the config file exists either way.
if [ ! -d "$scriptdir" -a $dump != true ]; then
    echo "$prog: error: can't find script dir $scriptdir" >&2
    exit -1
elif [ ! -f "$config" ]; then
    echo "$prog: error: can't find config file $config" >&2
    exit -1
fi

logeion_args=--all
. "$config"
for prop in greek_lexicon latin_lexicon dico_root logeion_root; do
    if [ -z "$prop" ]; then
        echo "$prog: error: required property $prop not defined" >&2
        exit -1
    fi
done

# Don't have a more elegant way to do this at the moment, since reflection
# doesn't seem to be bash's strong suit.
if [ $dump = true ]; then
    echo "scriptdir: $scriptdir"
    echo "config: $config"
    echo "lemmastoknow: $lemmastoknow"
    echo "greek_lexicon: $greek_lexicon"
    echo "latin_lexicon: $latin_lexicon"
    echo "dico_root: $dico_root"
    echo "logeion_root: $logeion_root"
    echo "logeion_args: $logeion_args"
    exit 0
fi
    

if [ -n "$lemmastoknow" ]; then
    print_header "1) Updating shortdefs"
    "$scriptdir/update_shortdefs.py" "$lemmastoknow" "$greek_lexicon"

    print_header "2) Grabbing contents of lemmastoknow"
    logeion_staging=/tmp/logeion_staging
    if [ -d "$logeion_staging" ]; then
        rm -r "$logeion_staging"
    fi
    mkdir "$logeion_staging"
    "$scriptdir/grab_lemmastoknow.py" --lemmastoknow "$lemmastoknow" \
        --outdir "$logeion_staging" all
    log_and_move "$logeion_staging/mastro.dat" "$dico_root/Mastronarde"
    log_and_move "$logeion_staging/hq.dat" "$dico_root/HansenQuinn"
    log_and_move "$logeion_staging/jact.dat" "$dico_root/JACT"
    log_and_move "$logeion_staging/ltrg.dat" "$dico_root/LTRG"
    log_and_move "$logeion_staging/shortdefs.dat" "$dico_root/GreekShortDefs"
    rm -r "$logeion_staging"
else
    print_header "No lemmastoknow defined; skipping first two steps..."
fi

print_header "3) Running logeion_parse.py $logeion_args"
echo "Changing directory -> $logeion_root"
cd "$logeion_root"
"$logeion_root/logeion_parse.py" $logeion_args
echo "Returning to calling directory"
cd -
