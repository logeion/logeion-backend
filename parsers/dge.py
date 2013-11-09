# -*- coding: utf-8 -*-
from __future__ import with_statement
from BeautifulSoup import BeautifulStoneSoup
from glob import glob
import re

name = 'DGE'
type = 'greek'
caps = 'precapped'

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
    return head

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/*.xml'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:
        with open(xmlfile) as infh:
            soup = BeautifulStoneSoup(infh)
            for entry in soup.findAll('entry'):
                head = entry['xml:id']

                # Usually, the xml:id attr is more accurate, but it doesn't
                # distinguish between a dash and whitespace, so we take form
                if '-' in head:
                    try:
                        head = entry.find('form', rend='b').text
                    except(AttributeError):                    
                        pass
                    
                try:
                    head = cleanup_head(head)
                    attrs = {'head': head.strip(),
                             'content': str(entry).decode('utf-')}
                    dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], content[:50], e))
                    
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
        
    return dico, tobelogged
