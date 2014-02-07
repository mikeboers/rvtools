import re


rules = [
    (r'(\s+)', 'SPACE' , lambda s: s),
    (r'(\w+)', 'WORD' , lambda s: s),
    (r'(?:#|//)([^\n\r]*)'  , 'COMMENT', lambda s: s),
    (r'(\()', 'OPEN_PAREN', lambda s: s),
    (r'(\))', 'CLOSE_PAREN', lambda s: s),
    (r'({)', 'OPEN_BRACE', lambda s: s),
    (r'(})', 'CLOSE_BRACE', lambda s: s),
    (r'(:)', 'COLON', lambda s: s),
    (r'(=)', 'EQUALS', lambda s: s),
    (r'"((?:[^"]*(?:\\")?)*)"', 'STRING', lambda s: s.decode('string-escape')),
    (r"'((?:[^']*(?:\\')?)*)'", 'STRING', lambda s: s.decode('string-escape')),
    (r'([+-]?\d*(\d\.?|\d?\.)\d*)' , 'FLOAT' , lambda s: float(s)),
]

rules = [(re.compile(p), t, f) for p, t, f in rules]


def iter_tokens(source):

    start = 0
    while start < len(source):
        for pattern, type_, func in rules:
            m = pattern.match(source, start)
            if m:
                token = func(*m.groups())
                yield (type_, token)
                start = m.end(0)
                break
        else:
            raise ValueError('cannot parse past %d: %r' % (start, source[start:]))



class Reader(object):

    def __init__(self):
        self.buffer = []

    def filter_tokens(self, tokens):
        for type_, value in tokens:
            if type_ not in ('SPACE', 'COMMENT'):
                yield type_, value
        yield ('EOF', None)

    def parse(self, source):
        self.token_iter = self.filter_tokens(iter_tokens(source))
        self.parse_header()
        while self.peek()[0] != 'EOF':
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

        if type_ and token[0] != type_:
            self.buffer.insert(0, type_)
            raise ValueError('%s is not %s' % (token[0], type_))

        return token

    def get_word(self):
        return self.next('WORD')[1]

    def get_int(self):
        return int(self.get_word())

    def parse_header(self):
        magic = self.peek()
        if magic == ('WORD', 'GTOa'):
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

        print 'OBJECT', name, protocol, version

        try:
            self.next('OPEN_BRACE')
        except ValueError:
            return
        else:
            while self.peek()[0] != 'CLOSE_BRACE':
                self.parse_component()
            self.next()

    def parse_component(self):

        name = self.peek(0)[1]
        switch = self.peek(1)
        interpretation = None

        if switch == ('WORD', 'as'):
            self.next() # Skip name
            self.next() # Skip "as"
            interpretation = self.get_word()

        elif switch[0] != 'OPEN_BRACE':

            self.parse_property()
            return

        # Skip the brace.
        self.next()

        print 'COMPONENT', name, interpretation

        try:
            self.next('OPEN_BRACE')
        except ValueError:
            return
        else:
            while self.peek()[0] != 'CLOSE_BRACE':
                self.parse_component()
            self.next()

    def get_type(self):

        base = self.get_word()
        if base not in ('string'):
            raise ValueError('bad GTO type %r' % base)

    def get_value(self):

        token = self.next()
        if token[0] == 'WORD':
            token = ('INTEGER', int(token[1]))

        if token[0] not in ('STRING', 'INTEGER'):
            raise ValueError('bad value %r' % token)

        return token


    def parse_property(self):

        type_ = self.get_type()
        name = self.get_word()

        self.next('EQUALS')

        value = self.get_value()

        print 'PROPERTY', type_, name, repr(value)

















if __name__ == '__main__':

    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--lex', action='store_true')
    parser.add_argument('input', nargs='?')
    args = parser.parse_args()

    input_fh = open(args.input) if args.input else sys.stdin

    if args.lex:
        for type_, value in iter_tokens(input_fh.read()):
            print type_, repr(value)

    else:
        parser = Reader()
        parser.parse(input_fh.read())

