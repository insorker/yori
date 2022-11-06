from metadata import gl_metadata
from page import PageBase, Page


def gen_index(config, output_dir, env):
    index_page = PageBase(config)
    index_page.METADATA.update({
        'template': 'index.html',
        '__url': 'index.html',
        '__info': gl_metadata['__index'],
    })
    index_page.output(output_dir, env)


def gen_post(config, output_dir, env):
    page = PageBase(config)
    page.METADATA.update({
        'template': 'post.html',
        '__url': 'post.html',
        '__info': gl_metadata['__navigation']['post'],
    })
    page.output(output_dir, env)


def gen_project(config, output_dir, env):
    page = PageBase(config)
    page.METADATA.update({
        'template': 'project.html',
        '__url': 'project.html',
        '__info': gl_metadata['__navigation']['project'],
    })
    page.output(output_dir, env)


def gen_about(config, output_dir, env):
    page = Page(config, 'about/about.md')
    page.METADATA.update({
        'template': 'about.html',
        '__url': 'about.html',
    })
    page.render_markdown()
    page.output(output_dir, env)
