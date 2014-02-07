from . import *

from rvtools.gto.reader import iter_tokens


class TestGTOLexer(TestCase):

    def test_spaces(self):

        tokens = list(iter_tokens(' aaa bbb '))
        self.assertEqual(tokens, [
            ('SPACE', ' '),
            ('WORD', 'aaa'),
            ('SPACE', ' '),
            ('WORD', 'bbb'),
            ('SPACE', ' '),
        ])

    def test_comment(self):

        tokens = list(iter_tokens('''
            // comment 1
            aaa
            # comment 2
            bbb
        '''))
        tokens = [t for t in tokens if t[0] != 'SPACE']

        self.assertEqual(tokens, [
            ('COMMENT', ' comment 1'),
            ('WORD', 'aaa'),
            ('COMMENT', ' comment 2'),
            ('WORD', 'bbb'),
        ])
