#!/usr/bin/env python2

from datetime import datetime
import optparse
import os

import config
import rssdownload.updater as updater
import rssdownload.exporter as exporter

p = optparse.OptionParser()

p.add_option('-u', dest='updatefeeds', action='store_true', help='Update feeds')
p.add_option('-e', dest='exporthtml', action='store_true', help='Export unread posts to HTML')
p.add_option('-m', dest='markread', action='store_true', help='Mark exported as read')
p.add_option('-s', dest='send', action='store_true', help='Send unread posts as emails')

opt, args = p.parse_args()

if opt.updatefeeds:
    urls = updater.parse_config(config.CONFIG_PATH)
    updater.RSSUpdater(config.DB_PATH, urls)

if opt.exporthtml or opt.send:
    posts = exporter.get_not_exported_posts(config.DB_PATH)
    if posts:
        if opt.exporthtml:
            export_path = config.EXPORT_PATH+datetime.now().strftime('%Y-%m-%d %H:%M/')
            if not os.path.exists(export_path):
                os.makedirs(export_path)
            exporter.write_html_pages(posts, 'category', export_path)
            exporter.write_html_index_by_category(posts, export_path)
        elif opt.send:
            pass
            # TODO hier weitermachen.
            # exporter muss umgebaut werden. sodass er in einer eigener funktion speichern tut.
    else:
        print "Nothing to do. No posts"

    
if opt.markread:
    exporter.set_exported_for_all(config.DB_PATH)

