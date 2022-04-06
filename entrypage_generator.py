from global_metadata import GLOBAL_METADATA
from page_generator import PageBase, Page


def gen_indexpage(config, _config, env):
    index_page = PageBase(_config)
    index_page.METADATA.update({
        'template': 'index.html',
        '__url': 'index.html',
        '__output_path': 'index.html',
        '__links': GLOBAL_METADATA['__index_links'],
    })
    index_page.pagebase_output(config['output'], env)


def gen_gallerypage(config, _config, env):
    if 'gallery' not in config['entries']:
        return

    gallery_page = PageBase(_config)
    gallery_page.METADATA.update({
        'template': 'gallery.html',
        '__url': 'gallery.html',
        '__output_path': 'gallery.html',
        '__posts': GLOBAL_METADATA['__posts_metadata']['gallery'],
    })
    gallery_page.pagebase_output(config['output'], env)


def gen_projectpage(config, _config, env):
    if 'project' not in config['entries']:
        return

    project_page = PageBase(_config)
    project_page.METADATA.update({
        'template': 'project.html',
        '__url': 'project.html',
        '__output_path': 'project.html',
        '__projects': GLOBAL_METADATA['__posts_metadata']['project'],
    })
    project_page.pagebase_output(config['output'], env)


def gen_slidepage(config, _config, env):
    if 'slide' not in config['entries']:
        return

    slide_page = PageBase(_config)
    slide_page.METADATA.update({
        'template': 'slide.html',
        '__url': 'slide.html',
        '__output_path': 'slide.html',
        '__slides': GLOBAL_METADATA['__posts_metadata']['slide'],
    })
    slide_page.pagebase_output(config['output'], env)


def gen_wikipage(config, _config, env):
    if 'wiki' not in config['entry-wiki']:
        return

    wiki_page = PageBase(_config)
    wiki_page.METADATA.update({
        'template': 'wiki.html',
        '__url': 'wiki.html',
        '__output_path': 'wiki.html',
        '__wikis': GLOBAL_METADATA['__posts_metadata']['wiki'],
    })
    wiki_page.pagebase_output(config['output'], env)


def gen_categorypage():
    pass
    # ==building==
    # category_page = PageBase(_config)
    # category_page.METADATA.update({
    #     'template': 'category.html',
    #     '__url': 'category.html',
    #     '__output_path': 'category.html',
    #     '__posts': GLOBAL_METADATA['__posts_metadata']['gallery'],
    # })
    # category_page.pagebase_output(config['output'], env)


def gen_aboutpage(config, _config, env):
    if 'about' not in config['entries']:
        return

    about_page = Page(_config, 'about/about.md')
    about_page.METADATA.update({
        'template': 'about.html',
        '__url': 'about.html',
        '__output_path': 'about.html',
    })
    about_page.page_render_default()
    about_page.pagebase_output(config['output'] + '/', env)
