#!/usr/bin/env python
from __future__ import with_statement
import sys, sqlite3
import itertools

default_infodb = './greekInfo.db'
default_lexicon = '/Library/WebServer/CGI-Executables/perseus/GreekLexicon.db'
default_bibliography = '/var/lib/philologic/databases/GreekFeb2011/bibliography'
authors = {'Lysias': [], 'Plato': []}

prog = sys.argv[0].split('/')[-1]

file2authorwork = {}

def usage(prog):
    print 'Usage: %s [options]' % prog
    print '    --infodb <info-db>'
    print '        DB where samples are eventually stored'
    print '    --lexicon <lexicon>'
    print '        Perseus lexicon for querying token, parse data'
    print '    --bibliography <bib>'
    print '        File for getting mapping from file names to author/work;'
    print '        should be in /var/lib/philologic/databases/<database>/'
    print '    --confirm'
    print '        If present, displays a prompt for user to double-'
    print '        check the input arguments'
    print '    --help'

def check_db_or_die(db):
    try:
        open(db).close()
        tmp_db = sqlite3.connect(db)
        tmp_curs = tmp_db.cursor()
        tmp_curs.execute('select * from sqlite_master')
        tmp_db.close()
    except IOError, e:
        print >> sys.stderr, '%s: error: %s' % (prog, str(e))
        sys.exit(-1)
    except sqlite3.DatabaseError, e:
        print >> sys.stderr, '%s: error: %s' % (prog, str(e))
        sys.exit(-1)
    return db

def parse_args(args):
    options = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--infodb':
            options['infodb'] = args[i+1]
            i += 1
        elif a == '--lexicon':
            options['lexicon'] = args[i+1]
            i += 1
        elif a == '--bibliography':
            options['bibliography'] = args[i+1]
            i += 1
        elif a == '--confirm':
            options['confirm'] = True
        elif a == '--help':
            usage(prog)
            sys.exit(0)
        else:
            print >> sys.stderr, '%s: warning: ignoring argument %s' % a
        i += 1
    return options

def get_token_context(c, tid):
    res = c.execute('select seq,file from tokens where tokenid=?', (tid,)).fetchone()
    seq, file = res['seq'], res['file']
    first_seq = seq-20 if seq > 20 else 0
    last_seq = seq+20
    c.execute('select tokenid,content,type from tokens where '+\
        'seq>=? and seq<=? and file=? order by seq', (first_seq, last_seq, file))
    return c.fetchall()

def encapsulate_with_tag(target_tid, row):
    if row['type'] == 'punct':
        return row['content']
    tid, content = row['tokenid'], row['content']
    if tid == target_tid:
        return '<w class="sample_hw" id="%d">%s</w>' % (tid, content) 
    return '<w id="%d">%s</w>' % (tid, content)

def get_file_from_tokenid(c, tid):
    return c.execute('select file from tokens where tokenid=?', (tid,)).fetchone()['file']

# Given a cursor to the lexicon file and a set of tokenids,
# store the proper number of examples in dictionary
def commit_to_db(lexc, infoc, lemma, ranked_tids):
    global file2authorwork
    ranked_tids = sorted(ranked_tids, key=lambda (r,t): r)[:10]
    token_contexts = [(r, t, get_file_from_tokenid(lexc,t), \
                       get_token_context(lexc,t)) for r,t in ranked_tids]
    strlemma = lemma[0]
    if isinstance(strlemma, unicode):
        strlemma = strlemma.encode('utf-8')
    tags = [(strlemma.decode('utf-8'), r, \
             u' '.join([encapsulate_with_tag(tid,t) for t in ts]), \
             file2authorwork[f][0], file2authorwork[f][1]) \
                for r,tid,f,ts in token_contexts]
    infoc.executemany('insert into samples values (?,?,?,?,?)', tags)
    #print 'Committing %s: %s' % (strlemma,  str(tags))

def load_file2authorwork(bibliography):
    global file2authorwork
    with open(bibliography) as fh:
        for line in fh:
            comps = line.strip().split('\t')
            f = filter(lambda c: c.find('.xml') >= 0, comps)[0]
            file2authorwork[f] = (comps[1], comps[0]) # (author, work)

