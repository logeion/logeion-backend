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

def parse(dico_path, log, log_error):
    xmlfile = dico_path+'/shortdefs.dat'
    dico = []
    errors_occurred = False
    
    for line in open(xmlfile):
        try:
            head, content = line.strip().split('\t')
            attrs = {'head': head, 'content': content}
            dico.append(attrs)
        except(Exception), e:
            log_error("%s couldn't parse line \"%s\"...: %s" \
                % (xmlfile.split('/')[-1], str(entry).decode('utf-8')[:50], str(e)))
            errors_occurred = True
    log('%s finished parsing' % xmlfile.split('/')[-1])
    dico = sorted(dico, key=lambda e: e['head'])
    return dico, errors_occurred
