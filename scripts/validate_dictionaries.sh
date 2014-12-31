#!/bin/bash
# Short script to recursively run xmllint on the children of the given
# directories. Used to verify the correctness of XML files post-edit.

validate_r () {
    d="$1"
    for f in $(ls $d); do
        d="$1"
        path="$d/$f"
        echo "Validating $path"
        if [ -d "$path" ]; then
            validate_r "$path"
        else
            xmllint --noout "$path"
        fi
    done
    return
}

if [ "$#" == "0" ]; then
    echo "Usage: $0 dir1 dir2 ..."
    exit 1
fi
while (( "$#" )); do
    validate_r "$1"
    shift
done
