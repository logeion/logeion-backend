#!/usr/bin/env python
#
# fix_lsj_issues.py
# Author: Matt Shanahan
#
# NB: DON'T JUST RUN THIS AND EXPECT YOUR PROBLEMS TO BE
# SOLVED. There are known issues (at least by me) in LSJ
# re: the <p><entryFree></div2> scenario, a lack of closing
# <text>, <div1>, and <tei.2> tags, and other small, screwed-
# up dealios. Run everything through `xmllint --noout FILE`
# to see the damage, before and after.

from __future__ import with_statement
import sys
import re

find_div2 = re.compile('(.*?)((<div2|</div2)[^>]*>)', re.S)

# So basically, div1 tags get opened like crayzay, so we're
# just going to straight up delete them (if they aren't
# the slightly-more-legitimate alphabetical separators);
# we've also got a lack of closing text and tei.2 tags,
# so we'll throw those in when necessary. EASY.
# (There might be scenarios where there is a closing text
# tag and not a closing tei tag, in which case see disclaimer)
def fix_easy_problems(text):
    text = re.sub('<div1>', '', text)
    if re.search('<text', text) and not re.search('</text>', text):
        text += '\n</text>'
    if not re.search('</tei.2>', text):
        text += '\n</tei.2>'
    if re.search('<div1[^>]*type="alphabetic letter"', text) and \
       re.search('</div0>', text):
        text = re.sub('</div0>', '</div1>', text)
    return text

# Assumes sense tags aren't nested (please oh god please)
find_sense = re.compile('(.*?)((<sense|</sense|</div2)[^>]*>)', re.S)
def fix_sense(text):
    text_chunks = []
    last_end_index = 0
    last_tag_opened = False
    for m in find_sense.finditer(text):
        if m.group(3) == '<sense':
            if last_tag_opened:
                text_chunks.append(m.group(1))
                text_chunks.append('</sense>')
                text_chunks.append(m.group(2))
            else:
                text_chunks.append(m.group(0))
                # WHY WOULD SENSE BE SELF-CLOSING WHAT IS THIS
                if not re.search('<sense[^>]*/[\s]*>', m.group(2)):
                    last_tag_opened = True
        elif m.group(3) == '</sense':
            if last_tag_opened:
                text_chunks.append(m.group(0))
                last_tag_opened = False
            else:
                text_chunks.append(m.group(1))
                text_chunks.append('<!--')#--/sense-->')
                text_chunks.append(m.group(2))
                text_chunks.append('-->')
        elif m.group(3) == '</div2':
            if last_tag_opened:
                text_chunks.append(m.group(1))
                text_chunks.append('</sense>')
                text_chunks.append(m.group(2))
                last_tag_opened = False
            else:
                text_chunks.append(m.group(0))
        else:
            print >> sys.stderr, 'something is fubar in fix_sense'
            print >> sys.stderr, m.group(0)
            sys.exit(1)
        last_end_index = m.end()
    text_chunks.append(text[last_end_index:])
    return ''.join(text_chunks)


