#!/usr/bin/env python
# -*- coding: utf-8 -*-
#############################################################
# logeion_parse.py
# Parses text or xml files and inserts them into sqlite
# table for use by Logeion; see "Logeion_upload_instructions" 
# for details on parsers and dir structure.
#############################################################
import xml.parsers.expat
import sqlite3
import sys
import re
import logging
import unicodedata
import htmlentitydefs
import os.path

try:
    from parsers import *
except(Exception), e:
    print '%s: error: import failed: %s' % (sys.argv[0], str(e))
    sys.exit(-1)

# Some basic globals: usage string, Greek-to-Roman map, and entity-to-Unicode map

prog = sys.argv[0].split('/')[-1]
usage = """\
Usage: %s [options] [dico ...]
    --all           Parse all dictionaries.
    --latin         Parse Latin dictionaries and references (cumulative).
    --greek         Parse Greek dictionaries (cumulative).
    --sidebar       Parse textbooks (cumulative).
    --not <dicos>[,<dico>]*
                    Ignore given dicos when parsing (i.e. remove from set to be parsed).
    --db <db>       Use <db> as output database instead of './new_dvlg-wheel.sqlite'.
    --dico-root <root>
                    Folder containing the dictionary source folders; defaults to
                    ./dictionaries
    --help          Display this message and exit
    --level <level> Log at level <level>; default is INFO. Case-insensitive.
                    Options: %s""" \
                    % (prog, str([f for f in dir(logging) 
                                    if f.isupper() and \
                                    type(logging.getLevelName(f)) is int and \
                                    logging.getLevelName(f) > 0]))

alpha_trans = {'α': 'a', 'β': 'b', 'γ': 'c', 'δ': 'd', 'ε': 'e', 
               'ϝ': 'f', 'ζ': 'g', 'η': 'h', 'θ': 'i', 'ι': 'j',
               'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'o',
               'ο': 'p', 'π': 'q', 'ϟ': 'r', 'ρ': 's', 'σ': 't',
               'τ': 'u', 'υ': 'v', 'φ': 'w', 'χ': 'x', 'ψ': 'y',
               'ω': 'z'}

other_entities = {
'&Amacron;': u'\u0100'.encode('utf-8'), '&Emacron;': u'\u0112'.encode('utf-8'),
'&Imacron;': u'\u012a'.encode('utf-8'), '&Omacron;': u'\u014c'.encode('utf-8'),
'&Scedil;': u'\u015e'.encode('utf-8'),  '&T-vorm;': 'T',#unichr(0x1d413).encode('utf-8'),
'&Turkse-I;': u'\u0130'.encode('utf-8'),'&Turkse-i;': u'\u0131'.encode('utf-8'),
'&Umacron;': u'\u016a'.encode('utf-8'), '&abreve;': u'\u0103'.encode('utf-8'),
'&amacron;': u'\u0101'.encode('utf-8'), '&breuk1-10;': '1/10',
'&breuk1-12;': '1/12',                  '&breuk1-2;': u'\u00bd'.encode('utf-8'),
'&breuk1-200;': '1/200',                '&breuk1-24;': '1/24',
'&breuk1-3;': u'\u2153'.encode('utf-8'),'&breuk1-4;': u'\u00bc'.encode('utf-8'),
'&breuk1-6;': u'\u2159'.encode('utf-8'),'&breuk1-72;': '1/72',
'&breuk1-8;': u'\u215b'.encode('utf-8'),'&breuk1-96;': '1/96',
'&breuk3-4;': u'\u00be'.encode('utf-8'),'&breuk5-12;': '5/12',
'&breuk7-12;': '7/12',                  '&breve;': u'\u02d8'.encode('utf-8'),
'&c-mirror;': u'\u0186'.encode('utf-8'),'&dice-5;': u'\u2684'.encode('utf-8'),
'&eacute;': u'\u00E9'.encode('utf-8'),
'&ebreve;': u'\u0115'.encode('utf-8'),  '&ei;': 'ei',
'&emacron;': u'\u0113'.encode('utf-8'), '&eu;': 'eu',
'&ghacek;': u'\u01e7'.encode('utf-8'),  '&hk;': u'\u2014'.encode('utf-8'),
'&imacron;': u'\u012b'.encode('utf-8'), '&lquote;': u'\u2018'.encode('utf-8'),
'&obreve;': u'\u014f'.encode('utf-8'),  '&oe;': 'oe',
'&oi;': 'oi',                           '&omacron;': u'\u014d'.encode('utf-8'),
'&perc;': u'\u0025'.encode('utf-8'),    '&pijl;': u'\u27a4'.encode('utf-8'),
'&poolse-l;': u'\u0142'.encode('utf-8'),'&rquote;': u'\u2019'.encode('utf-8'),
'&scedil;': u'\u015f'.encode('utf-8'),  '&slash;': u'\u002f'.encode('utf-8'),
'&ss;': u'\u00df'.encode('utf-8'),      '&super1;': u'\u00b9'.encode('utf-8'),
'&super2;': u'\u00b2'.encode('utf-8'),  '&super3;': u'\u00b3'.encode('utf-8'),
'&super4;': u'\u2074'.encode('utf-8'),  '&super5;': u'\u2075'.encode('utf-8'),
'&tcedil;': u'\u0163'.encode('utf-8'),  '&umacron;': u'\u016b'.encode('utf-8'),
'&wit;': ' ',                           '&yi;': 'yi',
'&ymacron;': u'\u0233'.encode('utf-8')
}

