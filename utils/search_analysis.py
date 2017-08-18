import redis
import csv

r = redis.StrictRedis('ecs-search-001.cpzshl.0001.apse1.cache.amazonaws.com', 8080, 9)

with open('daily.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile)
    for row in r.hkeys('daily_search_activity'):
        (pdate, platform, lang, text) = row.split('|')
        count = r.hget('daily_search_activity', row)
        try:
            spamwriter.writerow([pdate, platform, lang, text, count])
        except Exception as err:
            print row


with open('user.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile)
    for row in r.hkeys('user_search_activity_detail'):
        (pdate, platform, lang, userid, author_found, pratilipi_found, text) = row.split('|')
        try:
            spamwriter.writerow([pdate, platform, lang, userid, author_found, pratilipi_found, text])
        except Exception as err:
            print row
