# -*- coding: utf-8 -*-
"""
Sample entry:

<!ENTITY breve "&#x23d1;">
<!ENTITY nbspace "&#x00a0;">
]><entry xml:space="preserve"><ls><lm><l>rinatrix</l><et>cf. <e lang="CL">natrix</e></et></lm></ls><s1><s2><def>water-snake</def></s2><q1><q2><qt><q>†rimatrix <ed>MS: rinatrix</ed>, serpens aquitilis</q><ref><place><au>Osb. Glouc.</au><wk>Deriv.</wk><loc>508</loc></place></ref></qt><qt><q>~ix serpens ‥ veneno aquas inficiens</q><ref><place><au>Bart. Angl.</au><loc>XVIII 8 p. 1000</loc></place></ref></qt></q2></q1></s1></entry>
"""

from __future__ import with_statement
from BeautifulSoup import BeautifulStoneSoup
from glob import glob
from lxml import etree
import os.path

name = 'DMLBS'
type = 'latin'
caps = 'precapped'
convert_xml = False

# Main method
def parse(dico_path, log, log_warning):
    dico_data = sorted(glob(os.path.join(dico_path, '*.xml')))
    dico = []
    errors_occurred = False

    for xmlfile in dico_data:
        try:
            # Since we don't have diacritics in the headwords, we can
            # pull it straight from the filename - with some caveats...
            xmlfile_leaf = os.path.basename(xmlfile)
            head = strip_extension.search(xmlfile_leaf).group(1)
            content = ''
            with open(xmlfile) as infh:
                full_content = infh.read()
                log('Converting contents via BeautifulSoup')
                soup = BeautifulStoneSoup(full_content)
                if soup.find('entry'):
                    content = str(soup)

            dico.append({'head': head,
                         'content': content})

            log('%s finished parsing' % xmlfile.split('/')[-1])
        except(Exception), e:
            log_warning('Error occurred while parsing %s: %s' % (xmlfile.split('/')[-1], str(e)))
            errors_occurred = True
        
    return dico, errors_occurred
