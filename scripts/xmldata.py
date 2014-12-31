#!/usr/bin/env python
# Fun little script that spits out all tags that appear in the given set of XML files
# as well as every attribute that tag can have and every value that attribute takes on.
from __future__ import with_statement
import re
import sys

# THIS IS NOT AN XML VERIFIER, IT JUST DOES THE MINIMUM TO GET PARTS OF VALID XML TAGS.
# <[ ]* -> start of tag followed by any space
# ([^ /]+?) -> name of tag; adding `/` removes end tags
# ([ ]*[^=]+="[^"]*"[ ]*)* -> any number of things of the form `attr="value"` surrounded by space on either side
# [ /]*> -> ended by space or a `/` (in the case of self-closing tags)
get_whole_tag = re.compile(r'<[ ]*([^ />]+)([ ]*[^=>]+="[^"]*"[ ]*)*[ /]*>')
parse_tag_attrs = re.compile(r'[ ]*([^=]+)="([^"]*)"[ ]*')
prog = ''

def usage(error=None):
    if error:
        print >> sys.stderr, error
    print >> sys.stderr, 'Usage: %s <file> ...' % prog
    sys.exit(-1)

def validate_args(args):
    for a in args:
        try:
            open(a).close()
        except IOError, e:
            usage("Error: could not open file %s for read (%s)" % (a, e.message))

def main():
    prog = sys.argv[0]
    files = sys.argv[1:]
    if not files:
        usage()
    validate_args(files)
    tags = {}
    print >> sys.stderr, '%d files to process...' % len(files)
    for f in files:
        text = ''
        with open(f) as infh:
            text = infh.read()
        tagmatch_iter = get_whole_tag.finditer(text)
        for tag_m in tagmatch_iter:
            tagname = tag_m.group(1)
            attrs_asstr = tag_m.group(2)
            if tagname not in tags:
                tags[tagname] = {}
            if attrs_asstr:
                for attr_m in parse_tag_attrs.finditer(attrs_asstr):
                    attrname, attrvalue = attr_m.group(1), attr_m.group(2)
                    tag_attrs = tags[tagname]
                    if attrname not in tag_attrs:
                        tag_attrs[attrname] = set([attrvalue])
                    else:
                        tag_attrs[attrname].add(attrvalue)
        #tags.update(set([m.group(1) for m in tag_patt.finditer(text)]))
    for t,attrs in tags.items():
        print t
        for attr,values in attrs.items(): 
            print '\t%s=%s' % (attr, str(list(values)))
    #print '\n'.join(tags)

if __name__ == '__main__':
    main()
