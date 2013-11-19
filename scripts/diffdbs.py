#!/usr/bin/env python
import difflib, re, sqlite3, sys

def validate_args(argv):
    do_quiet_output = False
    table_list = []
    filters = []
    if '-q' in argv:
        do_quiet_output = True
        argv.remove('-q')
    if '-t' in argv:
        ind = argv.index('-t')
        table_list = argv[ind+1].split(',')
        argv = argv[:ind] + argv[ind+2:]
    if '-f' in argv:
        ind = argv.index('-f')
        filters = argv[ind+1].split(',')
        argv = argv[:ind] + argv[ind+2:]
    if len(argv) != 2:
        print >> sys.stderr, usage
        sys.exit(1)
    db_from, db_to = argv[:2]
    try:
        open(db_from).close()
        open(db_to).close()
    except IOError, e:
        print >> sys.stderr, '%s: %s' % (prog, str(e))
        sys.exit(1)
    return db_from, db_to, do_quiet_output, table_list, filters

def validate_database(db):
    conn = sqlite3.connect(db)
    conn.text_factory = sqlite3.OptimizedUnicode
    cursor = conn.cursor()
    try:
        cursor.execute('select * from sqlite_master')
    except sqlite3.DatabaseError, e:
        print >> sys.stderr, '%s: error in opening %s: %s' % (prog, db, str(e))
        sys.exit(1)
    return conn, cursor

def rows2lines(rows):
    lines = []
    for row in rows:
        str_comps = []
        for c in row:
            if type(c) is unicode:
                str_comps.append(c.encode('utf-8'))
            else:
                str_comps.append(str(c))
        lines.append('|'.join(str_comps)+'\n')
    return lines

def main():
    global prog, usage
    prog = sys.argv[0].split('/')[-1]
    usage =  'Usage: %s [-q] [-t table1,table2,...] <db1> <db2>\n' % prog
    usage += '    -q                    Quiet output; only display if tables differ\n'
    usage += '    -t table1,table2,...  Only display data for given tables\n'
    usage += '    -f col1=val1,...      Filter by given data'

    db_from, db_to, do_quiet_output, table_list, filters = validate_args(sys.argv[1:])
    conn_from, cursor_from = validate_database(db_from)
    conn_to, cursor_to = validate_database(db_to)

    cursor_from.execute('select name from sqlite_master where type="table"')

    for table in [t[0] for t in cursor_from.fetchall()]:
        if table_list and table not in table_list:
            continue
        if filters:
            filter_string = ' and '.join(filters)
            print filter_string
            cursor_from.execute('select * from ' + table + ' where ' + filter_string)
            cursor_to.execute('select * from ' + table + ' where ' + filter_string)
        else:
            cursor_from.execute('select * from ' + table)
            cursor_to.execute('select * from ' + table)
        no_error = True
        try:
            lines_from = rows2lines(cursor_from.fetchall())
        except sqlite3.OperationalError, e:
            print >> sys.stderr, '%s: warning: in table %s in %s:' \
                % (prog, table, db_from),
            print >> sys.stderr, e.message
            if e.message.find('Could not decode') >= 0:
                offending_char = re.search("with text '([^']*)'",
                e.message).group(1)
                print >> sys.stderr, "offender: 0x%s" \
                    % ''.join('%x' % ord(c) for c in offending_char)
            no_error = False
        try:
            lines_to = rows2lines(cursor_to.fetchall())
        except sqlite3.OperationalError, e:
            print >> sys.stderr, '%s: warning: in table %s in %s:' \
                % (prog, table, db_to),
            print >> sys.stderr, e.message
            if e.message.find('Could not decode') >= 0:
                offending_char = re.search("with text '([^']*)'",
                e.message).group(1)
                print >> sys.stderr, "offender: 0x%s" \
                    % ''.join('%x' % ord(c) for c in offending_char)
            no_error = False
        if no_error:
            if do_quiet_output and lines_from != lines_to:
                print 'table %s differs' % table
            elif not do_quiet_output:
                diff_lines = list(difflib.unified_diff(\
                                    lines_from, lines_to,\
                                    fromfile=db_from, tofile=db_to))
                if diff_lines:
                    print 'In table %s:' % table
                    for line in diff_lines:
                        sys.stdout.write(line)
        else:
            print >> sys.stderr, '%s: warning: skipping table %s' \
                % (prog, table)

if __name__ == '__main__':
    main()
