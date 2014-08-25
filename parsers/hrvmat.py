name = 'hrvmatlat'
type = 'latin'
caps = 'precapped'
convert_xml = False

def parse(dico_path):
  xmlfile = dico_path+'/hrvmatlat.csv'
  dico = []
  tobelogged = {'warning': [], 'info': []}

  for line in open(xmlfile):
    try:
      head, content = line.strip().split('\t')
      attrs = {'head': head, 'content': content.decode('utf-8')}
      dico.append(attrs)
    except(Exception), e:
        tobelogged['warning'].append("%s couldn't parse line \"%s\"...: %s" \
        % (xmlfile.split('/')[-1], content[:50], e))
  tobelogged['info'].append('%s finished parsing' % xmlfile.split('/')[-1])
  dico = sorted(dico, key=lambda e: e['head'])
  return dico, tobelogged
    
