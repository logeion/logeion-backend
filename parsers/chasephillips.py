# -*- coding: utf-8 -*-
"""
Sample entry:

ἀγαθός	ἀγαθή, ἀγαθόν	noble, good	3
"""

from __future__ import with_statement
from glob import glob

name = 'ChasePhillips'
type = 'sidebar'
caps = 'precapped'
convert_xml = False

# Main method
def parse(dico_path, log, log_error):
    # dico_path will point to the parent directory of your files;
    # grab your files accordingly
    dico_data = sorted(glob(dico_path+'/C&P.txt'))
    dico = []
    errors_occurred = False
    
    for xmlfile in dico_data:
        with open(xmlfile) as infh:
            for row in infh:
                try:
                    cols = row.strip().split('\t')
                    head, chapter = cols[0], cols[-1]
                    if head != 'headword':
                        dico.append({'head': cols[0],
                                     'content': '',
                                     'chapter': chapter})
                except(Exception), e:
                    log_error("%s couldn't parse line \"%s\"...: %s" \
                        % (xmlfile.split('/')[-1], str(entry).decode('utf-8')[:50], str(e)))
                    errors_occurred = True
    log('%s finished parsing' % xmlfile.split('/')[-1])
        
    return dico, errors_occurred 
