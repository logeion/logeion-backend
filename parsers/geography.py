# -*- coding: utf-8 -*-
"""
Sample entry:

<div2 type="entry" id="abae-geo" org="uniform" sample="complete">
  <head orig="ABAE">ABAE</head>
  <p>
    <label>ABAE</label>(<label lang="greek">Ἄβαι</label>. 
    <title>Eth.</title><label lang="greek">Ἀβαῖος</label>: 
    near <label>Exarkhó</label>, Ru.), 
    an ancient town of Phocis, near the frontiers of the ...
  </p>
</div2>
"""

import re
from glob import glob

name = 'Geography'
type = 'latin'
caps = 'precapped'

# regex patterns
find_head = re.compile('<label( lang="la")?')
get_head = re.compile('<label(.)*?>(.)*?</label>')
clean_head = re.compile('<label(.)*?>|<p>|</label>| \(<label|´')
find_entry = re.compile('<div2 type="entry"')
end_entry = re.compile('/div2>')

# Removes leading and trailing chars, etc.  
def clean_headword(headword):
    headword = clean_head.sub('', headword)
    headword_parts = headword.split()                
    for each in headword_parts:
        headword_parts[headword_parts.index(each)] = each[0]+each[1:].lower()
                    
    return ' '.join(headword_parts).strip()
                    
# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/geo_dico*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}
    
    begin = False
    label_found = False
    
    for xmlfile in dico_data:        
        content = ''
        for line in open(xmlfile):
            if find_head.search(line) and begin and not label_found:                
                head_match = get_head.search(line)
                label_found = True
            
            if find_entry.search(line):
                begin = True
                content += line          
            elif re.match('<pb',line.lstrip(' ')):
                pass
            elif end_entry.search(line):
                try:
                    content = (content+line).strip()
                    headword = clean_headword(head_match.group(0))
                    attrs = {'head': headword, 'content': content}
                    dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], content[:50], e))
                (headword, content) = ('', '')
                begin = False
                label_found = False
            elif begin:
                content += line
                    
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
    
    return dico, tobelogged
