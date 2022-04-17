from jinja2 import Environment, FileSystemLoader
import yaml
import os
import sys
import distutils.dir_util
import distutils.file_util
import operator
import http.server
import socketserver
import entry_generator as eg
import global_metadata as gm
from page_generator import Page, Wiki

'''document'''
DOCUMENT_URL = 'https://github.com/insorker/yori'


def file_get_recursive(root: str) -> [str]:
    files_rec = []
    files = os.listdir(root)

    for file in files:
        file = os.path.join(root, file)

        if os.path.isfile(file):
            files_rec.append(file)
        elif os.path.isdir(file):
            files_rec.extend(file_get_recursive(file))

    return files_rec


def yori_render(config: dict, env):
    try:
        with open(config['templates'] + '/_config.yml', 'r', encoding='utf-8') as _config_file:
            _config = yaml.safe_load(_config_file)
    except FileNotFoundError:
        print('File \"%s/_config.yml\" cannot be found.' % config['templates'])
        print('See %s for more information.' % DOCUMENT_URL)

    for entry in config['entries']:
        if not os.path.exists(entry):
            print('Directory \"%s\" cannot be found.' % entry)
            print('See %s for more information.' % DOCUMENT_URL)
            continue

        gm.add_index_links(entry)

        # page_metadata of entry
        posts_metadata = []
        # files in entry folder
        files = file_get_recursive(entry)
        for file in files:
            # ==BUG== I'm not satisfied with this method
            # if len(file.split('\\')) >= 3:
            #     _config['category'] = file.split('\\')[1]
            # else:
            #     _config['category'] = 'default'

            page = Page(_config, file)

            if entry == 'slide':
                page.page_set_template('reveal.html')
                page.page_render_markdown(raw=True)
                page.pagebase_output(config['output'] + '/', env)
            else:
                page.page_render_default()
                page.pagebase_output(config['output'] + '/', env)

            posts_metadata.append(page.METADATA)
        # sorted by top and date
        gm.add_posts_metadata(entry, sorted(posts_metadata,
                                            key=operator.itemgetter('top', 'date'), reverse=True))

    for entry in config['entry-wiki']:
        if not os.path.exists(entry):
            print('Directory \"%s\" cannot be found.' % entry)
            print('See %s for more information.' % DOCUMENT_URL)
            continue

        gm.add_index_links(entry)

        posts_metadata = []
        for file in os.listdir(entry):
            wiki = Wiki(_config, entry, file)

            posts_metadata.append(wiki.METADATA)
        gm.add_posts_metadata(entry, posts_metadata)

    eg.gen_indexpage(config, _config, env)
    eg.gen_gallerypage(config, _config, env)
    eg.gen_projectpage(config, _config, env)
    eg.gen_slidepage(config, _config, env)
    eg.gen_wikipage(config, _config, env)
    eg.gen_aboutpage(config, _config, env)


def static_dir_copy(static_dir, output_dir):
    distutils.dir_util.copy_tree(static_dir, output_dir)


def static_file_copy(static_file, output_dir):
    distutils.file_util.copy_file(static_file, output_dir)


if __name__ == "__main__":
    try:
        with open('config.yml', 'r', encoding='utf-8') as cfg_file:
            cfg = yaml.safe_load(cfg_file)
    except FileNotFoundError:
        print('File \"config.yml\" cannot be found.')
        print('See %s for more information.' % DOCUMENT_URL)

    for static_files in cfg['static']:
        static_dir_copy(static_files, cfg['output'])
    static_dir_copy('wiki', cfg['output'] + '/wiki')
    static_file_copy('.nojekyll', cfg['output'])

    yori_render(cfg, Environment(loader=FileSystemLoader(cfg['templates'])))

    print("Yori( ᐛ )( ᐛ )( ᐛ )...done!")

    if len(sys.argv) > 1:
        if sys.argv[1] == 'server':
            port = 8000
            handl = http.server.SimpleHTTPRequestHandler

            with socketserver.TCPServer(('127.0.0.1', port), handl) as httpd:
                os.chdir(cfg['output'])
                print('web site at localhost:8000')
                httpd.serve_forever()
