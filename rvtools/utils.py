import os
import re


def parse_eye(name, default=None):
    m = re.match(r'(.+)_(mono|left|right)', name, re.I)
    if m:
        return m.groups()
    else:
        return name, default


class FileSequence(object):

    # /Volumes/k2r3/vfx_submissions/dpx3/TB_0780_V0012_MONO/2156x1804/tb_0780_v0012_mono.[1008-1160].dpx (153)

    def __init__(self, line):

        m = re.match(r'^(.+) \((\d+)\)$', line)
        if not m:
            raise ValueError('no frame count')

        self.expr, frame_count = m.groups()
        self.frame_count = int(frame_count)

        m = re.search(r'\[(\d+)-(\d+)\]', self.expr)
        if not m:
            raise ValueError('no frame range')
        start, end = m.groups()
        self.start = int(start)
        self.end = int(end)

        if (self.end - self.start) + 1 != self.frame_count:
            raise ValueError('bad start/end/duration combo')

        self.glob = '%s*%s' % (self.expr[:m.start()], self.expr[m.end():])
        self.rv_pattern = '%s#%s' % (self.expr[:m.start()], self.expr[m.end():])
        
        self.fullname = os.path.basename(self.expr).split('.')[0]
        self.name, self.eye = parse_eye(self.fullname)


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



