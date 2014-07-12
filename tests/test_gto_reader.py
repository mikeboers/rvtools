from . import *

from rvtools.gto import loads


class TestGTOReading(TestCase):

    def test_one_object(self):

        gto = loads('''
            GTOa (3)
            Object : Protocol (1) {
                Component {
                    float float_prop = 3.14
                    int[4] int_array_prop = [ [ 1 2 3 4 ] ]
                    string[2] string_array_prop = [ [ "a" "b" ] [ "c" "d" ] ]
                    string string_prop = "hello"
                }
            }
        ''')

        self.assertEqual(gto.version, 3)
        self.assertEqual(len(gto), 1)

        obj = gto['Object']
        self.assertEqual(obj.name, 'Object')
        self.assertEqual(obj.protocol, 'Protocol')
        self.assertEqual(obj.version, 1)
        self.assertEqual(len(obj), 1)

        comp = obj['Component']

        # And so on...

        self.assertEqual(comp['string_prop'].value, 'hello')
