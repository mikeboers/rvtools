import re
from unittest import TestCase as _TestCase


class TestCase(_TestCase):

    def assertSimilarStrings(self, a, b, *args):
        a = re.sub(r'\s+', ' ', a.strip())
        b = re.sub(r'\s+', ' ', b.strip())
        self.assertEqual(a, b, *args)

