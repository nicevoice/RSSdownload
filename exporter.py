from datetime import datetime
import sqlite3
import os.path

EXPORT_PATH = '/home/marek/Dropbox/projekte/RSSdownload/'+datetime.now().strftime('%Y-%m-%d %H:%M/')

if not os.path.exists(EXPORT_PATH):
    os.makedirs(EXPORT_PATH)
 
DB_PATH = '/home/marek/Dropbox/projekte/RSSdownload/rssdownload.db'

HEADER = '''<html>\n
            <head>\n
            <meta http-equiv="content-type" content="application/xhtml+xml;charset=utf-8" />\n

            </head>\n
            <body>

'''

FOOTER = '''</body></html>'''

def get_not_exported_posts(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''SELECT category, feed, datepublished, title, description, link FROM posts
                 WHERE exported = 'False' ORDER BY category,feed ''')
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

def write_feed(f, feed):
    if feed != None:
        feed = feed.encode('utf8')
    f.write('<h2>'+feed+'</h2>\n')

def write_post(f,title,link,description, date_published):
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
    if date_published == None:
        date_published = ''
    else:
        date_published = datetime.strptime(date_published[:10], '%Y-%m-%d')
        date_published = date_published.strftime('%Y-%m-%d')


    f.write('<a href='+link+'><h4>'+date_published+': '+title+'</h4></a>\n')
    f.write('<p>'+description+'</p>\n')

def export_with_categories(posts):
    category = ''
    feed = ''
    categories = []
    for post in posts:
        if post[0] != category:
            category = post[0]
            categories.append(category)
            f = open(EXPORT_PATH+category+'.html', 'w')
            f.write(HEADER)
        if post[1] != feed:
            feed = post[1]
            write_feed(f, feed)
        write_post(f,post[3], post[5], post[4], post[2])
    f.close()
    return categories

def create_index(categories):
    f = open(EXPORT_PATH+'index.html','w')
    f.write(HEADER)
    for c in categories:
        f.write('<a href=\"'+c+'.html\">'+c+'</a><br>\n')
    f.close()
    
posts = get_not_exported_posts(DB_PATH)
categories = export_with_categories(posts)
create_index(categories)

set_exported_for_all(DB_PATH)
