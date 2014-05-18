#!/usr/bin/env python
import sys, sqlite3

default_infodb = './greekInfo.db'
default_lexicon = '/Library/WebServer/CGI-Executables/perseus/GreekLexicon.db'
authors = {'Lysias': [], 'Plato': []}

prog = sys.argv[0].split('/')[-1]

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
    if len(args) > 2:
        printf >> sys.stderr, '%s: warning: ignoring arguments "%s"' \
            % (prog, ' '.join(args[2:]))
    options = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--infodb':
            options['infodb'] = args[i]
            i += 1
        elif a == '--lexicon':
            options['lexicon'] = args[i]
            i += 1
        i += 1
    return options

# Given a cursor to the infodb file and a set of tokenids,
# store the proper number of examples in dictionary
def commit_to_db(cursor, lemma, tids):
    tids = list(tids)[:10]
    return
    

def main():
    args = sys.argv[1:]
    options = parse_args(args)
    infodb = default_infodb \
             if 'infodb' not in options \
             else options['infodb']
    lexicon = default_lexicon \
              if 'lexicon' not in options \
              else options['lexicon']
    print 'Using "%s" as info db' % infodb
    print 'Using "%s" as lexicon' % lexicon
    yn = ''
    while yn not in ('y', 'n', 'yes', 'no'):
        yn = raw_input("Are these arguments OK? (y/n) ").lower()
    if yn in ('n','no'):
        usage(prog)
        sys.exit(0)

    check_db_or_die(infodb)
    check_db_or_die(lexicon)
    info_conn = sqlite3.connect(infodb)
    info_cursor = info_conn.cursor()
    lex_conn = sqlite3.connect(lexicon)
    lex_cursor = lex_conn.cursor()

    for a in authors:
        authors[a] = [f[0] for f in lex_cursor.execute('select distinct file from tokens where file like "%s%%"' % a).fetchall()]

    info_cursor.execute('select lemma from frequencies')
    lemma = info_cursor.fetchone()
    current = 0
    while lemma:
        current += 1
        if current % 1000 == 0:
          print current, 
        lex_cursor.execute('select lexid from Lexicon where lemma=?', lemma)
        lexids = lex_cursor.fetchall()
        tokenids = []
        for l in lexids:
            lex_cursor.execute('select tokenid from parses where lex=?', (l,))
            tokenids.expand([t[0] for t in lex_cursor.fetchall()])
        simple_tids = set([t for t in tokenids if c.execute('select * from tokens where tokenid=? and (file like "Lysias%" or file like "Plato%")', (t,))])
        athzd_tids = set([t for t in tokenids if c.execute('select * from authorized where tokenid=?', (t,))])

        # First, take all examples from simple authors and authorized
        final_tids = simple_tids.intersection(athzd_tids)
        if len(final_tids) >= 10:
            commit_to_db(info_cursor, final_tids)
            continue

        # Not enough from authorized and simple, so take all authorized
        final_tids = final_tids.union(athzd_tids)
        if len(final_tids) >= 10:
            commit_to_db(info_cursor, final_tids)
            continue

        # If still not enough, take all simple authors too
        final_tids = final_tids.union(simple_tids)
        if len(final_tids) >= 10:
            commit_to_db(info_cursor, final_tids)
            continue

        # Finally, take all instances
        commit_to_db(info_cursor, set(tokenids))

        lemma = cursor.fetchone()


if __name__ == '__main__':
    main()
