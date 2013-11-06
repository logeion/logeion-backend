# -*- coding: utf-8 -*-
import re, unicodedata as ud
from glob import glob

name = 'PrincetonEncyclopedia'
type = 'latin'
caps = 'precapped'

# regex patterns    
find_head = re.compile('<settlement>(.)*?</settlement>')
clean_head = re.compile('<settlement>|</settlement>')
find_entry = re.compile('<div1')
end_entry = re.compile('</div1>')

ignore = ['by', 'on', 'in', 'ad', 'the', 'en', 'near', 'of', 'or', 'les', 
          'del', 'el', 'sur', 'de', 'apud', 'le', 'cwm', 'di', 'da', 'upon', 
          'sous', 'am', 'la', 'et', 'und', 'a', 'er', 'es', 'ez', 'lez', 'du', 
          'los', 'au', 'bei', 'las', 'an', 'der', 'della', 'tis', 'tou', 'al', 
          'il', 'ir', 'and', 'im', 'do', 'ben', 'bou', 'des', 'under', 'n', 
          'dei', 'ob', 'aux', 'y']

# Normalizes letters and removes other excess chars
def clean_headword(headword):
    headword = clean_head.sub('', headword)
    headword = re.sub('“|”', '', headword)
    headword = re.sub('[*/_0-9\[\]!?]', '', headword)                
    headword = re.sub('[.,]', '', headword)
    headword = re.sub('[ ][ ]+', ' ', headword)
    #headword = re.sub(' \(.*\)', '', headword)
    headword = unicode(headword)    
    newheadword = ''
    for char in headword:
        charname = ud.name(char)
        if 'LATIN' in charname:
            newcharname = re.search('LATIN (CAPITAL|SMALL) LETTER [\w]', charname).group(0)
        else:
            newcharname = charname
        newheadword += ud.lookup(newcharname)
    
    '''
    headword = headword.lower()
    
    headword = re.sub('Ï|İ|Î|Ī|Ì|Í', 'i', headword)
    headword = re.sub('Ç|ç|Ć|Č', 'c', headword)
    headword = re.sub('Ş|Š', 's', headword)
    headword = re.sub('Ḥ', 'h', headword)
    headword = re.sub('Á|Â|Ă|À|Ã|Ā|ă', 'a', headword)        
    headword = re.sub('É|È|Ë|Ē|Ê', 'e', headword)
    headword = re.sub('Ü|Ù|Ú|Ū|Û', 'u', headword)
    headword = re.sub('Ő|Ö|Ô|Ó|Ò|ö', 'o', headword)
    headword = re.sub('Ż|Ž', 'z', headword)
    headword = re.sub('Ġ|Ğ', 'g', headword)
    headword = re.sub('Ţ', 't', headword)
    headword = re.sub('Ÿ', 'y', headword)
    headword = re.sub('Ñ', 'n', headword)
    '''
    return newheadword.lower()

# Capitalizes entries according to the standard conventions for place names
def capitalize(headword):
    headword = unicode(headword).lower()
                
    if re.search('[^a-zA-Z][^a-zA-Z][^a-zA-Z]+', headword, re.U):
        headword = re.sub('[^a-zA-Z][^a-zA-Z][^a-zA-Z]+', '', headword, re.U)
                
    # Diff. along whitespace, then capitalize                
    headword_comps_spc = headword.split()                
    for comp in headword_comps_spc:                    
        index = 0
        # Skip if comp is an ignored word and is neither the first nor last word of
        # the headword; an e
        if comp in ignore and not \
        (headword_comps_spc.index(comp) == 0 or \
        (headword_comps_spc.index(comp) == len(headword_comps_spc)-1 and len(comp) == 1)):
            continue
        for char in comp:
            # Capitalize if an alphabetic char is 1) a standalone letter, 2) at the beginning
            # of comp and not followed by a ', or 3) not at the beginning and was preceded by a
            # non-alphabetic character (as in 'Erythrai (Greece)')
            # An exception is if a letter is followed in two chars by a dash: that is, words
            # such as al-..., el-..., or es-...
            # It will also capitalize the first letter of a contracted article if it is
            # part of the first comp (e.g. "L'Ecluse")
            if re.match('[\w]', char, re.U) and (len(comp) == 1 or (index == 0 and \
            not comp[index+1] == "'") or (index > 0 and not re.match('[\w]', comp[index-1], re.U))) \
            and not (index < len(comp)-2 and comp[index+2] == '-'):
                comp_ind = headword_comps_spc.index(comp)
                headword_comps_spc[comp_ind] = comp[:index]+char.upper()+comp[index+1:]
                break
            index += 1
                                                    
    headword = ' '.join(headword_comps_spc)                
                
    # Diff. along dashes, then capitalize               
    headword_comps_dsh = headword.split('-')                
    for comp in headword_comps_dsh:                    
        index = 0
        if comp in ignore and not headword_comps_dsh.index(comp) == 0:
            continue                     
        for char in comp:
            if re.match('[\w]', char, re.U) and (len(comp) == 1 or (index == 0 and \
            not comp[index+1] == "'") or (index > 0 and \
            not re.match('[\w]', comp[index-1], re.U))):
                comp_ind = headword_comps_dsh.index(comp)
                headword_comps_dsh[comp_ind] = comp[:index]+char.upper()+comp[index+1:]
                break
            index += 1
            
    headword = '-'.join(headword_comps_dsh)

    # Diff. along apostrophe to handle special cases
    headword_comps_aps = headword.split("'")
    for comp in headword_comps_aps:
        if re.match('an', comp, re.U):
            comp_ind = headword_comps_aps.index(comp)
            headword_comps_aps[comp_ind] = comp[0].upper()+comp[1:]
        elif comp == 'l':
            comp_ind = headword_comps_aps.index(comp)
            headword_comps_aps[comp_ind] = comp.upper()
    headword = "'".join(headword_comps_aps)
                
    # Fix an extremely annoying part of an entry
    if re.search('\(Near', headword):
        headword = re.sub('Near', 'near', headword)
    if re.search('near la Spezia', headword):
        headword = re.sub('near la Spezia', 'near La Spezia', headword)
                
    # Fix an issue with Roman numerals
    if re.search('Iii', headword):
        headword = re.sub('Iii', 'III', headword)                
    elif re.search('Ii', headword):
        headword = re.sub('Ii', 'II', headword)
        
    return headword

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/princeton*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}
    
    begin = False
    head_found = False   
    for xmlfile in dico_data:        
        content = ''
        for line in open(xmlfile):           
            if find_head.search(line) and begin and not head_found:                
                head_match = find_head.search(line)
                head_found = True
                content += line            
            elif find_entry.search(line):
                begin = True                
                content += line          
            elif end_entry.search(line):
                try:
                    content += line                
                    content = content.strip('\n')                
                    headword = clean_headword(head_match.group(0))
                    headword = capitalize(headword)
                    attrs = {'head': headword, 'content': content}
                    dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], content[:50], e))
                (headword, content) = ('', '')
                begin = False
                head_found = False
            elif begin:
                    content += line
                    
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, tobelogged
                    
                    

                    
                    
                
