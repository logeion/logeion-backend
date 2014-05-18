#!/usr/bin/env python
# Checks if a given tag is nested within (an)
# XML document(s)

from __future__ import with_statement
import re, sys

prog = sys.argv[0].split('/')[-1]
args = sys.argv[1:]
usage = 'usage: %s PATTERN FILE ...' % prog
if len(args) < 2:
    if len(args) == 1:
        print >> sys.stderr, '%s: error: need at least two args' % prog
    print >> sys.stderr, usage
    sys.exit(0-len(args))
tag_name = args[0]
tag_patt = re.compile('<(/)?[\s]*'+tag_name)
files = args[1:]
for f in files:
    with open(f) as infh:
        last_was_open = False
        for m in tag_patt.finditer(infh.read()):
            if (last_was_open and not m.group(1)) or \
               (not last_was_open and m.group(1)):
                print '<%s> in %s is nested' % (tag_name, f)
                break
            last_was_open = not last_was_open
