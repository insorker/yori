class Metadata:
    def __init__(self, metadata: dict):
        self.metadata = metadata

    def update(self, metadata):
        self.metadata.update(metadata)

    def setdefault(self, key, value):
        self.metadata.setdefault(key, value)

    def __getitem__(self, index):
        return self.metadata[index]

    def __setitem__(self, index, value):
        self.metadata[index] = value

    def __delitem__(self, index):
        del self.metadata[index]


class GlobalMetadata(Metadata):
    def __init__(self):
        super(GlobalMetadata, self).__init__(dict())

        self.metadata = {
            '__index': [],
            '__navigation': {},
        }

    def index_append(self, navigation: str):
        self.metadata['__index'].append({
            'name': navigation,
            'url': navigation + '.html',
        })
        self.metadata['__navigation'].setdefault(navigation, [])

    def navigation_append(self, navigation: str, navigation_metadata: dict):
        self.metadata['__navigation'][navigation] = navigation_metadata


gl_metadata = GlobalMetadata()
