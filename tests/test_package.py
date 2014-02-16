import yaml

from rvtools.package import Package

from . import *


class TestPackageInfo(TestCase):

    def test_main(self):

        meta_path = os.path.join(self.sandbox(), 'PACKAGE')
        with open(meta_path, 'w') as fh:
            fh.write(yaml.dump(dict(
                package='test_rvtools_info',
                version='1.0.0',
            ), default_flow_style=False, indent=4))

        pkg = Package(self.sandbox())
        self.assertEqual(pkg.meta['package'], 'test_rvtools_info')
        self.assertEqual(pkg.meta['version'], '1.0.0')

