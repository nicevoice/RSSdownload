from datetime import datetime
import optparse
import os

import config
import rssdownload.exporter as updater
import rssdownload.importer as importer

p = optparse.OptionParser()

p.add_option('-u', dest='updatefeeds', action='store_true', help='Update feeds')
p.add_option('-e', dest='exporthtml', action='store_true', help='Export unread posts to HTML')
p.add_option('-m', dest='markread', action='store_true', help='Mark exported as read')
p.add_option('-s', dest='send', action='store_true', help='Send unread posts as emails')

opt, args = p.parse_args()

if opt.updatefeeds:
    urls = updater.parse_config(config.CONFIG_PATH)
    updater.RSSUpdater(config.DB_PATH, urls)
if opt.exporthtml:
    export_path = config.EXPORT_PATH+datetime.now().strftime('%Y-%m-%d %H:%M/')
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    posts = exporter.get_not_exported_posts(config.DB_PATH)
    categories = exporter.export_with_categories(posts, export_path)
    exporter.create_index(categories, export_path)
if opt.markread:
    exporter.set_exported_for_all(conig.DB_PATH)

