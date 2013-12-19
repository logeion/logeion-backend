logeion-backend
===============

Backend scripts, files, etc. for parsing/updating dictionaries.

General introduction and terms
------------------------------



Process for updating Logeion
----------------------------

**NB:** If you're running any of the Logeion generating scripts, run them in the top-level
Logeion dir (i.e. /Users/Shared/Logeion_parsers on grade)

1.  **If you are not parsing GreekShortDefs or LatinShortDefs, you may skip this step.**  
    To grab Latin and Greek shortdefs, first run:  
        `$ scripts/update_shortdefs.py <lemmastoknow> <lexicon>`  
    This will update the lemmastoknow file with modified entries from the lexicon. Then,  

        $ scripts/grab_lemmastoknow.py <dico> ...
          dico: [HQ | JACT | LTRG | Mastro | shortdefs | all]  

    The appropriately-named files should be in the current directory; put them in the right  
    spots in the dictionaries directory. Make sure that `lemmastoknow.sqlite` is in your  
    current directory.
2.  Then run:  
        `$ ./logeion_parse.py <dico> ([ --latin | --greek | --sidebar ])* ...`  
    to regenerate each dictionary. For example, if you want to parse GreekShortDefs, LatinShortDefs,  
    and all of the textbooks, you would run:  
        `$ ./logeion_parse.py GreekShortDefs LatinShortDefs --sidebar`  
    If you want to regenerate all dictionaries, then just run:  
        `$ ./logeion_parse.py --all`  
    When it's finished, the new database will be in the current directory as `new_dvlg-wheel.sqlite`.  
    `parser.log` will detail any errors that the parsers reported. (They should also be visible on `STDOUT`.)  

    If you're only generating data for one dictionary, then run:  
        `$ ./logeion_parse.py <dico> --db path/to/database.db`

Adding a new dictionary
-----------------------
*   A parser script must have:  
    1.  a method called `parse` which returns a `dict` of values, formatted
            {'head': lemma, 'orth_orig': lemma with proper diacritics, 'content': entire entry}  
        if the dictionary is not a textbook/is not going into the sidebar, and formatted
            {'head': lemma, 'content': entry, 'chapter': chapter num}  
        if it is;
    2.  three global variables called `name`, `type`, and `caps`:  
            + `name`: name of the dictionary (same as dictionary folder)  
            + `type`: `(latin|greek|sidebar)`  
            + `caps`: `(uncapped|source|precapped)`; `uncapped` means that capitalization needs to 
              be performed on it, `source` means that other uncapped dicos should
              be compared to it, and `precapped` means that it shouldn't be touched during
              capitalization.  
*   Regarding clean-up: the standard is to not have diacritics at all in the Latin 
    lemmas (e.g. macrons, breves, circumflexes, etc.).  For Greek lemmas, get rid of 
    anything that isn't an accent, and consult Helma if entries have multiple accents 
    (e.g. they use a circumflex for a macron).
*   Put the new parser in `Logeion_parsers/parsers`. It will be imported automatically.
*   Put all the dico files to be parsed in `Logeion_parsers/dictionaries`, in a folder 
    named the same as the dictionary. (So, `NewDico.xml` should be in `Logeion_parsers/dictionaries/NewDico`.)
*   The `logeion_parse.py` script uses the `parsers/` directory as a plugins directory, i.e.
    it will automatically load all files in that directory and call them appropriately,
    given that they have the appropriate types. It finds the xml files based on the
    `name` property in the parser file.

More on cleaning up dicos
-------------------------
*   It's been the practice to modify textbook entries by adding the unmodified lemma to the
    beginning of the entry content.  For example, `{'amatus, -a, -um': 'beloved'}` would be 
    added to Logeion as `{'amatus': 'amatus, -a, -um, beloved'}`, etc.
*   If the lemma contains diacritics that you're getting rid of, add them to the content
    first.  So, `{'amātus, -a, -um': 'beloved'}` => `{'amatus': 'amātus, -a, -um, beloved'}`.
*   XML entities are evil; excepting the core HTML entities (&(gt|lt|amp|apos|quot);), they should
    all be gone.
