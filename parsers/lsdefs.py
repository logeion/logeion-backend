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

def parse(dico_path):
    #dico_data = sorted(glob(dico_path+'/LatinShortDefs*'))
    xmlfile = dico_path+'/shortdefs.dat'
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for line in open(xmlfile):
        try:
            head, content = line.strip().split('\t')
            content = re.sub(':$', '', content.strip())
            attrs = {'head': head, 'content': content}
            dico.append(attrs)
        except(Exception), e:
            tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
            % (xmlfile.split('/')[-1], content[:50], e))
    tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
    dico = sorted(dico, key=lambda e: e['head'])
    return dico, tobelogged
