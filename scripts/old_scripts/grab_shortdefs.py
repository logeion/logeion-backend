#!/usr/bin/env python
# Copy over shortdefs from lexicon, but replacing entries with those from
# lemmastoknow.sqlite if they exist; results are printed to stdout
# NB: Should be run in /Users/Shared/Logeion_parsers on grade, or wherever
# the lemmastoknow.sqlite db is located. Also, since (at the time of writing)
# lemmastoknow only holds Greek shortdefs, make sure this isn't used for Latin

from __future__ import with_statement
import sys, sqlite3
prog = sys.argv[0]
usage = 'Usage: %s lexicon [lemmastoknow db]' % prog
outfile = 'shortdefs.dat'

if len(sys.argv[1:]) not in (1,2):
    print >> sys.stderr, '%s: error: wrong number of arguments' % prog
    print >> sys.stderr, usage
    sys.exit(1)

lexicon = sys.argv[1]
try:
    open(lexicon).close()
except IOError, e:
    print >> sys.stderr, '%s: %s' % (prog, str(e))
    sys.exit(1)

lemmastoknow = sys.argv[2] if len(sys.argv[1:]) == 2 else 'lemmastoknow.sqlite'
try:
    open(lemmastoknow).close()
except IOError, e:
    print >> sys.stderr, '%s: %s' \ % (prog, str(e))
    sys.exit(1)

try:
    open(outfile, 'a').close()
except IOError, e:
    print >> sys.stderr, '%s: %s' % (prog, str(e))
    sys.exit(1)

lex_conn = sqlite3.connect(lexicon)
lem_conn = sqlite3.connect(lemmastoknow)
lex_conn.text_factory = str
lem_conn.text_factory = str
lex_cursor, lem_cursor = lex_conn.cursor(), lem_conn.cursor()
lem_cursor.execute('select * from shortdefs')
lex_cursor.execute('select * from shortdefs')
lem_entries = lem_cursor.fetchall()
lex_entries = lex_cursor.fetchall()
lem_heads = [e[0] for e in lem_entries]
lex_heads = [e[0] for e in lex_entries]
lem_entries = dict(lem_entries)
lex_entries = dict(lex_entries)

with open(outfile, 'w') as outfh:
    for e in lex_heads:
        if e in lem_heads:
            pair = (e, lem_entries[e])
        else:
            pair = (e, lex_entries[e])
        print >> outfh, '\t'.join(pair)
