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

def parse(dico_path, log, log_error):
    xmlfile = dico_path+'/mastro.dat'
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
