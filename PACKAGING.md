What is required to install lucy.
So that may become some hints to create the package.
This not an "INSTALL" file as I hope we'll never have to install the system 
like this...
And I use virtualenvwrapper here for my sanity, preferably replaced in 
production by installing the debian packages instead of using pip

System : fresh wheezy, up to date on 04 Jul 2013

(root)
* Create a dedicated user in the machine
    adduser --disabled-password --disabled-login --gecos "Lucy manager,,," --home /srv/lucy lucy

(lucy)
* Fetch the repo of lucy
    cd ~ && git clone https://github.com/paultag/lucy.git

(root)
* Install mongoDB
    apt-get install mongodb

(root)
* Enable the interface to query mongo
# TODO : put some auth before mean hackers dominate the DB
SAMPLE conf /etc/mongodb.conf
###############################################################
bind_ip = 0.0.0.0
###############################################################

(root)
* Install some deps :
    apt-get install virtualenvwrapper
    # For gevent
    apt-get install cython
    # For jinja2
    apt-get install python2.7-dev
    # For lucy-process-incoming
    apt-get install inoticoming

(lucy)
* Reconnect as lucy for virtualenvwrapper hooks
    mkvirtualenv lucy && workon lucy

(lucy) virtualenv=lucy
* Install lucy dependancies
    cd ~/lucy
    pip install -r requirements.txt
    pip install python-debian
    pip install chardet

(lucy) virtualenv=lucy
* Install lucy
    python setup.py develop

(lucy) virtualenv=lucy
* Install the config, by creating a file like the sample and run
    lucy-init config.json

SAMPLE conf JSON file :
#FIXME : there is nothing behind the "keyring" stuff :)
###############################################################
{
    "configs": [
        {
            "_id": "default",
            "arches": [
                "amd64"
            ],
            "incoming": "/srv/local-mirror/incoming",
            "job_classes": {
                "binary": [
                    "piuparts",
                    "adequate",
                    "lintian",
                    "lintian4py"
                ],
                "source": [
                    "lintian",
                    "lintian4py"
                ]
            },
            "keyring": "/var/lib/lucy/keyring",
            "pool": "/srv/local-mirror/pool",
            "public": "http://debian-archive.via.ecp.fr/pool",
            "suites": [
                "unstable",
                "testing"
            ]
        }
    ],
    "machines": [
        {
            "_id": "debian-builder1",
            "auth": "password",
            "gpg": "D0FEF8101640900183B8C37A42FE51628224AAA3",
            "owner": "leo"
        }
    ],
    "users": [
        {
            "_id": "leo",
            "email": "leo+debian@cavaille.net",
            "gpg": "B11A9FEC01B2B1F6C1C31DD4896AE222CC16515C",
            "name": "Léo Cavaillé",
            "auth": "secret"
        }
    ]
}
###############################################################

(root)
* Create the paths and give rigts to lucy
    mkdir -p /srv/local-mirror/pool /srv/local-mirror/incoming
    chown -R lucy:lucy /srv/local-mirror

(lucy)
* Configure dput locally so that lucy can dput packages to the local mirror
SAMPLE ~lucy/.dput.cf:
###############################################################
[local]
fqdn = localhost
method = local
incoming = /srv/local-mirror/incoming
###############################################################

(root)
* Setup an HTTP server for the local mirror
    apt-get install nginx
* Edit the conf
SAMPLE /etc/nginx/sites-available/default:
###############################################################
server {
    root /srv/local-mirror/;
    server_name debian-archive;
    location / {
        # First attempt to serve request as file, then
        # as directory, then fall back to displaying a 404.
        try_files $uri $uri/;
    }
}
###############################################################
* Start the daemon
    service nginx start


(lucy) virtualenv=lucy
* Run lucy
    lucyd
    ~/lucy/scripts/lucy-processd
* Start your ethel builders
