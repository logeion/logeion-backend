# -*- coding: utf-8 -*-
import re
from glob import glob

name = 'Mastronarde'
type = 'sidebar'
caps = 'precapped'

# regex patterns
find_chapter = re.compile('^\([\d]+\)')
find_head = re.compile('^.+ ==')
find_mod = re.compile('\+ (gen\.|dat\.|acc\.|adv\.)|\+ subj\. or opt\.')
clean_chapter = re.compile('[()]')
clean_head = re.compile(' ==|\(.+?\)|[\[\]]')

def clean_headword(head):
    head = clean_head.sub('', head)
    if ',' in head: # pp's, mult. forms, etc.
        head = head.split(',')[0]
    if ' . ' in head: # Take out spaces separating periods in an ellipsis
        head = re.sub(' \. \. \.[ ]?', '...', head)
    if ' / ' in head: # Take out the spaces before and after a slash
        head = head.split(' / ')[0]+'/'+head.split(' / ')[1]    
    
    return head.strip()

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/mastro.*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}
    
    for xmlfile in dico_data:
        for line in open(xmlfile):
            if find_chapter.search(line):
                chapter = find_chapter.search(line).group(0)
                chapter = clean_chapter.sub('', chapter)
            else:
                try:
                    head = find_head.search(line).group(0)
                    if find_mod.search(head): # Gets "+ acc.", etc. off of forms
                        mod = find_mod.search(head).group(0)
                    else:
                        mod = ''
                    content = line.replace(head, '')
                    head = clean_headword(head)
                    content = content.strip()
                    if mod: content += ' (%s)' % mod
                    content = '%s, ' % head + content
                    head = head.split('/')
                    for each in head:
                        attrs = {'head': each, 'content': content, 'chapter': chapter}
                        dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], content[:50], e))                            
                (head, content, mod) = ('', '', '') # chapter isn't reset; it needs to carry over
    
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
        
    return dico, tobelogged