def main():
    args = sys.argv[1:]
    options = parse_args(args)
    infodb = default_infodb \
             if 'infodb' not in options \
             else options['infodb']
    lexicon = default_lexicon \
              if 'lexicon' not in options \
              else options['lexicon']
    bibliography = default_bibliography \
              if 'bibliography' not in options \
              else options['bibliography']
    print 'Using "%s" as info db' % infodb
    print 'Using "%s" as lexicon' % lexicon
    print 'Using "%s" as bibliography' % bibliography

    if 'confirm' in options:
        yn = None
        while yn not in ('y', 'n', 'yes', 'no', ''):
            yn = raw_input("Are these arguments OK? (Y/n) ").lower().strip()
        if yn in ('n','no'):
            usage(prog)
            sys.exit(0)

    check_db_or_die(infodb)
    check_db_or_die(lexicon)
    info_conn = sqlite3.connect(infodb)
    info_cursor = info_conn.cursor()
    lex_conn = sqlite3.connect(lexicon)
    lex_cursor = lex_conn.cursor()
    load_file2authorwork(bibliography)

    for a in authors:
        authors[a] = [f[0] for f in lex_cursor.execute('select distinct file from tokens where file like "%s%%"' % a).fetchall()]
    author_files = list(itertools.chain(*authors.values()))

    print authors

    lex_cursor.row_factory = sqlite3.Row
    print 'Fetching parses table...'
    all_tokenid_entries = lex_cursor.execute('select lex,tokenid from parses').fetchall()
    lexid2tokenids = {}
    print 'Num entries: %d' % len(all_tokenid_entries)
    print 'Creating lexid2tokenids map...',
    sys.stdout.flush()

    for i,e in enumerate(all_tokenid_entries):
        #if (i+1) % 1000 == 0:
        #    print i+1,
        #    sys.stdout.flush()
        if e['lex']:
            lexid2tokenids[e['lex']] = lexid2tokenids.setdefault(e['lex'], []) + [e['tokenid']]
    print 'done.'
    all_tokenids = [e['tokenid'] for e in all_tokenid_entries]
    all_authorized = set([int(e['tokenid']) for e in lex_cursor.execute('select tokenid from authorized').fetchall()])

    info_cursor.executescript(\
        '''drop table if exists samples;
           drop index if exists s_lem;
           create table samples (lemma text, rank integer, sample text, author text, work text);
           create index s_lem on samples(lemma);''')
    info_cursor.execute('select lemma from frequencies')
    lemmas = info_cursor.fetchall()
    print 'Creating samples...',
    for current,lemma in enumerate(lemmas):
        if current % 1000 == 0:
          print current, 
        tokenids = []
        simple_tids, athrzd_tids, final_tids = set(), set(), set()
        found_sufficient = False

        #print 'Lemma ' + lemma[0].encode('utf-8'),
        #sys.stdout.flush()
        lex_cursor.execute('select lexid from Lexicon where lemma=?', lemma)
        lexids = lex_cursor.fetchall()

        # Shortcut for [[1,2,3],[4,5,6],...] => [1,2,3,4,5,6,...]
        flatten = lambda iters: list(itertools.chain(*iters))
        these_tokenids = flatten(filter(lambda t: t != None, [lexid2tokenids.get(l['lexid']) for l in lexids]))
        # TODO: maybe cache this data?
        these_tokenid_entries = flatten([lex_cursor.execute('select tokenid,file from tokens where tokenid=?', (t,)).fetchall() for t in these_tokenids])
        for e in these_tokenid_entries:
            if e['file'] in author_files:
                simple_tids.add(e['tokenid'])
            if e['tokenid'] in all_authorized:
                athrzd_tids.add(e['tokenid'])

        #print 'Tokenids grabbed', 
        # First, take all examples from simple authors and authorized
        final_tids1 = simple_tids.intersection(athrzd_tids)
        ranked_tids = [(1,e) for e in final_tids1]
        if len(final_tids1) >= 10:
            commit_to_db(lex_cursor, info_cursor, lemma, ranked_tids)
            found_sufficient = True

        # Not enough from authorized and simple, so take all authorized
        final_tids2 = final_tids1.union(athrzd_tids)
        ranked_tids.extend([(2,e) for e in final_tids2.difference(final_tids1)])
        if len(final_tids2) >= 10 and not found_sufficient:
            commit_to_db(lex_cursor, info_cursor, lemma, ranked_tids)
            found_sufficient = True

        # If still not enough, take all simple authors too
        final_tids3 = final_tids2.union(simple_tids)
        ranked_tids.extend([(3,e) for e in final_tids3.difference(final_tids2)])
        if len(final_tids3) >= 10 and not found_sufficient:
            commit_to_db(lex_cursor, info_cursor, lemma, ranked_tids)
            found_sufficient = True

        # Finally, take all instances
        final_tids4 = final_tids3.union(set(these_tokenids))
        ranked_tids.extend([(4,e) for e in final_tids4.difference(final_tids3)])
        if not found_sufficient:
            commit_to_db(lex_cursor, info_cursor, lemma, ranked_tids)

        #lemma = info_cursor.fetchone()

    print 'Done; committing data'
    info_conn.commit()

if __name__ == '__main__':
    main()
