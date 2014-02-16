from __future__ import print_function

import collections
import os
import sys
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


def error(x):
    print('%s: %s', file=sys.stderr)


def confirm(msg, args):
    msg = '%s [Yn]:' % msg
    print(msg, endl=' ')
    return args.yes or raw_input().lower().startswith('y')


def main():

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-E', '--list-envs', action='store_true', help='list all support areas')
    parser.add_argument('-l', '--list', action='store_true', help='list all packages')

    parser.add_argument('-c', '--copy', action='store_true', help='copy package to support area')
    parser.add_argument('-r', '--remove', action='store_true', help='remove package from support area')

    parser.add_argument('-i', '--install', action='store_true', help='install package')
    parser.add_argument('-u', '--uninstall', action='store_true', help='uninstall package')

    parser.add_argument('-y', '--yes', action='store_true', help='respond "yes" to all questions')

    parser.add_argument('-e', '--env', help='use this support area; defaults to first')
    parser.add_argument('package', nargs='*')

    args = parser.parse_args()


    command_count = (
        int(args.copy or args.install) +
        int(args.remove or args.uninstall) + 
        int(args.list) + 
        int(args.list_envs)
    )
    if command_count != 1:
        parser.print_usage()
        exit(1)

    if args.list_envs:
        for env in get_envs():
            print(env)
        return

    if args.list:
        pkgs = []
        for env in [args.env] if args.env else get_envs():
            pkgs.extend(iter_installed(env))
        pkgs.sort(key=lambda (p, i, m): (m['package'], i, p))

        for path, installed, meta in pkgs:
            print('%s "%s" v%s: %s' % (
                '*' if installed else ' ',
                meta['package'],
                meta['version'],
                path,
            ))
        return

    if not args.package:
        parser.error('package is required')

    for pkg in args.package:
        process_one(pkg, args)


def process_one(package, args):

    env = args.env or get_envs()[0]
    if not os.path.exists(env):
        if confirm('create env %s?' % env):
            os.makedirs(env)
        else:
            error('env does not exist')

    if args.copy:
        if not os.path.exists(package):
            error('package does not exist: %s' % package)
            return
        if not os.path.splitext(package)[1] in ('.zip', '.rvpkg'):
            error('package has wrong extension: %s' % os.pth.splitext(package)[1])
            return

        # TODO: make sure it doesn't exist, or offer to remove it
        # TODO: copy it in






if __name__ == '__main__':
    main()
