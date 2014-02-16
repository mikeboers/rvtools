import os

import yaml


class Package(object):

    def __init__(self, root=None, **kwargs):
        self.root = root
        if self.root:
            with open(os.path.join(root, 'PACKAGE')) as fh:
                self.meta = yaml.load(fh.read())
        else:
            self.meta = {}
        self.meta.update(kwargs)



def build_files_list(root, install_root='SupportFiles/$PACKAGE'):

    res = []
    root = os.path.abspath(root)

    for dir_path, dir_names, file_names in os.walk(root):
        dir_path_rel = os.path.relpath(dir_path, root)

        for file_name in file_names:
            if file_name.startswith('.'):
                continue

            res.append({
                'file': os.path.append(dir_path_rel, file_name),
                'location': os.path.append(install_root, dir_path_rel),
            })

    return res


