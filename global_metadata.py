# global metadata
GLOBAL_METADATA = {
    '__index_links': [],
    '__posts_metadata': {},
}


def add_index_links(entry: str):
    """ add entry to index links """
    GLOBAL_METADATA['__index_links'].append(
        {
            'name': entry,
            'url': entry + '.html',
        }
    )
    GLOBAL_METADATA['__posts_metadata'].setdefault(entry, [])


def add_posts_metadata(entry: str, posts_metadata):
    """ add posts_metadata to specified entry """
    GLOBAL_METADATA['__posts_metadata'][entry] = posts_metadata
