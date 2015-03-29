# -*- coding: utf-8 -*-
"""
Sample data:

...
ABARIS	N	Abaris	"Abaris, is, m."	"a Rutulian warrior, 9.344."
ABAS	N	Abas	"Abās, antis, m."	"1. The twelfth king of Argos,..."
ABDO		abdo	"abdō, didī, ditus, 3, a."	"to put away; with the..."
ABDVCO		abduco	"abdūcō, dūxī, ductus, 3, a."	"to lead away; remove,..."
...

"""
from __future__ import with_statement
import csv

name = 'FriezeDennisonVergil'
type = 'latin'
caps = 'source'
convert_xml = False

def parse(dico_path, log, log_error):
    datafile = dico_path+'/friezedennison.txt'
    dico = []
    errors_occurred = False

    with open(datafile) as infh:
        reader = csv.reader(infh, delimiter='\t', quotechar='"')
        for row in reader:
            try:
                row = [c.decode('utf-8') for c in row]
                head = row[2]
                content = row[3] + u': ' + row[4]
                orth_orig = row[3].split(',')[0]
                attrs = {'head': head, 'content': content, 'orth_orig': orth_orig}
                dico.append(attrs)
            except(Exception), e:
                log_error("%s couldn't parse line \"%s\"...: %s" \
                    % (datafile.split('/')[-1], '\t'.join(row)[:50], e))
                errors_occurred = True

    log('%s finished parsing' % datafile.split('/')[-1])
    return dico, errors_occurred
