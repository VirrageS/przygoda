# Przygoda | [![Code Health](https://landscape.io/github/VirrageS/przygoda/master/landscape.svg?style=flat&badge_auth_token=2d1ada759c4f46399a06205375c04926)](https://landscape.io/github/VirrageS/przygoda/master) | [![Circle CI](https://circleci.com/gh/VirrageS/przygoda.svg?style=shield&&circle-token=bbdd9a0c1379c15241b877d9678c64538730b6d5)](https://circleci.com/gh/VirrageS/przygoda) | [![Build Status](https://magnum.travis-ci.com/VirrageS/przygoda.svg?token=cnzFxz77oBFevu6Vrpep&branch=master)](https://magnum.travis-ci.com/VirrageS/przygoda)
Aplikacja Przygoda jest najlepszym sposobem na znajdowanie miłośników rowerów

# Instalacja

## Clone GitHub project

Our first move is to clone GitHub project into our computer.

	MacBook-Air-Janusz:Desktop VirrageS$ sudo apt-get install git
	MacBook-Air-Janusz:Desktop VirrageS$ git clone https://github.com/VirrageS/przygoda
	MacBook-Air-Janusz:Desktop VirrageS$ cd przygoda

## Virtual Environment initialization

Now we have to install virtual env and get all python packages we need.
So lets get python packages first:

	MacBook-Air-Janusz:przygoda VirrageS$ sudo apt-get update
	MacBook-Air-Janusz:przygoda VirrageS$ sudo apt-get install python3-pip python3-dev
	MacBook-Air-Janusz:przygoda VirrageS$ sudo apt-get build-dep python3-psycopg2

Now we need to install virtual env:

	MacBook-Air-Janusz:przygoda VirrageS$ sudo pip3 install virtualenv

Lets

	MacBook-Air-Janusz:przygoda VirrageS$ virtualenv env

Now we have to start our virtual env (if ever would want to leave virtual env just type `deactivate`):

	MacBook-Air-Janusz:przygoda VirrageS$ source env/bin/activate

We should get something like this:

	(env)MacBook-Air-Janusz:przygoda VirrageS$

And finally install requirements which we need to make our app running.
This code will install all dependencies which our app is using. You can open `requirements.txt` to see what they are.

	(env)MacBook-Air-Janusz:przygoda VirrageS$ pip3 install -r requirements.txt

## Database

Now we have to create simply database which will handle our queries.
To make one, type:

	(env)MacBook-Air-Janusz:przygoda VirrageS$ python3 shell.py
	>>> db.create_all()
	>>> exit()

**IMPORTANT**: you have to be in virtual environment

Unfortunetly if we use sqlite database we need delete our database and
create fresh one every time we code new model or add something to existing one.

## Run app

Now we can run our app by just typing `python3 run.py`.

	(env)MacBook-Air-Janusz:przygoda VirrageS$ python3 run.py
	 * Running on http://127.0.0.1:5000/
	 * Restarting with reloader

**IMPORTANT**: you have to be in virtual environment

Hurray! Our app is alive. Open [http://127.0.0.1:5000] in your browser and that's it!

## Testing

To run unit tests type:

	MacBook-Air-Janusz:przygoda VirrageS$ python3 -m unittest discover

# Virtual Server

Now I will show you how to setup running app on your custom virtual server.
This tutorial I have been using to setup my first server on [Digital Ocean](digitalocean.com)
I used `Ubuntu 14.04`

## SSH

So our first step after starting our server is to set SSH between virtual server and our local machine.
So on local machine type:

	local$ ssh root@SERVER_IP_ADDRESS

It should ask us for current user and current password (you should get it in email) and then
it will us to change this password. After we do that lets go deeper.

## New custom user

Now it is time to create our own user. To do it type on virtual server command.

	adduser USER

`USER` is your custom **username**.

Now we must add all privileges to our new user. To make it happen type:

	gpasswd -a USER sudo

## SSH next part

On our local machine we must create new SSH key to make it easy to communicate with our virtual server. Type:

	local$ ssh-keygen

After it will ask us to provide some info but better is to leave it default
so we just click enter until we do not have to :)

Now we have to copy SSH key to our virtual server. Type:

	local$ ssh-copy-id USER@SERVER_IP_ADDRESS


## Security

To make our server a little bit secure we must deactivate root user.
Type

	sudo nano /etc/ssh/sshd_config

and change line

	PermitRootLogin yes

to

	PermitRootLogin no

Now click `CTRL + X` then `YES` and click enter. That is it we deactivated root user.

## SSH Testing

Now lets restart our SSH

	local$ service ssh restart

Make new tab (or new window) in terminal and type:

	local$ ssh USER@SERVER_IP_ADDRESS

Now we should been redirected to our virtual server. Hurray! :)

## All in one

This part is for people who understand what is going on and wants to make it fast to set up server.
Scroll if you want to dive into details.

	sudo apt-get update; sudo apt-get build-dep python3-psycopg2; sudo apt-get install python3-pip python3-dev nginx git; sudo pip3 install virtualenv; s cd przygoda; virtualenv env; source env/bin/activate; pip3 install psycopg2; pip3 install -r requirements.txt; deactivate; sudo nano /etc/init/przygoda.conf;

