#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
/usr/bin/curl -X GET https://fradgify.kozow.com/api/album_list >> /var/www/fradgify.kozow.com/album-player/crontab.log 2>&1