#########################
#       FUNCTIONS       #
#########################

# StateManager and Functions for XML parsers

class StateManager:
    def __init__(self):
        self.closeSpan = False
        self.needsFirstUL = True
        self.content = ""
        self.currentLevel = 0

def did_start_element(name, attrs):
    if name == "sense":
        if sm.closeSpan:
             sm.content += "</span></li>" 
        sm.sl = int(attrs.setdefault("level", 0))
        if not sm.sl:
            sm.sl = 1
        sm.sense_n = attrs.setdefault("n", '0')
        if sm.sense_n == "0":
            sm.sense_n = "" 
        logging.debug('In: sm.currentLevel=%d, sm.sl=%d' % (sm.currentLevel, sm.sl))
        while sm.currentLevel < sm.sl:
            sm.needsFirstUL = False 
            if sm.currentLevel > 0:
                sm.content += "<li>"
            sm.content +="<ul>"
            sm.currentLevel+=1 
        logging.debug('Out: sm.currentLevel=%d, sm.sl=%d' % (sm.currentLevel, sm.sl))
        while sm.currentLevel > sm.sl:
            sm.content +="</ul>"
            if sm.currentLevel > 0:
                sm.content += "</li>"
            sm.currentLevel-=1
        if not sm.currentLevel == sm.sl:
            assert()
        sm.content +="<li><span class=\"bullet\">%s</span><span class=\"content\">" % sm.sense_n
        sm.closeSpan = True          
    elif name == "i":
        sm.content +="<i>"
    elif name == "bibl":
        sm.content +="<b>"
    else:
         return

def did_end_element(name):
    if name == "i":
        sm.content +="</i>" 
    elif name == "bibl":
        sm.content +="</b>"
    elif name == "head":
        sm.content += " "

def did_find_char_data(data):
    sm.content += data

# Set up XML parser
#xml_parser = xml.parsers.expat.ParserCreate()
#xml_parser.StartElementHandler = did_start_element
#xml_parser.EndElementHandler = did_end_element
#xml_parser.CharacterDataHandler = did_find_char_data

def clean_one_entry(data):
    #assert isinstance(data, unicode)
    data = data.encode('utf-8')
    global sm
    sm = StateManager()
    try:
        xml_parser = xml.parsers.expat.ParserCreate()
        xml_parser.StartElementHandler = did_start_element
        xml_parser.EndElementHandler = did_end_element
        xml_parser.CharacterDataHandler = did_find_char_data
        xml_parser.Parse(data)
    except xml.parsers.expat.ExpatError, e:
        print >> sys.stderr, '\n' + str(e)
        print >> sys.stderr, data
        m = re.search('column ([0-9]+)', str(e))
        if m:
            print >> sys.stderr, '...'+data[int(m.group(1)):]
        sys.exit(1)
    if sm.closeSpan:
        sm.content += "</span></li>"
    while (sm.currentLevel):
        sm.content += "</ul>"
        if sm.currentLevel > 1:
            sm.content += "</li>"
        sm.currentLevel -= 1
    return sm.content

