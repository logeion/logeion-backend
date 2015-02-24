#!/usr/bin/env python
from __future__ import with_statement
from BeautifulSoup import BeautifulStoneSoup
import sys

prog = None

def read_from_files(tag, files, print_file_names):
    for f in files:
        try:
            open(f).close()
        except IOError, e:
            print >> sys.stderr, "%s: warning: could not open file %s: %s" % (prog, f, str(e))
            continue

        with open(f) as infh:
            if print_file_names: print '*** %s:' % f
            soup = BeautifulStoneSoup(infh)
            tags_in_f = soup.findAll(tag)
            for t in tags_in_f:
                print t

def read_from_stdin(tag):
    pass

if __name__ == '__main__':
    prog = sys.argv[0].split('/')[-1]
    if len(sys.argv[1:]) == 1:
        # Read from stdin
        read_from_stdin(sys.argv[1])
    else:
        read_from_files(sys.argv[1], sys.argv[2:], len(sys.argv[2:]) > 1)
