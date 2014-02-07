from . import *

from rvtools.gto import GTO


class TestGTOWriting(TestCase):

    def test_header(self):

        gto = GTO(3)
        self.assertSimilarStrings(gto.dumps(), 'GTOa (3)')

    def test_constructors(self):

        gto = GTO(object={'component': {'property': 3}})
        self.assertSimilarStrings(gto.dumps(), '''
            object {
                component {
                    int property = 3
                }
            }
        ''')

