from cStringIO import StringIO

from . import *

from rvtools.gto import GTO
from rvtools.gto.writer import Writer


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


class TestOldWriter(TestCase):

    def test_old(self):

        fh = StringIO()
        gto = Writer(fh)

        with gto.object('Object'):
            with gto.component('Component'):
                gto.property('float_prop', 3.14)
                gto.property('int_array_prop', [[1, 2, 3, 4]])
                gto.property('string_prop', "hello")

        self.assertSimilarStrings(fh.getvalue(), '''
            GTOa (3)
            Object {
                Component {
                    float float_prop = 3.14
                    int[4] int_array_prop = [ [ 1 2 3 4 ] ]
                    string string_prop = "hello"
                }
            }
        ''')

    def test_new(self):

        gto = GTO(3, Object=dict(
            Component=dict(
                string_prop='hello',
                float_prop=3.14,
                int_array_prop=[[1, 2, 3, 4]],
            )
        ))

        self.assertSimilarStrings(gto.dumps(), '''
            GTOa (3)
            Object {
                Component {
                    float float_prop = 3.14
                    int[4] int_array_prop = [ [ 1 2 3 4 ] ]
                    string string_prop = "hello"
                }
            }
        ''')
