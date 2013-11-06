import re
from glob import glob

name = 'HansenQuinn'
type = 'sidebar'
caps = 'precapped'

def parse(dico_path):
    xmlfile = dico_path+'/hq.dat'
    dico = []
    tobelogged = {'warning': [], 'info': []}
    
    for line in open(xmlfile):
        head, chapter, content = line.strip().split('\t')
        attrs = {'head': head, 'chapter': chapter, 'content': content}
        dico.append(attrs)
    tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
    return dico, tobelogged
