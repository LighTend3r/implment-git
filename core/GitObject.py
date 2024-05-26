import os
import zlib
import hashlib
from core.GitRepository import GitRepository, repo_file
from io import BufferedReader
from typing import Optional, List, Tuple
from core.gitObject.GitBlob import GitBlob
from core.gitObject.GitCommit import GitCommit
from core.gitObject.GitTree import GitTree
from core.gitObject.GitTag import GitTag


class GitObject (object):
    """A git object."""

    def __init__(self, data=None):
        if data != None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self, repo):
        """This function MUST be implemented by subclasses.
            It must read the object's contents from self.data, a byte string, and do
            whatever it takes to convert it into a meaningful representation.  What exactly that means depend on each subclass."""
        raise Exception("Unimplemented!")

    def deserialize(self, data):
        raise Exception("Unimplemented!")

    def init(self):
        pass # Just do nothing. This is a reasonable default!





def object_read(repo: GitRepository, sha: str) -> Optional[GitObject]:
    """Read object object_id from Git repository repo.  Return a GitObject whose exact type depends on the object.

    Args:
        repo (GitRepository): The repository to read from.
        sha (str): The SHA1 hash of the object to read.

    Raises:
        Exception: The object is malformed.
        Exception: The object type is unknown.

    Returns:
        Optional[GitObject]: The object read from the repository. If the object does not exist, return None.
    """

    path = repo_file(repo, "objects", sha[0:2], sha[2:])

    if not os.path.isfile(path):
        return None

    with open (path, "rb") as f:
        raw = zlib.decompress(f.read())

        # Read object type
        x = raw.find(b' ')
        fmt = raw[0:x]

        # Read and validate object size
        y = raw.find(b'\x00', x)
        size = int(raw[x:y].decode("ascii"))
        if size != len(raw)-y-1:
            raise Exception("Malformed object {0}: bad length".format(sha))

        # Pick constructor
        match fmt:
            case b'commit' : c=GitCommit
            case b'tree'   : c=GitTree
            case b'tag'    : c=GitTag
            case b'blob'   : c=GitBlob
            case _:
                raise Exception("Unknown type {0} for object {1}".format(fmt.decode("ascii"), sha))

        # Call constructor and return object
        return c(raw[y+1:])



def object_write(obj: GitObject, repo: GitRepository=None) -> str:
    """Write object to Git repository repo.  Return SHA1 hash of object.

    Args:
        obj (GitObject): The object to write.
        repo (GitRepository, optional): The current repository. Defaults to None.

    Returns:
        str: The SHA1 hash of the object.
    """
    # Serialize object data
    data = obj.serialize()
    # Add header
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    # Compute hash
    sha = hashlib.sha1(result).hexdigest()

    if repo:
        # Compute path
        path=repo_file(repo, "objects", sha[0:2], sha[2:], mkdir=True)

        if not os.path.exists(path):
            with open(path, 'wb') as f:
                # Compress and write
                f.write(zlib.compress(result))
    return sha

def object_find(repo: GitRepository, name: str, fmt=None, follow: bool=True) -> str:
    return name

def object_hash(fd: BufferedReader, fmt: bytes, repo: GitRepository=None) -> str:
    """Compute hash of object data read from file-like object fd.

    Args:
        fd (BufferedReader): The bytes to hash.
        fmt (bytes): The format of the object.
        repo (GitRepository, optional): The current repository. Defaults to None.

    Raises:
        Exception: If the format is unknown.

    Returns:
        str: The SHA1 hash of the object.
    """
    data = fd.read()

    # Choose constructor according to fmt argument
    match fmt:
        case b'commit' : obj=GitCommit(data)
        case b'tree'   : obj=GitTree(data)
        case b'tag'    : obj=GitTag(data)
        case b'blob'   : obj=GitBlob(data)
        case _: raise Exception("Unknown type %s!" % fmt)

    return object_write(obj, repo)
