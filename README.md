# MARC-Notifier
Simple python script that pushes MARC train notifications via SNS

### Usage
```
usage: marc-feed.py [-h] [--dry-run] topicarn

positional arguments:
  topicarn    enter ARN for SNS topic

optional arguments:
  -h, --help  show this help message and exit
  --dry-run   run with this flag to send test notification
  ```

### Setup
*Below is example setup, feel free to run this however you would like!*
- [Install Redis](https://redis.io/topics/quickstart) on EC2 instance
- cron python script
- Ensure IAM user/role has permissions to publish to your SNS topic
