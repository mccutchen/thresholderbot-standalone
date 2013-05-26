Thresholderbot
==============

Thresholderbot is a personal software robot that will monitor your Twitter
timeline and send you daily reports containing links that were shared over
a certain *threshold* number of times.

It's designed as a kind of set-it-and-forget-it service to be deployed for
free on [Heroku][heroku].


Prerequisites
-------------

 1. [The Heroku Toolbelt][heroku-toolbelt]


Installation
------------

Installation will hopefully be pretty straightforward. The most complicated
part will be figuring out the Twitter credentials to use.

First, clone this git repo:

```bash
git clone git@github.com:mccutchen/thresholderbot.git
cd thresholderbot
```

Next, set up the Heroku app:

```bash
heroku create
heroku addons:add rediscloud:20
heroku addons:add mandrill:starter
```

Create an appropriate config file. I recommend keeping your config in
a `.env` file, [for use with Foreman and the heroku-config plugin][heroku-config].

Here's what your Heroku environment should look like:

```bash
cat .env
```
```bash
# Twitter app and access token credentials
CONSUMER_KEY=aaa
CONSUMER_SECRET=bbb
ACCESS_TOKEN_KEY=xxx
ACCESS_TOKEN_SECRET=yyy

# Set your threshold (defaults to 5)
THRESHOLD=5

# Recipient of reports
TO_ADDRESS=you@yourdomain.com
```

Push your config out to Heroku:

```bash
heroku plugins:install git://github.com/ddollar/heroku-config.git
heroku config:push
```

Deploy to heroku and scale up to one process:

```bash
git push heroku master
heroku ps:scale thresholderbot=1
```


Verify that it's working
------------------------

Watch the logs for a little while:

```bash
heroku logs -t
```


Local Development/Testing
-------------------------

To run a Thresholderbot locally, you'll make sure you have the following
prerequisites:

 1. [Foreman][foreman] (installed by the Heroku Toolbelt)
 2. [pip][pip]
 3. [MongoDB][mongodb]

Once those are met, running locally should be as simple as:

```bash
pip install -r requirements.txt
foreman start
```

[heroku]: https://heroku.com/
[heroku-toolbelt]: https://toolbelt.heroku.com/
[heroku-config]: https://devcenter.heroku.com/articles/config-vars#local-setup
[foreman]: https://github.com/ddollar/foreman
[pip]: http://www.pip-installer.org/
[mongodb]: http://mongodb.org/
