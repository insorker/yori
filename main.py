from jinja2 import Environment, FileSystemLoader
import yaml
import markdown
import os
import time
import shutil

'''document'''
DOCUMENT_URL = '...'

'''markdown extensions'''
MARKDOWN_EXTS = [
    'markdown.extensions.extra',
    'markdown.extensions.toc',
    'pymdownx.magiclink',
    'pymdownx.keys',
    'pymdownx.mark',
    'pymdownx.tilde',
    'pymdownx.inlinehilite',
    'pymdownx.tasklist',
]


class PageBase:
    def __init__(self):
        self.METADATA = {
            ''' program generate '''
            '__url': '',
            '__content': '',
            '__output_path': '',
        }

    def pagebase_render(self, env):
        return jj2_render(self, env)

    def pagebase_output(self, output_dir, env):
        page_content = jj2_render(self, env)
        page_output_path = os.path.join(output_dir, self.METADATA['__output_path'])

        os.makedirs(os.path.dirname(page_output_path), exist_ok=True)
        with open(page_output_path, 'w', encoding='utf-8') as f:
            f.write(page_content)


class Page(PageBase):
    def __init__(self, config, file):
        super(Page, self).__init__()

        self.file = file
        self.METADATA.update({
            ''' user define '''
            # file name default
            'title': '',
            # post.html template default
            'template': 'post.html',
            # render default
            # 'render': True,
            # form recommended: %Y-%m-%d--%H-%M
            'date': '',
        })
        self.METADATA.update(config)

    def page_render(self):
        self.METADATA['__url'], self.METADATA['title'] = os.path.split(self.file)
        self.METADATA['title'] = os.path.splitext(self.METADATA['title'])[0]
        self.METADATA['date'] = time.strftime('%Y-%m-%d--%H-%M', time.localtime(time.time()))

        if self.file.endswith('md'):
            self.page_render_markdown()
        else:
            with open(self.file, 'r', encoding='utf-8') as f:
                self.METADATA['__content'] = f.read()

        self.METADATA['__output_path'] = self.METADATA['__url'] + '\\' + self.METADATA['title'] + '.html'

    def page_render_markdown(self):
        with open(self.file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        yaml_lines, content_lines = Page.split_markdown(lines)

        if yaml_lines:
            yaml_header = yaml.safe_load(''.join(yaml_lines))
            for key, value in yaml_header.items():
                if key in self.METADATA and key[0: 2] != '--':
                    self.METADATA[key] = value

        self.METADATA['__content'] = ''.join(content_lines)
        self.METADATA['__content'] = markdown.markdown(self.METADATA['__content'], extensions=MARKDOWN_EXTS)

    @staticmethod
    def split_markdown(lines: [str]) -> ([], [str]):
        if not lines:
            return [], ['']

        if lines[0] == '---\n':
            for idx in range(1, len(lines)):
                if lines[idx] == '---\n':
                    return lines[1: idx], lines[idx + 1:]

        return [], lines


def file_get_recursive(root):
    files_rec = []
    files = os.listdir(root)

    for file in files:
        file = os.path.join(root, file)

        if os.path.isfile(file):
            files_rec.append(file)
        elif os.path.isdir(file):
            files_rec.extend(file_get_recursive(file))

    return files_rec


def jj2_render(page, env):
    return env.get_template(page.METADATA['template']).render(page.METADATA)


def index_render(output_dir, env):
    index = PageBase()
    index_metadata = {
        'template': 'index.html',
        '__output_path': 'index.html',
    }
    index.METADATA.update(index_metadata)
    index.pagebase_render(env)
    index.pagebase_output(output_dir, env)


def yori_render(config: dict, env):
    index_render(config['output'], env)

    for category in config['categories']:
        if not os.path.exists(category):
            print('Directory \"%s\" cannot be found.' % category)
            print('See %s for more information.' % DOCUMENT_URL)
            continue
        files = file_get_recursive(category)

        for file in files:
            try:
                with open(config['templates'] + '\\_config.yml', 'r', encoding='utf-8') as _config_file:
                    _config = yaml.safe_load(_config_file)
                page = Page(_config, file)
                page.page_render()
                page.pagebase_output(config['output'] + '\\', env)
            except FileNotFoundError:
                print('File \"%s\\_config.yml\" cannot be found.' % config['templates'])
                print('See %s for more information.' % DOCUMENT_URL)
                continue


if __name__ == "__main__":
    try:
        with open('config.yml', 'r', encoding='utf-8') as cfg_file:
            cfg = yaml.safe_load(cfg_file)
        if os.path.exists(cfg['output']):
            shutil.rmtree(cfg['output'])
        yori_render(cfg, Environment(loader=FileSystemLoader(cfg['templates'])))
    except FileNotFoundError:
        print('File \"config.yml\" cannot be found.')
        print('See %s for more information.' % DOCUMENT_URL)
