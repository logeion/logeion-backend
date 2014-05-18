#!/usr/bin/env python
# Takes newfreq table from lemmastoknow.sqlite (or equivalent) and updates
# Logeion info db with them; lemmastoknow db must have table "newfreq" and
# info db must have table "frequencies", both of which are formatted the
# same (i.e. same number of columns and same order of columns, but not necessarily
# the same exact names)
import sys, sqlite3

def validate_args(argv):
    if len(argv) != 2:
        print >> sys.stderr, '%s: error: wrong number of args' % prog
        print >> sys.stderr, usage
        sys.exit(1)
    lemmastoknowdb, infodb = argv[:2]
    try:
        open(lemmastoknowdb).close()
        open(infodb).close()
        open(infodb, 'a').close()
    except IOError, e:
        print >> sys.stderr, '%s: %s' % (prog, str(e))
        sys.exit(1)
    return lemmastoknowdb, infodb

def validate_db_and_connect(dbname, table):
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    try:
        cursor.execute('select * from ' + table)
    except sqlite3.DatabaseError, e:
        print >> sys.stderr, '%s: error: %s (%s)' % (prog, str(e), dbname)
        sys.exit(1)
    return conn, cursor

def main():
    global prog, usage
    prog = sys.argv[0].split('/')[-1]
    usage = 'Usage: %s LEMMASTOKNOWDB INFODB' % prog
    lemmastoknowdb, infodb = validate_args(sys.argv[1:])
    ltk_conn, ltk_cursor = validate_db_and_connect(lemmastoknowdb, 'newfreq')
    freq_entries = ltk_cursor.execute('select * from newfreq').fetchall()
    ltk_conn.close()

    info_conn, info_cursor = validate_db_and_connect(infodb, 'frequencies')
    for e in freq_entries: # not using UPDATE makes it a little more portable
        info_cursor.execute('delete from frequencies where lemma=?', e[0])
        info_cursor.execute('insert into frequencies values (?,?,?,?)', e)
    info_conn.commit()
    info_conn.close()

if __name__ == '__main__':
    main()
