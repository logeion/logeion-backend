#!/usr/bin/env python
# Creates the authorFreqs table in the latinInfo db for Logeion;
# values are configured to be run on diderot (Perseus home).
# Last modified: 09/15/2013
from __future__ import with_statement
import itertools
import re
import sqlite3
import sys
import urllib2
import operator

dict_home    = '/Volumes/data/var/lib/philologic/databases/LatinAugust2012'
default_infodb      = './latinInfo.db'
#default_lemmafile    = dict_home + '/frequencies/lemmafile'
default_lexicon      = '/Library/WebServer/CGI-Executables/perseus/LatinLexicon.db'
default_countbydocid = dict_home  + '/countbydocid'
default_bibliography = dict_home + '/bibliography'

# Returns a array of counts indexed by docid
def parse_text_counts(countbydocid):
    mapping = []
    with open(countbydocid) as infh:
        for line in infh:
            if re.search('^[\d]', line):
                mapping.append(int(line.strip().split('\t')[-1]))
    return mapping

# Returns a map of authors to lists of (text,docid) pairs
def parse_author_texts(bibliography):
    mapping = dict()
    with open(bibliography) as infh:
        for line in infh:
            comps = line.strip().split('\t')
            author = comps[1]
            text = comps[-3]
            docid = int(comps[-1])
            if author in mapping.keys():
                mapping[author].append((text,docid))
            else:
                mapping[author] = [(text,docid)]
    return mapping

# Returns a map of authors to (count, list of texts) pairs
def flatten_mappings(docid2count, author2texts):
    mapping = dict()
    for author in author2texts:
        texts_docids = author2texts[author]
        texts = [p[0] for p in texts_docids]
        docids = [p[1] for p in texts_docids]
        count = sum([docid2count[i] for i in range(len(docid2count)) if i in docids]) 
        mapping[author] = (count, texts)
    return mapping

def usage(prog):
    print 'Usage: %s [options]' % prog
    print '    --infodb <info-db>'
    print '    --lexicon <lexicon>'
    print '    --countbydocid <countbydocid-file>'
    print '    --bibliography <bibliography-file>'
    print '    --confirm'
    print '    --help'

def parse_arguments(args):
    options = {}
    args = sys.argv[1:]
    argc = len(args)
    i = 0
    while i < argc:
        try:
            if args[i] == '--infodb':
                options['infodb'] = args[i+1]
                i += 2
            elif args[i] == '--lexicon':
                options['lexicon'] = args[i+1]
                i += 2
            elif args[i] == '--countbydocid':
                options['countbydocid'] = args[i+1]
                i += 2
            elif args[i] == '--bibliography':
                options['bibliography'] = args[i+1]
                i += 2
            elif args[i] == '--confirm':
                options['confirm'] = True
                i += 1
            elif args[i] == '--help':
                usage(prog)
                sys.exit(0)
            else:
                print >> sys.stderr, '%s: error: unrecognized arg %s' % args[i]
                usage(prog)
                sys.exit(1)
        except IndexError, e:
            print >> sys.stderr, '%s: error: no value following %s' % (prog, args[i])
            usage(prog)
            sys.exit(1)
    return options

