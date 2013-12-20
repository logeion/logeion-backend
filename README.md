logeion-backend
===============

Backend scripts, files, etc. for parsing/updating dictionaries. Feel free to pull this to
add your own dictionaries/try out Logeion for yourself; instructions for doing so are
<a href="#deploying-logeion">at the bottom</a> of this README.


Process for updating Logeion
----------------------------

**NB:** If you're running any of the Logeion generating scripts, run them in the top-level
Logeion dir (i.e. /Users/Shared/Logeion_parsers on grade)

1.  **If you are not parsing GreekShortDefs or LatinShortDefs, you may skip this step.**  
    To grab Latin and Greek shortdefs, first run:  
        `$ scripts/update_shortdefs.py <lemmastoknow db> <lexicon db>`  
    This will update the lemmastoknow file with modified entries from the lexicon. Then,  

        $ scripts/grab_lemmastoknow.py <dico> ...
          dico: [HQ | JACT | LTRG | Mastro | shortdefs | all]  

    The appropriately-named files should be in the current directory; put them in the right
    spots in the dictionaries directory. Make sure that `lemmastoknow.sqlite` is in your
    current directory.
2.  Then run:  
        `$ ./logeion_parse.py <name of dictionary> ([ --latin | --greek | --sidebar ])* ...`  
    to regenerate each dictionary. For example, if you want to parse GreekShortDefs, LatinShortDefs,
    and all of the textbooks, you would run:  
        `$ ./logeion_parse.py GreekShortDefs LatinShortDefs --sidebar`  
    If you want to regenerate all dictionaries, then just run:  
        `$ ./logeion_parse.py --all`  
    When it's finished, the new database will be in the current directory as `new_dvlg-wheel.sqlite`.
    `parser.log` will detail any errors that the parsers reported. (They should also be visible on `STDOUT`.)
3.  If you're only generating data for one dictionary, then run:  
        `$ ./logeion_parse.py <name of dictionary>`  
    For any of the above, if you wish modify/create a specifically-named dictionary, use the
    `--db` option; for example, to reparse all of the Latin and Greek dictionaries in `dvlg-wheel.sqlite`,
    run:  
        `$ ./logeion_parse.py --latin --greek --db dvlg-wheel.sqlite`  
    Note that, since `new_dvlg-wheel.sqlite` is the default database name, running `logeion_parse.py` with
    `new_dvlg-wheel.sqlite` in your current directory will overwrite whatever dictionaries your are parsing.


Adding a new dictionary
-----------------------
*   A parser script must have:  
    1.  a method called `parse` which returns a list of `dict`s of values. Each entry in the list should
        be formatted as such if the dictionary is not textbook:  
            `{'head': lemma, 'orth_orig': lemma with proper diacritics, 'content': entire entry}`  
        and as such if it is a textbook:  
            `{'head': lemma, 'content': entire entry, 'chapter': chapter num}`;
    2.  three global variables called `name`, `type`, and `caps`:  
            + `name`: name of the dictionary (same as dictionary folder)  
            + `type`: `(latin|greek|sidebar)`  
            + `caps`: `(uncapped|source|precapped)`; `uncapped` means that capitalization needs to
              be performed on it, `source` means that other `uncapped` dictionaries should
              be compared to it, and `precapped` means that it shouldn't be touched during
              capitalization.  
    With regard to capitalization: if the lemmas are in all-caps in the source texts, then normalize
    them to all-lowercase in the output (but keep them the same in the actual entry). `logeion_parse.py`
    runs a routine that attempts to guess proper capitalization based on other similar lemmas, and might
    not work correctly if the lemmas for a given directory are all capitalized.
*   Regarding clean-up: the standard is to not have diacritics at all in the Latin
    lemmas (e.g. macrons, breves, circumflexes, etc.).  For Greek lemmas, get rid of
    anything that isn't an accent, and consult Helma if entries have multiple accents
    (e.g. they use a circumflex for a macron).
*   Put the new parser in `Logeion_parsers/parsers`. The `logeion_parse.py` script uses the
    `parsers/` directory as a plugins directory, i.e. it will automatically load all files in
    that directory and call them appropriately, given that they have the appropriate types.
    It finds the xml files based on the `name` property in the parser file.
