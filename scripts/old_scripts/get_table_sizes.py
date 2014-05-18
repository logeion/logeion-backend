#!/usr/bin/env python
from __future__ import with_statement
import sys
import sqlite3



def main():
    prog = sys.argv[0].split('/')[-1]
    usage =  'Usage: %s [-c column=value] [-t table1,table2,...] db ...\n' % prog
    usage += '    -c column=value       Only show counts for where column=value\n'
    usage += '    -t table1,table2,...  Only print data from listed tables'

    dicos = sys.argv[1:]
    constraints = ''
    table_list = []
    if '-c' in dicos:
        ind = dicos.index('-c')
        constraints = dicos[ind+1]
        dicos = dicos[:ind] + dicos[ind+2:]
    if '-t' in dicos:
        ind = dicos.index('-t')
        table_list = dicos[ind+1].split(',')
        dicos = dicos[:ind] + dicos[ind+2:]
    if not dicos:
        print >> sys.stderr, usage
        sys.exit(1)
    for d in dicos:
        try:
            open(d).close()
        except IOError, e:
            print >> sys.stderr, '%s: %s' % (prog, str(e))
            sys.exit(1)
    print_names = len(dicos) > 1
    for d in dicos:
        if print_names:
            print d + ':'
        conn = sqlite3.connect(d) 
        cursor = conn.cursor()
        for t in cursor.execute('select name from sqlite_master where type="table"').fetchall():
            table_name = t[0]
            if table_list and table_name not in table_list:
                continue
            print table_name+':',
            if constraints:
                print
                if '=' in constraints:
                    print '\twhere ' + constraints + ':',
                    sys.stdout.flush()
                    print len(cursor.execute('select rowid from '+table_name+' where '+constraints).fetchall())
                else:
                    relevant_vals = [r[0] for r in
                        cursor.execute('select distinct ' + constraints + ' from ' + table_name)]
                    for v in relevant_vals:
                        print '\t'+v+':',
                        sys.stdout.flush()
                        print len(cursor.execute('select rowid from '+table_name+' where '+constraints+'="'+v+'"').fetchall())
            else:
                sys.stdout.flush()
                print len(cursor.execute('select rowid from '+table_name).fetchall())
        if print_names:
            print

if __name__ == '__main__':
    main()