```
description "Gunicorn application server running PROJECT_NAME"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid USER
setgid www-data

env PATH=/home/USER/PROJECT_NAME/env/bin
chdir /home/USER/PROJECT_NAME
exec gunicorn --workers 3 --bind unix:PROJECT_NAME.sock -m 007 run:app
```

	sudo start przygoda; sudo rm -rf /etc/nginx/sites-enabled/default; sudo rm -rf /etc/nginx/sites-available/default; sudo nano /etc/nginx/sites-available/przygoda

```
server {
    listen 80;
    server_name ;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/przygoda/przygoda.sock;
        proxy_connect_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

	sudo ln -s /etc/nginx/sites-available/przygoda /etc/nginx/sites-enabled; sudo nginx -t; sudo service nginx restart


## Application

To make our app working on our virtual server lets install some packages.

	sudo apt-get update
	sudo apt-get build-dep python3-psycopg2
	sudo apt-get install python3-pip python3-dev nginx git
	sudo pip3 install virtualenv

Now lets clone our project:

	git clone https://github.com/VirrageS/przygoda
	cd ~/przygoda

Setup virtual env and activate it

	virtualenv env
	source env/bin/activate

Install all packages

	pip3 install psycopg2
	pip3 install -r requirements.txt

Deactivate virtual env because for the next part we will not need it

	deactivate

## Gunicorn

Now we have to create script that will run our server. First step is to type:

	sudo nano /etc/init/przygoda.conf

and put this code:

```
description "Gunicorn application server running PROJECT_NAME"

start on runlevel [2345]
stop on runlevel [!2345]

respawn
setuid USER
setgid www-data

env PATH=/home/USER/PROJECT_NAME/env/bin
chdir /home/USER/PROJECT_NAME
exec gunicorn --workers 3 --bind unix:PROJECT_NAME.sock -m 007 run:app
```

Before saving. Change **USER** and **PROJECT_NAME** to our current user and project name for example `przygoda`.
Now lets test our script and set it running.

	sudo start przygoda

## NGINX

First step is to remove default sites because we will not need them. Type:

	sudo rm -rf /etc/nginx/sites-enabled/default
	sudo rm -rf /etc/nginx/sites-available/default

Create new site by:

	sudo nano /etc/nginx/sites-available/PROJECT_NAME

and put code like this:

```
server {
    listen 80;
    server_name SERVER_IP_ADDRESS;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/USER/PROJECT_NAME/PROJECT_NAME.sock;
        proxy_connect_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

Now we have to connect our site to enabled sites. Type:

	sudo ln -s /etc/nginx/sites-available/PROJECT_NAME /etc/nginx/sites-enabled

Check if our nginx configuration is properly set:

	sudo nginx -t

And start nginx:

	sudo service nginx restart

Now, if we type SERVER_IP_ADDRESS into our browser we should see our app up and running :)!

## Stress tests

To check if our site is able to handle a lot of traffic we can preform stress tests:

	ab -k -r -n 50000 -c 500 http://..../

Parameter | Desc | Value
--- | --- | ---
-n | Set how much packets will be send to our server | 50000
-c | Simulate simultaneous user connections (most important parameter) | 500

# Amazon AWS

## Init EC2 instance

Initing EC2 is quite simple but good practice is to set init code into our instance.

	#!/bin/bash
	apt-get -y update
	apt-get -y install awscli
	apt-get -y install ruby2.0
	cd /home/ubuntu
	aws s3 cp s3://aws-codedeploy-eu-west-1/latest/install . --region eu-west-1
	chmod +x ./install
	./install auto

## Instance Role

Inline Policies:

	{
	    "Statement": [
	        {
	            "Resource": "*",
	            "Action": [
	                "autoscaling:Describe*",
	                "cloudformation:Describe*",
	                "cloudformation:GetTemplate",
	                "s3:Get*",
	                "s3:List*"
	            ],
	            "Effect": "Allow"
	        }
	    ]
	}

Trust relationships:

	{
	  "Version": "2012-10-17",
	  "Statement": [
	    {
	      "Sid": "",
	      "Effect": "Allow",
	      "Principal": {
	        "Service": "ec2.amazonaws.com"
	      },
	      "Action": "sts:AssumeRole"
	    }
	  ]
	}

## CodeDeploy Role

Inline Policies:

	{
	    "Version": "2012-10-17",
	    "Statement": [
	        {
	            "Action": [
	                "autoscaling:PutLifecycleHook",
	                "autoscaling:DeleteLifecycleHook",
	                "autoscaling:RecordLifecycleActionHeartbeat",
	                "autoscaling:CompleteLifecycleAction",
	                "autoscaling:DescribeAutoscalingGroups",
	                "autoscaling:PutInstanceInStandby",
	                "autoscaling:PutInstanceInService",
	                "ec2:Describe*"
	            ],
	            "Effect": "Allow",
	            "Resource": "*"
	        }
	    ]
	}

Trust relationships:

	{
	  "Version": "2008-10-17",
	  "Statement": [
	    {
	      "Sid": "1",
	      "Effect": "Allow",
	      "Principal": {
	        "Service": "codedeploy.amazonaws.com"
	      },
	      "Action": "sts:AssumeRole"
	    }
	  ]
	}
