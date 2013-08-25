#!/usr/bin/env python2

from datetime import datetime
import glob
import os
import sqlite3

from feedreader.parser import from_url
from lxml import etree as ET

from config import CONFIG_PATH, DB_PATH

def parse_config(directory):
    feeds = {}
    # ugly
    os.chdir(directory)
    url_files = glob.glob('*.txt')

    for f in url_files:
        category = f[:-4]
        category_feeds = []
        with open(f) as f:
            for line in f:
                category_feeds.append(line.strip('\n'))
        feeds[category] = category_feeds
    return feeds 


class Post(object):
    def __init__(self, db_conn, date_added, date_published, feed, category, title, link, description):
        self.db_conn = db_conn
        self.feed = feed
        self.title = title
        self.link = link
        self.description = description
        self.category = category
        self.date_added = date_added
        self.date_published = date_published

        self.insert_post()

    def _insert_into_db(self):
        values = [self.date_added,
                  self.date_published,
                  self.feed,
                  self.category,
                  self.link, 
                  self.title,
                  self.description]
        c = self.db_conn.cursor()
        c.execute('''INSERT INTO posts (dateadded,
                                        datepublished,
                                        feed,
                                        category,
                                        link, 
                                        title,
                                        description) 
                     VALUES (?,?,?,?,?,?,?)''', values)
        self.db_conn.commit()

    def insert_post(self):
        if not self._post_exists():
            self._insert_into_db()

    def _post_exists(self):
        c = self.db_conn.cursor()
        values = [self.feed, self.title, self.date_published]
        c.execute('SELECT id FROM posts WHERE feed = ? AND title = ? AND datepublished = ?', values)
        return True if len(c.fetchall()) is not 0 else False


class RSSImporter(object):
    def __init__(self, db_path, feeds):
        self.feeds = feeds
        self.date_added = datetime.now()

        self.db_conn = sqlite3.connect(db_path)
        self.process_feeds()
        self.db_conn.close()

    def _categories_list(self):
        return self.feeds.keys()

    def process_feeds(self):
        categories = self._categories_list()
        for c in categories:
            self._process_category(c)

    def _process_category(self, category):
        urls = self.feeds[category]
        for u in urls:
            print 'Parsing: '+u
            try:
                parsed = from_url(u)
                for entry in parsed.entries:
                    title = self._process_entry_item(entry.title)
                    link = self._process_entry_item(entry.link)
                    description = self._process_entry_item(entry.description)
                    published = self._process_entry_item(entry.published)
                    Post(self.db_conn, self.date_added, published, u, category, title, link, description)
            except Exception as e:
                print 'ERROR: Parsing of '+u+' was not possible'
                print e

    def _process_entry_item(self, text):
        result = ''
        try:
            result = text.text
        except AttributeError:
            result = text
        if result == None:
            result = ''
        return result
            

urls = parse_config(CONFIG_PATH)
RSSImporter(DB_PATH, urls)
