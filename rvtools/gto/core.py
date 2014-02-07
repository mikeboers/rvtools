import collections
import re


rules = [
    (r'(\s+)', 'SPACE' , lambda s: s),
    (r'([+-]?\d*(?:\d\.|\.\d)\d*)' , 'FLOAT' , lambda s: float(s)),
    (r'([+-]?\d+)', 'INTEGER' , lambda s: int(s)), # must be after FLOAT
    (r'(\w+)', 'WORD' , lambda s: s), # must be after INTEGER
    (r'(?:#|//)([^\n\r]*)'  , 'COMMENT', lambda s: s),
    (r'(\()', 'OPEN_PAREN', lambda s: s),
    (r'(\))', 'CLOSE_PAREN', lambda s: s),
    (r'({)', 'OPEN_BRACE', lambda s: s),
    (r'(})', 'CLOSE_BRACE', lambda s: s),
    (r'(\[)', 'OPEN_BRACKET', lambda s: s),
    (r'(\])', 'CLOSE_BRACKET', lambda s: s),
    (r'(:)', 'COLON', lambda s: s),
    (r'(=)', 'EQUALS', lambda s: s),
    (r'"((?:[^"]*(?:\\")?)*)"', 'STRING', lambda s: s.decode('string-escape')),
    (r"'((?:[^']*(?:\\')?)*)'", 'STRING', lambda s: s.decode('string-escape')),
]

rules = [(re.compile(p), t, f) for p, t, f in rules]


_Token = collections.namedtuple('Token', 'type value line column')
class Token(_Token):
    def __str__(self):
        return '<%s %r at %d:%d>' % self


class ParseError(ValueError):

    def __init__(self, msg, token=None):
        if token:
            msg = '%s at line %s, column %s' % (msg, token.line, token.column)
        super(ParseError, self).__init__(msg)
        self.token = token


def iter_tokens(source):
    for line_no, line in enumerate(source):
        start = 0
        while start < len(line):
            for pattern, type_, func in rules:
                m = pattern.match(line, start)
                if m:
                    value = func(*m.groups())
                    yield Token(type_, value, line_no + 1, start)
                    start = m.end(0)
                    break
            else:
                raise ValueError('cannot tokenize past line %d, column %d; %s' % (line_no + 1, start, line[start:]))


def filter_tokens(tokens):
    for token in tokens:
        if token.type not in ('SPACE', 'COMMENT'):
            yield token


class Object(object):

    def __init__(self, name, protocol='object', version=0):
        self.name = name
        self.protocol = protocol
        self.version = version
        self.children = {}

    def append(self, other):
        self.children[other.name] = other

    def iter_dumps(self, indent=''):
        yield indent
        yield self.name
        if self.protocol != 'object':
            yield ' : ' + self.protocol
        if self.version:
            yield ' (%d)' % self.version
        if self.children:
            yield ' {\n'
            for name, child in sorted(self.children.iteritems()):
                for x in child.iter_dumps(indent + '    '):
                    yield x
            yield indent + '}\n'


class Component(object):

    def __init__(self, name, interpretation=None):
        self.name = name
        self.interpretation = interpretation
        self.children = {}

    def append(self, other):
        self.children[other.name] = other

    def iter_dumps(self, indent=''):
        yield indent
        yield self.name
        if self.interpretation:
            yield ' as ' + self.interpretation
        yield ' {\n'
        for name, child in sorted(self.children.iteritems()):
            for x in child.iter_dumps(indent + '    '):
                yield x
        yield indent + '}\n'


class Property(object):

    def __init__(self, name, value, type=None, basetype=None, interpretation=None):
        self.name = name
        self.value = value
        self.type = type or basetype
        self.interpretation = interpretation

    def iter_dumps(self, indent=''):
        yield '%s%s %s = %r\n' % (indent, self.type, self.name, self.value)


class GTO(object):

    def __init__(self):
        self.buffer = []
        self.children = {}

    def iter_dumps(self):
        if self.version:
            yield 'GTOa (%d)' % self.version
        for k, v in sorted(self.children.iteritems()):
            for x in v.iter_dumps():
                yield x

    def dumps(self):
        return ''.join(self.iter_dumps())

    def parse(self, source):
        self.token_iter = filter_tokens(iter_tokens(source))
        self.parse_header()
        while True:
            try:
                self.peek()
            except StopIteration:
                break
            else:
                self.parse_object()

    def peek(self, index=0):
        while len(self.buffer) <= index:
            self.buffer.append(next(self.token_iter))
        return self.buffer[index]

    def next(self, type_=None):

        if self.buffer:
            token = self.buffer.pop(0)
        else:
            token = next(self.token_iter)

        if type_ and token.type != type_:
            self.buffer.insert(0, token)
            raise ParseError('expected %s; got %s %r' % (type_, token.type, token.value), token)

        return token

    def get_word(self):
        return self.next('WORD').value

    def get_int(self):
        return self.next('INTEGER').value

    def parse_header(self):
        magic = self.peek()
        if magic.type == 'WORD' and magic.value == 'GTOa':
            self.next()
            self.next('OPEN_PAREN')
            self.version = self.get_int()
            self.next('CLOSE_PAREN')
        else:
            self.version = None

    def parse_object(self):

        name = self.get_word()
        try:
            self.next('COLON')
        except ValueError:
            protocol = 'object'
        else:
            protocol = self.get_word()

        try:
            self.next('OPEN_PAREN')
        except ValueError:
            version = 0
        else:
            version = self.get_int()
            self.next('CLOSE_PAREN')

        obj = Object(name, protocol, version)
        self.children[obj.name] = obj

        try:
            self.next('OPEN_BRACE')
        except ValueError:
            return
        else:
            while self.peek()[0] != 'CLOSE_BRACE':
                self.parse_component(obj)
            self.next()

    def parse_component(self, parent):

        name = self.peek(0)[1]
        switch = self.peek(1)
        interpretation = None

        if switch == ('WORD', 'as'):
            self.next() # Skip name
            self.next() # Skip "as"
            interpretation = self.get_word()

        elif switch[0] != 'OPEN_BRACE':

            self.parse_property(parent)
            return

        # Skip the brace.
        self.next()

        comp = Component(name, interpretation)
        parent.children[comp.name] = comp

        try:
            self.next('OPEN_BRACE')
        except ValueError:
            return
        else:
            while self.peek()[0] != 'CLOSE_BRACE':
                self.parse_component(comp)
            self.next()

    def get_type(self):
        base = self.get_word()
        if base not in ('string', 'int', 'float'):
            raise ValueError('bad GTO type %r' % base)

        sizes = []
        try:
            while True:
                self.next('OPEN_BRACKET')
                try:
                    while True:
                        sizes.append(self.get_int())
                except ValueError:
                    pass
                self.next('CLOSE_BRACKET')

        except ValueError:
            pass

        return base, sizes

    def get_value(self, inner=False):

        token = self.next()

        if token.type in ('STRING', 'INTEGER', 'FLOAT',):
            return token.value

        if inner and token.type == 'CLOSE_BRACKET':
            return

        if token.type == 'OPEN_BRACKET':
            value = []
            while True:
                sub_v = self.get_value(True)
                if sub_v is None:
                    break
                else:
                    value.append(sub_v)
            return value

        raise ParseError('bad value %s %r' % (token.type, token.value), token)


    def parse_property(self, comp):

        type_, sizes = self.get_type()
        name = self.get_word()

        self.next('EQUALS')

        value = self.get_value()

        prop = Property(name, value, type=type_)
        comp.children[prop.name] = prop

