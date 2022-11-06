from jinja2 import Environment, FileSystemLoader
import os
import sys
import operator
import utils
import generator
from metadata import gl_metadata
from page import Page


def yori_render(config: dict, env):
    _config = utils.config_open(config['template'] + '/_config.yml')

    for navigation in config['navigation']:
        if not os.path.exists(navigation):
            print('Directory \"%s\" cannot be found.' % navigation)
            continue

        navigation_metadata = []
        gl_metadata.index_append(navigation)

        for path in utils.file_walk(navigation):
            page = Page(_config, path)
            page.render_markdown()
            page.output(config['output'] + '/', env)
            page.METADATA.pop('__content')

            navigation_metadata.append(page.METADATA)

        gl_metadata.navigation_append(navigation, sorted(navigation_metadata,
                                                         key=operator.itemgetter('top', 'date'), reverse=True))

    generator.gen_index(_config, gl_config['output'], env)
    generator.gen_post(_config, gl_config['output'], env)
    generator.gen_project(_config, gl_config['output'], env)
    generator.gen_about(_config, gl_config['output'], env)


if __name__ == "__main__":
    # open config file
    gl_config = utils.config_open('config.yml')

    # delete output
    utils.dir_delete(gl_config['output'])

    # copy static files
    for static_dir in gl_config['static']:
        utils.dir_copy(static_dir, gl_config['output'])

    # render html
    yori_render(gl_config, Environment(loader=FileSystemLoader(gl_config['template'])))

    # finish
    print('Yori( ᐛ )( ᐛ )( ᐛ )...done!')

    # local preview
    if len(sys.argv) > 1:
        if sys.argv[1] == 'server':
            utils.local_server(gl_config['output'], 8000)
