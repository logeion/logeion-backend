# -*- coding: utf-8 -*-
"""
Sample entries:

ἀγαθός	2
ἀγορά	1
ἄγω	5
ἀγών	6
"""

import re
from glob import glob

name = 'LTRG'
type = 'sidebar'
caps = 'precapped'

def parse(dico_path):
    xmlfile = dico_path+'/ltrg.dat'
    dico = []
    tobelogged = {'warning': [], 'info': []}
    
    for line in open(xmlfile):
        head, chapter = line.strip().split('\t')
        attrs = {'head': head, 'chapter': chapter, 'content': None}
        dico.append(attrs)
    tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
    return dico, tobelogged