# Hammer XML so that it fits basic specifications, then clean
# and convert into rational HTML; does it for every dictionary
# except for DGE and DuCange
def clean_xml_and_convert(dico_parsed):
    for i in range(len(dico_parsed)):
        content = dico_parsed[i]['content']
        content = unescape(content)
        #assert type(content) == unicode
        logging.debug('Cleaning/converting entry ' + dico_parsed[i]['head'])
        logging.debug('Entry ' + dico_parsed[i]['head'] + ' has data:\n' + content.encode('utf-8'))
        if content is None:
            logging.warning('content is None for entry ' + dico_parsed[i]['head'])
        else:
            dico_parsed[i]['content'] = clean_one_entry(content).strip()
        logging.debug('Content coming out:\n' + dico_parsed[i]['content'])
    return dico_parsed

# Substitute out all entities for Unicode equivalents (except for those maintained
# by the HTML standard)
def unescape(read_in):
    if read_in is None: return None
    if type(read_in) is not unicode: read_in = read_in.decode('utf-8')
    all_entities = list(set(re.findall('&#?[\w\-0-9]+;', read_in)))
    hed_ent_names = htmlentitydefs.name2codepoint.keys()
    for e in all_entities:
        # First of these based on unescape() by Fredrik Lundh 
        # (http://effbot.org/zone/re-sub.html#unescape-html)
        if e in ('&lt;','&gt;','&amp;','&apos;','&quot;'):
            continue
        elif e[:2] == "&#":
            try:
                if e[:3] == "&#x":
                    replace_chr = unichr(int(e[3:-1],16))
                else:
                    replace_chr = unichr(int(e[2:-1]))
            except(ValueError):
                continue
        elif e[1:-1] in hed_ent_names:
            replace_chr = unichr(htmlentitydefs.name2codepoint[e[1:-1]])
        else:
            replace_chr = other_entities[e].decode('utf-8')
        read_in = re.sub(e.decode('utf-8'), replace_chr, read_in)
    return read_in

# "Transliterates" the Greek headwords.  Roman letters are chosen by alphabetical order,
# purely for sorting
def translit(greek):
    roman = ''
    for char in removediacr(greek):
        if char not in alpha_trans.keys():
            roman += char
        else:
            roman += alpha_trans[letter]
    return roman

# Removes all diacritics and breathings for a transliterated column to serve as a
# base for Roman-letter Greek word entry
def removediacr(greek):
    ugreek = greek.decode('utf-8')
    newugreek = u''.join(c for c in unicodedata.normalize('NFD', ugreek) if unicodedata.category(c) != 'Mn')
    return newugreek.encode('utf-8')

# False if character is a combining breve/macron mark,
# true otherwise; used to flatten headwords to lookupforms
def not_length_marker(c):
    return unicodedata.category(c) != 'Mn' or \
           not ('BREVE' in unicodedata.name(c) or \
                'MACRON' in unicodedata.name(c))

# Changes a headword to a lookupform-acceptable entry; remove
# all non-essential diacritics (e.g. macrons and breves), as
# well as extra digits and slashes
def change_to_lookup(head):
    if type(head) is str:
        try:
            head = head.decode('utf-8')
        except UnicodeDecodeError:
            head = head.decode('latin1')
    tmp = unicodedata.normalize('NFD', head)
    head = ''.join([c for c in tmp if not_length_marker(c)])
    head = unicodedata.normalize('NFC', head) # recombine characters
    return re.sub('[0-9\[\]]', '', head)

