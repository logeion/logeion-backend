#!/usr/bin/env python
# Grab dictionaries and textbooks from lemmastoknow.sqlite db for logeion_parse.py; output
# in tab-separated file named <lowercase_tablename>.dat

import sqlite3
import sys

def main():
    dbname = 'lemmastoknow.sqlite'
    tables = ['HQ', 'JACT', 'LTRG', 'Mastro', 'shortdefs']
    prog = sys.argv[0].split('/')[-1]
    usage = 'Usage: %s <dico> ...' % prog
    usage += '\ndico: [' + ' | '.join(tables) + ' | all]'
    dicos_to_pull = sys.argv[1:]
    if dicos_to_pull and dicos_to_pull[0] == 'all':
        dicos_to_pull = tables
    elif not dicos_to_pull or any(d not in tables for d in dicos_to_pull):
        print >> sys.stderr, usage
        sys.exit(1)
    conn = sqlite3.connect(dbname)
    conn.text_factory = str
    conn.row_factory = lambda _,r: '\t'.join(map(str, r))
    cursor = conn.cursor()
    for table in dicos_to_pull:
        cursor.execute('select * from '+table) # Assuming no injection from ourselves
        try:
            outfh = open(table.lower()+'.dat', 'w')
            print >> outfh, '\n'.join(cursor.fetchall())
        except IOError, e:
            print >> sys.stderr, "%s: warning: could not open %s for write: %s" \
                % (prog, table2dico[table], str(e))

    conn.close()

if __name__ == '__main__':
    main()
