# -*- coding: utf-8 -*-
# For dvlg-final db or other two-column sqlite db
"""
Sample entry:

<div2 type="entry" id="authepsa-cn" org="uniform" sample="complete">
  <head orig="AUTHEPSA">AUTHEPSA</head>
  <p><label>AUTHEPSA</label>(<label lang="greek">αὐθέψης</label>), or <quote>self-boiler,</quote>was...</p>
  <p>Nazionale (formerly Borbonico) at Naples. It is probable...</p>
  <byline>[<ref type="cross" target="author.W.S" targOrder="U">W.S</ref>] [<ref type="cross" target="author.W.W" targOrder="U">W.W</ref>]</byline>
</div2>
"""

import re
from glob import glob

name = 'Antiquities'
type = 'latin'
caps = 'uncapped'
convert_xml = True

# regex patterns
find_head = re.compile('<label(.)*?>(.)*?</label>')
clean_head1 = re.compile('<label(.)*?>|<p>')
clean_head2 = re.compile('</label>| \(<label')
find_entry = re.compile('<div2 type="entry"')
end_entry = re.compile('</div2')
remove_headfig = re.compile('<headfig.+?</headfig>')
remove_whitespace = re.compile('[ ][ ]+')
find_actual = re.compile('<head orig="[^"]+"')
clean_actual = re.compile('<head orig=|"')

# Removes excessive whitespace from content
def clean_content(content):
    content = content.replace('<title>', '<i>') # <title> not rendered in Logeion
    content = content.replace('</title>', '</i>')
    content = content.strip('\n')
    content = remove_whitespace.sub(' ', content)

    return content

# Fixes common issue where <headfig> from previous entry becomes
# headword for next entry
def fix_headword(head_match, content):
    headword = head_match.group(0)
    headword = clean_head1.sub('', headword)
    headword = clean_head2.sub('', headword)
    headword = headword.replace('´', '')
    try:
        actual_head = clean_actual.sub('', find_actual.search(content).group(0))
    except(AttributeError):
        pass
    else:    
        actual_head = actual_head.replace('´', '')
        if actual_head != headword.upper():
            print 'ISSUE FOUND:', headword, actual_head
            headword = actual_head
            content = content.replace(headword, actual_head)
    headword = headword.replace('È', 'e').lower()

    return (headword, content)

# Main method
def parse(dico_path, log, log_error):
    dico_data = sorted(glob(dico_path+'/antiquities_dico*'))
    dico = []
    errors_occurred = False
    
    begin = False
    label_found = False

    for xmlfile in dico_data:        
        content = ''
        for line in open(xmlfile):
            if re.search('<p>AK', line): # Covers abnormal issue in xml
                content += line
                head_match = re.search('<p(.)*?\(<label', line, re.DOTALL)                
                label_found = True
            elif re.search('<label( lang="la")?', line) and begin and not label_found:                
                head_match = find_head.search(line)
                label_found = True

            if find_entry.search(line):
                begin = True
                content += line          
            elif end_entry.search(line):
                try:
                    content = clean_content(content + line)
                    (headword, content) = fix_headword(head_match, content)
                    attrs = {'head': headword, 'content': content}
                    dico.append(attrs)
                except(Exception), e:
                    log_warning("%s couldn't parse line \"%s\"...: %s" \
                        % (xmlfile.split('/')[-1], content[:50], e))
                    errors_occurred = True
                (headword, content) = ('', '')
                begin = False
                label_found = False
            elif begin:
                line = remove_headfig.sub('', line)
                content += line
        
        log('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, errors_occurred
