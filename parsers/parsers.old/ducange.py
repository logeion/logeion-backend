# -*- coding: utf-8 -*-
import re
from glob import glob

name = 'DuCange'
type = 'latin'
caps = 'uncapped'

# regex patterns
find_head = re.compile('xml:id=".+?"')
find_head2 = re.compile('<form rend="b">.+?</form>')
clean_head = re.compile('xml:id=|"|<[/]?[^<>]*>|[0-9]')
find_entry = re.compile('<entry')
end_entry = re.compile('</entry>')
nested_ws = re.compile('^[ ][ ]+')

# Gets rid of unnecessary tags, spacing, and chars in headword
def cleanup_head(head):
    head = clean_head.sub('', head).lower()
    head = re.sub('^[\s]*[.]|[.][\s]*$', '', head)
    head = head.replace('Æ', 'ae')   
    
    return head    

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/*.xml'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    begin = False
    rendHead = False
        
    for xmlfile in dico_data:
        content = ''
        whitespace = ''
        for line in open(xmlfile):
            if find_entry.search(line):
                begin = True
                head = find_head.search(line).group(0)
                # Usually, the xml:id attr is more accurate, but it doesn't
                # distinguish between a dash and whitespace, so we take form                
                if '-' in head:
                    rendHead = True           
                whitespace = nested_ws.search(line).group(0)
                content += line
            elif rendHead and re.search('<form rend="b"', line):
                try:
                    head = find_head2.search(line).group(0)
                except(AttributeError):                    
                    pass
                rendHead = False
            elif begin:
                line = line.lstrip(whitespace)
                content += line
                
            if end_entry.search(line):
                try:
                    head = cleanup_head(head)
                    attrs = {'head': head.strip(), 'content': content}
                    dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], content[:50], e))
                (head, content) = ('', '')
                begin = False
                
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
        
    return dico, tobelogged