def main():
    global prog
    prog = sys.argv[0].split('/')[-1]
    options = parse_arguments(sys.argv[1:])
    infodb = default_infodb \
            if 'infodb' not in options \
            else options['infodb']
    lexicon = default_lexicon \
            if 'lexicon' not in options \
            else options['lexicon'] 
    countbydocid = default_countbydocid \
            if 'countbydocid' not in options \
            else options['countbydocid']
    bibliography = default_bibliography \
            if 'bibliography' not in options \
            else options['bibliography']

    print 'Using ' + infodb + ' as info db'
    print 'Using ' + lexicon + ' as lexicon'
    print 'Using ' + countbydocid + ' as countbydocid file'
    print 'Using ' + bibliography + ' as bibliography file'

    if 'confirm' in options:
        yn = ''
        while yn not in ('y', 'n', 'yes', 'no'):
            yn = raw_input("Are these arguments OK? (y/n) ").lower()
        if yn in ('n','no'):
            usage(prog)
            sys.exit(0)

    try:
        open(countbydocid).close()
        open(lexicon).close()
        sqlite3.connect(lexicon).cursor().execute('select * from Lexicon limit 1')
        #with sqlite3.connect(lexicon) as tmp_conn:
        #    tmp_conn.cursor().execute('select * from Lexicon limit 1')
    except IOError, e:
        print >> sys.stderr, '%s: %s' % (prog, str(e))
        sys.exit(1)
    except sqlite3.DatabaseError, e:
        print >> sys.stderr, '%s: error reading %s: %s' % (prog, lexicon, str(e))
        sys.exit(1)
    except sqlite3.ProgrammingError, e:
        print >> sys.stderr, '%s: error reading %s: %s' % (prog, lexicon, str(e))
        sys.exit(1)

    try:
        open(infodb).close()
    except IOError, e: # If file doesn't exist, keep going
        pass
    else: # Otherwise, check that it's writeable and actually a SQLite db
        try:
            open(infodb, 'a').close()
            sqlite3.connect(infodb).cursor().execute('select * from sqlite_master')
        except IOError, e:
            print >> sys.stderr, '%s: %s' % (prog, str(e))
            sys.exit(1)
        except sqlite3.DatabaseError, e:
            print >> sys.stderr, '%s: error reading %s: %s' % (prog, infodb, str(e))
            sys.exit(1)

    # Slower, but less memory-hungry; we'll sort out actual lemmas
    # from other entries later
    print 'Reading lemmas...'
    all_lemmas = dict()




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
    print >> sys.stderr, 'Reversing mapping...'
    for i,e in enumerate(entries):
        if e and e not in all_lemmas:
            all_lemmas[e] = [i]
        elif e:
            all_lemmas[e].append(i)



    """
    with open(lemmafile) as infh:
        for line in infh:
            if line.strip() and len(line.strip().split('\t')) > 1:
                tokenid, lemma = line.strip().decode('utf-8').split('\t')
                if lemma in all_lemmas:
                    all_lemmas[lemma].append(int(tokenid))
                else:
                    all_lemmas[lemma] = [int(tokenid)]
    all_lemmas.pop('nolemma')
    all_lemmas.pop('textbound')
    """
    print len(all_lemmas), 'lemmas found.'

    print 'Creating docid-to-wordcount mapping'
    docids2counts = parse_text_counts(countbydocid)
    print 'Creating author-to-text mapping'
    authors2texts = parse_author_texts(bibliography)
    print 'Creating author-to-count/text mapping'
    author2textinfo = flatten_mappings(docids2counts, authors2texts)

    # Create text-to-author lookup to speed up next loop
    all_texts = list(itertools.chain(*authors2texts.values()))
    texts2authors = dict()
    for author,texts in authors2texts.items():
        for t in texts:
            texts2authors[t[0]] = author

    print 'Inserting results into db...'
    #with sqlite3.connect(infodb) as info_conn:
    #    with sqlite3.connect(lexicon) as lex_conn:
    info_conn = sqlite3.connect(infodb)
    lex_conn = sqlite3.connect(lexicon)
    info_cursor = info_conn.cursor()
    info_cursor.executescript("""
        drop table if exists authorFreqs;
        create table authorFreqs(lemma text, rank integer, author text, freq float);
        create index aF_l on authorFreqs(lemma);""")
    lex_cursor = lex_conn.cursor()
    file_query = 'select file from tokens where tokenid=?'
    counter = 1
    for lemma, tokenids in all_lemmas.items():
        author_freqs = dict()
        if counter % 10000 == 0:
            print counter
        elif counter % 100 == 0:
            print counter,
        sys.stdout.flush()

        files = [r[0] for tid in tokenids
                      for r in lex_cursor.execute(file_query, (tid,)).fetchall()]
        for f in files:
            author = texts2authors[f]
            author_freqs[author] = author_freqs.setdefault(author, 0) + 1
        for author in author_freqs:
            count = author_freqs[author]
            author_freqs[author] = (count * 10000.0) / author2textinfo[author][0]

        # Top 5 author names sorted by frequency (highest to lowest)
        ranked_authors = sorted(author_freqs.keys(),
                                key=lambda k: author_freqs[k],
                                reverse=True)[:5]
        # Dict with ranked_authors as keys and corresponding freqs as values
        author_freqs_top5 = dict([p for p in author_freqs.items()
                                    if p[0] in ranked_authors])
        # List of 4-tuples: (lemma, rank, author, frequency) (per lemma)
        data_to_insert = map(lambda (a,f): (lemma, ranked_authors.index(a)+1, a, f),
                             author_freqs_top5.items())
        info_cursor.executemany('insert into authorFreqs values (?,?,?,?)',
                                data_to_insert)
        counter += 1
    info_conn.commit()

if __name__ == '__main__':
    main()
