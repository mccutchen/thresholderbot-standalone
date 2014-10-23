# Thresholderbot

Thresholderbot is a simple app that grew out of this conversation with
[@mattlemay][mattlemay]:

![](https://raw.github.com/mccutchen/thresholderbot-standalone/master/resources/germ-of-an-idea.png)

It's a personal software robot that will monitor your Twitter timeline and
send you an email every time it sees a link more than a certain *threshold*
number of times. This is super-stupid **Data Science** built on the **Big
Data** of your personal Twitter timeline.

The emails it sends you look like this:

![](https://raw.github.com/mccutchen/thresholderbot-standalone/master/resources/thresholderbot-email.png)

Thresholderbot is designed to be deployed for free on [Heroku][heroku].


## Prerequisites

 1. A [Heroku][heroku] account
 2. The [Heroku Toolbelt][heroku-toolbelt]
 3. A [Twitter app][twitter-apps] whose credentials Thresholderbot can use to
    access your timeline


## Installation

Installation is pretty straightforward (hopefully). The most complicated
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

**A note on access tokens:** To do its job, Thresholderbot must be granted
access to your account by way of OAuth tokens issued for a Twitter app
connected to your account. This is probably the trickiest part of configuring
Thresholderbot. If you have already created a Twitter app, you can go ahead and
[generate the appropriate credentials][twitter-credentials].
Otherwise, you'll need to [create a new Twitter app][twitter-apps] first, then
[generate the appropriate credentials][twitter-credentials].

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


### Verify that it's working

Watch the logs for a little while:

```bash
heroku logs -t
```

You should see some messages like this:

```
2013-06-04T16:30:07.448916+00:00 heroku[api]: Scale to thresholderbot=1 by mccutchen@gmail.com
2013-06-04T16:30:10.148498+00:00 heroku[thresholderbot.1]: Starting process with command `python thresholderbot.py`
2013-06-04T16:30:11.399506+00:00 heroku[thresholderbot.1]: State changed from starting to up
2013-06-04T16:30:48.969903+00:00 app[thresholderbot.1]: INFO thresholderbot.py:22: Got 462 friends on startup
```

When you see the message about friends on startup, you know your Thresholderbot is configured correctly.


## Adjusting the threshold

The default threshold is **5**, which means you'll only receive emails for
links shared at least 5 times by accounts you follow on Twitter. You'll
probably wan to adjust the threshold as necessary to tune how many emails you
get from Thresholderbot, depending on the nature of the accounts you follow
and how much overlap there is in the content they share.

For my personal account, I've found that a threshold of 4 seems to hit the
right balance of signal to noise.

Updating the threshold is easy and (essentially) instant. For example, if you
want to receive more emails from Thresholderbot, you might want to set your
threshold at 2:

```bash
heroku config:set THRESHOLD=2
```


## Local Development/Testing

To run a Thresholderbot locally, you'll make sure you have the following
prerequisites:

 1. [foreman][foreman] (installed by the Heroku Toolbelt)
 2. [pip][pip]
 3. [redis][redis]

Once those are met, running locally should be as simple as:

```bash
pip install -r requirements.txt
foreman start
```


## Contributing

Suggestions/ideas/insults/pull requests are welcome!


[mattlemay]: https://twitter.com/mattlemay
[heroku]: https://heroku.com/
[heroku-toolbelt]: https://toolbelt.heroku.com/
[heroku-config]: https://devcenter.heroku.com/articles/config-vars#local-setup
[twitter-credentials]: https://dev.twitter.com/docs/auth/tokens-devtwittercom
[twitter-apps]: https://dev.twitter.com/apps
[foreman]: https://github.com/ddollar/foreman
[pip]: http://www.pip-installer.org/
[redis]: http://redis.io/
