# -*- coding: utf-8 -*-
"""
Sample entry:

<article class="entry" id="ἀάατος">
    <nav class="prevnext">
        <a class="prev" href="ἀά">&lt; ἀά</a>
        <a class="next" href="Ἀάβ">Ἀάβ &gt;</a>
    </nav>
    <header class="form">
        <strong class="lemma2 grc">ἀάατος</strong>
        , <span class="gram">-ον</span>
        <div class="form"><div class="prosodia"><label>Prosodia</label>:
        [ᾰᾱᾰ-, pero ᾰᾱᾱ- <em>Il</em>.14.271] </div></div>
    </header>
  <section class="sense " id="">
    <dfn>que no puede ser inducido a error<i> o </i>engañado</dfn>,
    <dfn>infalible</dfn>
      <span class="cit" id="ἀάατος_cit1">
          <q class="grc">μοι ὄμοσσον ἀάατον Στυγὸς ὕδωρ</q>
      </span> <em>Il</em>.14.271, 
      <span class="cit" id="ἀάατος_cit2">
          <q class="grc">μνηστήρεσσιν ἄεθλον ἀάατον</q>
      </span> <em>Od</em>.22.5, cf. 21.91
      <section class="sense " id="">
        <b class="num">•</b> <dfn>imbatible</dfn>
        <span class="cit" id="ἀάατος_cit3">
          <q class="grc">νοήσας πυγμαχίην, ᾗ κάρτος ἀάατος</q>
          <em class="tr"> habiendo observado su forma de pelear,
              dónde su fuerza era imbatible</em>
        </span> A.R.2.77, cf.
        <em>AB</em> 321.1. 
      </section>
  </section>
  <footer>
    <div class="etym">
      <label>Etimología</label>: Comp. neg. sobre la r. de 
      <a>ἀάω</a> q.u.
    </div>
  </footer>
</article>
"""

from __future__ import with_statement
from BeautifulSoup import BeautifulStoneSoup
from glob import glob
import re

name = 'DGE'
type = 'greek'
caps = 'precapped'

# regex patterns
clean_head = re.compile(u'xml:id=|"|<[/]?[^<>]*>|[0-9]')
find_entry = re.compile(u'<entry.*?</entry>', re.S)

# Gets rid of unnecessary tags, spacing, and chars in headword
def cleanup_head(head):
    head = clean_head.sub('', head)
    head = re.sub(u'^[\s]*[.]|[.][\s]*$', '', head)
    head = head.replace(u'_', u' ')
    return head

# Does any relevant search-replace within the whole entry
def cleanup_entry(entry):
    return entry.replace(u'<num>;</num>', '<num>•</num>'.decode('utf-8'))

dash = '-'.decode('utf-8')

# Main method
def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/*.xml'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:
        with open(xmlfile) as infh:
            soup = BeautifulStoneSoup(infh)
            for entry in soup.findAll('entry'):
                try:
                    head = entry['xml:id']
                    orth_orig = entry.find('orth', type='lemma').text


                    # Usually, the xml:id attr is more accurate, but it doesn't
                    # distinguish between a dash and whitespace, so we take form
                    if dash in head:
                        try:
                            head = entry.find('form', rend='b').text
                        except(AttributeError):                    
                            pass
                    
                    head = cleanup_head(head)
                    entry = cleanup_entry(str(entry).decode('utf-8'))
                    attrs = {'head': head.strip(),
                             'orth_orig': orth_orig.strip(),
                             'content': entry}
                    dico.append(attrs)
                except(Exception), e:
                    tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                    % (xmlfile.split('/')[-1], str(entry).decode('utf-8')[:50], str(e)))
                    
        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
        
    return dico, tobelogged