# Stores each dico
def dico_loader(dico, entries):
    if not entries: # Usually due to parser error
    	sys.stdout.flush()
        return False
    elif dico not in sidebar_dicos:
        c.execute('delete from Entries where dico=(?)', (dico,))
        for entry in entries:
            # Take entities out of all values
            #entry = dict([(x, unescape(y)) for (x, y) in entry.items()])
            if 'orth_orig' not in entry.keys() or entry['orth_orig'] is None:
                #entry['orth_orig'] = ""
                entry['orth_orig'] = entry['head']
            c.execute('insert into Entries values (?,?,?,?,?)',
                (entry['head'], entry['orth_orig'],
                 entry['content'], dico, change_to_lookup(entry['head'])))
    else:
        c.execute('delete from Sidebar where dico=(?)', (dico,))
        for entry in entries: 
            c.execute('insert into Sidebar values (?,?,?,?,?)', (entry['head'], entry['content'],
            entry['chapter'], dico, change_to_lookup(entry['head'])))

    return True

#######################
#        SETUP        #
#######################

# Setup SQLite connection
args = sys.argv[1:]
if not args:
    print >> sys.stderr, usage
    sys.exit(1)

# Create diconame-to-module dict
all_dicos = {}
for module in sys.modules:
    if 'parsers.' in module:
        parser = sys.modules[module]
        try:
            all_dicos[parser.name] = parser
        except(AttributeError):
            pass

# For easy access during capitalization and headword table creation
latin_dicos = [d.name for d in all_dicos.values() if d.type == 'latin']
greek_dicos = [d.name for d in all_dicos.values() if d.type == 'greek']
sidebar_dicos = [d.name for d in all_dicos.values() if d.type == 'sidebar']
uncapped = [d.name for d in all_dicos.values() if d.caps == 'uncapped']
source = [d.name for d in all_dicos.values() if d.caps == 'source']
convert_xml = [d.name for d in all_dicos.values() \
               if hasattr(d, 'convert_xml') and d.convert_xml]

# Parse command-line arguments
dicos = {}
flag2dicos = {'--greek': greek_dicos,     '--latin': latin_dicos,
              '--sidebar': sidebar_dicos, '--all': all_dicos.keys()}
dbname = 'new_dvlg-wheel.sqlite'
dico_root = './dictionaries'
notdbs = None
loglevel = logging.INFO
i = 0
while i < len(args):
    if args[i] == '--help':
        print >> sys.stderr, usage
        sys.exit(0)
    elif args[i] == '--level': # set log level
        levelname = logging.getLevelName(args[i+1].upper())
        loglevel = levelname if type(levelname) is int else loglevel
        i += 1
    elif args[i] == '--db': # use provided db name
        dbname = args[i+1]
        i += 1
    elif args[i] == '--dico-root':
        dico_root = args[i+1]
        i += 1
    elif args[i] == '--all': # parse all dicos
        dicos.update([(k,all_dicos[k]) for k in latin_dicos])
        dicos.update([(k,all_dicos[k]) for k in greek_dicos])
        dicos.update([(k,all_dicos[k]) for k in sidebar_dicos])
    elif args[i] == '--latin': # parse Latin/English dicos
        dicos.update([(k,all_dicos[k]) for k in latin_dicos])
    elif args[i] == '--greek': # parse Greek dicos
        dicos.update([(k,all_dicos[k]) for k in greek_dicos])
    elif args[i] == '--sidebar': # parse textbooks
        dicos.update([(k,all_dicos[k]) for k in sidebar_dicos])
    elif args[i] == '--not': # ignore the following dico
        notdbs = args[i+1].split(',')
        i += 1
    else: # all other args
        if args[i] in all_dicos:
            dicos[args[i]] = all_dicos[args[i]]
        else:
            print >> sys.stderr, '%s: error: dico/option %s not recognized' \
                % (prog, args[i])
            print >> sys.stderr, usage
            sys.exit(1)
    i += 1

if notdbs:
    for ndb in notdbs:
        if ndb in dicos: del dicos[ndb]
conn = sqlite3.connect(dbname)
conn.text_factory = str
c = conn.cursor()