# Alright, so I KNOW that some foreign tags are nested
# (even in the same language), so there are no assumptions
# here, just moments, lost, like tears in rain
find_foreign = re.compile('(.*?)((<foreign|</foreign)[^>]*>)', re.S)
find_nongreek = re.compile('([^\s]*)[a-zA-Z]+', re.S)
def fix_foreign(text):
    text_chunks = []
    last_end_index = 0
    last_tag_opened = False

    # So, we're basically going to go through this thang,
    # and if we find non-Greek, non-punctuation characters
    # before we hit the closing tag, we're gonna put in a
    # closing tag; it might create errors occasionally, but
    # we're DEFINITELY reducing errors overall
    for m in find_foreign.finditer(text):
        if m.group(3) == '<foreign':
            if last_tag_opened: # nested, or someone f'ed up
                from_last_opening = m.group(1)
                ng_match = find_nongreek.search(from_last_opening)
                if ng_match:
                    text_chunks.append(from_last_opening[:ng_match.start()])
                    text_chunks.append('</foreign>')
                    text_chunks.append(from_last_opening[ng_match.start():])
                else:
                    text_chunks.append(from_last_opening)
                    text_chunks.append('</foreign>')
                text_chunks.append(m.group(2))
                last_tag_opened = True
            else:
                text_chunks.append(m.group(0))
                last_tag_opened = True
        elif m.group(3) == '</foreign': # pretty much identical to above
            if last_tag_opened:
                text_chunks.append(m.group(0))
                last_tag_opened = False
            else:
                from_last_closing = m.group(1)
                ng_match = find_nongreek.search(from_last_closing)
                if ng_match:
                    text_chunks.append(from_last_closing[:ng_match.start()])
                    text_chunks.append('<foreign lang="greek">')
                    text_chunks.append(from_last_closing[ng_match.start():])
                else:
                    text_chunks.append(from_last_closing)
                    text_chunks.append('<foreign lang="greek">')
                text_chunks.append(m.group(2))
                last_tag_opened = False
        else:
            print >> sys.stderr, 'something is fubar in fix_foreign'
            print >> sys.stderr, m.group(0)
            sys.exit(1)
        last_end_index = m.end()
    text_chunks.append(text[last_end_index:])
    return ''.join(text_chunks)
 

find_entryFree = re.compile('.*?(<p>)[\s]*<entryFree[^>]*>', flags=re.S)
find_entryFree_div2 = re.compile('(.*?)</(entryFree|div2)>', flags=re.S)

def fix_entryFree(text):
    text_chunks = []
    last_end_index = 0

    #print len(find_entryFree.findall(text))

    for m in find_entryFree.finditer(text):
        begin_entryFree = m.end()
        closing_m = find_entryFree_div2.search(text[begin_entryFree:])
        text_chunks.append(m.group(0))
        # If entryFree not properly closed (i.e. closed by </div2>),
        # then comment out wrong closing tag and close properly
        if closing_m.group(2) == 'entryFree':
            text_chunks.append(closing_m.group(0))
        else:
            text_chunks.append(closing_m.group(1))
            text_chunks.append('<!--/div2-->')
            text_chunks.append('</entryFree>')

        # usually, the <p> tag "enclosing" the entryFree block isn't closed
        if re.search('<(/?p)[^>]*>', text[m.end(1):]).group(1) != '</p>':
            text_chunks.append('</p>')
        last_end_index = closing_m.end()
        print text[m.end()-80:m.end()+80]
    print 'appending last bit'
    text_chunks.append(text[last_end_index:])
    return ''.join(text_chunks)

def repair_entryFree(m):
    return m.group(1)+'<!--/div2--></entryFree></p>'

def fix_entryFree_stupid(text):
    return re.sub('(<p>[\s]*<entryFree.*?)</div2>', repair_entryFree, text)


def main():
    prog = sys.argv[0].split('/')[-1]
    usage = 'Usage: %s file ...' % prog
    files = sys.argv[1:]
    if not files:
        print >> sys.stderr, usage
        sys.exit(1)
    for f in files:
        print f,
        sys.stdout.flush()
        try:
            with open(f) as infh:
                text = infh.read()
        except IOError, e:
            print >> sys.stderr, '%s: warning: %s' % (prog, str(e))
            continue
        print 'fixing easy stuff...',
        sys.stdout.flush()
        text = fix_easy_problems(text)
        print 'fixing sense...',
        sys.stdout.flush()
        text = fix_sense(text)
        #newtext = fix_div2(text)
        print 'fixing foreign...',
        sys.stdout.flush()
        text = fix_foreign(text)
        print 'fixing entryFree...'
        text = fix_entryFree_stupid(text)
        try:
            with open(f+'.out','w') as outfh:
                print >> outfh, text
        except IOError, e:
            print >> sys.stderr, '%s: %s' % (prog, str(e))

if __name__ == '__main__':
    main()
