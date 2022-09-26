import urllib.parse
import os.path


def linkify(title):
    return urllib.parse.quote(title)


def titlify(filename):
    return '.'.join(filename.rsplit('.')[:-1]).title()


def tag_spans(iterator, className=''):
    return '\n'.join('<span class="{}"><a href="search/{}">{}</a></span>'.format(className, urllib.parse.quote(i), i) for i in iterator)


def style(html_template):
    with open(os.path.join('private', 'stylesheet.css')) as f:
        return html_template.replace('@css-content {}', f.read())


def index_entry(filename, meta):
    return '''
    <div class="post">
    <div class="blog-title"> <a href="{}">{}</a></div>
    <div class="summary">{}</div>
    <div class="footer tags">Tags: {}</div>
    <div class="footer published">Published: <span class="pub-date">{}</span></div>
    </div>
    <hr>
    '''.format(linkify(filename), titlify(filename), meta['summary'], tag_spans(meta['tags'], className='tag'),
               meta['date'])
