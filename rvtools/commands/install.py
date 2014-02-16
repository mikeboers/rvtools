from __future__ import print_function
import argparse
import os
import re
import sys
from shutil import copy
from subprocess import check_output, call


def iter_existing():
    raw = check_output(['rvpkg', '-list'])
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue

        m = re.match(r'^([I-]) ([L-]) ([O-]) ([\w\.-]+) "([^"]*)" (.+)$', line)
        if not m:
            print('{}: could not match line: {}'.format(sys.argv[0], line), file=sys.stderr)
            continue

        installed_flag, loaded_flag, optional_flag, version, name, path = m.groups()
        yield {
            'installed': installed_flag == 'I',
            'loaded': loaded_flag == 'L',
            'optional': optional_flag == 'O',
            'version': version,
            'name': name,
            'path': path,
        }


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='/Users/mikeboers/Library/Application Support/RV')
    parser.add_argument('package', nargs='+')
    args = parser.parse_args()

    for pkg in args.package:
        install(pkg, args)

def install(package, args):

    pkg_path = package
    pkg_base = os.path.basename(pkg_path)

    for installed in iter_existing():
        if pkg_base == os.path.basename(installed['path']):
            call(['rvpkg', '-remove', '-force', installed['path']])

    if False:
        dst_path = os.path.join(args.dir, 'Packages', pkg_base)
        copy(pkg_path, dst_path)        
        call(['rvpkg', '-force', '-install', dst_path])
    else:
        call(['rvpkg', '-force', '-install', '-add', args.dir, package])