# Log config
logging.basicConfig(filename='parser.log',
                    format='%(asctime)s:%(levelname)s:%(message)s',
                    filemode='w', level=loglevel, datefmt='%m/%d/%Y %I:%M:%S %p')

if not dicos:
    print >> sys.stderr, '%s: error: no dictionaries specified' % prog
    print >> sys.stderr, usage
    sys.exit(-1)
logging.info('Dicos to be parsed: '+str(dicos.keys()))

# Will skip creating Latin/GreekHeadwords if nothing has changed
# in either (same with capitalization)
lFlag = any([k in latin_dicos for k in dicos])
gFlag = any([k in greek_dicos for k in dicos])
cFlag = any([k in uncapped    for k in dicos])

#######################
#       PARSERS       #
#######################

# Create dico tables in wheel from those in final
print 'Parsing dictionary files...'
try: # See if Entries already exists; if not, create it and index
    c.execute('select lookupform from Entries')
except(sqlite3.OperationalError):
    c.executescript('create table Entries(head text, orth_orig text, content text, dico text, lookupform text); \
                     create index lookupform_index_e on Entries (lookupform);')
try: # See if Sidebar already exists; if not, create it
    c.execute('select lookupform from Sidebar')
except(sqlite3.OperationalError):
    c.executescript('create table Sidebar(head text, content text, chapter text, dico text, lookupform text); \
                     create index lookupform_index_s on Sidebar (lookupform);')

# Parse each dico and send the resulting list to dico_loader
for dico in dicos:
    spcs = ' '*(25-len(dico))
    logging.info('Parsing %s:', dico)
    sys.stdout.write('\t%s:%sparsing\r' % (dico, spcs)) 
    sys.stdout.flush()
    try:
        #dico_parsed, tobelogged = getattr(dicos[dico], 'parse')('dictionaries/'+dico)
        dico_parsed, tobelogged = getattr(dicos[dico], 'parse')(dico_root+'/'+dico)
        logging.info(dico + ' finished parsing; applying html cleanup and inserting into db')
    except(Exception), e: # Either error in calling the actual function itself or in documenting normal error
        logging.warning('While parsing %s: %s' % (dico, e))
        sys.stdout.write('\t%s:%suncaught exception; check log and parser. Dico not loaded.\n' % (dico, spcs))
        sys.stdout.flush()
    else: 
    	# Logs errors, etc. from parsing dico

        # This little bit comes from the mix of unicode and str types that
        # are typical of Python 2.x; rather than expect one type from the
        # parsers, we just convert everything to UTF-8-encoded strings here
        logging.debug('Converting everything to UTF-8 string from unicode')
        for i in range(len(dico_parsed)):
            for k in dico_parsed[i]:
                if isinstance(dico_parsed[i][k], unicode):
                    dico_parsed[i][k] = dico_parsed[i][k].encode('utf-8')
        for level in tobelogged:
            for event in tobelogged[level]:
                getattr(logging, level)(event)

    	# Loads entries to SQLite table
        sys.stdout.write('\t%s:%sloading\r' % (dico, spcs))
        sys.stdout.flush()
        if dico in convert_xml:
            dico_parsed = clean_xml_and_convert(dico_parsed)
        loaded_successfully = dico_loader(dico, dico_parsed)
        if tobelogged['warning']:
            sys.stdout.write('\t%s:%snon-fatal errors during parse; check log.\n' % (dico, spcs))
        elif not loaded_successfully:
            sys.stdout.write('\t%s:%sno entries passed.\n' % (dico, spcs))
        else:
            sys.stdout.write('\t%s:%scomplete.\n' % (dico, spcs))
        
########################
#    CAPITALIZATION    #
########################

# Capitalizes headwords based on dictionaries labled "source" and other entries within the dictionaries;
# 
if not cFlag:
    print 'Skipping capitalization...'
