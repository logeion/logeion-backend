# -*- coding: utf-8 -*-
import re
from glob import glob

name = 'PerseusEncyclopedia'
type = 'latin'
caps = 'source'

# regex patterns
find_head = re.compile('<head(.)*?/head>')
clean_head = re.compile("<[^<]+>|^'|'$")
find_entry = re.compile('<div1')
end_entry = re.compile('</div1>')

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/persencyc*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    begin = False   
    for xmlfile in dico_data:        
        content = ''
        for line in open(xmlfile):
            if find_head.search(line) and begin:                
                head_match = find_head.search(line)
                content += line
            elif find_entry.search(line):
                begin = True                
                content += line            
            elif end_entry.search(line):
                try:
                    content += line
                    headword = head_match.group(0)                
                    headword = clean_head.sub('', headword.strip())
                    headword = re.sub("^'|'$", '', headword)
                    if headword == '':
                        print headword,'\n'+content
                    content = content.strip('\n')      
                    attrs = {'head': headword, 'content': content}
                    dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], content[:50], e))                
                (headword, content) = ('', '')
                begin = False
            elif begin:
                content += line
                    
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, tobelogged
