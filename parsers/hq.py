# -*- coding: utf-8 -*-
"""
Sample entries:

ἀγαθός	4	ἀγαθός, ἀγαθή, ἀγαθόν, good
ἀγγέλλω	10	ἀγγέλλω, ἀγγελῶ, ἤγγειλα, ἤγγελκα, ἤγγελμαι, ἠγγέλθην, announce
ἄγγελος	2	ἄγγελος, ἀγγέλου, ὁ, messenger
ἀγορά	1	ἀγορά, ἀγορᾶς, ἡ, marketplace
"""

import re
from glob import glob

name = 'HansenQuinn'
type = 'sidebar'
caps = 'precapped'

def parse(dico_path, log, log_error):
    xmlfile = dico_path+'/hq.dat'
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
