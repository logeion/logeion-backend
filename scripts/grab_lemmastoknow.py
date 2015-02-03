#!/usr/bin/env python
# Grab dictionaries and textbooks from lemmastoknow.sqlite db for logeion_parse.py; output
# in tab-separated file named <outdir>/<lowercase_tablename>.dat

import sqlite3
import sys
import os.path

def validate_range(i, args):
    global usage
    if i >= len(args)-1:
        print >> sys.stderr, "%s: error: need argument for flag %s" % (prog, args[i])
        print >> sys.stderr, usage
        sys.exit(-1)

def main():
    global usage
    dbname = 'lemmastoknow.sqlite'
    outdir = '.'
    tables = ['HQ', 'JACT', 'LTRG', 'Mastro', 'shortdefs']
    prog = sys.argv[0].split('/')[-1]
    usage = 'Usage: %s [--lemmastoknow <lemmastoknow>] [--outdir <output-dir>] <dico> ...' % prog
    usage += '\ndico: [' + ' | '.join(tables) + ' | all]'
    args = sys.argv[1:]
    dicos_to_pull = []
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == '--lemmastoknow':
            validate_range(i, args)
            dbname = args[i+1]
            i += 1 # skip next argument
        elif arg == '--outdir':
            validate_range(i, args)
            outdir = args[i+1]
            i += 1 # skip next argument
        else:
            dicos_to_pull.append(arg)
        i += 1
    if dicos_to_pull and dicos_to_pull[0] == 'all':
        dicos_to_pull = tables
    elif not dicos_to_pull or any(d not in tables for d in dicos_to_pull):
        print >> sys.stderr, usage
        sys.exit(-1)
    if not os.path.isdir(outdir):
        print >> sys.stderr, '%s: error: directory "%s" does not exist or is not a directory' % (prog, outdir)
        sys.exit(-1)
    conn = sqlite3.connect(dbname)
    conn.text_factory = str
    conn.row_factory = lambda _,r: '\t'.join(map(str, r))
    cursor = conn.cursor()
    for table in dicos_to_pull:
        target_file = '%s/%s.dat' % (outdir, table.lower())
        print 'Printing %s -> %s' % (table, target_file)
        cursor.execute('select * from '+table) # Assuming no injection from ourselves
        try:
            outfh = open(target_file, 'w')
            print >> outfh, '\n'.join(cursor.fetchall())
        except IOError, e:
            print >> sys.stderr, '%s: warning: could not open "%s" for write: %s' \
                % (prog, table2dico[table], str(e))

    conn.close()

if __name__ == '__main__':
    main()
