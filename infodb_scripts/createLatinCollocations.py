#!/usr/bin/env python
# coding=utf-8

import sqlite3
import re
import operator
import unicodedata
import sys

# Do basic config: grab lexicon location, assign infodb and lemmafile,
# and check that lexicon and lemmafile exist and are readable

infodb    = './latinInfo.db'
lexicon   = '/Library/WebServer/CGI-Executables/perseus/LatinLexicon.db'
confirm = False

prog = sys.argv[0].split('/')[-1]

def usage(prog):
    print 'usage: %s [options]' % prog
    print '    --infodb <info-db>'
    print '    --lexicon <lexicon>'
    print '    --confirm'

# Get command-line arguments
args = sys.argv[1:]
argc = len(args)
i = 0
while i < argc:
    try:
        if args[i] == '--infodb':
            infodb = args[i+1]
            i += 2
        elif args[i] == '--lexicon':
            lexicon = args[i+1]
            i += 2
        elif args[i] == '--confirm':
            confirm = True
            i += 1
        else:
            print >> sys.stderr, '%s: error: unrecognized arg %s' % (prog, args[i])
            usage(prog)
            sys.exit(1)
    except IndexError, e:
        print >> sys.stderr, '%s: error: no value following %s' % (prog, args[i])
        usage(prog)
        sys.exit(1)

print 'Using "%s" as info db' % infodb
print 'Using "%s" as lexicon' % lexicon

if confirm:
    yn = ''
    while yn not in ('y', 'n', 'yes', 'no'):
        yn = raw_input("Are these arguments OK? (y/n) ").lower()
    if yn in ('n','no'):
        usage(prog)
        sys.exit(0)

try:
    open(lexicon).close()
except IOError, e:
    print >> sys.stderr, '%s: %s' % (prog, str(e))
    sys.exit(1)

# Read in lemmas; lemmafile contains tab-separated fields of (tokenid, lemma)
# for all tokenids

#print 'Reading lemma file...'
print 'Obtaining tokenid-to-lemma mapping...'

db = sqlite3.connect(lexicon)
db.row_factory = sqlite3.Row
curs = db.cursor()
curs.execute('\
SELECT tokens.tokenid, Lexicon.lemma, parses.prob \
FROM tokens LEFT JOIN parses \
ON tokens.tokenid = parses.tokenid \
LEFT JOIN Lexicon \
ON parses.lex = Lexicon.lexid')

# Aggregate entries with the same tid
# (i.e. different parses of same token)
i = 0
aggr_rows = {}
for row in curs.fetchall():
    i += 1
    tid = row['tokenid']
    if tid not in aggr_rows:
        aggr_rows[tid] = [row]
    else:
        aggr_rows[tid].append(row)

# Now choose only tids where prob is max
print >> sys.stderr, i
print >> sys.stderr, len(aggr_rows)

# Alright, so here's some crazy bullshit: there something like 40k
# missing tokenids, so we need to fill those in somehow: if a tokenid
# is missing in the tokens table, then we fill it in with 'nolemma',
# and '' is reserved for entries in the tokens table without a parse
# (i.e. punctuation and headers)

i = 1
entries = []
sorted_items = sorted(aggr_rows.items(), key=operator.itemgetter(0))
for tid,rs in sorted_items:
    #print 'i = %d, tid = %d' % (i,tid)
    while i < tid:
        #entries[i] = u'nolemma'
        entries.append(u'')
        i += 1
    r = sorted(rs, key=operator.itemgetter('prob'), reverse=True)[0]
    if r['lemma']:
        #entries[tid] = r['lemma']
        entries.append(r['lemma'])
    else:
        #entries[tid] = u''
        entries.append(u'')
    i += 1

print >> sys.stderr, len(entries)
#for i,l in enumerate(entries):
#    print '%d|%s' % (i,l.encode('utf-8'))
#sys.exit(0)

stopwords = [u'et',
             u'non',
             u'qui',
             u'in',
             u'is',
             u'atque',
             u'neque',
             u'autem',
             u'ne',
             u'sum',
             u'hic',
             u'ut',
             u'ab',
             u'ad',
             u'cum',
             u'cum2',
             u'de2',
             u'inter',
             u'per',
             u'ex',
             u'ego',
             u'tu',
             u'sed',
             u'si',
             u'omnis',
             u'quam',
             u'quis',
             u'quod',
             u'ille',
             u'illa',
             u'ipse',
             u'meus',
             u'tuus',
             u'suus',
             u'sui']
              
#i = 5

word = ""
left = []
right = []
counts = {}

lemmas_to_skip = (u'nolemma', u'<unknown>', u'textbound')
end_of_sentence = (u'.', u'?', u'!')

# Now, grab 5-word context from lexicon for each token; compare accentless
print '\nGrabbing context from lexicon...'
print 'entries[:5] = [', u','.join(entries[:5]).encode('utf-8'), ']'
#for i,word in entries:
for i,word in enumerate(entries):
    if i % 100000 == 0:
        print str(i),
        sys.stdout.flush()
    tid = i+1
    
    if not word or word in lemmas_to_skip:
        continue

    left = entries[i-5:i]
    left.reverse()
    right = entries[i+1:i+6]
    
    if not word in counts:
        counts[word] = {}
    
    # TODO: implement 'nolemma'
    for l in left:
        accentless = u''.join([c for c in unicodedata.normalize("NFD", l) \
                              if unicodedata.category(c) != 'Mn'])
        if not l:
            curs.execute("select content from tokens where tokenid=?", (tid,))
            try:
                punct = curs.fetchone()[0]
            except TypeError:
                #print "Bad tokenid @ " + str(i)
                print tid, 'not in table'
            else:
                # If end of sentence, stop gathering context
                if punct in end_of_sentence:
                    break
                continue
        elif accentless in stopwords:
            continue
            
        if l in counts[word]:
            counts[word][l] += 1
        else:
            counts[word][l] = 1

    for r in right:
        accentless = u''.join([c for c in unicodedata.normalize("NFD", r) \
                              if unicodedata.category(c) != 'Mn'])
        if not r:
            curs.execute("select content from tokens where tokenid=?", (tid,))
            try:
                punct = curs.fetchone()[0]
            except TypeError:
                print tid, 'not in table'
            else:
                # If end of sentence, stop gathering context
                if punct in end_of_sentence:
                    break
                continue
        elif accentless in stopwords:
            continue
            
        if r in counts[word]:
            counts[word][r] += 1
        else:
            counts[word][r] = 1

sortedCounts = sorted(counts.iteritems())
print "\n# of lemmas = " + str(len(sortedCounts))
i = 0
db.close()

# Organize results and write them out to info db

print 'Organizing results and writing to db...'

db = sqlite3.connect(infodb)
curs = db.cursor()

curs.executescript("""
drop table if exists collocations;
create table collocations (lemma text, collocation text, count integer, lookupform text);
create index c_l on collocations(lookupform);""")

for w, cs in sortedCounts:
    if i % 1000 == 0:
        print str(i),
        sys.stdout.flush()
    
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
