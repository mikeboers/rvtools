
class Object(object):

    def __init__(self, name, protocol='object', version=0):
        self.name = name
        self.protocol = protocol
        self.version = version
        self.children = {}

    def append(self, other):
        self.children[other.name] = other

    def pprint(self, indent=''):
        print '%s%s%s%s%s' % (
            indent,
            self.name,
            ' : ' + self.protocol if self.protocol != 'object' else '',
            ' (%d)' % self.version if self.version else '',
            ' {' if self.children else '',
        )
        for k, v in sorted(self.children.iteritems()):
            v.pprint(indent + '    ')
        if self.children:
            print '%s}' % (indent, )



class Component(object):

    def __init__(self, name, interpretation=None):
        self.name = name
        self.interpretation = interpretation
        self.children = {}

    def append(self, other):
        self.children[other.name] = other

    def pprint(self, indent=''):
        print '%s%s%s {' % (indent, self.name, ' as ' + self.interpretation if self.interpretation else '')
        for k, v in sorted(self.children.iteritems()):
            v.pprint(indent + '    ')
        print '%s}' % (indent, )


class Property(object):

    def __init__(self, name, value, type=None, basetype=None, interpretation=None):
        self.name = name
        self.value = value
        self.type = type or basetype
        self.interpretation = interpretation

    def pprint(self, indent=''):
        print '%s%s %s = %r' % (indent, self.type, self.name, self.value)
