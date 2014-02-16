import collections
import os
import zipfile
from subprocess import check_output

import yaml


_envs = []
def get_envs():
    if not _envs:
        envs = check_output(['rvpkg', '-env']).strip().splitlines()
        envs = [e.strip() for e in envs]
        envs = [os.path.dirname(e) for e in envs if e.endswith('Packages')]
        _envs.extend(envs)
    return _envs[:]


InstallItem = collections.namedtuple('InstallItem', 'installed basename')
def loads_rvinstall(encoded):
    res = []
    for line in encoded.splitlines():
        line = line.strip()
        if not line:
            continue
        installed = line.startswith('*')
        if installed:
            line = line[1:]
        res.append(InstallItem(installed, line))
    return res


def read_package_metadata(path):
    zip_fh = zipfile.ZipFile(path)
    encoded_package = zip_fh.read('PACKAGE')
    return yaml.load(encoded_package)


def iter_installed(env):

    try:
        with open(os.path.join(env, 'Packages', 'rvinstall')) as fh:
            rvinstall = loads_rvinstall(fh.read())
    except IOError:
        return

    for install in rvinstall:
        path = os.path.join(env, 'Packages', install.basename)
        meta = read_package_metadata(path)
        yield path, install.installed, meta


def main():

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-E', '--list-envs', action='store_true')
    parser.add_argument('-l', '--list', action='store_true')

    parser.add_argument('-a', '--add', action='store_true')
    parser.add_argument('-r', '--remove', action='store_true')

    parser.add_argument('-i', '--install', action='store_true')
    parser.add_argument('-u', '--uninstall', action='store_true')

    parser.add_argument('-f', '--force', action='store_true')

    parser.add_argument('-e', '--env')
    parser.add_argument('package', nargs='*')

    args = parser.parse_args()

    if args.list_envs:
        for env in get_envs():
            print env
        return

    if args.list:
        pkgs = []
        for env in get_envs():
            pkgs.extend(iter_installed(env))
        pkgs.sort(key=lambda (p, i, m): (m['package'], i, p))

        for path, installed, meta in pkgs:
            print '%s "%s" v%s: %s' % (
                '*' if installed else ' ',
                meta['package'],
                meta['version'],
                path,
            )
        return

    for pkg in args.package:
        process_one(pkg, args)


def process_one(package, args):

    print package





if __name__ == '__main__':
    main()
