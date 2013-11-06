from glob import glob
__all__ = map(lambda x: x.split('/')[-1][:-3], glob('parsers/*.py'))
#__all__ = filter(lambda x: x != '__init__' and x != 'lewisshort.old', __all__)
__all__.remove('__init__')
