# -*- coding: utf-8 -*-
"""
Sample entry:

<div2 id="crossa^vus" orig_id="n1666" key="a^vus">
  <head extent="full" lang="la" opt="n" orth_orig="avus">avus</head>ī,
  <gen opt="n">m</gen>
  <sense id="n1666.0" level="0" n="0" opt="n">
    <etym lang="la" opt="n">1 AV-</etym>,
    <i><i>a grandfather</i></i>: <foreign lang="la">huius: maternus</foreign>,
    <usg opt="n">L.</usg>—Of bees, <i><i>a grandsire</i></i>,
    <usg opt="n">V.</usg>—<i><i>An ancestor, forefather</i></i>:
    <foreign lang="la">paternus</foreign>, <usg opt="n">H.</usg>:
    <foreign lang="la">avi atavique</foreign>, <usg opt="n">V.</usg>
  </sense>
</div2>
"""
import re
from glob import glob

name = 'Lewis'
type = 'latin'
caps = 'source'
convert_xml = True

# regex patterns
find_head = re.compile('<head.*?/head>', flags=re.S)
clean_head = re.compile('<head[^>]*>|</head>')
#find_entry = re.compile('<div2')
find_entry = re.compile('<div2.*?</div2>', flags=re.S)
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
        for entry_m in find_entry.finditer(open(xmlfile).read()):
            try:
                entry = entry_m.group(0)
                head_tags = find_head.search(entry)
                orth_orig = find_orth.search(head_tags.group(0))
                if orth_orig: orth_orig = orth_orig.group(1) # Either result of match or None
                headword = clean_headword(head_tags.group(0))
                content = entry.strip()
                attrs = {'head': headword, 'content': content, 'orth_orig': orth_orig}
                dico.append(attrs)
            except(Exception), e:
                content = line
                tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                % (xmlfile.split('/')[-1], content[:50], e))

            (headword, content) = ('', '')

        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, tobelogged
