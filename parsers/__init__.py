from glob import glob
__all__ = map(lambda x: x.split('/')[-1][:-3], glob('parsers/*.py'))
__all__.remove('__init__')