*   Put all the dictionary files to be parsed in `Logeion_parsers/dictionaries`, in a folder
    named the same as the dictionary. (E.g. `NewDico.xml` should be in `Logeion_parsers/dictionaries/NewDico`.)
   

More on cleaning up dictionaries
-------------------------
*   It's been the practice to modify textbook entries by adding the unmodified lemma to
    the beginning of the entry          content.  For example, `{'amatus, -a, -um': 'beloved'}`
    would be added to Logeion as `{'amatus': 'amatus, -a, -um,      beloved'}`, etc.
*   If the lemma contains diacritics that you're getting rid of, add them to the content
    first.  So, `{'amātus, -a, -um': 'beloved'}` => `{'amatus': 'amātus, -a, -um, beloved'}`.
*   XML entities are evil; excepting the core HTML entities (&(gt|lt|amp|apos|quot);), they should
    all be gone.


Schemata for various databases
------------------------------
dvlg-wheel.sqlite:  

    CREATE TABLE Entries(head text, orth_orig text, content text, dico text, lookupform text);
    CREATE INDEX lookupform_index_e on Entries (lookupform);
    CREATE TABLE Sidebar(head text, content text, chapter text, dico text, lookupform text);
    CREATE INDEX lookupform_index_s on Sidebar (lookupform);
    CREATE TABLE LatinHeadwords (head text);
    CREATE TABLE GreekHeadwords (head text);
    CREATE TABLE Transliterated (normhead text, transhead text);
    CREATE INDEX trans_index on Transliterated (transhead);

(greek|latin)Info.db:

    CREATE TABLE authorFreqs(lemma text, rank integer, author text, freq float, lookupform text);
    CREATE TABLE collocations (lemma text, collocation text, count integer, lookupform text);
    CREATE TABLE frequencies (lemma text, rank integer, count integer, rate real, lookupform text);
    CREATE TABLE samples (lemma text, rank integer, sample text, author text, work text);
    CREATE INDEX aF_l on authorFreqs(lookupform);
    CREATE INDEX c_l on collocations(lookupform);
    CREATE INDEX f_l on frequencies(lookupform);
    CREATE INDEX s_lem on samples(lemma);


Deploying Logeion
-----------------

If you want to deploy Logeion to a new server, or want to check it out and test it/make it your own,
follow these steps. (Sample databases are located
<a href="https://sourceforge.net/p/logeion/files/?source=navbar">here</a>.)

1.  **If you want to add your own dictionaries/data, follow this step; otherwise, go to step 2.**  
    Checkout the backend code. Follow the instructions for adding a new parser and putting the
    dictionary files in the correct places. If you want to generate a database with just your
    data, then run  
        `$ ./logeion_parse.py <name of dictionary>`  
    If you want to add on to the provided `dvlg-wheel-mini.sqlite`, then run  
        `$ ./logeion_parse.py <name of dictionary> --db dvlg-wheel-mini.sqlite`  
    (assuming `dvlg-wheel-mini.sqlite` is in your current directory).  
    If your dictionary is in CSV format or you want to preserve its current (X|HT)ML structure, then
    you will want to add its name (i.e. the value of the `name` property in the parser) to the tuple
    in lines 394-5 of `logeion_parse.py`. *(Very hacky; will be updated ASAP.)*
2.  Once you have a database appropriately structured (either from step 1 or from the SourceForge links
    above), checkout the CGI and HTML repos (`logeion-cgi` and `logeion-html`, respectively). The files
    on the `master` branch require the two directories `cgi-bin` and `html` to be siblings, though feel
    free to change this as needed.
3.  Add all relevant databases to the CGI directory. Logeion requires `greekInfo.db`, `latinInfo.db`, and
    `dvlg-wheel.sqlite`. For the last, you may also rename `dvlg-wheel-mini.sqlite` or edit
    the CGI scripts so that they point to the correct file.
4.  After configuring your server appropriately, you should be good to go! Direct any questions/issues to
    Helma Dik (helmadik@gmail.com) or Matt Shanahan (mrshanahan@uchicago.edu).
