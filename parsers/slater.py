# -*- coding: utf-8 -*-
import re
from glob import glob

name = 'Slater'
type = 'greek'
caps = 'precapped'

# regex patterns
find_head = re.compile('<head(.)*?</head>')
clean_head = re.compile('<head(.)*?>|</head>|[\[\]]')
find_entry = re.compile('<div2')
end_entry = re.compile('</div2>')
find_orth = re.compile('orth_orig="([^"]+)"')

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/pindar_dico*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}
    
    content = ''
    begin = False
    for xmlfile in dico_data:
        for line in open(xmlfile):
            if find_entry.search(line):
                begin = True
                headword = find_head.search(line).group(0)
                orth_orig = find_orth.search(headword)
                if orth_orig: orth_orig = orth_orig.group(1)
                content += line
            elif begin:
                content += line
        
            if end_entry.search(line):
                try:
                    headword = clean_head.sub('', headword)
                    headword = re.sub('<[^<]+>', '', headword)    
                    content = content.strip('\n')
                    headword = headword.split(';')
                    for head in headword:
                        head = head.split(',')
                        if '' in head:
                            head.remove('')
                        for each in head: # Splits along commas, but ditches endings
                            if not '-' in each and each.strip() not in ('τό','ὁ'):
                                if not re.search('ς ', each):
                                    each = re.sub('[\']?[ ][\]]?', '', each, re.U) 
                                attrs = {'head': each.strip(), 'content': content.strip()}
                                dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], content[:50], e))
                
                (headword, content) = ('', '')
                begin = False
                
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, tobelogged
