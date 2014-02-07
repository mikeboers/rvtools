import os
import re


flag_types = {
    'mono': 'eye',
    'left': 'eye',
    'right': 'eye',
    'n': 'grade',
}


def split_flags(name):

    flags = {}

    flags_re = r'^(.+?)((?:_(?:%s))*)$' % '|'.join(flag_types)
    m = re.match(flags_re, name.lower())

    for flag in m.group(2).strip('_').split('_'):
        if flag:
            flags[flag_types[flag]] = flag

    return m.group(1), flags


class FileSequence(object):
    
    """One line of ld_tree.py output."""

    # /Volumes/k2r3/vfx_submissions/dpx3/TB_0780_V0012_MONO/2156x1804/tb_0780_v0012_mono.[1008-1160].dpx (153)

    def __init__(self, line):

        m = re.match(r'^(.+) \((\d+)\)$', line)
        if not m:
            self.start = self.end = self.frame_count = None
            self.expr = self.pattern = line
            self.suffix = os.path.splitext(self.expr)[1]

        else:

            self.expr, frame_count = m.groups()
            self.frame_count = int(frame_count)

            m = re.search(r'\[(\d+)-(\d+)\]', self.expr)
            if not m:
                raise ValueError('cannot find sequence')

            start, end = m.groups()
            self.start = int(start)
            self.end = int(end)

            if (self.end - self.start) + 1 != self.frame_count:
                raise ValueError('bad start/end/duration combo')

            self.prefix = self.expr[:m.start()]
            self.suffix = self.expr[m.end():]
            self.pattern = '%s{}%s' % (self.prefix, self.suffix)
        
        self.full_name = os.path.basename(self.expr).split('.')[0]
        self.name, self.flags = split_flags(self.full_name)

    @property
    def eye(self):
        return self.flags.get('eye')

    @property
    def grade(self):
        return self.flags.get('grade')

    @property
    def first_frame(self):
        if self.start:
            return self.pattern.format(self.start)
        else:
            return self.expr


def parse_ld_tree_output(fh):

    for line in fh:

        line = line.strip()
        if not line or line[0] == '#':
            continue

        try:
            seq = FileSequence(line)
        except ValueError as e:
            raise ValueError('%s in %r' % (e.args[0], line))

        yield seq



