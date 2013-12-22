# -*- coding: utf-8 -*-
"""
Sample entry:

<div2 id="crossabaculus" type="entry" org="uniform" sample="complete">
  <head orig="Abacŭlus">Abaculus</head>
  <p> (Gr. <foreign lang="greek">ἀβακίσκος</foreign>), 
      diminutive of <ref type="cross" target="crossabacus">abacus</ref>
      (q. v.), and denoting a tile of marble, glass, etc.,
      used in making ornamental pavements. See
      <ref type="cross" target="crossmusivum-opus">Musivum Opus</ref>.
  </p>
</div2>
"""

import re, unicodedata as ud
from glob import glob

name = 'Harpers'
type = 'latin'
caps = 'uncapped'

# regex patterns    
find_head = re.compile('<head(.)*?/head>')
clean_head = re.compile('<[^<]+>|“|”')
find_entry = re.compile('<div2')
end_entry = re.compile('</div2>')
find_paren_head = re.compile('\(.*')
remove_parens = re.compile('\([^)]*\)')
lessen_ws = re.compile('[ ][ ]+')

dontsplit = ['certi, incerti', 'exhibendum', 'fabula palliata', 'greek, pronun',
             'ioppe, ioppa', 'ius, vocatio in', 'metal, art', 'salinator',
             'spartianus', 'strabo', 'sura, ']
             
def dosplit(head):
    for each in dontsplit:
        if each in head: return False
    return True

# Gets rid of diacritics and tags
def clean_headword(headword, content):
    headword = clean_head.sub('', headword).lower()
    newhead = u''
    for char in unicode(headword):
        charname = ud.name(char)
        if 'LATIN' in charname:
            newcharname = re.search('LATIN SMALL LETTER [\w]+', charname).group(0)
        else:
            newcharname = charname             
        newhead += ud.lookup(newcharname)
    newhead = re.sub('[;,]$', '', newhead)

    # Splits "leuci (albi) montes" into "leuci montes" and "albi montes", etc.
    if '(' in newhead:
        newhead2 = find_paren_head.search(newhead).group(0)
        newhead2 = newhead2.replace('(','').replace(')','')
        newhead = remove_parens.sub('', newhead)
        newhead = lessen_ws.sub(' ', newhead)
        newhead = [newhead, newhead2]
    # Splits all entries w/commas that are not names of people or in a certain list
    elif ',' in newhead and 'persName' not in content and dosplit(newhead):        
        newhead = newhead.split(',')
    # If a headword meets neither of the above req's, gets split by semicolon
    else:
        newhead = newhead.split(';')
    
    return newhead

# Strips unnecessary newlines, and exchanges <title> for <i>
def clean_content(content):
    content = re.sub('<title[^>]*>', '<i>', content) # <title> not rendered in Logeion
    content = content.replace('</title>', '</i>')
    content = content.strip('\n')

    return content

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/harpers_cls_ant*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    begin = False    
    for xmlfile in dico_data:        
        content = ''
        head_found = False        
        for line in open(xmlfile):
            if find_head.search(line) and begin and not head_found:
                head_match = re.search(find_head, line)
                head_found = True
                content += line
            elif find_entry.search(line):
                begin = True           
                content += line
            elif end_entry.search(line):
                try:
                    content += line
                    content = clean_content(content)
                    headword = clean_headword(head_match.group(0), content)                    
                    for head in headword:
                        attrs = {'head': head.lower().strip(), 'content': content}
                        dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], content[:50], e))
                (headword, content) = ('', '')
                begin = False
                head_found = False
            # If the line is right before a page break, a newline is put
            # in after a space; we want the whitespace, but not the newline
            elif not re.match('>$', line.rstrip()) and begin:
                content += line.rstrip('\n')
            elif begin:
                content += line
                    
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
    
    return dico, tobelogged
