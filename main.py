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
    'markdown.extensions.toc',
    'markdown.extensions.codehilite',
    'markdown.extensions.nl2br',
    'markdown.extensions.sane_lists',
    'pymdownx.extra',
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
        return env.get_template(self.METADATA['template']).render(self.METADATA)

    def pagebase_output(self, output_dir, env):
        page_content = self.pagebase_render(env)
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
            # folder name default
            'category': 'default',
            # 是否置顶
            'top': 0,
        })
        self.METADATA.update(config)

        self.METADATA['__url'], self.METADATA['title'] = os.path.split(self.file)
        self.METADATA['title'] = os.path.splitext(self.METADATA['title'])[0]
        self.METADATA['__url'] = self.METADATA['__url'].replace('\\', '/') + '/' + self.METADATA['title'] + '.html'
        self.METADATA['__output_path'] = self.METADATA['__url']

    def page_set_template(self, template):
        self.METADATA.update({
            'template': template,
        })

    def page_render_default(self):
        if self.file.endswith('.md'):
            self.page_render_markdown()
        else:
            with open(self.file, 'r', encoding='utf-8') as f:
                self.METADATA['__content'] = f.read()

    def page_render_markdown(self, raw=False):
        content_lines = Page.render_markdown_yaml(self.file, self.METADATA)
        if raw:
            self.METADATA['__content'] = ''.join(content_lines)
        else:
            self.METADATA['__content'] = markdown.markdown(''.join(content_lines), extensions=MARKDOWN_EXTS)

    @staticmethod
    def render_markdown_yaml(file, metadata):
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        yaml_lines, content_lines = Page.split_markdown_yaml(lines)

        if yaml_lines:
            yaml_header = yaml.safe_load(''.join(yaml_lines))
            for key, value in yaml_header.items():
                if key in metadata:
                    metadata[key] = value

        # ==BUG== 2021-1-1 will be converted into <class 'datetime.date'>
        metadata['date'] = str(metadata['date'])
        try:
            datetime.strptime(metadata['date'], "%Y-%m-%d")
        except ValueError:
            metadata['date'] = datetime.now().strftime("%Y-%m-%d")

        return content_lines

    @staticmethod
    def split_markdown_yaml(lines: [str]) -> ([], [str]):
        if not lines:
            return [], ['']

        if len(lines[0]) == 4 and lines[0].replace('\n', '') == '---' \
                or len(lines[0]) == 5 and lines[0][1:].replace('\n', '') == '---':
            for idx in range(1, len(lines)):
                if lines[idx].replace('\n', '') == '---':
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

        files = file_get_recursive(entry)

        GLOBAL_METADATA['__links'].append(
            {
                'name': entry,
                'url': entry + '.html',
            }
        )
        GLOBAL_METADATA['__posts_metadata'].setdefault(entry, [])

        page_metadate = []
        for file in files:
            # ==BUG== I'm not satisfied with this method
            if len(file.split('\\')) >= 3:
                _config['category'] = file.split('\\')[1]
            else:
                _config['category'] = 'default'

            page = Page(_config, file)

            if entry == 'slide':
                page.page_set_template('reveal.html')
                page.page_render_markdown(raw=True)
                page.pagebase_output(config['output'] + '/', env)
            else:
                page.page_render_default()
                page.pagebase_output(config['output'] + '/', env)

            page_metadate.append(page.METADATA)
        # sorted by top and date
        GLOBAL_METADATA['__posts_metadata'][entry] = sorted(page_metadate,
                                                            key=operator.itemgetter('top', 'date'),
                                                            reverse=True)

    index_page = PageBase(_config)
    index_page.METADATA.update({
        'template': 'index.html',
        '__url': 'index.html',
        '__output_path': 'index.html',
        '__links': GLOBAL_METADATA['__links'],
    })
    index_page.pagebase_output(config['output'], env)

    gallery_page = PageBase(_config)
    gallery_page.METADATA.update({
        'template': 'gallery.html',
        '__url': 'gallery.html',
        '__output_path': 'gallery.html',
        '__posts': GLOBAL_METADATA['__posts_metadata']['gallery'],
    })
    gallery_page.pagebase_output(config['output'], env)

    project_page = PageBase(_config)
    project_page.METADATA.update({
        'template': 'project.html',
        '__url': 'project.html',
        '__output_path': 'project.html',
        '__projects': GLOBAL_METADATA['__posts_metadata']['project'],
    })
    project_page.pagebase_output(config['output'], env)

    slide_page = PageBase(_config)
    slide_page.METADATA.update({
        'template': 'slide.html',
        '__url': 'slide.html',
        '__output_path': 'slide.html',
        '__slides': GLOBAL_METADATA['__posts_metadata']['slide'],
    })
    slide_page.pagebase_output(config['output'], env)

    # ==building==
    # category_page = PageBase(_config)
    # category_page.METADATA.update({
    #     'template': 'category.html',
    #     '__url': 'category.html',
    #     '__output_path': 'category.html',
    #     '__posts': GLOBAL_METADATA['__posts_metadata']['gallery'],
    # })
    # category_page.pagebase_output(config['output'], env)

    about_page = Page(_config, 'about/about.md')
    about_page.METADATA.update({
        'template': 'about.html',
        '__url': 'about.html',
        '__output_path': 'about.html',
    })
    about_page.page_render_default()
    about_page.pagebase_output(config['output'] + '/', env)


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
