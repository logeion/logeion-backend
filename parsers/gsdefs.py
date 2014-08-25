# -*- coding: utf-8 -*-
"""
Sample entries:

ἀάατος	not to be injured, inviolable
ἀαγής	unbroken, not to be broken, hard, strong
ἄαδα	unpleasant
ἀάζω	breathe with the mouth wide open
"""

import re
from glob import glob

name = 'GreekShortDefs'
type = 'greek'
caps = 'precapped'
convert_xml = False

def parse(dico_path):
    xmlfile = dico_path+'/shortdefs.dat'
    dico = []
    tobelogged = {'warning': [], 'info': []}
    
    for line in open(xmlfile):
        head, content = line.strip().split('\t')
        attrs = {'head': head, 'content': content}
        dico.append(attrs)
    tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
    dico = sorted(dico, key=lambda e: e['head'])
    return dico, tobelogged
