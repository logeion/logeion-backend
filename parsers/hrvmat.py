name = 'hrvmatlat'
type = 'latin'
caps = 'precapped'
convert_xml = False
enabled = False

def parse(dico_path, log, log_error):
  xmlfile = dico_path+'/hrvmatlat.csv'
  dico = []
  errors_occurred = False

  for line in open(xmlfile):
    try:
      head, content = line.strip().split('\t')
      attrs = {'head': head, 'content': content.decode('utf-8')}
      dico.append(attrs)
    except(Exception), e:
        log_error("%s couldn't parse line \"%s\"...: %s" \
            % (xmlfile.split('/')[-1], content[:50], e))
        errors_occurred = True
  log('%s finished parsing' % xmlfile.split('/')[-1])
  dico = sorted(dico, key=lambda e: e['head'])
  return dico, errors_occurred
    
