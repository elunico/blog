import urllib.parse

from ebbuild.util import linkify, titlify


def tag_spans(iterator, className=''):
    return '\n'.join('<span class="{}"><a href="/blog/search.html?tag={}">{}</a></span>'.format(className, urllib.parse.quote(i), i) for i in iterator)


def index_entry(filename, meta, page):
    link = linkify(filename) if page is None else '/blog/page-{}/{}'.format(page, linkify(filename))

    return '''
    <article class="post index-post">
    <a class="post-outer-link" href={}>
    <section class="blog-title">{}</section>
    <summary class="summary">{}</summary>
    </a>
    {}
    <section class="footer published">Published: <span data-has-date class="pub-date">{}</span></section>
    </article>

    '''.format(link, titlify(filename), meta['summary'].result, tags_for_file(meta),
               meta['date'].result)


def tags_for_file(meta):
    return '<div class="footer tags">Tags: {}</div>'.format(tag_spans(meta['tags'].result, className='tag'))
