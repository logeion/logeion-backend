from glob import glob

name = 'GreekShortDefs'
type = 'greek'
caps = 'precapped'

def clean_head(head):
    return head

def parse(dico_path):
    dico_data = sorted(glob(dico_path+'/GreekShortDefs*'))
    dico = []
    tobelogged = {'warning': [], 'info': []}

    for xmlfile in dico_data:
        for line in open(xmlfile):
            try:
                (head, content) = line.split('SEPARATOR')
                head = clean_head(head).strip()
                content = content.strip()
                attrs = {'head': head, 'content': content}
                dico.append(attrs)
            except(Exception), e:
                tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
                % (xmlfile.split('/')[-1], content[:50], e))

        tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])

    return dico, tobelogged
