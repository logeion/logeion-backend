#!/usr/bin/env python
# Creates and exports a frequency table for Logeion. Data is based on 
from __future__ import with_statement
import re, sqlite3, sys

def is_valid_file(f):
    try:
        open(f).close()
    except IOError, e:
        print >> sys.stderr, '%s: warning: %s' % (prog, str(e))
        return False
    return True

def validate_args(args):
    if len(args) < 2:
        print >> sys.stderr, usage
        sys.exit(1)
    info_db, freq_files = args[0], args[1:]
    try:
        open(info_db).close()
        open(info_db, 'a').close()
    except IOError, e:
        print >> sys.stderr, '%s: error: cannot open db (%s)' % (prog, str(e))
        sys.exit(1)
    freq_files = filter(is_valid_file, freq_files)
    return info_db, freq_files

def validate_db_and_connect(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    try:
        cursor.execute('select * from sqlite_master')
    except sqlite3.DatabaseError, e:
        print >> sys.stderr, '%s: error reading from %s: %s' % (prog, db, e.message)
        sys.exit(1)
    return conn, cursor

split_patt = re.compile('^(.+)[\s]+([\d]+)[\s]+([\d]+)$')

def main():
    global prog, usage
    prog = sys.argv[0].split('/')[-1]
    usage = 'Usage: %s <info_db> <lemmafreq> ...' % prog
    usage += '\ninfo_db:      database containing extra Logeion info (e.g. greekInfo.db); r/w'
    usage += '\nlemmafreq:    lemmafreq file(s) containing frequency data; read-only'
    info_db, freq_files = validate_args(sys.argv[1:])
    if not freq_files:
        print >> sys.stderr, '%s: error: must provide at least one valid file' % prog
        print >> sys.stderr, usage
        sys.exit(1)
    conn, cursor = validate_db_and_connect(info_db)
    word_freq_map = dict()
    for f in freq_files:
        with open(f) as infh:
            lines = infh.readlines()
            for l in lines:
                if re.search('^[^a-zA-Z]+', l):
                    try:
                        lemma_str, freq, real = split_patt.search(l).groups()
                    except AttributeError, e:
                        print l
                        sys.exit(1)
                    lemma = lemma_str.decode('utf-8').strip()
                    word_freq_map[lemma] = word_freq_map.setdefault(lemma, 0) + int(freq)

    sorted_count = sorted(list(set(word_freq_map.values())), reverse=True)
    count2rank = dict(zip(sorted_count, [i+1 for i in range(len(sorted_count))]))
    total_count_base = sum(sorted_count) / 10000.0
    cursor.execute('delete from frequencies')
    for word,count in word_freq_map.items():
        cursor.execute('insert into frequencies values (?,?,?,?)',
            (word, count2rank[count], count, count / total_count_base))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
