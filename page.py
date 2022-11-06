import yaml
import markdown
import os
from datetime import datetime
from metadata import Metadata

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
    def __init__(self, config: dict):
        self.METADATA = {
            # public
            'author': 'anonymous',
            'date': datetime.now().strftime("%Y-%m-%d"),
            'template': 'pagebase.html',

            # private
            '__id': '',
            '__url': '',
            '__content': '',
        }
        self.METADATA.update(config)

    def update(self, config):
        self.METADATA.update(config)

    def render(self, env):
        return env.get_template(self.METADATA['template']).render(self.METADATA)

    def output(self, output_dir, env):
        content = self.render(env)
        output_path = os.path.join(output_dir, self.METADATA['__url'])

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


class Page(PageBase):
    def __init__(self, config: dict, path: str):
        super(Page, self).__init__(config)

        self.path = path
        self.METADATA.update({
            'title': '',
            'template': 'page.html',
            'tag': '',
            'category': 'default',
            # 是否置顶
            'top': 0,
        })
        self.METADATA.update(config)

        self.METADATA['__id'] = str(os.path.getctime(self.path))
        self.METADATA['__url'] = self.path.replace('\\', '/') + '.html'
        # self.METADATA['__url'], self.METADATA['title'] = os.path.split(self.path)
        # self.METADATA['title'] = os.path.splitext(self.METADATA['title'])[0]
        # self.METADATA['__url'] = self.METADATA['__url'].replace('\\', '/') + '/' + self.METADATA['title'] + '.html'

    # def render_default(self):
    #     if self.path.endswith('.md'):
    #         self.render_markdown()
    #     else:
    #         self.render_markdown(True)
    #         # with open(self.path, 'r', encoding='utf-8') as f:
    #         #     self.METADATA['__content'] = f.read()

    def render_markdown(self, option='md'):
        content = self.render_yaml(self.path)
        if option == 'raw':
            self.METADATA['__content'] = content
        elif option == 'md':
            self.METADATA['__content'] = markdown.markdown(content, extensions=MARKDOWN_EXTS)

    def render_yaml(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        yaml_lines, content_lines = Page.split_yaml_content(lines)

        if yaml_lines:
            yaml_header = yaml.safe_load(''.join(yaml_lines))
            for key, value in yaml_header.items():
                if key in self.METADATA:
                    self.METADATA[key] = value
            self.render_yaml_check()

        return ''.join(content_lines)

    def render_yaml_check(self):
        # in case 2021-1-1 would be converted into <class 'datetime.date'>
        self.METADATA['date'] = str(self.METADATA['date'])

        # try if date is correct
        try:
            datetime.strptime(self.METADATA['date'], "%Y-%m-%d")
        except ValueError:
            self.METADATA['date'] = datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def split_yaml_content(lines: [str]) -> ([], [str]):
        if not lines:
            return [], ['']

        if lines[0].find('---\n') != -1:
            for idx in range(1, len(lines)):
                if lines[idx].find('---\n') != -1:
                    return lines[1: idx], lines[idx + 1:]

        return [], lines
