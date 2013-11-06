#!/usr/bin/env python
# Creates the authorFreqs table in the greekInfo db for Logeion;
# values are configured to be run on diderot (Perseus home).
# Last modified: 09/15/2013
from __future__ import with_statement
import itertools
import re
import sqlite3
import sys
import urllib2

dict_home    = '/Volumes/data/var/lib/philologic/databases/GreekFeb2011'
info_db      = './greekInfo.db'
lemmafile    = dict_home + '/frequencies/lemmafile'
lexicon      = '/Library/WebServer/CGI-Executables/perseus/GreekLexicon.db'
countbydocid = dict_home  + '/countbydocid'
bibliography = dict_home + '/bibliography'

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
    print '    --info-db <info-db>'
    print '    --lemmafile <lemma-file>'
    print '    --lexicon <lexicon>'
    print '    --countbydocid <countbydocid-file>'
    print '    --bibliography <bibliography-file>'
    print '    --help'

def parse_arguments(args):
    global info_db, lemmafile, lexicon, countbydocid, bibliography, prog
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
            elif args[i] == '--countbydocid':
                countbydocid = args[i+1]
                i += 2
            elif args[i] == '--bibliography':
                bibliography = args[i+1]
                i += 2
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

def main():
    global info_db, lemmafile, lexicon, countbydocid, bibliography, prog
    prog = sys.argv[0].split('/')[-1]
    parse_arguments(sys.argv[1:])
        
    print 'Using ' + info_db + ' as info db'
    print 'Using ' + lemmafile + ' as lemma file'
    print 'Using ' + lexicon + ' as lexicon'
    print 'Using ' + countbydocid + ' as countbydocid file'
    print 'Using ' + bibliography + ' as bibliography file'

    yn = ''
    while yn not in ('y', 'n', 'yes', 'no'):
        yn = raw_input("Are these arguments OK? (y/n) ").lower()
    if yn in ('n','no'):
        usage(prog)
        sys.exit(0)

    try:
        open(lemmafile).close()
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
        open(info_db).close()
    except IOError, e: # If file doesn't exist, keep going
        pass
    else: # Otherwise, check that it's writeable and actually a SQLite db
        try:
            open(info_db, 'a').close()
            #with sqlite3.connect(info_db) as tmp_conn:
            #    tmp_conn.cursor().execute('select * from sqlite_master')
            sqlite3.connect(info_db).cursor().execute('select * from sqlite_master')
        except IOError, e:
            print >> sys.stderr, '%s: %s' % (prog, str(e))
            sys.exit(1)
        except sqlite3.DatabaseError, e:
            print >> sys.stderr, '%s: error reading %s: %s' % (prog, info_db, str(e))
            sys.exit(1)

    # Slower, but less memory-hungry; we'll sort out actual lemmas
    # from other entries later
    print 'Reading lemmas...'
    all_lemmas = dict()
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
    #with sqlite3.connect(info_db) as info_conn:
    #    with sqlite3.connect(lexicon) as lex_conn:
    info_conn = sqlite3.connect(info_db)
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
