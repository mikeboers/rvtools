import contextlib


def gto_repr(value):

    if isinstance(value, basestring):
        return '"%s"' % value
    elif isinstance(value, (tuple, list)):
        return '[ %s ]' % ' '.join(gto_repr(x) for x in value)
    else:
        return str(value)


class Writer(object):

    def __init__(self, fh):
        self.fh = fh
        self._indent = 0
        self.writeline('GTOa (3)')

    def indent(self, amount=1):
        self._indent += amount

    def dedent(self, amount=1):
        self._indent -= amount

    def writeline(self, line):
        self.fh.write('%s%s\n' % ('\t' * self._indent, line))

    def begin_object(self, name, protocol='object', version=0):
        self.writeline('%s : %s (%d)' % (gto_repr(name), protocol, version))
        self.writeline('{')
        self.indent()

    def end_object(self):
        self.dedent()
        self.writeline('}')

    @contextlib.contextmanager
    def object(self, *args, **kwargs):
        self.begin_object(*args, **kwargs)
        try:
            yield
        finally:
            self.end_object()

    def begin_component(self, name, interpretation=None):
        if interpretation:
            line = '%s as %s' % (gto_repr(name), gto_repr(interpretation))
        else:
            line = gto_repr(name)
        self.writeline(line)
        self.writeline('{')
        self.indent()

    end_component = end_object

    @contextlib.contextmanager
    def component(self, *args, **kwargs):
        self.begin_component(*args, **kwargs)
        try:
            yield
        finally:
            self.end_component()

    def property(self, name, value, type=None, basetype=None, interpretation=None):

        if type is None:
            sizes = []
            to_type = value
            while isinstance(to_type, (list, tuple)):
                sizes.insert(0, len(to_type))
                to_type = to_type[0]
            sizes = sizes[:-1] # ignore the final size

            basetype = basetype or str(to_type.__class__.__name__)
            basetype = {'str': 'string'}.get(basetype, basetype)

            if sizes:
                type = '%s[%s]' % (basetype, ','.join(str(x) for x in sizes))
            else:
                type = basetype

        if interpretation:
            line = '%s %s as %s = %s' % (type, gto_repr(name), interpretation, gto_repr(value))
        else:
            line = '%s %s = %s' % (type, gto_repr(name), gto_repr(value))

        self.writeline(line)





