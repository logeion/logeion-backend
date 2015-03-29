# -*- coding: utf-8 -*-
"""
Sample entry:

<div1 id="crossa)/atos1" orig_id="n3" key="a)/atos1">
  <p />
  <head extent="full" lang="greek" opt="n" orth_orig="a)/atos">ἄατος</head>
  <etym opt="n"><foreign lang="greek">ἄω</foreign> C</etym>
  <sense level="0" n="0" id="n3.0" opt="n">
    <trans opt="n"><i>insatiate</i></trans>,
    c. gen., <foreign lang="greek">Ἄρης ἆτος πολέμοιο</foreign>
    <usg opt="n">Il.</usg>
  </sense>
</div1>
"""
import re
from glob import glob

name = 'MiddleLiddell'
type = 'greek'
caps = 'precapped'
convert_xml = True

# regex patterns
find_head = re.compile('<head(.)*?/head>')
clean_head = re.compile('<head(.)*?>|</head>|[0-9]')
find_entry = re.compile('<div1')
end_entry= re.compile('</div1>')

def clean_headword(headword):
    headword = clean_head.sub('', headword)
    if not re.search('-$', headword):
        headword = re.sub('-', '', headword)
    headword = headword.split(',')
        
    return headword
    

# Main method
def parse(dico_path, log, log_error):
    dico_data = sorted(glob(dico_path+'/middleLiddell*'))
    dico = []
    errors_occurred = False
        
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
                    headword = clean_headword(head_match.group(0))
                    
                    content = content.strip('\n')
                    for head in headword:
                        attrs = {'head': head.strip(), 'content': content}
                        dico.append(attrs)
                except(Exception), e:
                    log_error("%s couldn't parse line \"%s\"...: %s" \
                        % (xmlfile.split('/')[-1], content[:50], e))
                    errors_occurred = True
                (headword, content) = ('', '')
                begin = False
                head_found = False
            elif begin:
                content += line
                    
        log('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, errors_occurred
