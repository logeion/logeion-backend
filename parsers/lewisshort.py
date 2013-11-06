from __future__ import with_statement
from glob import glob
import re

name = 'LewisShort'
type = 'latin'
caps = 'source'

# regex patterns
#is_meta = re.compile('[\s]*<[?][\s]*xml')
find_head = re.compile('<head(.)*?/head>')
clean_head = re.compile('<head(.)*?>|</head>')
clean_headorth = re.compile('<orth(.)*?>|</orth>')
find_entry = re.compile('<div1')
find_pb = re.compile('<pb n="[0-9]*" /> <')
find_orth = re.compile('orth_orig="([^"]+)"')

# Remove unnecessary chars, charrefs, and tags, and changes j's to i's
def clean_headword(headword):
    headword = clean_head.sub('', headword)            
    headword = re.sub('[/!?\']|lig;| \(Rheg', '', headword)           
    headword = re.sub('cardu \.s', 'cardu.s', headword)
    headword = re.sub('j', 'i', headword)            
  
    # Checks for a rare exception in the html structure
    if re.match('<orth|/orth', headword):
        headword = clean_headorth.sub('', headword)
        
    return headword

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/latindico*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:    
        content = ''
        split_flag = False 

        # Currently goes line-by-line; this doesn't make much sense, so I'm going
        # to switch it over to entry-by-entry via regex soon enough (once I can
        # code a version that doesn't miss several megabytes of info) - MS
        with open(xmlfile) as infh:
            for line in infh:#open(xmlfile):
                if line.find('<?xml') >= 0 or not (find_entry.search(line) or find_pb.search(line) or split_flag):
                    continue
                content += line
                head_tags = find_head.search(content, re.S)
                orth_orig = find_orth.search(head_tags.group(0))
                
                if not re.search('[\n]*</div1>[\s]*', line):
                    split_flag = True
                    continue
                    
                try:
                    headword = clean_headword(head_tags.group(0))
                    """
                    if orth_orig is None:
                        orth_orig = headword
                    else:
                    """
                    orth_orig = orth_orig.group(1)
                    content = content.strip('\n')
                    attrs = {'head': headword, 'content': content, 'orth_orig': orth_orig}
                    dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], content[:50], e))
                (headword, content) = ('', '')
                split_flag = False
               
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
  
    return dico, tobelogged
