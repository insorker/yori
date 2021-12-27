from jinja2 import Environment, FileSystemLoader
import yaml
import markdown
import os
from datetime import datetime
import distutils.dir_util
import operator

'''document'''
DOCUMENT_URL = 'https://insorker.github.io/'

GLOBAL_METADATA = {
    '__links': [],
    '__posts_metadata': {},
}

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
    def __init__(self, config):
        self.METADATA = {
            'author': 'anonymous',
            'date': datetime.now().strftime("%Y-%m-%d"),
            'template': '',
            '__url': '',
            '__content': '',
            '__output_path': '',
        }
        self.METADATA.update(config)

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
        super(Page, self).__init__(config)

        self.file = file
        self.METADATA.update({
            # file name default
            'title': '',
            # 'tag': '',
            # post.html template default
            'template': 'post.html',
        })

        self.METADATA['__url'], self.METADATA['title'] = os.path.split(self.file)
        self.METADATA['title'] = os.path.splitext(self.METADATA['title'])[0]
        self.METADATA['__url'] = self.METADATA['__url'].replace('\\', '/') + '/' + self.METADATA['title'] + '.html'
        self.METADATA['__output_path'] = self.METADATA['__url']

    def page_render(self):
        if self.file.endswith('.md'):
            self.page_render_markdown()
        else:
            with open(self.file, 'r', encoding='utf-8') as f:
                self.METADATA['__content'] = f.read()

    def page_render_markdown(self):
        with open(self.file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        yaml_lines, content_lines = Page.split_markdown(lines)

        if yaml_lines:
            yaml_header = yaml.safe_load(''.join(yaml_lines))
            for key, value in yaml_header.items():
                if key in self.METADATA:
                    self.METADATA[key] = value

        # ==BUG== 2021-1-1 will be converted into <class 'datetime.date'>
        self.METADATA['date'] = str(self.METADATA['date'])
        try:
            datetime.strptime(self.METADATA['date'], "%Y-%m-%d")
        except ValueError:
            self.METADATA['date'] = datetime.now().strftime("%Y-%m-%d")

        self.METADATA['__content'] = markdown.markdown(''.join(content_lines), extensions=MARKDOWN_EXTS)

    @staticmethod
    def split_markdown(lines: [str]) -> ([], [str]):
        if not lines:
            return [], ['']

        if lines[0] == '---\n':
            for idx in range(1, len(lines)):
                if lines[idx] == '---\n':
                    return lines[1: idx], lines[idx + 1:]

        return [], lines


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


def jj2_render(page: PageBase, env):
    return env.get_template(page.METADATA['template']).render(page.METADATA)


def yori_render(config: dict, env):
    try:
        with open(config['templates'] + '/_config.yml', 'r', encoding='utf-8') as _config_file:
            _config = yaml.safe_load(_config_file)
    except FileNotFoundError:
        print('File \"%s/_config.yml\" cannot be found.' % config['templates'])
        print('See %s for more information.' % DOCUMENT_URL)

    for category in config['categories']:
        if not os.path.exists(category):
            print('Directory \"%s\" cannot be found.' % category)
            print('See %s for more information.' % DOCUMENT_URL)
            continue

        files = file_get_recursive(category)

        GLOBAL_METADATA['__links'].append(
            {
                'name': category,
                'url': category + '.html',
            }
        )
        GLOBAL_METADATA['__posts_metadata'].setdefault(category, [])

        page_metadate = []
        for file in files:
            page = Page(_config, file)
            page.page_render()
            page.pagebase_output(config['output'] + '/', env)

            page_metadate.append(page.METADATA)
        GLOBAL_METADATA['__posts_metadata'][category] = sorted(page_metadate,
                                                               key=operator.itemgetter('date'))

    index = PageBase(_config)
    index.METADATA.update({
        'template': 'index.html',
        '__url': 'index.html',
        '__output_path': 'index.html',
        '__links': GLOBAL_METADATA['__links'],
    })
    index.pagebase_render(env)
    index.pagebase_output(config['output'], env)

    gallery = PageBase(_config)
    gallery.METADATA.update({
        'template': 'gallery.html',
        '__url': 'gallery.html',
        '__output_path': 'gallery.html',
        '__posts': GLOBAL_METADATA['__posts_metadata']['gallery'],
    })
    gallery.pagebase_render(env)
    gallery.pagebase_output(config['output'], env)

    project = PageBase(_config)
    project.METADATA.update({
        'template': 'project.html',
        '__url': 'project.html',
        '__output_path': 'project.html',
        '__projects': GLOBAL_METADATA['__posts_metadata']['project'],
    })
    project.pagebase_render(env)
    project.pagebase_output(config['output'], env)


def static_copy(static_dir, output_dir):
    distutils.dir_util.copy_tree(static_dir, output_dir)


if __name__ == "__main__":
    try:
        with open('config.yml', 'r', encoding='utf-8') as cfg_file:
            cfg = yaml.safe_load(cfg_file)
    except FileNotFoundError:
        print('File \"config.yml\" cannot be found.')
        print('See %s for more information.' % DOCUMENT_URL)

    static_copy(cfg['static'], cfg['output'])
    yori_render(cfg, Environment(loader=FileSystemLoader(cfg['templates'])))
