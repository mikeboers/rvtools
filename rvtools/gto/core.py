import collections
import itertools
import re


def gto_repr(value, ident=False):

    if isinstance(value, basestring):
        escaped = value.encode('string-escape')
        if ident and value == escaped and not re.search(r'\s+', value):
            return value
        return '"%s"' % escaped

    elif isinstance(value, (tuple, list)):
        return '[ %s ]' % ' '.join(gto_repr(x) for x in value)

    else:
        return str(value)


def gto_type(value, base=None):
    sizes = []
    to_type = value
    while isinstance(to_type, (list, tuple)) and to_type:
        sizes.insert(0, len(to_type))
        to_type = to_type[0]
    sizes = sizes[:-1] # ignore the final size

    base = base or str(to_type.__class__.__name__)
    base = {'str': 'string'}.get(base, base)

    if sizes:
        return '%s[%s]' % (base, ','.join(str(x) for x in sizes))
    else:
        return base


class Base(collections.MutableMapping):
    
    def __init__(self, *args, **kwargs):
        self._children = {}
        for x in itertools.chain(args, [kwargs]):
            self.update(x)

    def __getitem__(self, key):
        return self._children[key]

    def __delitem__(self, key):
        return self._children[key]

    def __setitem__(self, key, value):

        if isinstance(value, dict) and not isinstance(value, Base):
            value = self._child_class(key, **value)
        elif not isinstance(value, (Base, Property)):
            value = Property(key, value)

        self._children[key] = value

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return iter(self._children)

    def add(self, obj, *args, **kwargs):
        if not isinstance(obj, (Base, Property)):
            obj = self._child_class(obj, *args, **kwargs)
        self._children[obj.name] = obj
        return obj


class Object(Base):

    def __init__(self, name, protocol='object', version=0, **kwargs):
        super(Object, self).__init__(kwargs)
        self.name = name
        self.protocol = protocol
        self.version = version

    def iter_dumps(self, indent=''):
        yield indent
        yield gto_repr(self.name, True)
        if self.protocol != 'object':
            yield ' : ' + gto_repr(self.protocol, True)
        if self.version:
            yield ' (%d)' % self.version
        yield '\n%s{\n' % indent
        for i, (name, child) in enumerate(sorted(self._children.iteritems())):
            if i:
                yield '\n'
            for x in child.iter_dumps(indent + '    '):
                yield x
        yield '%s}\n' % indent


class Component(Base):

    def __init__(self, name, interpretation=None, **kwargs):
        super(Component, self).__init__(kwargs)
        self.name = name
        self.interpretation = interpretation

    def iter_dumps(self, indent=''):
        yield indent
        yield gto_repr(self.name, True)
        if self.interpretation:
            yield ' as '
            yield gto_repr(self.interpretation, True)
        yield '\n%s{\n' % indent
        for name, child in sorted(self._children.iteritems()):
            for x in child.iter_dumps(indent + '    '):
                yield x
        yield '%s}\n' % indent


class Property(object):

    def __init__(self, name, value, type=None, basetype=None, interpretation=None):
        self.name = name
        self.value = value
        self.type = type or basetype
        self.interpretation = interpretation

    def iter_dumps(self, indent=''):
        yield indent
        yield gto_type(self.value, self.type)
        yield ' '
        yield gto_repr(self.name, True)
        yield ' = '
        yield gto_repr(self.value)
        yield '\n'


class GTO(Base):

    def __init__(self, version=None, **kwargs):
        super(GTO, self).__init__(kwargs)
        self.version = version

    def iter_dumps(self):
        if self.version:
            yield 'GTOa (%d)\n' % self.version
        for i, (k, v) in enumerate(sorted(self._children.iteritems())):
            if self.version or i:
                yield '\n'
            for x in v.iter_dumps():
                yield x

    def dumps(self):
        return ''.join(self.iter_dumps())


Object._child_class = Component
Component._child_class = Component
GTO._child_class = Object


