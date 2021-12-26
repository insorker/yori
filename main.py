from jinja2 import Environment, FileSystemLoader
import yaml
import markdown
import os
import time

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


class Page:
    def __init__(self, config, file):
        self.file = file
        self.METADATA = {
            ''' user define '''
            # file name default
            'title': '',
            # post.html template default
            'template': 'post.html',
            # render default
            # 'render': True,
            # form recommended: %Y-%m-%d--%H-%M
            'date': '',
            ''' program generate '''
            '__url': '',
            '__content': '',
            '__output_path': '',
        }
        self.METADATA.update(config)

        self.page_render()

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


def jj2_render(page, env):
    return env.get_template(page.METADATA['template']).render(page.METADATA)


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


def yori_render(config: dict, env):
    files = file_get_recursive(config['posts'])

    for file in files:
        try:
            with open(config['templates'] + '\\_config.yml', 'r', encoding='utf-8') as _config_file:
                _config = yaml.safe_load(_config_file)
                page = Page(_config, file)
        except FileNotFoundError:
            print('File \"%s\\_config.yml\" cannot be found.' % config['templates'])
            print('See ... for more information.')
            continue

        page_content = jj2_render(page, env)
        page_output_path = os.path.join(config['output'] + '\\', page.METADATA['__output_path'])

        os.makedirs(os.path.dirname(page_output_path), exist_ok=True)
        with open(page_output_path, 'w', encoding='utf-8') as f:
            f.write(page_content)


if __name__ == "__main__":
    try:
        with open('config.yml', 'r', encoding='utf-8') as cfg_file:
            cfg = yaml.safe_load(cfg_file)
        yori_render(cfg, Environment(loader=FileSystemLoader(cfg['templates'])))
    except FileNotFoundError:
        print('File \"config.yml\" cannot be found.')
        print('See ... for more information.')
