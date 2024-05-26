from core.GitObject import GitObject
from typing import List, Tuple


class GitTree(GitObject):
    """A git tree object."""
    fmt=b'tree'

    def deserialize(self, data):
        self.items = tree_parse(data)

    def serialize(self):
        return tree_serialize(self)

    def init(self):
        self.items = list()

class GitTreeLeaf (object):
    def __init__(self, mode: bytes, path: str, sha: str):
        self.mode: bytes = mode
        self.path: str = path
        self.sha: str = sha

def tree_parse_one(raw: bytes, start: int=0) -> Tuple[int, GitTreeLeaf]:
    # Find the space terminator of the mode
    x = raw.find(b' ', start)
    assert x-start == 5 or x-start==6

    # Read the mode
    mode = raw[start:x]
    if len(mode) == 5:
        # Normalize to six bytes.
        mode = b" " + mode

    # Find the NULL terminator of the path
    y = raw.find(b'\x00', x)
    # and read the path
    path = raw[x+1:y]

    # Read the SHA and convert to a hex string
    sha = format(int.from_bytes(raw[y+1:y+21], "big"), "040x")
    return y+21, GitTreeLeaf(mode, path.decode("utf8"), sha)

def tree_parse(raw: bytes) -> List[GitTreeLeaf]:
    pos = 0
    max_ = len(raw)
    ret: List[GitTreeLeaf] = list()
    while pos < max_:
        pos, data = tree_parse_one(raw, pos)
        ret.append(data)

    return ret

# Notice this isn't a comparison function, but a conversion function.
# Python's default sort doesn't accept a custom comparison function,
# like in most languages, but a `key` arguments that returns a new
# value, which is compared using the default rules.  So we just return
# the leaf name, with an extra / if it's a directory.
def tree_leaf_sort_key(leaf: GitTreeLeaf):
    if leaf.mode.startswith(b"10"):
        return leaf.path
    else:
        return leaf.path + "/"


def tree_serialize(obj: GitTree):
    obj.items.sort(key=tree_leaf_sort_key)
    ret = b''
    for i in obj.items:
        ret += i.mode
        ret += b' '
        ret += i.path.encode("utf8")
        ret += b'\x00'
        sha = int(i.sha, 16)
        ret += sha.to_bytes(20, byteorder="big")
    return ret
