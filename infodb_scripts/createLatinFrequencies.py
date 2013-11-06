#!/usr/bin/env python

import sqlite3
import urllib2
import sys
import re
from BeautifulSoup import BeautifulStoneSoup

def main():
    prog = sys.argv[0].split('/')[-1]
    usage = prog + ' [LATININFODB]'
    dbname = 'latinInfo.db'
    if len(sys.argv[1:]) > 1:
        print >> sys.stderr, '%s: error: need at most one argument' % prog
        print >> sys.stderr, usage
        sys.exit(1)
    elif len(sys.argv[1:]) == 1:
        dbname = sys.argv[1]
    else:
        yn = ''
        while yn not in ('y', 'n', 'yes', 'no'):
            yn = raw_input("Use default dbname (%s)? (y/n) " % dbname).lower()
        if yn in ('n','no'):
            print >> sys.stderr, usage
            sys.exit(0)

    try:
        open(dbname).close()
    except IOError, e:
        print >> sys.stderr, '%s: %s' % (prog, str(e))
        sys.exit(1)

    f = urllib2.urlopen("http://perseus.uchicago.edu/cgi-bin/LatinFrequency.pl?author=&title=&genre=&editor=&language=NOT+English&displaymorethan=49&displaylessthan=1000000000&sortby=decreasingFreq&searchby=searchbylemma")
    soup = BeautifulStoneSoup(f.read())
    f.close()

    tds = soup.findAll("td")
    ltds = len(tds) / 3
    print "# of lemmas (with a count of at least 50) = " + str(ltds)

    db = sqlite3.connect(dbname)
    curs = db.cursor()

    curs.executescript("""
    drop table if exists frequencies;
    create table frequencies (lemma text, rank integer, count integer, rate real, lookupform text);
    create index if not exists f_l on frequencies(lookupform);""")

    i = 0
    rank = 0
    prevCount = 0
    extrasAtThisRank = 0

    while i < ltds:
        j = i*3
        word = tds[j].contents[0].string
        count = int(tds[j+1].string)
        rate = tds[j+2].string
        lookupform = re.sub('[\d\[\]]', '', word)
        if rank == 0 or count < prevCount:
            rank += 1 + extrasAtThisRank
            extrasAtThisRank = 0
        elif count == prevCount:
            extrasAtThisRank += 1

        curs.execute("insert into frequencies values (?,?,?,?,?)", (word, rank, count, rate, lookupform))
        prevCount = count
        i += 1
    db.commit()
    db.close()

if __name__ == '__main__':
    main()
