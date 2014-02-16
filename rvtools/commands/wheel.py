import argparse
import errno
import os
import re
import shutil
import zipfile
from subprocess import call

import yaml

from rvtools.utils import mkdir


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--build', default='build')
    parser.add_argument('-t', '--target', default='.')
    parser.add_argument('package', nargs='+')
    args = parser.parse_args()

    for pkg in args.package:
        wheel(pkg, args)


def wheel(package, args):

    build_dir = os.path.join(args.build, re.sub(r'\W+', '-', package).strip('-'))
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    call(['pip', 'wheel', '--no-deps', '-w', build_dir, package])

    # Get the metadata.
    wheels = os.listdir(build_dir)
    if len(wheels) != 1:
        raise RuntimeError('`pip wheel` resulted in more than one file')
    wheel_path = os.path.join(build_dir, wheels[0])
    zip_fh = zipfile.ZipFile(wheel_path)
    metadata_path = [name for name in zip_fh.namelist() if name.endswith('METADATA')][0]
    metadata_lines = zip_fh.read(metadata_path).splitlines()
    metadata = dict(line.split(': ', 1) for line in metadata_lines if ':' in line)

    pkg_dir = build_dir + '-rvpkg'
    if os.path.exists(pkg_dir):
        shutil.rmtree(pkg_dir)
    os.makedirs(pkg_dir)

    call(['unzip', os.path.abspath(wheel_path)], cwd=pkg_dir)

    files_list = []
    for dir_path, dir_names, file_names in os.walk(pkg_dir):
        rel_dir = os.path.relpath(dir_path, pkg_dir)
        for file_name in file_names:
            if file_name.startswith('.'):
                continue
            files_list.append({
                'file': os.path.join(rel_dir, file_name),
                'location': os.path.join('Python/$PACKAGE', rel_dir),
            })

    version = re.sub(r'[^\d]+', '.', metadata['Version']).strip('.')
    version = '.'.join((version.split('.') + ['0', '0'])[:2])
    rvpkg_metadata = {
        'package': 'python_' + metadata['Name'],
        'version': version,
        'files': files_list,
    }

    with open(os.path.join(pkg_dir, 'PACKAGE'), 'w') as fh:
        fh.write(yaml.dump(rvpkg_metadata, indent=4, default_flow_style=False, canonical=True))

    pkg_name = 'python_%s-%s.rvpkg' % (metadata['Name'], version)
    pkg_path = os.path.join(args.build, pkg_name)
    call(['zip', '-r', os.path.abspath(pkg_path)] + os.listdir(pkg_dir), cwd=pkg_dir)


