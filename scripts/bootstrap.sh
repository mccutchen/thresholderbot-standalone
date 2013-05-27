#!/bin/sh

set -e

# Make sure we're in the project root
# http://stackoverflow.com/a/4774063/151221
pushd `dirname $0` > /dev/null
scriptpath=`pwd -P`
popd > /dev/null
cd $scriptpath/..

# Make sure the heroku toolbelt is installed
command -v heroku >/dev/null || {
    echo "Please install the heroku toolbelt:"
    echo "https://toolbelt.heroku.com/"
    exit 1
}

git remote | grep heroku >/dev/null && {
    app=`git remote -v | grep heroku | grep -v fetch | awk '{ print $2 }' | awk -F":" '{print $2}' | awk -F"." '{print $1}'`
    echo "Found existing heroku app: $app"
} || {
    echo "Creating new heroku app..."
    heroku create
}
echo

# Set up appropriate environment vars, only if a .env file doesn't exist
if ! [ -f .env ]; then
    echo "We're going to create a .env file containing your Thresholderbot's configuration."
    echo
    echo "You need the consumer key and consumer secret for a Twitter app, along with your account's access token key and secret for that app."
    echo
    echo "You can create an app (or choose one of your existing apps) here:"
    echo "https://dev.twitter.com/apps"
    echo
    echo "And here are instructions for generating an access token for your account for that app:"
    echo "https://dev.twitter.com/docs/auth/tokens-devtwittercom"
    echo
    read -p "Enter the app's consumer key: " consumer_key
    read -p "Enter the app's consumer secret: " consumer_secret
    read -p "Enter your access token key: " access_token_key
    read -p "Enter your access token secret: " access_token_secret
    echo
    echo "Now we will configure the Thresholderbot itself."
    read -p "How many times must a link appear in your timeline before you are notified? (default: 5) " threshold
    read -p "What email address should notifications be sent to? " to_address

    if [ -n $threshold ]; then
        threshold=5
    fi

    cat > .env <<EOF
THRESHOLD=$threshold
TO_ADDRESS=$to_address
FROM_ADDRESS=thresholderbot@mccutch.org

CONSUMER_KEY=$consumer_key
CONSUMER_SECRET=$consumer_secret
ACCESS_TOKEN_KEY=$access_token_key
ACCESS_TOKEN_SECRET=$access_token_secret
EOF
else
    echo "Skipping existing .env file"
fi
echo

echo "Installing required addons..."
heroku addons:add rediscloud:20
heroku addons:add mandrill:starter
echo

echo "Syncing .env with heroku..."
heroku plugins:install git://github.com/ddollar/heroku-config.git
heroku config:push
heroku config:pull
echo

echo "Deploying to heroku..."
git push heroku master
echo

echo "Finished. Now either test your config by running locally:"
echo
echo "  $ foreman start"
echo
echo "or start your thresholderbot in production:"
echo
echo "  $ heroku ps:scale thresholderbot=1"
