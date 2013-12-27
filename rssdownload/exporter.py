#!/usr/bin/env python2

from collections import defaultdict
from datetime import datetime
import sqlite3
    
HEADER = '''<html>\
<head>\n
<meta http-equiv="content-type" content="application/xhtml+xml;charset=utf-8" />\n
<link rel="stylesheet" href="../libs/bootstrap.min.css">\n
</head>\n
<body>\n
<div class="col-lg-6">\n
'''

FOOTER = '''</div></body></html>'''

def get_not_exported_posts(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT category, feed, datepublished, title, description, link FROM posts
                 WHERE exported = 'False' ORDER BY category, feed ''')
    return c.fetchall()
    
def set_exported_for_all(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''UPDATE posts SET exported = 'True' ''')
    conn.commit()
    conn.close()

def write_category(f, category):
    if category != None:
        category = category.encode('utf8')
    f.write('<h1>'+category+'</h1>\n')

def write_feed(f, feed, feed_id):
    if feed != None:
        feed = feed.encode('utf8')
    f.write('<h2 id="{}">{}</h2>\n'.format(feed_id, feed))

def write_post(f, title, link, description, date_published, post_id):
    if title == None:
        title = ''
    else:
        title = title.encode('utf8')
    if link == None:
        link = ''
    else:
        link = link.encode('utf8')
    if description == None:
        description = ''
    else:
        description = description.encode('utf8')

    if not date_published:
        date_published = 'No date'
    else:
        date_published = datetime.strptime(date_published[:10], '%Y-%m-%d')
        date_published = date_published.strftime('%Y-%m-%d')


    f.write('<a href={0}><h4 id={1}>{2}: {3}</h4></a>\n'.format(link, post_id, date_published, title))
    f.write('<p>'+description+'</p>\n<hr>\n')

def export_with_categories(posts, export_path):
    category = ''
    feed = ''
    categories = defaultdict(lambda: defaultdict(list))
    feed_id = 0
    post_no = 0
    post_id = ''
    new_feed = False
    for post in posts:
        if post[0] != category:
            # new category
            feed_id = 0
            post_no = 0
            category = post[0]
            f = open(export_path+category+'.html', 'w')
            f.write(HEADER)
        if post[1] != feed:
            # new feed
            feed = post[1]
            write_feed(f, feed, feed_id)
            new_feed = True
        post_id = '{0}{1}'.format(feed_id, post_no)
        write_post(f,post[3], post[5], post[4], post[2], post_id)
        post_no += 1
        categories[category][feed].append([post[3], post_id, post[5]])
        if new_feed:
            feed_id += 1
            new_feed = False
    f.write(FOOTER)
    f.close()
    return categories

def create_index(categories, export_path):
    f = open(export_path+'index.html','w')
    f.write(HEADER)
    f.write('<h1>Index</h1>')
    f.write('<ul>\n')
    for category, feeds in categories.items():
        f.write('<ul>\n')
        f.write('<li><a href="{0}.html">{0}</a></li>\n'.format(category))
        for feed, posts in feeds.items():
            f.write('<ul>\n')
            f.write('<li><a href="{0}.html#{2}">{1}</a></li>\n'.format(category, feed, posts[0][1][0]))
            f.write('<ul>\n')
            for post in posts:
                f.write('<li><a href="{0}.html#{1}">{2}</a>&nbsp;'\
                        '[<a href="{3}">link</a>]</li>\n'.format(category,
                                                                 post[1],
                                                                 post[0].encode('utf8'), 
                                                                 post[2].encode('utf8')))
            f.write('</ul>\n')
            f.write('</ul>\n')
        f.write('</ul>\n')
    f.write('</ul>\n')
    f.write(FOOTER)
    f.close()
