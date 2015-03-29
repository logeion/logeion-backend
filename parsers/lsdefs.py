"""
Sample entries:

ab	from, away from, out of
abactus	driven away, driven off
abacus	 a table of precious material for the display of plate
abalienatio	a transfer of property, sale, cession
"""
from glob import glob
import re

name = 'LatinShortDefs'
type = 'latin'
caps = 'source'
convert_xml = False

def parse(dico_path, log, log_error):
    xmlfile = dico_path+'/shortdefs.dat'
    dico = []
    errors_occurred = False

    for line in open(xmlfile):
        try:
            head, content = line.strip().split('\t')
            content = re.sub(':$', '', content.strip())
            attrs = {'head': head, 'content': content}
            dico.append(attrs)
        except(Exception), e:
            log_error("%s couldn't parse line \"%s\"...: %s" \
                % (xmlfile.split('/')[-1], content[:50], e))
            errors_occurred = True
    log('%s finished parsing' % xmlfile.split('/')[-1])
    dico = sorted(dico, key=lambda e: e['head'])
    return dico, errors_occurred 
