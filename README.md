Thresholder
===========

Basic steps:

```bash
heroku create
git push heroku master
heroku addons:add mongohq:sandbox
heroku config:set ACCESS_TOKEN_KEY="xxx" ACCESS_TOKEN_SECRET="yyy" CONSUMER_KEY="aaa" CONSUMER_SECRET="bbb"
heroku ps:scale watcher=1
```
