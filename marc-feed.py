import argparse
import boto3
import feedparser
import re
import redis
import sys
from datetime import date, datetime, timedelta


url = 'http://mtamarylandalerts.com/rss.aspx?ma'


def publish_notification(summary, topic):
    """
    Accepts message and topic for sending SNS notification
    """
    sns_client = boto3.client('sns',region_name='us-east-1')

    return sns_client.publish(TopicArn=topic, Message=summary)


def redis_helper(summary, action):
    """
    Helper function used to interface with redis cache to perform
    get and set operations
    """
    rlist = "%s_MARCeNotifications" % (date.today())
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    if action == "get":
        items = r.lrange(rlist, 0, -1)
        if summary in items:
            return True
        else:
            return False
    elif action == "set":
        # check if list exists...if so append. If not create new list/set TTL
        if r.exists(rlist) is True:
            r.rpush(rlist, summary)
        else:
            r.lpush(rlist, summary)
            r.expire(rlist, 86400)


def dry_run(topic):
    """
    This function is used test SNS notifications
    """
    try:
        publish_notification("MARC eNotifications Sample Notification",
                             topic)
        return "Sample notification sent!"
    except Exception as e:
        sys.exit(e)


def rss_parser(url, topic):
    """
    Main RSS feed parser function
    """
    rss_data = feedparser.parse(url)
    for entry in rss_data['entries']:
        pub_date = entry['published']
        to_est = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S GMT')
        to_est += - timedelta(hours=5)
        summary = ("Published @ %s EST %s\n\n" % (to_est,
                    entry['summary_detail']['value']))
        check_cache = redis_helper(summary, "get")
        if check_cache is True:
            pass
        else:
            publish_notification(summary, topic)
            redis_helper(summary, "set")
            print "Posted latest notifications to SNS topic!"
        summary = ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('topicarn', help='enter ARN for SNS topic')
    parser.add_argument('--dry-run', help='run with this flag to send test\
                        notification', action='store_true')
    args = parser.parse_args()
    topic = args.topicarn

    t_match = re.search(r'arn:aws:sns:\w*-\w*-\d:\d\d\d\d\d\d\d\d\d\d\d\d:\w*',
                        topic)

    if t_match:
        topic = t_match.group()
        if args.dry_run:
            print dry_run(topic)
        else:
            print rss_parser(url, topic)
    else:
        sys.exit("Please input valid SNS Topic ARN...")


if __name__ == '__main__':
    main()
