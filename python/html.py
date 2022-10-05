import urllib.parse
import os.path


def linkify(title):
    return urllib.parse.quote(title)


def titlify(filename):
    return '.'.join(filename.rsplit('.')[:-1]).title()


def tag_spans(iterator, className=''):
    return '\n'.join('<span class="{}"><a href="/blog/search.html?tag={}">{}</a></span>'.format(className, urllib.parse.quote(i), i) for i in iterator)


def style(html_template):
    with open(os.path.join('private', 'stylesheet.css')) as f:
        return html_template.replace('@css-content {}', f.read())


def index_entry(filename, meta, page):
    link = linkify(filename) if page is None else '/blog/page-{}/{}'.format(page, linkify(filename))

    return '''
    <article class="post">
    <section class="blog-title"> <a href="{}">{}</a></section>
    <summary class="summary">{}</summary>
    {}
    <section class="footer published">Published: <span data-has-date class="pub-date">{}</span></section>
    </article>
    <hr>
    '''.format(link, titlify(filename), meta['summary'], tags_for_file(filename, meta),
               meta['date'])


def tags_for_file(filename, meta):
    return '<div class="footer tags">Tags: {}</div>'.format(tag_spans(meta['tags'], className='tag'))
