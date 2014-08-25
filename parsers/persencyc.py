# -*- coding: utf-8 -*-
"""
Sample entry:

<div1 type="entry" id="abai" org="uniform" sample="complete">
  <head>Abai</head>
  <subhead type="alt">Abae</subhead>
  <div2 type="subentry" id="abai-1" org="uniform" sample="complete">
    <subhead><placeName>Abai</placeName>, city of <placeName>Phocis</placeName></subhead>
    <div3 type="index" org="uniform" sample="complete">
      <list type="index">
        <item>
          <bibl n="Paus. 10.35.1-4" default="NO" valid="yes">Paus. 10.35.1-4</bibl>
        </item>
        <item>not destroyed after Sacred War:
          <bibl n="Paus. 10.3.2" default="NO" valid="yes">Paus. 10.3.2</bibl>
        </item>
        <item>oracle at: <bibl n="Paus. 4.32.5" default="NO" valid="yes">Paus. 4.32.5</bibl>,
          <bibl n="Paus. 10.35.1" default="NO" valid="yes">Paus. 10.35.1</bibl>,
          <bibl n="Hdt. 1.46" default="NO" valid="yes">Hdt. 1.46</bibl>,
          <bibl n="Hdt. 8.27" default="NO" valid="yes">Hdt. 8.27</bibl>,
          <bibl n="Hdt. 8.33" default="NO" valid="yes">Hdt. 8.33</bibl>,
          <bibl n="Hdt. 8.134" default="NO" valid="yes">Hdt. 8.134</bibl>
        </item>
      </list>
    </div3>
  </div2>
</div1>
"""

import re
from glob import glob

name = 'PerseusEncyclopedia'
type = 'latin'
caps = 'source'
convert_xml = True

# regex patterns
find_head = re.compile('<head(.)*?/head>')
clean_head = re.compile("<[^<]+>|^'|'$")
find_entry = re.compile('<div1')
end_entry = re.compile('</div1>')

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/persencyc*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    begin = False   
    for xmlfile in dico_data:        
        content = ''
        for line in open(xmlfile):
            if find_head.search(line) and begin:                
                head_match = find_head.search(line)
                content += line
            elif find_entry.search(line):
                begin = True                
                content += line            
            elif end_entry.search(line):
                try:
                    content += line
                    headword = head_match.group(0)                
                    headword = clean_head.sub('', headword.strip())
                    headword = re.sub("^'|'$", '', headword)
                    if headword == '':
                        print headword,'\n'+content
                    content = content.strip('\n')      
                    attrs = {'head': headword, 'content': content}
                    dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], content[:50], e))                
                (headword, content) = ('', '')
                begin = False
            elif begin:
                content += line
                    
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, tobelogged
