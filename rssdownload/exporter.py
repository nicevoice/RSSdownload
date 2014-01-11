#!/usr/bin/env python2

from collections import defaultdict, namedtuple
from datetime import datetime
import sqlite3
    

Post = namedtuple('Post', ['date_published', 'title', 'description', 'link', 'post_id'])

def get_not_exported_posts(db_path, html=True):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT category, feed, datepublished, title, description, link FROM posts
                 WHERE exported = 'False' ORDER BY category, feed ''')
    posts = defaultdict(lambda: defaultdict(list))
    post_id_counter = 0
    for p in c.fetchall():
        category = p[0].encode('utf8')
        feed = p[1].encode('utf8')
        date_published = p[2].encode('utf8')
        title = p[3].encode('utf8')
        description = p[4].encode('utf8')
        link = p[5].encode('utf8')
        post_id = 'post_{}'.format(str(post_id_counter).rjust(4, '0'))
        if html:
            new_post = '<a href={}><h4 id={}>{}: {}</h4></a>'\
                       '<p>{}</p><hr>'.format(link,
                                              post_id,
                                              date_published,
                                              title,
                                              description)

        else:
            new_post = Post(date_published = date_published,
                            title = title,
                            description = description,
                            link = link,
                            post_id = post_id)
        posts[category][feed].append(new_post)
        post_id_counter+=1
    return posts

def get_feed_ids(posts):
    # category ids are not needed because they are anyway unique
    feed_ids = defaultdict(lambda: defaultdict(dict))
    counter = 0
    for category in posts.keys():
        for feed in posts[category].keys():
            counter += 1
            feed_ids[category][feed] = 'feed_{}'.format(str(counter).rjust(3, '0'))
    return feed_ids

def generate_html_pages(posts, split_by, feed_ids):
    if split_by not in ['category', 'feed']:
        return None
    html_pages = {}
    page_lines = []
    for category in posts:
        page_lines.append('<h1 id="{0}">{0}</h1>'.format(category))
        for feed in posts[category]:
            feed_id = feed_ids[category][feed]
            page_lines.append('<h2 id="{}">{}</h2>'.format(feed_id, feed))
            for post in posts[category][feed]:
                page_lines.append(post)
            if split_by == 'feed':
                html_pages[feed] = '\n'.join(page_lines)
                page_lines = []
        if split_by == 'category':
            html_pages[category] = '\n'.join(page_lines)
            page_lines = []
    return html_pages

def write_html_pages(posts, split_by, path):
    header = '''<html>\n
    <head>\n
    <meta http-equiv="content-type" content="application/xhtml+xml;charset=utf-8" />\n
    <link rel="stylesheet" href="../libs/bootstrap.min.css">\n
    </head>\n
    <body>\n
    <div class="col-lg-6">\n
    '''
    footer = '''</div></body></html>'''
    feed_ids = get_feed_ids(posts)
    html_pages = generate_html_pages(posts, split_by, feed_ids)
    for name, page in html_pages.items():
        save = '{}{}{}'.format(header, page, footer)
        with open('{}{}.html'.format(path, name), 'w') as f:
            f.write(save)

def write_html_index_by_category(posts, path):
    header = '''<html>\n
    <head>\n
    <meta http-equiv="content-type" content="application/xhtml+xml;charset=utf-8" />\n
    <link rel="stylesheet" href="../libs/bootstrap.min.css">\n
    </head>\n
    <body>\n
    <div class="col-lg-6">\n
    '''
    footer = '''</div></body></html>'''
    feed_ids = get_feed_ids(posts)
    lines = []
    for category in posts:
        lines.append('<ul>')
        lines.append('<li><a href="{0}.html">{0}</a></li>'.format(category))
        for feed in posts[category]:
            lines.append('<ul>')
            feed_id = feed_ids[category][feed]
            lines.append('<li><a href="{}.html#{}">{}</a></li>'.format(category,
                                                                       feed_id,
                                                                       feed))
            lines.append('</ul>')
        lines.append('</ul>')
    html = '{}\n{}'.format(header, '\n'.join(lines), footer)
    with open('{}index.html'.format(path), 'w') as f:
        f.write(html)

def set_exported_for_all(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''UPDATE posts SET exported = 'True' ''')
    conn.commit()
    conn.close()
