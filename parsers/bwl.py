# -*- coding: utf-8 -*-
"""
Sample entry:

<term date="8/17/2006" editinglevel="3" editor="Sara Koerber" 
      id="id2379614" lemma="abdo" rev="9" time="10:56:43">
<defs>
  <en>to hide, conceal</en>
</defs>
<exs>
  <ex>
    <english>he hid himself within Apulia</english>
    <latin>penitus in Apuliam se abdidit</latin>
  </ex>
</exs>
<locked>no</locked>
<pos>
  <class>verb</class>
  <extra>-dere, -didi, -ditum</extra>
  <poetic>no</poetic>
  <type>3rd (-ere)</type>
</pos>
<revcomment>This is a test.</revcomment>
<uncertain>yes</uncertain>
<xrefs>
  <LTRL/>
  <Wheelock/>
</xrefs>
</term>
"""

import re, unicodedata as ud
from glob import glob

name = 'BWL'
type = 'latin'
caps = 'precapped'

# regex patterns
head_flag = re.compile('<term ')
find_head = re.compile('lemma=".+?"')
clean_head = re.compile('lemma=|"')
ex_flag = re.compile('<exs>')    
find_ex = re.compile('<latin>.+?</latin>')
clean_ex = re.compile('<latin>|</latin>')
end_flag = re.compile('</term>')

diacr = {u'ā': u'a', u'ē': u'e', u'ë': u'e', u'ī': u'i', u'ō': u'o', u'ū': u'u'}

# Deletes macrons and other diacritical marks
def clean_diacr(head):
    head = unicode(head)
    newhead = ''
    for char in head:
        try:
            newhead += diacr[char]
        except(KeyError):
            newhead += char
    newhead = re.sub('[\s]*\.\.\.[\s]*', '...', newhead)
    newhead = re.sub('\([^)]*\)', '', newhead)
    if ' or ' in newhead:
        newhead = newhead.split(' or ')
    if not isinstance(newhead, list):
        newhead = str(newhead).split(',') 
    
    return newhead

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/latin_vocab.xml'))
    dico = []
    tobelogged = {'warning': [], 'info': []}    

    begin_exs = False
    exs = []
    content = ''
    for xmlfile in dico_data:
        for line in open(xmlfile):
            if head_flag.search(line): # Finds line denoting beginning of entry
                head = find_head.search(line).group(0)
                head = clean_head.sub('', head)
            elif ex_flag.search(line): # Finds section of entry containing examples
                begin_exs = True
            elif find_ex.search(line) and begin_exs: # Finds and gets examples
                this_ex = find_ex.search(line).group(0)
                exs.append(clean_ex.sub('', this_ex))
            elif end_flag.search(line) and exs: # End of entry; load lemma and examples
                try:
                    head = clean_diacr(head)
                    for ex in exs:
                        content += '<sense>%s</sense>\n' % ex
                    for each in head:
                        attrs = {'head': each.strip(), 'content': content.strip()}
                        dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], content[:50], e))
                (head, content, exs) = ('', '', [])
                begin_exs = False
        
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
    
    return dico, tobelogged
