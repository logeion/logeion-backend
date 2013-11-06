# -*- coding: utf-8 -*-
import re
from glob import glob

name = 'LSJ'
type = 'greek'
caps = 'precapped'

# regex patterns
find_head = re.compile('<head(.)*?/head>')
clean_head = re.compile('<[^<>]+>')
find_entry = re.compile('<div2')
find_pb = re.compile('<pb n="[0-9]*" /> <')
find_orth = re.compile('orth_orig="([^"]+)"')

# Remove unnecessary chars and tags
def clean_headword(headword, content):
    headword = clean_head.sub('', headword)
    headword = re.sub('[/!?\']', '', headword)
    headword = re.sub('·|,.+', '', headword)
    headword = re.sub('ὶ\.γ', 'ὶ γ', headword)
    
    if not re.search('^[^-]+$|-$', headword): # Removes non-terminal dash
        headword = headword.replace('-', '')
    if re.search('id="cross(\*[\w]"|koppa")', content): # Changes "Α α" to "Α", etc.
        headword = unicode(headword.replace(' ', ''))[0]
    
    return headword

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/greatscott*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:
        content = ''
        split_flag = False
        for line in open(xmlfile):
            if not (find_entry.search(line) or find_pb.search(line) or split_flag):
                continue
            content += line
            head_tags = find_head.search(content, re.S)
            
            if not re.search('[\n]*</div2>[\s]*', line):
                split_flag = True
                continue
            
            try:
                orth_orig = find_orth.search(head_tags.group(0))
                if orth_orig: orth_orig = orth_orig.group(1)
                content = content.strip('\n')
                headword = clean_headword(head_tags.group(0), content)
                attrs = {'head': headword, 'content': content, 'orth_orig': orth_orig}
                if not re.search('λέγω =.+?λέχω', headword) and re.search('<div2 id', content):
                    dico.append(attrs)
            except(Exception), e:
                tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s; (head_tags = %s, orth_orig = %s)" \
                % (xmlfile.split('/')[-1], content[:50], e, str(head_tags), str(orth_orig)))
            (headword, content) = ('', '')
            split_flag = False
            
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
  
    return dico, tobelogged
