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

def parse(dico_path, log, log_error):
    xmlfile = dico_path+'/ltrg.dat'
    dico = []
    errors_occurred = False
    
    for line in open(xmlfile):
        try:
            head, chapter = line.strip().split('\t')
            attrs = {'head': head, 'chapter': chapter, 'content': None}
            dico.append(attrs)
        except(Exception), e:
            log_error("%s couldn't parse line \"%s\"...: %s" \
                % (xmlfile.split('/')[-1], str(entry).decode('utf-8')[:50], str(e)))
            errors_occurred = True
    log('%s finished parsing' % xmlfile.split('/')[-1])
    return dico, errors_occurred
