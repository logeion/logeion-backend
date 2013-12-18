# -*- coding: utf-8 -*-
from __future__ import with_statement
from BeautifulSoup import BeautifulStoneSoup
from glob import glob
import re

name = 'DGE'
type = 'greek'
caps = 'precapped'

# regex patterns
clean_head = re.compile('xml:id=|"|<[/]?[^<>]*>|[0-9]')
find_entry = re.compile('<entry.*?</entry>', re.S)

# Gets rid of unnecessary tags, spacing, and chars in headword
def cleanup_head(head):
    head = clean_head.sub('', head)
    head = re.sub('^[\s]*[.]|[.][\s]*$', '', head)
    head = head.replace('_', ' ')
    return head

# Does any relevant search-replace within the whole entry
def cleanup_entry(entry):
    return entry.replace('<num>;</num>', '<num>•</num>')

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
                orth_orig = entry.find('orth', type='lemma').text

                # Usually, the xml:id attr is more accurate, but it doesn't
                # distinguish between a dash and whitespace, so we take form
                if '-' in head:
                    try:
                        head = entry.find('form', rend='b').text
                    except(AttributeError):                    
                        pass
                    
                try:
                    head = cleanup_head(head)
                    entry = cleanup_entry(str(entry))
                    attrs = {'head': head.strip(),
                             'orth_orig': orth_orig.strip().decode('utf-8'),
                             'content': entry.decode('utf-8')}
                    dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], str(entry)[:50], e))
                    
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
        
    return dico, tobelogged
