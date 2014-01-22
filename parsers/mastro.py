# -*- coding: utf-8 -*-
"""
Sample entries:

ἀγαθός	7	ἀγαθός, good, well-born, brave
ἄγαν	33	ἄγαν, very much; too much
ἀγγέλλω	19	ἀγγέλλω, bear a message, announce, report
ἄγγελος	3	ἄγγελος, messenger, herald
"""
import re
from glob import glob

name = 'Mastronarde'
type = 'sidebar'
caps = 'precapped'

def parse(dico_path):
    xmlfile = dico_path+'/mastro.dat'
    dico = []
    tobelogged = {'warning': [], 'info': []}
    
    for line in open(xmlfile):
        head, chapter, content = line.strip().split('\t')
        attrs = {'head': head, 'chapter': chapter, 'content': content}
        dico.append(attrs)
    tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
    return dico, tobelogged
