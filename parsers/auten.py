# -*- coding: utf-8 -*-
"""
Sample entry:

      <div2 id="crossa)a/atos" orig_id="main" key="a)a/atos" opt="n">
        <head extent="full" lang="greek" opt="n" orig="ἀ-άᾱτος">ἀάατος</head>
        (<quote lang="greek">ἀϝάω</quote>): of doubtful meaning. —(1) 
        <gloss>inviolable</gloss>(if <quote lang="greek">α</quote>privative), 
        ...
      </div2>
"""

import re#, unicodedata
from glob import glob

name = 'Autenrieth'
type = 'greek'
caps = 'precapped'

# regex patterns
find_head = re.compile('<head(.)*?/head>')
clean_head_tags = re.compile('<head(.)*?>|</head>')
clean_head_syms = re.compile('[ ]?-[ ]?|（.+）|\.')
find_entry = re.compile('<div2')

'''
# Autenrieth uses circumflexes for long marks, so we remove most of them here
def remove_perispomeni(headword):
    index = 0
    headword = unicode(headword)
        for char in headword:
          	charname = unicodedata.name(char)
           	if re.search('PERISPOMENI', charname):
           		new_charname = re.sub(' AND PERISPOMENI', '', charname)
           		new_charname = re.sub(' PERISPOMENI AND', '', new_charname)
          		new_charname = re.sub(' WITH PERISPOMENI', '', new_charname)
           		newchar = unicodedata.lookup(new_charname)
           		headword = headword[:index]+newchar+headword[index+1:]
           	index += 1

    return headword
'''
# Cleans up headword, and splits it up into separate entries if sep by commas
def make_headword(headword):
    headword = clean_head_tags.sub('', headword)
    if 'βράχω' in headword: # For one exception in xml; change source?
        headword = re.sub('（|）', '', headword)        
    headword = headword.split(',')
    if '' in headword: headword.remove('')
    for x in range(len(headword)): 
        headword[x] = headword[x].strip()
        headword[x] = clean_head_syms.sub('', headword[x])
        
    return headword

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/homer_dico*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:
        for line in open(xmlfile):
            if not find_entry.search(line):
                continue            
            try:
                content = line.strip()
                head_tags = find_head.search(line)
                headword = make_headword(head_tags.group(0)) # Returns list     
                attrs = []
                for component in headword:
                    attrs.append({'head': component, 'content': content})
                dico.extend(attrs)
            except(Exception), e:
                tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                % (xmlfile.split('/')[-1], content[:50], e))
            headword, content = '', ''

        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, tobelogged
