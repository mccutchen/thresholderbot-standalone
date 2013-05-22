Thresholder
===========

Basic steps:

```bash
# create a new app
heroku create

# add required addons
heroku addons:add mongohq:sandbox
heroku addons:add mailgun:starter
heroku addons:add scheduler:standard

# set up appropriate environment vars
cat > .env <<EOF

# Get these from an app at https://dev.twitter.com/apps
ACCESS_TOKEN_KEY=xxx
ACCESS_TOKEN_SECRET=yyy
CONSUMER_KEY=aaa
CONSUMER_SECRET=bbb

# Set your threshold (defaults to 5)
THRESHOLD=5

# Recipient of reports
TO_ADDRESS=you@yourdomain.com

# Find this via heroku addons:open mailgun
MAILGUN_DOMAIN=yourdomain.mailgun.org

EOF

# push config out to heroku
heroku plugins:install git://github.com/ddollar/heroku-config.git
heroku config:push

# schedule the report task
heroku addons:open scheduler
# add "scripts/report.py" in the task box, scheduled to run daily

# deploy and scale up to one process
git push heroku master
heroku ps:scale watcher=1
```
