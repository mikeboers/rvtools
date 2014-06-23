from rvtools.utils import FileSequence, split_flags

from . import *


class TestUtils(TestCase):

	def test_split_flags(self):
		
		name, flags = split_flags('basename')
		self.assertEqual(name, 'basename')
		self.assertEqual(flags, {})

		name, flags = split_flags('basename_mono_n')
		self.assertEqual(name, 'basename')
		self.assertEqual(flags, {
			'eye': 'mono',
			'grade': 'n',
		})

		name, flags = split_flags('basename_n_mono')
		self.assertEqual(name, 'basename')
		self.assertEqual(flags, {
			'eye': 'mono',
			'grade': 'n',
		})

	def test_split_flags_case(self):
		name, flags = split_flags('basename_n_MONO')
		self.assertEqual(name, 'basename')
		self.assertEqual(flags, {
			'eye': 'mono',
			'grade': 'n',
		})

	def test_split_flags_noname(self):
		name, flags = split_flags('')
		self.assertEqual(name, '')
		self.assertEqual(flags, {})

	def test_file_sequence(self):

		seq = FileSequence('/path/to/tb_0780_v0012_mono.[1008-1160].dpx (153)')
		self.assertEqual(seq.start, 1008)
		self.assertEqual(seq.end, 1160)
		self.assertEqual(seq.frame_count, 153)
		self.assertEqual(seq.full_name, 'tb_0780_v0012_mono')
		self.assertEqual(seq.prefix, '/path/to/tb_0780_v0012_mono.')
		self.assertEqual(seq.suffix, '.dpx')
		self.assertEqual(seq.name, 'tb_0780_v0012')
		self.assertEqual(seq.eye, 'mono')
		self.assertEqual(seq.grade, None)
		self.assertEqual(seq.expr, '/path/to/tb_0780_v0012_mono.[1008-1160].dpx')
		self.assertEqual(seq.pattern, '/path/to/tb_0780_v0012_mono.{}.dpx')

		seq = FileSequence('/path/to/tb_0780_v0012_n.[1008-1160].dpx (153)')
		self.assertEqual(seq.grade, 'n')


	def test_file_sequence_movie(self):

		seq = FileSequence('/path/to/tb_0780_v0012_mono.mov')
		self.assertEqual(seq.start, None)
		self.assertEqual(seq.end, None)
		self.assertEqual(seq.frame_count, None)
		self.assertEqual(seq.full_name, 'tb_0780_v0012_mono')
		self.assertEqual(seq.prefix, '/path/to/tb_0780_v0012_mono') # Note that this is a little different!
		self.assertEqual(seq.suffix, '.mov')
		self.assertEqual(seq.name, 'tb_0780_v0012')
		self.assertEqual(seq.eye, 'mono')
		self.assertEqual(seq.expr, '/path/to/tb_0780_v0012_mono.mov')
		self.assertEqual(seq.pattern, '/path/to/tb_0780_v0012_mono.mov')
