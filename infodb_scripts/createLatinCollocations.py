#!/usr/bin/env python

import sqlite3
import re
import operator
import sys

# Do basic config: grab lexicon location, assign infodb and lemmafile,
# and check that lexicon and lemmafile exist and are readable

infodb    = './latinInfo.db'
lemmafile = '/Volumes/data/var/lib/philologic/databases/LatinAugust2012/frequencies/lemmafile'
lexicon   = '/Library/WebServer/CGI-Executables/perseus/LatinLexicon.db'

prog = sys.argv[0].split('/')[-1]

def usage(prog):
    print 'usage: %s [options]' % prog
    print '    --infodb <info-db>'
    print '    --lemmafile <lemma-file>'
    print '    --lexicon <lexicon>'

# Get command-line arguments
args = sys.argv[1:]
argc = len(args)
i = 0
while i < argc:
    try:
        if args[i] == '--info-db':
            info_db = args[i+1]
            i += 2
        elif args[i] == '--lemmafile':
            lemmafile = args[i+1]
            i += 2
        elif args[i] == '--lexicon':
            lexicon = args[i+1]
            i += 2
        else:
            print >> sys.stderr, '%s: error: unrecognized arg %s' % (prog, args[i])
            usage(prog)
            sys.exit(1)
    except IndexError, e:
        print >> sys.stderr, '%s: error: no value following %s' % (prog, args[i])
        usage(prog)
        sys.exit(1)

print 'Using "%s" as info db' % infodb
print 'Using "%s" as lemma file' % lemmafile
print 'Using "%s" as lexicon' % lexicon

yn = ''
while yn not in ('y', 'n', 'yes', 'no'):
    yn = raw_input("Are these arguments OK? (y/n) ").lower()
if yn in ('n','no'):
    usage(prog)
    sys.exit(0)

try:
    open(lexicon).close()
    open(lemmafile).close()
except IOError, e:
    print >> sys.stderr, '%s: %s' % (prog, str(e))
    sys.exit(1)

# Read in lemmas; lemmafile contains tab-separated fields of (tokenid, lemma)
# for all tokenids

f = open(lemmafile)
lines = []
i = 0
for line in f:
    if i % 100000 == 0:
        print str(i)
    if line.strip():
        s = re.split('\t', line)
        lines.append(s[1].strip())
    i += 1
    
f.close()

# Set up lexicon

db = sqlite3.connect(lexicon)
curs = db.cursor()

stopwords = ['et',
             'non',
             'qui',
             'in',
             'is',
             'atque',
             'neque',
             'autem',
             'ne',
             'sum',
             'hic',
             'ut',
             'ab',
             'ad',
             'cum',
             'cum2',
             'de2',
             'inter',
             'per',
             'ex',
             'ego',
             'tu',
             'sed',
             'si',
             'omnis',
             'quam',
             'quis',
             'quod',
             'ille',
             'illa',
             'ipse',
             'meus',
             'tuus',
             'suus',
             'sui']

i = 5

word = ""
left = []
right = []
counts = {}

# Now, grab 5-word context from lexicon for each token

while i < len(lines):
    if i % 100000 == 0:
        print str(i)
    
    word = lines[i]
    if word == "nolemma" or word == "<unknown>" or word == "textbound":
        i += 1
        continue

    left = lines[i-5:i]
    left.reverse()
    right = lines[i+1:i+6]
    
    if not word in counts:
        counts[word] = {}
    
    for l in left:
        if l == "nolemma":
            curs.execute("select content from tokens where tokenid=?", (i,))
            try: 
                punct = curs.fetchone()[0].encode("utf-8")
            except TypeError:
                print "Bad tokenid @ " + str(i)
            else:
                if punct == '.' or punct == '?' or punct == '!':
                    break
                continue
        elif l == "textbound":
            break
        elif l == "<unknown>" or l in stopwords:
            continue
            
        if l in counts[word]:
            counts[word][l] += 1
        else:
            counts[word][l] = 1
    
    for r in right:
        if r == "nolemma":
            curs.execute("select content from tokens where tokenid=?", (i,))
            try: 
                punct = curs.fetchone()[0].encode("utf-8")
            except TypeError:
                print "Bad tokenid @ " + str(i)
            else:
                if punct == '.' or punct == '?' or punct == '!':
                    break
                continue
        elif r == "textbound":
            break
        elif r == "<unknown>" or r in stopwords:
            continue
            
        if r in counts[word]:
            counts[word][r] += 1
        else:
            counts[word][r] = 1
    
    i += 1

sortedCounts = sorted(counts.iteritems())
print "# of lemmas = " + str(len(sortedCounts))
i = 0
db.close()

# Organize results and write them out to info db

db = sqlite3.connect(infodb)
curs = db.cursor()

curs.executescript("""
drop table if exists collocations;
create table collocations (lemma text, collocation text, count integer, lookupform text);
create index c_l on collocations(lookupform);""")

for w, cs in sortedCounts:
    if i % 1000 == 0:
        print str(i)
    
    sorted_cs = sorted(cs.iteritems(), key=operator.itemgetter(1))
    sorted_cs.reverse()
    
    r = 0
    for c in sorted_cs:
        if r == 10:
            break
        col = c[0]
        count = c[1]
        lookupform = re.sub('[\d\[\]]', '', w)
        curs.execute("insert into collocations values (?,?,?,?)", (w, col, count, lookupform))
        r += 1
    i += 1
db.commit()
db.close()
