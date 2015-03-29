# -*- coding: utf-8 -*-
"""
Sample entries:

<item id="_2">
 <cat>1</cat>
 <Q>ager</Q>
 <A>agrī, m.
field</A>
</item>
<item id="_2.tr.1">
 <cat>1</cat>
 <Q>field</Q>
 <A>ager
agrī, m.</A>
</item>
"""

import re, unicodedata as ud
from glob import glob

name = 'LTRL'
type = 'sidebar'
caps = 'precapped'

# regex patterns   
clean_content = re.compile(u'<Q>|</Q>')
clean_head = re.compile(u'<A>|</A>')
find_chpt = re.compile(u'<cat>.+</cat>')
clean_chpt = re.compile(u'<cat>|</cat>')

# Assigns the correct chapter number to the entries with chapter 0
chapter_zero = \
    {'2': ['A.', 'Aeneas', 'Apollo', 'App.', 'C.', 'Catilina', 'Catullus', 'Cn.',
	       'D.', 'Ilium', 'L.', 'L. Sergius Catilina', 'Livia', 'M.', 'M’', 'P.',
	       'Q.', 'Ser.', 'Sex.', 'Sp.', 'T.', 'Ti.', 'Troia'],
	'6': ['Caesar', 'Cato', 'Ceres', 'Cicero', 'Cupido', 'Dido', 'Dis', 'divinus',
	       'divus', 'Hannibal', 'Iuno', 'Iuppiter', 'Latinus', 'Mars', 
	       'P. Vergilius Maro', 'Venus'],
	'7': ['herc(u)le', 'mehercule', 'mehercules', 'salus', 'salutem dicere', 'salve',
	       'salvete', 'vale', 'valete', 'valeo', 'ecce', 'heu', 'valde'],
       '10': ['centesimus', 'centum', 'decimus', 'duo', 'mille', 'milia', 'millesimus',
	       'nonus', 'novem', 'octavus', 'octo', 'primus', 'quartus', 'quattuor',
	       'quinque', 'quintus', 'secundus', 'septem', 'septimus', 'sex', 'sextus', 
	       'tertius', 'tres', 'tria'],
       '13': ['eo', 'hic', 'hinc', 'hinc… hinc/illinc…', 'huc', 'ibi', 'illic', 'illinc', 
	       'illuc', 'inde']}

for key in chapter_zero:
    chapter_zero[key] = [l.decode('utf-8') for l in chapter_zero[key]]

tosplit = [u'is ea id', u'hic haec hoc', u'qui quae quod', u'quis quid', u'maior maius',
         u'melior melius', u'minor minus', u'peior peius', u'prior prius', u'tres tria']

tonotsplit = [u'hinc/', u'gratiam/', u'plus/', u'sed/', u'neque/', u'quam ob', u'patres ',
              u'poenas ', u'vela ', u'bellum ', u'causam ', u'consilium ', u'se ferre',
              u'res ', u'legem ', u'opus ', u'orationem ', u'castra ', u'se eicere',
              u'male velle', u'se conferre', u'orbis ', u'salutem ', u'quo modo',
              u'prima ', u'bene velle', u'gratias ', u'quam primum', u'.', u'…', u';']
               
# Cheap functions, but more accurate than simply "newhead in tosplit", etc.
def dosplit(head):
    for each in tosplit:
        if each in head: return True
    return False

def dontsplit(head):
    for each in tonotsplit:
        if each in head: return False
    return True
    
# Gets rid of excess tags, chars, and diacritical marks, and splits
# headwords into separate entries where appropriates
def clean_headword(line, content):
    head = clean_head.sub('', line).strip()
    content = u'%s, %s' % (head, content)
    head = re.sub(u' -a -um', '', head)    
    head = re.sub(u'^(-)|_|—', '', head).lstrip()
    head = re.sub(u' \([^)]+\)$', '', head)
 
    newhead = ''
    for char in head:
        charname = ud.name(char)
        if 'LATIN' in charname:
            newcharname = re.search('LATIN (CAPITAL|SMALL) LETTER [\w]+', charname).group(0)
        else:
            newcharname = charname
        newhead += ud.lookup(newcharname)
        
    assert isinstance(newhead, unicode)
    #newhead = newhead.decode('utf-8')
    if ' ' in newhead.strip() and dosplit(newhead):
        newhead = newhead.split(' ')
    elif ' ' in newhead.strip() and dontsplit(newhead) and not dosplit(newhead):
        newhead = [newhead.split(' ')[0]]
    elif '/' in newhead and dontsplit(newhead):
        newhead = newhead.split('/')
    else:
        newhead = newhead.split(';')    
    
    return newhead, content

# Returns chapter if not 0; otherwise, finds correct chapter number
def check_chapter(head, chapter):
    if chapter != '0':
        return chapter
    else:
        assert isinstance(head, unicode)
        for key in chapter_zero:
            if head in chapter_zero[key]: return key
        raise Exception('lemma not in chapter_zero: '+head.encode('utf-8'))

# Main method
def parse(dico_path, log, log_error):
    dico_data = sorted(glob(dico_path+'/ltrl*'))
    dico = []
    errors_occurred = False
    
    begin = False
    for xmlfile in dico_data:
        for line in open(xmlfile):
            line = line.decode('utf-8')
            if re.search('id=".+?\.tr', line):
                id = re.sub('id="|"', '', re.search('id=".+?\.tr', line).group(0))
                begin = True
            elif not begin:
                pass
            elif re.search('<Q>', line):
                content = clean_content.sub('', line).strip()
            elif begin and re.search('<cat>', line):
                chapter = clean_chpt.sub('', find_chpt.search(line).group(0))
            elif re.search('<A>', line) and re.sub('<A>', '', re.search('<A>.*', line).group(0)).strip() \
            or re.search('</A>', line):
                try:
                    (head, content) = clean_headword(line, content)                    
                    if id not in  ('_167.tr',):
                        if isinstance(head, list):
                            for each in head:
                                assert isinstance(each, unicode)
                                each = each.strip()
                                chapter = check_chapter(each, chapter)
                                attrs = {'head': each, 'content': content, 'chapter': chapter}
                                dico.append(attrs)
                        else:
                            head = head.strip()
                            chapter = check_chapter(head, chapter)
                            attrs = {'head': head, 'content': content, 'chapter': chapter}
                            dico.append(attrs)
                except(Exception), e:
                    log_error("%s couldn't parse line \"%s\"...: %s" \
                        % (xmlfile.split('/')[-1], content[:50], e))            
                    errors_occurred = True
                (head, content, chapter) = ('', '', '')
                begin = False
            
        log('%s finished parsing' % xmlfile.split('/')[-1])
        
    return dico, errors_occurred
