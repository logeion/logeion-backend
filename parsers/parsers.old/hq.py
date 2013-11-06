# -*- coding: utf-8 -*-
import re, unicodedata as ud
from glob import glob

name = 'HansenQuinn'
type = 'sidebar'
caps = 'precapped'

split = ['οὐ, οὐκ, οὐχ', 'εἷς, μία, ἕν', 'ἐκ, ἐξ', 'οὕτω, οὕτως', 
         'τίς, τί ', 'τις, τι', 'τρεῖς, τρία']

# Cheap function that determines if a head is a certain entry
def insplit(head):
    for each in split:
        if each in head: return True
    return False    

# Removes excess chars and tags, and splits headwords into separate
# entries where appropriate
def cleanup(head):
    head = unicode(head)
    newhead = ''
    for char in head:
        charname = ud.name(char)
        newcharname = charname.replace(' WITH MACRON', '')
        newchar = ud.lookup(newcharname)
        newhead += newchar

    if not insplit(newhead): # Takes x of "x, y, z, ..." for headword
        try:
            newhead = [newhead.split(',')[0]]
        except(IndexError):
            newhead = newhead.split(',')
    else: # Takes x, y, and z as separate headwords
        newhead = newhead.split(',')        

    if len(newhead) == 1 and re.search('[()]', newhead[0]):
        newhead[0] = re.sub('\(.*', '', newhead[0])

    return newhead

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/HQvocab'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:
        for line in open(xmlfile):
            try:
                (head, content, chapter) = line.split('\t')
                content = '%s, %s' % (head, content)
                head = cleanup(head)
                for each in head:
                    attrs = {'head': each.strip(), 'content': content, 'chapter': chapter}
                    dico.append(attrs)
            except(Exception), e:
                tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                % (xmlfile.split('/')[-1], content[:50], e))

        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, tobelogged
