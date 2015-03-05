Installation Instructions
==========

## Audience

This document is intended for technical administrators planning to install and
maintain an instance of the CAP Creator.  The instructions currently assume you
plan to run the server on a Debian/Ubuntu Linux distribution, or on Google
AppEngine.

## Table of Contents

[Architecture](#architecture)

[Getting started](#getting-started)

  * [Decide on a database](#decide-on-a-database)
  * [Install Python and Git](#install-python-and-git)
  * [Download the application code](#download-the-application-code)
  * [Install required libraries](#install-required-libraries)
  * [Run the setup script](#run-the-setup-script)
  * [Configure the application for your organization](#configure-the-application-for-your-organization)

[Testing your setup](#testing-your-setup)

  * [Run a local version of the application](#run-a-local-version-of-the-application)
  * [Run the tests](#run-the-tests)

[Configuring CAP Creator Features](#configuring-cap-creator-features)

  * [Setting up users and passwords](#setting-up-users-and-passwords)
  * [Setting up templates](#setting-up-templates)
     * [Message templates](#message-templates)
     * [Area templates](#area-templates)
     * [Adding templates one at a time](#adding-templates-one-at-a-time)
     * [Adding templates in bulk](#adding-templates-in-bulk)

[Hosting Requirements](#hosting-requirements)

  * [Deploying to Google AppEngine](#deploying-to-google-appengine)
  * [Deploying to Google Compute Engine](#deploying-to-google-compute-engine)
  * [Installing a digital certificate](#installing-a-digital-certificate)

[Appendix](#appendix)

* [Tool limitations](#tool-limitations)
  * [Adding translations](#adding-translations)
  * [Generating code test coverage](#generating-code-test-coverage)
  * [Troubleshooting](#troubleshooting)


<a name="architecture"></a>
## Architecture

There are three main components of the CAP Creator:

1. Server
2. Database
3. User Interfaces

The Server is written in [Python](https://www.python.org/) using the
[Django](https://www.djangoproject.com/) framework.

The Database used can be [any database supported by Django](https://docs.djangoproject.com/en/dev/ref/databases/),
but at the moment, MySQL is assumed at a few points in the configuration.
It is recommended to make sure that the database used can be periodically
backed up in case of power outages or production failures.

The user interfaces are written using HTML and CSS whenever possible.  Dynamic
interaction is written in [Javascript](http://en.wikipedia.org/wiki/JavaScript)
using the [jQuery Mobile](http://jquerymobile.com/) framework.

<a name="getting-started"></a>
## Getting started

<a name="decide-on-a-database"></a>
#### 1. Decide on a database

If you plan to deploy CAP creator, you need to host the alerts it creates in a
database.  By default, the setup process guides you through configuring a MySQL
database.

For more information on setting up a database, refer to the
[Django documentation](https://docs.djangoproject.com/en/dev/ref/databases/#connecting-to-the-database).
If you plan to use Google Cloud SQL, refer to the
[Google Cloud SQL Getting Started guide](https://cloud.google.com/sql/docs/getting-started)
instead.

At minimum, you will need four values to enter as part of step 4.

* [HOST](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-HOST)
* [NAME](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-NAME)
* [USER](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-USER)
* [PASSWORD](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-PASSWORD)

<a name="install-python-and-git"></a>
#### 2. Install Python and Git

You first need to install Python, if you do not have it already.  To check,
type `python` in your shell and you should see something like

    $ python
    Python 2.7.5 (default, Mar  9 2014, 22:15:05)
    [GCC 4.2.1 Compatible Apple LLVM 5.0 (clang-500.0.68)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

Django works with any Python version from 2.6.5 to 2.7.  If you need to install
python or upgrade, [download python](http://www.python.org/download).

Next, you need to install Git if you don’t already have it.  To check if it’s
installed already, run

    $ git
    usage: git [--version] [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]
    ...

If you need to install it, follow the instructions at
[https://help.github.com/articles/set-up-git/](https://help.github.com/articles/set-up-git/)

<a name="download-the-application-code"></a>
#### 3. Download the application code

Download the source code for the application from GitHub.  The Python code is
hosted in a different repository than the Javascript code, so you have to
complete both steps

    $ mkdir CAPTools; cd CAPTools
    CAPTools$ git clone https://github.com/CAPTools/CAPCollector.git
    Cloning into 'CAPCollector'...

    CAPTools$ git clone https://github.com/CAPTools/CAPCreator.git
    Cloning into 'CAPCreator'...

If this was successful, you’ll now have 2 subpackages in your directory for each
repository.

<a name="install-required-libraries"></a>
#### 4. Install required libraries

The CAP Creator needs the following packages.  On Linux/UNIX, you can install
them using apt-get.

    CAPTools$ cd CAPCollector
    CAPCollector$ sudo apt-get update; sudo apt-get -y install $(grep -vE "^\s*#" packages.txt | tr "\n" " ")

Then, set up a virtual environment using pip.

    CAPCollector$ virtualenv ../venv
    CAPCollector$ source ../venv/bin/activate

<a name="run-the-setup-script"></a>
#### 5. Run the setup script

`setup.sh` does the following things:

* Creates a virtual environment for the application (Python virtualenv) and
installs required Python modules.
* Generates a [SECRET_KEY](https://docs.djangoproject.com/en/dev/ref/settings/#secret-key)
for your Django application and puts it to a file called `sensitive.py` where
Django knows to look for it.
* Downloads required Javascript libraries, CSS dependencies and images from
third-party libraries that are required for the editor to function.
* Prompts you to enter your database configuration settings (Database host,
name, user, password), which are also stored `sensitive.py`
* Prompts you to create a superuser for the application.  The superuser will be
able to add and remove users from the application.
* Synchronizes models to database and compiles translation files.

        (venv)CAPCollector$ export CAP_TOOLS_DEV=1
        (venv)CAPCollector$ bash setup.sh

<a name="configure-the-application-for-your-organization"></a>
#### 6. Configure the application for your organization

Modify `CapCollector/settings_prod.py`. The most common settings to update follow:

    # Change to the URL where users will find this app.
    SITE_DOMAIN = "myagency.gov"

    # A string representing the time zone for this installation.
    # https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
    TIME_ZONE = "US/Central"

    # The default language for the interface and all alerts.
    # See https://docs.djangoproject.com/en/dev/ref/settings/#language-code.
    LANGUAGE_CODE = "en-us"

    # All languages for which alerts will be created.
    # See https://docs.djangoproject.com/en/dev/ref/settings/#languages.
    LANGUAGES = (
    ("en-us", "English"),
    ("hi", "हिंदी"),
    ("pt-br", "Português"),
    )

    # A default map viewport for the alert area selector.
    MAP_DEFAULT_VIEWPORT = {
        "center_lat": 37.422,
        "center_lon": -122.084,
        "zoom_level": 12,
    }

<a name="testing-your-setup"></a>
## Testing your setup

<a name="run-a-local-version-of-the-application"></a>
#### Run a local version of the application

You can run a local version of the application against a test version of the
database with the following commands, as executed from the CAPCollector directory.
Make sure you have started a virtual environment and run setup.sh as above

    (venv)CAPCollector$ python manage.py runserver localhost:9090

This will start the server at [http://localhost:9090](http://localhost:9090).
If you want to use a different port

<a name="run-the-tests"></a>
#### Run the tests

You can also run the functional tests included with the code to ensure the
application is functioning correctly.

    (venv)CAPCollector$ python manage.py test

To rerun a single test that may have been failing

    (venv)CAPCollector$ python manage.py test tests.test_utils
    (venv)CAPCollector$ python manage.py test tests.test_utils.UtilsTests.test_parse_valid_alert

<a name="configuring-cap-creator-features"></a>
# Configuring CAP Creator Features

<a name="setting-up-users-and-passwords"></a>
#### Setting up users and passwords

Visit `https://YOUR_URL/admin/` and log in as the administrator you created
while running `setup.sh`.  You should see a screen like the following:

![image alt text](image_0.png)

To add a user, click the "Add" button to the right of Users, then click the gray
“Add user” button in the upper right of the screen.  You will be taken to a
screen where a new user can add their username and password.

![image alt text](image_1.png)

By default, the user will have privileges to log into the CAP Creator tool, but
they will not have privileges to release alerts to the public.  That privilege
is controlled by the `ALERT_CREATORS_GROUP_NAME` in `settings.py`, which defaults
to `"can release alerts"`.  To allow a user to release alerts, click on the newly
created user from `https://YOUR_URL/admin/auth/user/.`  Then
 1. click “can release alerts” under the Permissions Groups: subsection
 2. click the right arrow to move “can release alerts” to “Chosen groups”
 3. click “Save” at the bottom right of the page.

![image alt text](image_2.png)

<a name="setting-up-templates"></a>
#### Setting up templates

Templates are one of the most powerful features of the CAP Creator tool.  They
allow pre-configuration for each possible type of alert being issued and alert
area to which they can apply.  Configuring templates allows alert creators to
issue alerts faster, follow best practices, and reduce the chances of making
mistakes.

There are two types of templates in the CAP Creator tool: Message templates and
Area templates.  Each are explained below.

<a name="message-templates"></a>
##### Message templates

Message templates are defined as partially-complete CAP alerts.  They are
specified in XML.  Here is an example Message template for a "Minor earthquake"
CAP alert (this example is based on [Appendix A.3. in the Common Alerting
Protocol 1.2 specification](http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html)):

    <alert xmlns = "urn:oasis:names:tc:emergency:cap:1.2">
      <sender>trinet@caltech.edu</sender>
      <status>Actual</status>
      <msgType>Alert</msgType>
      <scope>Public</scope>
      <info>
        <category>Geo</category>
        <event>Earthquake</event>
        <responseType>None</responseType>
        <urgency>Past</urgency>
        <severity>Minor</severity>
        <certainty>Observed</certainty>
        <senderName>Southern California Seismic Network (TriNet) operated by Caltech and USGS</senderName>
        <headline>EQ {{MAGNITUDE}} {{LOCATION}}</headline>
        <description>A minor earthquake measuring {{MAGNITUDE}} on the Richter scale occurred near {{LOCATION}} at {{TIME}} {{TIMEZONE}} on {{DATE}}.</description>
        <web>http://www.trinet.org/scsn/scsn.html</web>
        <parameter>
          <valueName>EventID</valueName>
          <value>{{EVENT ID}}</value>
        </parameter>
        <parameter>
          <valueName>Version</valueName>
          <value>1</value>
        </parameter>
        <parameter>
          <valueName>Magnitude</valueName>
          <value>{{MAGNITUDE NUMBER}} Ml</value>
        </parameter>
        <parameter>
          <valueName>Depth</valueName>
          <value>{{DEPTH MILES}} mi.</value>
        </parameter>
      </info>
    </alert>


Templates should contain fields that are not expected to change between alerts
of the same type ("Minor earthquake" in this case).  `<identifier>`, `<sender>`,
`<sent>`, `<expires>`, etc are not good candidates for template parameters.

Other fields like `<description>` may contain some information that does not
change between alerts and other data that does.  In this case, you can fill in
the information that does not change and specify that the alert creator needs
to add in more using *placeholders*. Template placeholders are specified using
double curly braces, eg `{{MAGNITUDE}}`.

    <description>
      A minor earthquake measuring {{MAGNITUDE}} on the Richter scale occurred
      near {{LOCATION}} at {{TIME}} {{TIMEZONE}} on {{DATE}}.
    </description>


To make sure placeholders are not accidentally left in real alerts, the CAP
creator automatically validates that all instances of placeholders have been
removed before allowing the alert creator to continue.

![image alt text](image_3.png)

Note that at this time, message templates assume only a single `<info>` block.
Any `<area>` blocks present in a message template are ignored
(see [Area templates](#area-templates) below).

Message templates support one additional field that is not part of the CAP spec,
`expiresDurationMinutes`.  This field allows templates to set a default number
of minutes in the future a given alert should expire.  An example is below

    <alert xmlns = "urn:oasis:names:tc:emergency:cap:1.2">
      <info>
        <expiresDurationMinutes>48</expiresDurationMinutes>
      </info>
    </alert>

Applying this template would cause "48" minutes to appear in the manual
effective expiration field in the CAP creator.

![image alt text](image_4.png)

<a name="area-templates"></a>
### Area templates

Area templates are defined as partially-complete CAP `<area>` blocks.  Like
message templates, they are specified in XML.  Here is an example Area template
for Metro Manila in the Philippines:

    <area>
      <areaDesc>METRO MANILA</areaDesc>
      <geocode>
        <valueName>SAME</valueName>
        <value>130000000</value>
      </geocode>
    </area>

Area templates are most useful when alerts are issued according to predefined
geopolitical boundaries.  Ideally, each alert would have a custom area depending
on the specific threat, but there are numerous situations where that is not
currently possible.

Area templates also support `<polygon>` and `<circle>` elements.

Like Message templates, template placeholders work for area templates, and are
validated by the CAP Creator tool.  Here is an example:

    <area>
      <areaDesc>{{LOCATION NAME}}</areaDesc>
      <geocode>
        <valueName>SAME</valueName>
        <value>{{GEOCODE}}</value>
      </geocode>
    </area>


![image alt text](image_5.png)

<a name="adding-templates-one-at-a-time"></a>
#### Adding templates one at a time

From the administrator home page, select "Message Templates" to view existing
templates and add additional message templates.

![image alt text](image_6.png)

![image alt text](image_7.png)

From the administrator home page, select "Area Templates" to view and add area
templates.

![image alt text](image_8.png)

![image alt text](image_9.png)

<a name="adding-templates-in-bulk"></a>
#### Adding templates in bulk

To add templates in bulk, you need to create a file for each template and run
the [import_templates.py](https://github.com/CAPTools/CAPCollector/blob/master/core/management/commands/import_templates.py)
command to import them.
  1. Each file contains XML contents of template
  2. File name will be used as the template name shown in CAP Creator area
  selection drop down section

One option to generate all the template files for bulk upload is to use the
following steps



 * Create a file (i.e. areatemplates.txt) with the area template name as the
 first field and area template XML as the second with a non-comma separator such
 as pound (#) or semicolon (;)
    * This can be generated simply using spreadsheets
    * Include a line for each entry

            Masbate#<area><areaDesc>Masbate</areaDesc><geocode><valueName>SAME</valueName><value>54100000</value></geocode></area>
            Metro Manila#<area><areaDesc>Metro Manila</areaDesc><geocode><valueName>SAME</valueName><value>130000000</value></geocode></area>
            Philippine Area of Responsibility#<area><areaDesc>Philippine Area of Responsibility</areaDesc><polygon>21,120 21,135 5,135 5,122 10,113 15,113 15,113 21,120</polygon></area>


  * Run the following command which creates a list of files based on the first
  field in each line with file contents taken from the second field in each line

            awk -F[SEPARATOR] '{print $2 > $1; close($1);}' areatemplates.txt

   * If separator is #, then:

            awk -F# '{print $2 > $1; close($1);}' areatemplates.txt

 * Once you have a directory of all the appropriate templates, run the 
 [import_templates.py](https://github.com/CAPTools/CAPCollector/blob/master/core/management/commands/import_templates.py)
 script to upload by passing the directory containing all the files generated above

<a name="hosting-requirements"></a>
## Hosting Requirements

The CAP Creator Server can run on most Linux/UNIX-based operating systems,
any system where you can install Python and accept incoming web traffic.

The server can also run on most cloud service providers, including
[Google AppEngine](https://cloud.google.com/appengine),
[Amazon Web Services](http://aws.amazon.com/), [Heroku](https://www.heroku.com/),
and [Microsoft Azure](https://azure.microsoft.com/). More detailed instructions
follow for deploying to Google AppEngine and Google Compute Engine.

<a name="deploying-to-google-appengine"></a>
#### Deploying to Google AppEngine

The CAP Collector comes preconfigured with an app.yaml file for uploading to
[Google AppEngine](https://cloud.google.com/appengine).  To deploy to AppEngine

1. Install the Google Appengine SDK from the [downloads](https://cloud.google.com/appengine/downloads) page.
2. Register for a new AppEngine App by following the instructions at
"[Register the Application](https://cloud.google.com/appengine/docs/python/gettingstartedpython27/uploading)"
3. Update app.yaml to change the application id to the one that you registered.
4. Upload the application.  From the CAPCollector directory, run


        CAPCollector$ appcfg.py --oauth2 update  .

Note: Due to missing support for lib-xmlsecl on AppEngine, digital signatures
are disabled if you run your app on Google AppEngine.

<a name="deploying-to-google-compute-engine"></a>
## Deploying to Google Compute Engine

Allocate Compute Engine instance using
[https://console.developers.google.com](https://console.developers.google.com)

Install gcloud SDK from [https://cloud.google.com/sdk/](https://cloud.google.com/sdk/)

Log in to your instance and become superuser:

    $ gcloud compute --project "your-project" ssh --zone "instance-zone" "instance-id"
    $ sudo su

Add a new user for your application and install git client:

    # adduser captools --disabled-password
    # apt-get update; apt-get install git
    # cd /home/captools

Checkout CAPTools code from the Github:

    captools# git clone https://github.com/CAPTools/CAPCollector.git
    Cloning into 'CAPCollector'...

    captools# git clone https://github.com/CAPTools/CAPCreator.git
    Cloning into 'CAPCreator'...

Install required packages and apply proper permissions:

    captools# chown -R captools\: .
    captools# cd CAPCollector
    CAPCollector# apt-get install $(grep -vE "^\s*#" packages.txt | tr "\n" " ")
    CAPCollector# apt-get install nginx supervisor

Copy config examples for nginx and supervisor, then edit each file to replace
HOSTNAME with your actual HOSTNAME or IP address:

    CAPCollector# cp example/nginx.example.conf /etc/nginx/sites-enabled/$HOSTNAME.conf
    CAPCollector# cp example/supervisor.example.conf /etc/supervisor/conf.d/$HOSTNAME.conf

Become captools user, setup virtual environment and run setup script:

    CAPCollector$ virtualenv ../venv
    CAPCollector$ source ../venv/bin/activate
    CAPCollector$ bash setup.sh


Modify your settings_prod.py file and install certificate (see section below)

Run nginx and supervisor daemons:

    CAPCollector$ exit
    CAPCollector# /etc/init.d/nginx restart
    CAPCollector# supervisorctl update; supervisorctl start captools

To restart an app

    CAPCollector# supervisorctl restart captools

<a name="installing-a-digital-certificate"></a>
## Installing a digital certificate

CAP messages should be digitally signed for secure transmission over insecure
networks like http.

For testing, you can generate your own digital certificate.

    openssl genrsa -out server_name.key 1024
    openssl req -new -key server_name.key -out server_name.csr
    openssl x509 -req -days 365 -in server_name.csr -signkey server_name.key -out server_name.crt

In production, if you choose to run the CAP Creator at a URL that does not
already have a digital certificate, you should purchase a certificate that has
been signed by a certificate authority.

<a name="appendix"></a>
## Appendix

<a name="tool-limitations"></a>
#### Tool limitations

The CAP Creator tool supports the most common usages of the Common Alerting
Protocol specification, but it does not currently implement the full spec.
Here are known limitations of the tool.  More can be found in the issues list on
github ([CAPCollector issues](https://github.com/CAPTools/CAPCollector/issues)
[CAPCreator issues](https://github.com/CAPTools/CAPCreator/issues))

* Only one language can be used in a single message (however multiple messages
can be authored to address multilingual alerting requirements);
* All alerts are assumed to be effective immediately; the "effective" and
"onset" elements are not supported.
* Alerts are assumed not to contain links to external files; the "resources"
element is not supported
* The "restrictions", “note”, and “incidents” tags are not supported.

<a name="adding-translations"></a>
## Adding translations

Django settings.py contains LANGUAGES variable. To add new language modify this
setting with new language code/language pair. Then run

##### For .py and .tmpl files:
    $ python manage.py makemessages -e py -e tmpl -l hi -l pt_BR -l <your_new_lang_code>

##### For .js files:
    $ python manage.py makemessages -e js -d djangojs -l hi -l pt_BR -s</td>

This command creates new directory `<your_new_lang_code>` in `conf/locale/`. There
will be LC_MESSAGES/django.po and LC_MESSAGES/djangojs.po files. Your need to
translate existing phrases to new language.After it's done you need to run

     $ python manage.py compilemessages

This command creates  `conf/locale/<your_new_lang_code>/LC_MESSAGES/django.mo`.

The default language is controlled by LANGUAGE_CODE variable in settings.py

<a name="generating-code-test-coverage"></a>
## Generating code test coverage

    (venv)CAPCollector$ pip install coverage
    (venv)CAPCollector$ coverage run --source="."  manage.py test; coverage report

or

    (venv)CAPCollector$ coverage html; cd htmlcov; chrome index.html

<a name="troubleshooting"></a>
## Troubleshooting

* Problem: 400 error first time you load the URL for the app.
* Solution: Check CAPCollector/settings_prod.py to make sure `SITE_DOMAIN` matches
the URL you are loading.
