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
def parse(dico_path):
    # dico_path will point to the parent directory of your files;
    # grab your files accordingly
    dico_data = sorted(glob(dico_path+'/C&P.txt'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:
        with open(xmlfile) as infh:
            for row in infh:
                cols = row.strip().split('\t')
                head, chapter = cols[0], cols[-1]
                if head != 'headword':
                    dico.append({'head': cols[0],
                                 'content': '',
                                 'chapter': chapter})
    tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
        
    return dico, tobelogged
