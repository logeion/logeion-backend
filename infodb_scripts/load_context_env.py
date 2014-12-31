# -*- coding: utf-8 -*-
from __future__ import with_statement
import re
import sqlite3
import createGreekSamples_inmem as CGS

lemma2tokenids = {}
with open('samples.out') as infh:
    for line in infh:
        m = re.search('Committing (.*?): (.*)', line, re.UNICODE)
        if m: lemma2tokenids[m.group(1).decode('utf-8')] = eval(m.group(2))

conn = sqlite3.connect('GreekLexicon.db')
c = conn.cursor()
c.row_factory = sqlite3.Row
test_lemma = u'λόγος'
test_tokenids = lemma2tokenids[test_lemma]
