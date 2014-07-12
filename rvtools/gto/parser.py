import collections
import re

from .core import GTO, Object, Component, Property


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



class Parser(object):

    def __init__(self, gto):
        self.gto = gto
        self._buffer = []

    def parse(self, source):
        self._token_iter = filter_tokens(iter_tokens(source))
        self._parse_header()
        while True:
            try:
                self._peek()
            except StopIteration:
                break
            else:
                self._parse_object()

    def _peek(self, index=0):
        while len(self._buffer) <= index:
            self._buffer.append(next(self._token_iter))
        return self._buffer[index]

    def _next(self, type_=None):

        if self._buffer:
            token = self._buffer.pop(0)
        else:
            token = next(self._token_iter)

        if type_ and token.type != type_:
            self._buffer.insert(0, token)
            raise ParseError('expected %s; got %s %r' % (type_, token.type, token.value), token)

        return token

    def _get_word(self):
        return self._next('WORD').value

    def _get_int(self):
        return self._next('INTEGER').value

    def _parse_header(self):
        magic = self._peek()
        if magic.type == 'WORD' and magic.value == 'GTOa':
            self._next()
            self._next('OPEN_PAREN')
            self.gto.version = self._get_int()
            self._next('CLOSE_PAREN')
        else:
            self.gto.version = None

    def _parse_object(self):

        name = self._get_word()
        try:
            self._next('COLON')
        except ValueError:
            protocol = 'object'
        else:
            protocol = self._get_word()

        try:
            self._next('OPEN_PAREN')
        except ValueError:
            version = 0
        else:
            version = self._get_int()
            self._next('CLOSE_PAREN')

        obj = self.gto.add(Object(name, protocol, version))

        try:
            self._next('OPEN_BRACE')
        except ValueError:
            return
        else:
            while self._peek()[0] != 'CLOSE_BRACE':
                self._parse_component(obj)
            self._next()

    def _parse_component(self, parent):

        name = self._peek(0)[1]
        switch = self._peek(1)
        interpretation = None

        if switch == ('WORD', 'as'):
            self._next() # Skip name
            self._next() # Skip "as"
            interpretation = self._get_word()

        elif switch[0] != 'OPEN_BRACE':

            self._parse_property(parent)
            return

        # Skip the brace.
        self._next()

        comp = parent.add(Component(name, interpretation))

        try:
            self._next('OPEN_BRACE')
        except ValueError:
            return
        else:
            while self._peek()[0] != 'CLOSE_BRACE':
                self._parse_component(comp)
            self._next()

    def _get_type(self):
        base = self._get_word()
        if base not in ('string', 'int', 'float'):
            raise ValueError('bad GTO type %r' % base)

        sizes = []
        try:
            while True:
                self._next('OPEN_BRACKET')
                try:
                    while True:
                        sizes.append(self._get_int())
                except ValueError:
                    pass
                self._next('CLOSE_BRACKET')

        except ValueError:
            pass

        return base, sizes

    def _get_value(self, inner=False):

        token = self._next()

        if token.type in ('STRING', 'INTEGER', 'FLOAT',):
            return token.value

        if inner and token.type == 'CLOSE_BRACKET':
            return

        if token.type == 'OPEN_BRACKET':
            value = []
            while True:
                sub_v = self._get_value(True)
                if sub_v is None:
                    break
                else:
                    value.append(sub_v)
            return value

        raise ParseError('bad value %s %r' % (token.type, token.value), token)


    def _parse_property(self, comp):

        type_, sizes = self._get_type()
        name = self._get_word()

        self._next('EQUALS')

        value = self._get_value()

        comp.add(Property(name, value, type=type_))


def loads(input_):
    return load(input_.splitlines())

def load(input_):
    gto = GTO()
    parser = Parser(gto)
    parser.parse(input_)
    return gto


