import os
from core.GitObject import (
    object_read,
    GitObject
)
from core.GitRepository import (
    GitRepository
)


def tree_checkout(repo: GitRepository, tree: GitObject, path: str):
    for item in tree.items:
        obj = object_read(repo, item.sha)
        dest = os.path.join(path, item.path)

        if obj.fmt == b'tree':
            os.mkdir(dest)
            tree_checkout(repo, obj, dest)
        elif obj.fmt == b'blob':
            # @TODO Support symlinks (identified by mode 12****)
            with open(dest, 'wb') as f:
                f.write(obj.blobdata)