else:
    print 'Grabbing entries for capitalization...'
    
    # Grab all source dico entries
    query = 'select distinct head, dico from Entries where '
    query += ' or '.join(['dico=(?)']*len(source)) # "...where dico=(?) or dico=(?) or..."
    c.execute(query, source)
    all_entries = c.fetchall()
    srefs = {}
    
    # For each distinct headword, put tuples (head, dico name) in a list under it    
    for each in all_entries:
        if not each[0].lower() in srefs: 
            srefs[each[0].lower()] = [each]
        else:
            srefs[each[0].lower()].append(each)
    
    # Iterate over uncapped dicos
    for ucd in uncapped:
        spcs = ' '*(25-len(ucd))
        sys.stdout.write('\t%s:%squerying\r' % (ucd, spcs))
        sys.stdout.flush()
        # cols are (in order): head, content, dico, lookupform, rowid
        c.execute('select *, rowid from Entries where dico=(?)', (ucd,))
        this_dico = {}
        for row in c: # Create dict so that each corresponds to a head (and is unique)
            head = row[0]
            rowid = row[-1]
            this_dico['%s|%d' % (head, rowid)] = row[:-1] # not rowid
    
        # Creates ucrefs, a subset of srefs, which is all the entries of srefs
        # which are also in the current ucd
        ucrefs = {}    
        done = 0
        todo = len(this_dico)
        for key in this_dico:
            done += 1
            sys.stdout.write('\t%s:%sgathering %06d/%06d\r' % (ucd, spcs, done, todo))
            sys.stdout.flush()
            head = key.split('|')[0]
            try:
                if head.lower() not in ucrefs:
                    ucrefs[head.lower()] = srefs[head.lower()]
            except(KeyError):
                pass
            
        # Iterates over ucrefs to modify headwords and lookupforms in this_dico
        todo = len(ucrefs)
        done = 0
        for head in ucrefs:
            lower = False
            done += 1
            sys.stdout.write('\t%s:%sadjusting %06d/%06d\r' % (ucd, spcs, done, todo))
            sys.stdout.flush()

            # Checks if at least one headword is in lowercase; if none are lowercase, sets original head
            # to the first head of the first source dico
            any_heads_lowercase = any(ref[0].islower() for ref in ucrefs[head])             
            if not any_heads_lowercase:            
                newhead = ucrefs[head][0][0]
                for each in this_dico:
                    if each.split('|')[0].lower() == newhead.lower():
                        rowid = each.split('|')[1]
                        values = this_dico[each]
                        values = (newhead, values[1], values[2], values[3], change_to_lookup(newhead))
                        del this_dico[each]
                        this_dico['%s|%s' % (newhead, rowid)] = values
        
        todo = len(this_dico)
        done = 0
        c.execute('delete from Entries where dico=(?)', (ucd,))
        for each in this_dico:
            done += 1
            sys.stdout.write('\t%s:%supdating  %06d/%06d\r' % (ucd, spcs, done, todo))
            sys.stdout.flush()
            entry_query = '('+ ','.join(map(lambda x: '?', this_dico[each])) +')'
            c.execute('insert into Entries values '+entry_query, this_dico[each])
    
        sys.stdout.write('\t%s:%scomplete.' % (ucd, spcs) + (' '*14)+'\n')    

########################
#    HEADWORD LISTS    #
########################

print 'Creating headword tables...'

# Create headword and temp tables in wheel
c.executescript("""drop table if exists Temp;
                 create table Temp (head text);""")

# Fill temp and insert sorted, distinct entries into headword; this uses
# all the dicos, not just selected ones; will be skipped if no Latin-headword dicos
# were modified
spcs = ' '*11
if not lFlag:    
    sys.stdout.write('\tLatinHeadwords:%sskipped.\n' % spcs)
else:
    c.executescript('drop table if exists LatinHeadwords; \
                     create table LatinHeadwords (head text);')

    sys.stdout.write('\tLatinHeadwords:%screating \r' % spcs)
    sys.stdout.flush()

    for dico in latin_dicos:
        c.execute('insert into Temp select lookupform from Entries where dico=(?)',\
        (dico,))

    sys.stdout.write('\tLatinHeadwords:%sfilling  \r' % spcs)
    sys.stdout.flush()
    c.executescript('insert into LatinHeadwords select distinct * from Temp order by '+\
                    'head collate nocase; \
                     delete from Temp;')

    sys.stdout.write('\tLatinHeadwords:%scomplete.\n' % spcs)

