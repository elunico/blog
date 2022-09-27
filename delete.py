from fileinput import filename
import shutil
import os
import os.path
import urllib.parse


def filename_from_link(link):
    parts = urllib.parse.urlsplit(link).path.split('/')
    file = parts[-1]
    file = urllib.parse.unquote(file)
    return file


def md_from_link(link):
    return filename_from_link(link).removesuffix('.html') + '.md'


def html_from_link(link):
    return filename_from_link(link)


def main():
    link = input("Enter the URL of the post to delete: ").strip()
    md_file = md_from_link(link)
    html_file = html_from_link(link)
    md_path = os.path.join('source', md_file)
    html_path = os.path.join('public', html_file)
    confirm = input('PERMANENTLY DELETE "{}" and "{}"? (y/n) '.format(html_path, md_path)).strip().lower()
    if confirm.strip().lower().startswith('y'):
        os.unlink(md_path)
        os.unlink(html_path)
        result = input('(d)eploy changes to the web or just re(b)uild? '.format(html_path, md_path)).strip().lower()
        if result.startswith('b'):
            os.execl('/Users/thomaspovinelli/Coding/blog/venv/bin/python3', '/Users/thomaspovinelli/Coding/blog/venv/bin/python3', 'build.py')
        elif result.startswith('d'):
            os.execl('/bin/zsh', '/bin/zsh', '/Users/thomaspovinelli/Coding/blog/deploy.sh')


if __name__ == '__main__':
    raise SystemExit(main())
