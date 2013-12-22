"""
Sample entries:

amo,  amare,  amavi,  amatum	to love,  like	1
amabo te	please	1
cogito,  cogitare,  cogitavi,  cogitatum	to think,  ponder,  consider,  plan	1
debeo,  debere,  debui,  debitum	to owe;  ought,  must,  should	1
do,  dare,  dedi,  datum	to give,  offer	1
"""

import re
from glob import glob

name = 'Wheelock'
type = 'sidebar'
caps = 'precapped'

split = ['neque ,', 'atque', 'aliquis', 'quisquis', 're-', 'maior,']

# Cheap function that determines if a head is a certain entry
def insplit(head):
    for each in split:
        if each in head: return True
    return False

# Removes unnecessary chars from head, and splits it into separate entries
# where appropriate
def cleanup_head(head):
    head = head.replace('?', '')
    head = re.sub('\([^)]*\)|^-', '', head)
    head = re.sub('[ ][ ]+', ' ', head)
    # Splits for "qui, quae, quod" and those entries found by split
    if head == 'quis quid':
        head = head.split(' ')
    elif not re.search('^qui,', head) and not insplit(head):
        try:
            head = [head.split(',')[0]]
        except(IndexError):
            head = head.split(',')
    else:        
        head = head.split(',')        

    return head

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/Wheelockvocab*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:
        for line in open(xmlfile):
            try:
                (head, content, chapter) = line.split('\t')
                content = '%s, %s' % (head, content)
                head = cleanup_head(head)
                for each in head:
                    attrs = {'head': each.strip(), 'content': content, 'chapter': chapter}
                    dico.append(attrs)
            except(Exception), e:                
                tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                % (xmlfile.split('/')[-1], line[:50], e))

        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, tobelogged