# Make table containing Greek headwords in alphabetical order; will be skipped if no
# Greek-headword dicos were modified
if not gFlag:
    sys.stdout.write('\tGreekHeadwords:%sskipped.\n' % spcs)
else:
    sys.stdout.write('\tGreekHeadwords:%screating%s\r' % (spcs, ' '*21))
    sys.stdout.flush()
    
    c.executescript('drop table if exists GreekHeadwords; \
                     drop table if exists Transliterated; \
                     drop index if exists trans_index; \
                     create table GreekHeadwords (head text); \
                     create table Transliterated (normhead text, transhead text); \
                     create index trans_index on Transliterated (transhead);')

    for dico in greek_dicos:
        c.execute('insert into Temp select lookupform from Entries where dico=(?)', (dico,))
   
    # Grab all distinct Greek headwords
    c.execute('select distinct * from Temp')
    gheads = c.fetchall()

    hwords = {}
    done = 0
    todo = len(gheads)

    # Transliteration to Roman letters for sorting
    for x in range(todo):
        gheads[x] = gheads[x][0]
        done += 1
        sys.stdout.write('\tGreekHeadwords:%stransliterating %06d/%06d\r' % (spcs, done, todo))
        sys.stdout.flush()
        sort_head = translit(gheads[x])
        
        # Another convoluted work-around: if multiple entries under same sort_head,
        # create a list of them under the sort_head
        """
        if sort_head in hwords.keys():
            hwords[sort_head].append(gheads[x])
        else:
            hwords[sort_head] = [gheads[x]]
        """
        try:
            test = hwords[sort_head]
        except(KeyError):
            hwords[sort_head] = gheads[x]
        else:
            if isinstance(hwords[sort_head], list):
                hwords[sort_head].append(gheads[x])
            else:
                hwords[sort_head] = [hwords[sort_head], gheads[x]]
    
    sys.stdout.write('\tGreekHeadwords:%ssorting%s\r' % (spcs, ' '*22))
    sys.stdout.flush()
        
    sorted_trans = sorted(hwords.keys())
    todo = len(sorted_trans)
    done = 0
    
    sys.stdout.write('\tGreekHeadwords:%sfilling%s\r' % (spcs, ' '*22))
    sys.stdout.flush()
    
    for trans in sorted_trans: # Uses dict to insert correct Greek headwords in order
        #c.executemany('insert into GreekHeadwords values (?)', hwords[trans])
        if isinstance(hwords[trans], list):
            for greekhead in hwords[trans]:
                c.execute('insert into GreekHeadwords values (?)', (greekhead,))
                done += 1
        else:
            c.execute('insert into GreekHeadwords values (?)', (hwords[trans],))
            done += 1

    sys.stdout.write('\tGreekHeadwords:%scomplete.%s\n' % (spcs, ' '*20))

    # Create transliterated table (i.e. Greek alphabet w/o diacritics)
    sys.stdout.write('\tTransliterated:%screating \r' % spcs)
    sys.stdout.flush()
    
    c.execute('select * from GreekHeadwords')
    greek_heads = c.fetchall()
    #greek_heads = map(lambda x: x[0], c.fetchall())
    
    sys.stdout.write('\tTransliterated:%sfilling  \r' % spcs)
    sys.stdout.flush()
    #trans_heads = map(removediacr, greek_heads)
    #c.executemany('insert into Transliterated values (?,?)', greek_heads, trans_heads)
    for head in greek_heads:
        transhead = removediacr(head[0])
        c.execute('insert into Transliterated values (?,?)', (head[0],transhead))

    sys.stdout.write('\tTransliterated:%scomplete.\n' % spcs)

c.execute('drop table Temp')

# Commit changes and exit; only one commit done at the end, so that keyboard interrupts,
# etc. won't screw up the table
print 'Saving...'
conn.commit()

print 'Parsing complete.'

