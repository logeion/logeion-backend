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
import StringIO
from lxml import etree
from apply_css import apply_css

name = 'DMLBS'
type = 'latin'
caps = 'precapped'
convert_xml = False

strip_extension = re.compile('(.*?)\.')
doctype_patt = re.compile('<!DOCTYPE[^>]*>', re.S)

# Remove <!DOCTYPE> decl.   - Unnecessary, and only causes us headaches with lxml; see below
# &nbspace; -> non-breaking space Unicode literal
#                           - There's an &nbspace; entity defined in the DOCTYPE that doesn't
#                             work in HTML, but replacing it with &nbsp; breaks lxml.etree, so
#                             we just replace it with the literal Unicode
# {&breve;,&drachma;,&uncia;} -> Unicode literal
#                           - The DOCTYPE declaration isn't working with lxml.etree
# | -> /                    - '|' was used as a separator for lines of poetry
def clean_content(content):
    uc_content = content.decode('utf-8')
    uc_content = doctype_patt.sub(u'', uc_content)
    uc_content = uc_content.replace(u'&nbspace;', u'\u00a0')
    uc_content = uc_content.replace(u'&breve;', u'\u23d1')
    uc_content = uc_content.replace(u'&drachma;', u'\u0292')
    uc_content = uc_content.replace(u'&uncia;', u'\u2125')
    uc_content = uc_content.replace(u'|', u'/')
    return uc_content.encode('utf-8')

# <loc><type><wk>A</wk></type></loc><loc>3</loc> -> <loc><type><wk>A</wk><loc>3</loc></type></loc>
# We shouldn't run into any aliasing issues here - if we extract a loc's sibling and add it as the last
# child to loc's parent, then when that sibling shows up in this loop the loc.nextSibling test will fail
def fix_sibling_locs(entry):
    locs = entry.findAll('loc')
    for loc in locs:
        if loc.nextSibling and hasattr(loc.nextSibling, 'name') and loc.nextSibling.name == 'loc':
            loc_sibling = loc.nextSibling.extract()
            type_child = loc.find('type')
            type_child.append(loc_sibling)

# This is a fix for a strange formatting issue that comes up in the dictionary: basically,
# we need 2 separate CSS pseudo-element rules for qt depending on whether or not it has an
# empty v tag, but CSS doesn't have ancestor selectors and pseudo-elements aren't in the DOM
# (so jQuery can't edit them), so we mark qt tags with a certain class in the preprocessing
# step and have a separate rule in the CSS (qt+qt:before vs. qt.v+qt:before)
def fix_empty_v(entry):
    root = etree.fromstring(entry)
    qts = root.xpath('//qt/descendant::v[not(node())]/ancestor::qt')
    for qt in qts:
        qt.attrib['class'] = 'v'
    return etree.tostring(root)

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
                    log('Cleaning content')
                    content = clean_content(content)
                    log('Marking qt tags with empty v tags')
                    content = fix_empty_v(content)
                    log('Fixing sibling locs')
                    fix_sibling_locs(soup)
                    content = str(soup)

            dico.append({'head': head,
                         'content': content})

            log('%s finished parsing' % xmlfile.split('/')[-1])
        except(Exception), e:
            log_warning('Error occurred while parsing %s: %s' % (xmlfile.split('/')[-1], str(e)))
            errors_occurred = True
        
    return dico, errors_occurred
