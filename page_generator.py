import yaml
import markdown
import os
from datetime import datetime

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
            self.page_render_markdown(True)
            # with open(self.file, 'r', encoding='utf-8') as f:
            #     self.METADATA['__content'] = f.read()

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


class Wiki(PageBase):
    def __init__(self, config, entry, file):
        super(Wiki, self).__init__(config)
        self.METADATA['title'] = file
        self.METADATA['__url'] = entry + '/' + file + '/index.html'
