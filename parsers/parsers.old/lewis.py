# -*- coding: utf-8 -*-
import re
from glob import glob

name = 'Lewis'
type = 'latin'
caps = 'source'

# regex patterns
find_head = re.compile('<head(.)*?/head>')
clean_head = re.compile('<head(.)*?>|</head>')
find_entry = re.compile('<div2')
find_orth = re.compile('orth_orig="([^"]+)"')

# Removes diacritics, xml tags, etc.
def clean_headword(headword):
    headword = clean_head.sub('', headword)
    headword = re.sub('Ē', 'E', headword)
    headword = re.sub('ē', 'e', headword)
    headword = re.sub('ī', 'i', headword)
    headword = re.sub('ū', 'u', headword)
    headword = re.sub("'", '', headword)

    return headword

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/smalllatindico*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}    

    for xmlfile in dico_data:
        for line in open(xmlfile):
            if not find_entry.search(line):
                continue
            try:
                head_tags = find_head.search(line)
                orth_orig = find_orth.search(head_tags.group(0))
                if orth_orig: orth_orig = orth_orig.group(1) # Either result of match or None
                headword = clean_headword(head_tags.group(0))
                content = line.strip()
                attrs = {'head': headword, 'content': content, 'orth_orig': orth_orig}
                dico.append(attrs)
            except(Exception), e:
                content = line
                tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                % (xmlfile.split('/')[-1], content[:50], e))

            (headword, content) = ('', '')

        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, tobelogged
