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
import re
import os.path

name = 'DMLBS'
type = 'latin'
caps = 'precapped'
convert_xml = False

strip_extension = re.compile('(.*?)\.')

# &nbspace; -> &nbsp;   - From a reasonable misunderstanding
# | -> /                - '|' was used as a separator for lines of poetry
def clean_content(content):
    content = content.replace('&nbspace;', '&nbsp;')
    content = content.replace('|', '/') # Remarkably, this doesn't break anything
    return content

# Main method
def parse(dico_path):
    dico_data = sorted(glob(os.path.join(dico_path, '*.xml')))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:
        # Since we don't have diacritics in the headwords, we can
        # pull it straight from the filename - with some caveats...
        xmlfile_leaf = os.path.basename(xmlfile)
        head = strip_extension.search(xmlfile_leaf).group(1)#.encode('utf-8')
        content = ''
        with open(xmlfile) as infh:
            full_content = infh.read()
            content = str(BeautifulStoneSoup(full_content).find('entry'))
            content = clean_content(content)

        dico.append({'head': head,
                     'content': content})

        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
        
    return dico, tobelogged
