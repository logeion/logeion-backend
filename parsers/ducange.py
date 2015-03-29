# -*- coding: utf-8 -*-
"""
Sample entry:

<entry rend="carpentier" xml:id="AAISIENTIA">
  <dictScrap xml:id="AAISIENTIA-1"><form rend="b">AAISIENTIA</form>, Facultas utendi ex concessione rebus non suis, idem quod <ref target="AASANTIA">Aasantia</ref> et <ref target="AISANTIA">Aisantia</ref>. Charta ann. 1269. in Chartul.
    S. Joan. Laudun : <quote xml:lang="lat">Concedens eidem ecclesiæ.... omnimodas Aaisientias, quales,
      antiquitus in omni territorio et advocatia mea antiqui hospites dictæ ecclesiæ in eadem
      villa morantes habere solebant.</quote> Nostris olim <hi rend="i">Aaissier</hi>, idem quod Juvare,
    auxiliari, Gall. <foreign xml:lang="fro">Aider, donner du secours</foreign>. Chron. S. Diom. tom. 3. Collect. Histor.
    Franc. pag. 244 : <quote xml:lang="fro">Il tournerent à la maison d'un vilain pour demander à boire, et
      il leur dist que il n'avoit de quoi eulz Aaissier. Aaisier</quote> præterea dixerunt pro
    Ad tempus vel sub certis conditionibus aliquid commodare, concedere. Charta ann. 1271. in
    Chartul. Pontiniac. pag. 75 : <quote xml:lang="fro">Je Guiz chevaliers Sires de Chanlost fais asavoir...
      que li Abbés et li convenz de Pontigny.... m'ont presté et Aaisié leur maison de Sevyes,
      tant comme il plaira à eux. <note>(Vide infra
  <hi rend="i">Aisamenta</hi>.)</note></quote></dictScrap>
</entry>
"""
from __future__ import with_statement
from BeautifulSoup import BeautifulStoneSoup
from glob import glob
import re

name = 'DuCange'
type = 'latin'
caps = 'uncapped'
convert_xml = False

# regex patterns
find_head = re.compile('xml:id=".+?"')
find_head2 = re.compile('<form rend="b">.+?</form>')
clean_head = re.compile('xml:id=|"|<[/]?[^<>]*>|[0-9]')
find_entry = re.compile('<entry')
end_entry = re.compile('</entry>')
nested_ws = re.compile('^[ ][ ]+')

# Gets rid of unnecessary tags, spacing, and chars in headword
def cleanup_head(head):
    head = clean_head.sub('', head).lower()
    head = re.sub('^[\s]*[.]|[.][\s]*$', '', head)
    head = head.replace('Æ', 'ae')
    return head

# Main method
def parse(dico_path, log, log_error):
    dico_data = sorted(glob(dico_path+'/*.xml'))
    dico = []
    errors_occurred = False

    begin = False
    rendHead = False
        
    for xmlfile in dico_data:
        with open(xmlfile) as infh:
            # Adjust as necessary; if self-closing tags are not explicitly
            # passed, then parser stops short
            soup = BeautifulStoneSoup(infh, selfClosingTags=['pb','cb'])
            for entry in soup.findAll('entry'):
                head = entry['xml:id'].encode('utf-8')

                # Usually, the xml:id attr is more accurate, but it doesn't
                # distinguish between a dash and whitespace, so we take form
                if '-' in head:
                    try:
                        head = entry.find('form', rend='b').text.encode('utf-8')
                    except(AttributeError):                    
                        pass
                    
                try:
                    head = cleanup_head(head)
                    attrs = {'head': head.strip(),
                             'content': str(entry)}# Calling str() on a
                                                   # BeautifulSoup.Tag object
                                                   # encodes it in UTF-8 by
                                                   # default, so we're fine
                    dico.append(attrs)
                except(Exception), e:
                    log_error("%s couldn't parse line \"%s\"...: %s" \
                        % (xmlfile.split('/')[-1], str(entry)[:50], e))
                    
        log('%s finished parsing' % xmlfile.split('/')[-1])
        
    return dico, errors_occurred
