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

def parse(dico_path, log, log_error):
    xmlfile = dico_path+'/jact.dat'
    dico = []
    errors_occurred = False
    
    for line in open(xmlfile):
        try:
            head, chapter, content = line.strip().split('\t')
            attrs = {'head': head, 'chapter': chapter, 'content': content}
            dico.append(attrs)
        except(Exception), e:
            log_error("%s couldn't parse line \"%s\"...: %s" \
                % (xmlfile.split('/')[-1], str(entry).decode('utf-8')[:50], str(e)))
            errors_occurred = True
    log('%s finished parsing' % xmlfile.split('/')[-1])
    return dico, errors_occurred
