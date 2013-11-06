# -*- coding: utf-8 -*-
import re, sys, unicodedata as udata
from glob import glob

# Various attributes for logeion_parse.py
name = 'JACT'
type = 'sidebar'
caps = 'precapped'

remaining_spaces = {\
'σ(ε)αυτόν ήν': 'σεαυτοῦ',
'οὑτοσί αὑτηί τουτί': 'οὑτοσί αὑτηί τουτί',
'ὅ τι': 'ὅ τι',
'μᾶλλον ἤ': 'μᾶλλον',
'ἐν νῷ ἔχω': 'νόος',
'δίκην δίδωμι': 'δίκη',
'πράγματα παρέχω': 'πρᾶγμα',
'εἰρήνην ἄγω': 'εἰρήνη',
'πολύς πολλή πολύ': 'πολύς',
'φοβέομαι μή': 'φοβέομαι',
'χαλκοῦς ῆ οῦν': 'χαλκοῦς',
'ὁ ἡ τό': 'ὁ',
'τοιόσδε τοιήδε τοιόνδε': 'τοιόσδε',
'πλέως α ων': 'πλέως',
'μέλας μέλαινα μέλαν': 'μέλας',
'ὅδε ἥδε τόδε': 'ὅδε',
'ὅσπερ ἥπερ ὅπερ': 'ὅσπερ',
'τις τι': 'τις',
'μέγας μεγάλη μέγα': 'μέγας',
'γραφὴν γράφομαι': 'γραφή',
'τίς τί': 'τίς',
'ἐμαυτόν ήν': 'ἐμαυτόν',
'προσέχω τὸν νοῦν': 'νόος',
'ἅπας ἅπασα ἅπαν': 'ἅπας',
'οἷός τ᾽ εἰμί': 'οἷος',
'συγγνώμην ἔχω': 'συγγνώμη',
'εὔνους ουν': 'εὔνους',
'ἀσεβέω εἰς': 'ἀσεβέω',
'ἔτι καὶ νῦν': 'ἔτι',
'δίκην λαμβάνω': 'δίκη',
'εἰδώς εἰδυῖα εἰδός': 'εἰδώς',
'πρὶν ἄν': 'πρίν',
'τρεῖς τρία': 'τρεῖς',
'διὰ τί': 'διὰ',
'ὅστις ἥτις ὅ τι': 'ὅστις',
'τάλας τάλαινα τάλαν': 'τάλας',
'πᾶς πᾶσα πᾶν': 'πᾶς',
'χάριν οἶδα': 'χάρις'}

def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/JactVocab*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    # First, we'll define a few helper functions that will make comparison of different
    # possible lemmas and the filtering of types of lemmas a bit easier

    # Returns true if entry has the form "lemma, article", false otherwise
    def ends_with_article(h):
        articles = ['τό', 'ὁ', 'ἡ', 'τά', 'οἱ', 'αἱ']
        for a in articles:
            if re.search(' %s$' % a, h):
                return True
        return False

    # Removes all diacritics from a headword (for comparison)
    def flatten(h):
        new_h = ''
        h = h.decode('utf-8')
        for c in h: # char by char
            name = udata.name(c)
            if 'LETTER' in name and 'WITH' in name:
                name = re.search('(.+) WITH', name, re.S).group(1)
                new_h += udata.lookup(name)
            else:
                new_h += c
        return new_h

    # Begin actual parsing: loop over filenames (just one in this case, but structure
    # is the same across all Logeion parsers) and parse entry-by-entry (=line-by-line)

    for xmlfile in dico_data:
        for line in open(xmlfile):
            # Grab info from line
            head, defn, chapter, section, pos = line.strip().split('\t')
            chapter += section
            content = '%s, %s (%s)' % (head, defn, pos)

            # Parse the headword into one or various lemmas (for more effective lookup); 
            # lemmas is always a list. This may seem like conditional overkill, but there's
            # really no automatic, one-size-fits-all way to get a reasonable lemma from a
            # given entry.

            head = head.rstrip(';') # "τί;", "ποῦ;", etc. to standard forms

            # Skip over redundant λόγος entries, but still keep them in the source
            if u'λόγος, ὁ' in head.decode('utf-8') and not 'd (3c, 2c)' in head:
                continue

            # "λόγος, ὁ" -> [λόγος]; "ξένος (ξεῖνος), ὁ" -> [ξένος, ξεῖνος]
            if ',' in head and ends_with_article(head):
                lemmas = [head.split(',')[0].split(' ')[0]]
                if u'νοῦς' == lemmas[0].decode('utf-8'):
                    lemmas = ['νόος'] 
            # "οὐ, οὐκ, οὐχ" -> [οὐ, οὐκ, οὐχ]
            elif ',' in head and not '(' in head:
                lemmas = map(str.strip, head.split(','))
            # "ἄξιος α ον" -> [ἄξιος]; "ψευδής ές" -> [ψευδής]
            elif re.search(' ον$| ες$| α$|ος .*η .*ον?|ων .*ον|εις .*μια|υς .*εια .*υ'.decode('utf-8'), flatten(head)) is not None:
                lemmas = [head.split(' ')[0]]
            # "οὐδέπω / οὔπω" -> [οὐδέπω, οὔπω]; "κακὰ / κακὼς ποιέω" -> [κακὰ ποιέω, κακὼς ποιέω]
            elif '/' in head:
                lemmas = map(str.strip, head.split('/'))
                if ' ' in lemmas[-1]: # covers the "κακὰ / κακὼς ποιέω" cases
                    lemmas[-1], trailing = lemmas[-1].split(' ')
                    lemmas = map(lambda x: x+' '+trailing, lemmas)
            # "ἑαυτούς (αὑτούς), ἑαυτάς (αὑτάς), ἑαυτά (αὑτά)" -> [ἑαυτοῦ]
            elif re.search(ur'^ἑαυτ', head.decode('utf-8')) is not None:
                lemmas = ['ἑαυτοῦ']
            # Cases range between using one, using both, and using neither; see below
            elif '…' in head:
                lemmas = map(str.strip, head.split('…'))

                if lemmas[0] == lemmas[1]: # "μήτε … μήτε" -> [μήτε]
                    lemmas = lemmas[0]
                elif lemmas[0] in ['ἄλλος', 'ἕτερος']: # "ἄλλος … ἄλλον" -> [ἄλλος]
                    lemmas = [lemmas[0]]
                elif lemmas[0] == 'ὁ μέν': # "ὁ μέν … ὁ δέ" -> [μέν, δέ]
                    lemmas = ['μέν', 'δέ']
                elif lemmas[0] == 'οὐ μόνον': # "οὐ μόνον … ἀλλὰ καί" -> [μόνος]
                    lemmas = ['μόνος']
            # "Ἀθήνησι(ν)" -> [Ἀθήνησιν, Ἀθήνησι]
            elif head.decode('utf-8') == u"Ἀθήνησι(ν)" or head.decode('utf-8') == u'οὕτω(ς)':
                lemmas = [re.sub('[()]', '', head), re.sub('\(.+\)', '', head)]
            # Anything that isn't easily parsed
            elif head in remaining_spaces:
                lemmas = [remaining_spaces[head]]
            # One-word lemmas
            else:
                if re.search(u'[ ,]', head) and not re.search(ur'^καὶ [\S]+$', head.decode('utf-8')):
                    print head, "missed"
                    raise Exception
                lemmas = [head]

            # Process the entries 
            for l in lemmas:
                attrs = {'head': l, 'content': content, 'chapter': chapter}
                dico.append(attrs)

        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
    
    return dico, tobelogged

        

