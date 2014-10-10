#!/bin/bash
#
# Script to set up CAP Tools for running locally.
# It installs required Python modules and does post-configuration steps.
# The script was tested on Debian Linux OS with Python 2.7.
# Please run the following command first to install the required packages:
# sudo apt-get install python-virtualenv libxml2-dev libxslt-dev libxmlsec1-dev libmysqlclient-dev python-dev
# This script should be from a new directory you create to contain the running
# server. No superuser privileges required.

# TODO(arcadiy): automate code checkout and virtual environment setup processes
# after we check in code to GitHub.

PIP="../venv/bin/pip"
PYTHON="../venv/bin/python"

# Check virtual environment setup.
if [ ! -e "$PIP" ] && [ ! -e "$PYTHON" ]
then
  echo "Script expects that you have first run 'virtualenv ../venv'"
  exit 1
fi

# Install required modules if they don't already exist:

# beautifulsoup4 - Used to pretty-print HTML and XML feeds.
$PIP install beautifulsoup4

# django - CAP collector is written on top of the Django framework.
$PIP install django

# lxml - Required for parsing XML.
$PIP install lxml

# python-dateutil - Easy dates parsing.
$PIP install python-dateutil

# pytz - Timezone support for Python.
$PIP install pytz

# pyXMLSecurity - Required for computing XML signatures for CAP messages.
$PIP install pyXMLSecurity

# selenium - Functional testing framework.
$PIP install selenium


# Generate Django secret key.
SECRET_KEY=$(cat /dev/urandom | tr -dc 'a-z0-9!@#$%^&*()_+' | fold -w 50 | head -n 1)
echo 'SECRET_KEY="$SECRET_KEY"' > ./sensitive.py

# Create path for active alerts. Active alerts are served from this path in the
# file system.
mkdir -p alerts/active

# Create path for inactive alerts.  Active alerts are moved here once they
# expire and are kept forever.
mkdir alerts/inactive

# Link client part of the application.
ln -s ../../javascript/cap_creator client

# Download JQuery JS library, used to render the user interface.
wget http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js -O ./client/js/jquery-1.10.2.min.js

# Download JQuery library map file, not required for production, but improves debugger experience.
wget http://code.jquery.com/jquery-1.10.2.min.map -O ./client/js/jquery-1.10.2.min.map

# Download JQuery Mobile JS library, which improves things like touch support.
wget http://code.jquery.com/mobile/1.3.0/jquery.mobile-1.3.0.min.js -O ./client/js/jquery.mobile-1.3.0.min.js

# Download Moment JS library, for parsing, validating and displaying dates.
wget http://cdnjs.cloudflare.com/ajax/libs/moment.js/2.7.0/moment.min.js -O ./client/js/moment.min.js

# Download OpenLayers JS library, for displaying a dynamic map to create areas.
wget http://openlayers.org/api/2.11/OpenLayers.js -O ./client/js/OpenLayers.js

# Download JQuery mobile CSS file.
wget http://code.jquery.com/mobile/1.3.0/jquery.mobile-1.3.0.min.css -O ./client/css/jquery.mobile-1.3.0.min.css

# Sync Django models to databse. This involves superuser creation.
$PYTHON manage.py syncdb

# Compile translation messages to .mo files.
$PYTHON manage.py compilemessages
