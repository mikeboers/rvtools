import contextlib

from .core import gto_repr, gto_type


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
        name = gto_repr(name, True)
        if protocol != 'object':
            name = '%s : %s' % (name, protocol)
        if version:
            name = '%s (%d)' % (name, version)
        self.writeline(name)
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
            line = '%s as %s' % (gto_repr(name, True), gto_repr(interpretation))
        else:
            line = gto_repr(name, True)
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

        type = type or gto_type(value, basetype)
        if interpretation:
            line = '%s %s as %s = %s' % (type, gto_repr(name, True), interpretation, gto_repr(value))
        else:
            line = '%s %s = %s' % (type, gto_repr(name, True), gto_repr(value))

        self.writeline(line)





