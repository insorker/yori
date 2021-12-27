# yori (>_<)
A tiny static blog generator

Yori aims to help you escape from modern convenient but heavy tools. You can write your own html/css/js there, and yori's job is just collecting what you want, assembling them together, then putting them into a box.

Yori uses **jinja2** to parse html and **prism.js** to render markdown part.

You can have a look at some **examples** there:

- https://insorker.github.io/

## Install

You should install git and python3(recommended version >= 3.8) first.

Git clone the whole repository

```git
git clone git@github.com:insorker/yori.git
```

We recommond you to use virtual environment, like venv as example. Then install the requirements

```python
python -m venv venv
source venv/bin/activate
(venv)pip install -r requirements.txt
```

To test if every thing is ok, run the following command. If nothing goes wrong and a folder named "output" come out, congratulations

```python
(venv)python main.py
```

## Usage

To generate output, you should run

```python
python main.py
```

> !!! The next content (until the end) has not been updated, please watch carefully

### Use config.yml

```yaml
# path should be the relative path of config.yml
templates: templates
static: static
categories:
  - gallery
  - doc
output: output
```

- templates:
  - where to load your html templates

- static:
  - css/js

- categories:
  - each category corresponds to a folder where you can do what you want.
  - Like gallery, you can put your posts there.
- output:
  - output the results after `python main.py`

### Different structure

By default, you can write articles under folder named "gallery". If you want to add some categories, mkdir a folder under "gallery", and put the ariticles there, whose url is like `posts/your_category_name/your_article_name`. 

Also, you can mkdir like a tree, and create a path like `posts/your_category_name/.../your_category_name/your_article_name`.

If you want to do more things rather than just writing, mkdir folder at the same level of the folder "gallery" and name it yourself. Remember to add the name into config.yml's categories.

### Config template

> Learn more in [jinja2](https://jinja.palletsprojects.com/en/3.0.x/templates/)

Under the folder "templates", a file named "_config.yml" is ready for you to add variables in it. Each of the var will be mapped to the var in html file in a kind of {{ var }}. Now you can create your own html template.

If you want the template to be effective in the artile, add the template to the markdown yaml header.

A markdown yaml header is like this

```markdown
---
title: 123
date: 2021-12-27
template: post.html
---
```

All of the option are optional and have default value, but some of them are highly recommended to rewrite. You can read the code in main.py to get more information.

## Author

[insorker](https://github.com/insorker)



