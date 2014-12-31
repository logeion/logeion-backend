# -*- coding: utf-8 -*-
"""
Sample entry:

(PUT A SMALL SAMPLE ENTRY HERE.)
"""

from __future__ import with_statement
from glob import glob

name = 'YOUR_DICO_NAME' # The name as it will appear in Logeion
type = '' # 'latin' or 'greek'
caps = '' # 'precapped', 'uncapped', or 'source'
convert_xml = False # -> True if you want lists converted to HTML
enabled = False # Remove this line when your parser is ready

# Main method
def parse(dico_path):
    # dico_path will point to the parent directory of your files;
    # grab your files accordingly
    dico_data = sorted(glob(dico_path+'/*.xml'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:
        with open(xmlfile) as infh:
            ########### BEGIN_CODE ###########
            # Populate dico with the input text.
            # dico should be a list of dicts of the following form:
            #
            # - If you're writing a parser for a standard dictionary:
            #   {'head': HEADWORD, 'orth_orig'; HEADWORD-WITH-DIACRTICS,
            #    'content': FULL-ENTRY-TEXT, 'dico': DICTIONARY-NAME}
            #
            # - If you're writing a parser for a textbook:
            #   {'head': HEADWORD, 'content': FULL-ENTRY-TEXT, 'chapter': CHAPTER-WORD-APPEARS-IN}
            #
            # It's pretty hacky, but if you encounter any errors, log them like this:
            #   tobelogged['warning'].append(ERROR_MSG)
            pass
            ############ END_CODE ############

        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
        
    return dico, tobelogged
