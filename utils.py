import os
import yaml
import distutils.dir_util
import distutils.file_util
import http.server
import socketserver


def config_open(file: str):
    with open(file, 'r', encoding='utf-8') as config_file:
        return yaml.safe_load(config_file)


def dir_delete(root: str):
    for root, dirs, files in os.walk(root, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def dir_copy(src: str, dest: str):
    distutils.dir_util.copy_tree(src, dest)


def file_copy(src: str, dest: str):
    distutils.file_util.copy_file(src, dest)


def file_walk(root: str) -> [str]:
    path_list = list()

    for root, __, files in os.walk(root):
        for name in files:
            path_list.append(os.path.join(root, name))

    return path_list


def local_server(root: str, port: int):
    print('web site at localhost:%d' % port)

    os.chdir(root)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(('127.0.0.1', port), handler) as httpd:
        httpd.serve_forever()
