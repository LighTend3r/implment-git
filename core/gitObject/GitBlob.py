from core.GitObject import GitObject

class GitBlob(GitObject):
    """A GitBlob is a simple object that stores the raw data of a file. """
    fmt=b'blob'

    def serialize(self):
        return self.blobdata

    def deserialize(self, data):
        self.blobdata = data
