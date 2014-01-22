# -*- coding: utf-8 -*-
"""
Sample entries:

ἀγαθός	2b	ἀγαθός ή όν, good, noble, courageous (adjective)
ἄγαλμα	18d	ἄγαλμα, τό, image, statue (noun)
ἀγγέλλω	19f	ἀγγέλλω, report, announce (verb)
ἄγγελος	17c	ἄγγελος, ὁ, messenger (noun)
"""
import re
from glob import glob

name = 'JACT'
type = 'sidebar'
caps = 'precapped'

def parse(dico_path):
    xmlfile = dico_path+'/jact.dat'
    dico = []
    tobelogged = {'warning': [], 'info': []}
    
    for line in open(xmlfile):
        head, chapter, content = line.strip().split('\t')
        attrs = {'head': head, 'chapter': chapter, 'content': content}
        dico.append(attrs)
    tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
    return dico, tobelogged
