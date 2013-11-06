#!/usr/bin/env python
import sqlite3, sys

def validate_args(argv):
    if len(argv) != 2:
        print >> sys.stderr, usage
        sys.exit(1)
    lemmastoknow, lexicon = argv[:2]
    try:
        open(lemmastoknow).close()
        open(lemmastoknow, 'a').close()
        open(lexicon).close()
    except IOError, e:
        print >> sys.stderr, '%s: %s' % (prog, str(e))
        sys.exit(1)
    return lemmastoknow, lexicon

def validate_db_and_connect(dbname):
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    try:
        cursor.execute('select * from sqlite_master limit 1')
    except sqlite3.DatabaseError, e:
        print >> sys.stderr, '%s: %s' % (prog, str(e))
        sys.exit(1)
    except sqlite3.ProgrammingError, e:
        print >> sys.stderr, '%s: error: not a SQLite database (%s)' % (prog, str(e))
        sys.exit(1)
    except Exception, e:
        print >> sys.stderr, '%s: error: unexpected exception (%s)' % (prog, str(e))
        sys.exit(1)
    return conn, cursor

def insert_new_value(e, cursor):
    for table in ('HQ','Mastro','JACT'):
        results = cursor.execute('select '+table+'info from frequency where lookupentry=?', (e[0],)).fetchone()
        #results = cursor.execute('select info from ' + table + ' where lemma=?', (e[0],)).fetchone()
        if results and results[0]:
            #print 'Choosing ' + e[0] + ' from ' + table
            cursor.execute('update shortdefs set defs=? where lemma=?', (results[0],e[0]))
            return
    return # If none found, defaults to Perseusshortdefs entry

def main():
    global prog, usage
    prog = sys.argv[0].split('/')[-1]
    usage = 'Usage: %s <lemmastoknow> <lexicon>' % prog
    usage += '\nlemmastoknow: db containing modified textbook/shortdefs info; r/w'
    usage += '\nlexicon:      standard Perseus lexicon file (e.g. GreekLexicon.db); read-only'
    lemmastoknow, lexicon = validate_args(sys.argv[1:])
    lex_conn, lex_cursor = validate_db_and_connect(lexicon)
    lex_shortdefs = lex_cursor.execute('select * from shortdefs').fetchall()
    lex_conn.close()
    lem_conn, lem_cursor = validate_db_and_connect(lemmastoknow)
    # For some reason, SQLite isn't allowing "insert ... values (select * ...);" syntax
    lem_cursor.execute('delete from Perseusshortdefs')
    for e in lex_shortdefs:
        lem_cursor.execute('insert or replace into Perseusshortdefs values (?,?)', e)
    lem_cursor.execute('delete from shortdefs')
    lem_cursor.execute('insert into shortdefs select * from Perseusshortdefs')
    for e in lex_shortdefs:
        insert_new_value(e, lem_cursor)
    lem_conn.commit()
    lem_conn.close()

if __name__ == '__main__':
    main()
