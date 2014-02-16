import datetime
import os
import re
from unittest import TestCase as _TestCase

from rvtools.utils import mkdir, cached_property


now = datetime.datetime.now()

class TestCase(_TestCase):

    def sandbox(self):

        root = os.path.abspath(os.path.join(__file__, '..', 'sandbox'))
        per_run = os.path.join(root, now.isoformat('T'))
        per_case = os.path.join(per_run, self.__class__.__name__)
    
        mkdir(per_case)

        link = os.path.join(root, 'last')
        try:
            os.unlink(link)
        except OSError:
            pass    
        os.symlink(per_run, link)
        
        return per_case

    def assertSimilarStrings(self, a, b, *args):
        a = re.sub(r'\s+', ' ', a.strip())
        b = re.sub(r'\s+', ' ', b.strip())
        self.assertEqual(a, b, *args)

