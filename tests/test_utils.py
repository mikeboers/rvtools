from rvtools.utils import FileSequence

from . import *


class TestUtils(TestCase):

	def test_file_sequence(self):

		seq = FileSequence('/path/to/tb_0780_v0012_mono.[1008-1160].dpx (153)')
		self.assertEqual(seq.start, 1008)
		self.assertEqual(seq.end, 1160)
		self.assertEqual(seq.frame_count, 153)
		self.assertEqual(seq.full_name, 'tb_0780_v0012_mono')
		self.assertEqual(seq.name, 'tb_0780_v0012')
		self.assertEqual(seq.eye, 'mono')
		self.assertEqual(seq.expr, '/path/to/tb_0780_v0012_mono.[1008-1160].dpx')
		self.assertEqual(seq.glob, '/path/to/tb_0780_v0012_mono.*.dpx')
		self.assertEqual(seq.rv_pattern, '/path/to/tb_0780_v0012_mono.#.dpx')

	def test_file_sequence_movie(self):

		seq = FileSequence('/path/to/tb_0780_v0012_mono.mov')
		self.assertEqual(seq.start, None)
		self.assertEqual(seq.end, None)
		self.assertEqual(seq.frame_count, None)
		self.assertEqual(seq.full_name, 'tb_0780_v0012_mono')
		self.assertEqual(seq.name, 'tb_0780_v0012')
		self.assertEqual(seq.eye, 'mono')
		self.assertEqual(seq.expr, '/path/to/tb_0780_v0012_mono.mov')
		self.assertEqual(seq.glob, '/path/to/tb_0780_v0012_mono.mov')
		self.assertEqual(seq.rv_pattern, '/path/to/tb_0780_v0012_mono.mov')
