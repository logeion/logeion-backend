#!/usr/bin/env python
from __future__ import with_statement
import sqlite3
import sys

def main():
    prog = sys.argv[0].split('/')[-1]
    lexica = sys.argv[1:]
    usage = 'Usage: %s LEXICON ...' % prog

    if not lexica:
        print >> sys.stderr, usage
        sys.exit(1)
    add_postfix = len(lexica) > 1

    try:
        for l in lexica:
            open(l).close()
    except IOError, e:
        print >> sys.stderr, '%s: %s' % (prog, str(e))
        sys.exit(1)

    for l in lexica:
        conn = sqlite3.connect(l)
        cursor = conn.cursor()
        rows = cursor.execute('select * from shortdefs')
        fname = 'shortdefs.'+l.split('/')[-1]+'.dat' if add_postfix else 'shortdefs.dat'
        try:
            with open(fname, 'w') as outfh:
                for r in rows:
                    print >> outfh, '\t'.join(r)
        except IOError, e:
            print >> sys.stderr, '%s: %s' % (prog, str(e))
            sys.exit(1)
            


if __name__ == '__main__':
    main()
