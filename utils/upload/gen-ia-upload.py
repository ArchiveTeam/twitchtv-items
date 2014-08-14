#!/usr/bin/env python

import sys

collection = 'archiveteam_twitchtv'
with open('serial') as f:
        serial = f.read()

for dir in sys.argv[1:]:
        if len(os.listdir(dir)) > 0:
            last_component = dir.split('/')[-1]
            item_name = "archiveteam_twitchtv_%s_%s" % (last_component, serial.strip())
            title = 'Archive Team Twitch.tv: %s (%s)' % (last_component, serial.strip())

            print '/home/archiveteam/.local/bin/ia upload %s %s/*.warc.gz -c --metadata="mediatype:web" --metadata="title:%s" --metadata="date:2014" --metadata="language:eng" --metadata="collection:%s" --delete' % (item_name, dir, title, collection)
