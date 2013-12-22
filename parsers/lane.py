# -*- coding: utf-8 -*-
"""
Sample entry:

<LENTRY nummer="2756" id="avocamentum">
  <METALEX>
    <LCANON volg=""><ITEM>avocamentum</ITEM></LCANON>
    <LCAT><ITEM>sub</ITEM></LCAT>
    <CORP><ITEM>postklass.</ITEM></CORP>
  </METALEX>
  <VET>&amacron;voc&amacron;mentum, </VET>
  <NORMAAL taal="JJ">&imacron; </NORMAAL>
  <CURSIEF taal="JJ">n (avoco) (postklass.) </CURSIEF>
  <NORMAAL taal="NL">verstrooiing, afleiding.</NORMAAL>
</LENTRY>
"""

import re, htmlentitydefs as hed
from glob import glob

name = 'LaNe'
type = 'latin'
caps = 'precapped'

# regex patterns
find_entries = re.compile('<LENTRY.*?</LENTRY>', re.S)
find_head = re.compile('id="(.*?)"')
strip_head = re.compile('_x$|[0-9]')

# Tags to be deleted/switched with other tags in cleanup
tag_switch = {'<CURSIEF[^>/]*>': '<i>'}
tag_delete = ['<VET>', '<HALFVET>', '<NORMAAL[^>]*>', '<ADDINFO>', '<GOTO[^>]*>', '<CURSIEF[^>]*/>']
tag_delete_entire = ['<METALEX>[^<]*</METALEX>']

# Add closing tags
tag_switch.update(map(lambda x: map(lambda x: x[0]+'/'+x[1:], x), tag_switch.items()))
tag_delete.extend(map(lambda x: x[0]+'/'+x[1:], tag_delete))

tag_delete.extend(tag_delete_entire)
tag_switch.update(map(lambda x: (x,''), tag_delete))

# Uses tag_switch to swap out Dutch tags with standard ones, or delete them entirely
def cleanup(read_in):
    read_in = read_in.decode('utf-8')
    for key in tag_switch.keys():
        read_in = re.sub(key, tag_switch[key], read_in)

    return read_in

# Strips off various chars: numbers, underscores, and trailing "..._x"
def clean_head(head):
    new_head = strip_head.sub('', head)
    new_head = new_head.replace('_', ' ')
    return new_head.strip()

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/TopResBoek.xml'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:
        read_in = open(xmlfile).read()
        read_in = cleanup(read_in)
        entries = find_entries.findall(read_in)
        for entry in entries:
            try:
                head = find_head.search(entry).group(1)
                head = clean_head(head)
                attrs = {'head': head, 'content': entry}
                dico.append(attrs)
            except(Exception), e:
                tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                % (xmlfile.split('/')[-1], entry[:50], e))
            head = ''

        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, tobelogged
