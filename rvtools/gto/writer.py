"""DEPRECATED.

This is the first API for writing GTO files, and should no longer be used.
Try :module:`rvtools.gto.core` instead.

"""

import contextlib

from .core import GTO, Object, Component, Property


class Writer(object):

    def __init__(self, fh):
        self.fh = fh
        self.fh.write('GTOa (3)\n')
        self.gto = GTO()
        self.stack = []

    def begin_object(self, *args, **kwargs):
        self.stack.append(Object(*args, **kwargs))

    def end_object(self):
        obj = self.stack.pop()
        self.fh.write(''.join(obj.iter_dumps()))

    @contextlib.contextmanager
    def object(self, *args, **kwargs):
        self.begin_object(*args, **kwargs)
        try:
            yield
        finally:
            self.end_object()

    def begin_component(self, *args, **kwargs):
        comp = Component(*args, **kwargs)
        self.stack[-1].add(comp)
        self.stack.append(comp)

    def end_component(self):
        self.stack.pop()

    @contextlib.contextmanager
    def component(self, *args, **kwargs):
        self.begin_component(*args, **kwargs)
        try:
            yield
        finally:
            self.end_component()

    def property(self, *args, **kwargs):
        self.stack[-1].add(Property(*args, **kwargs))

