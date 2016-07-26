Summary
=======

This README files offers a brief introduction of how to deploy our
application on a server given the source code.


NOTICE::: "yelp_academic_dataset_business.json",
"yelp_academic_dataset_review.json", "yelp_academic_dataset_user.json" from Yelp challenge dataset is not contained in our package, because their size is too large.

How to install the software
===========================

In our test environment, a ubuntu Linux machine is used as the server.
Our application is mainly built on top of Flask web framework. A plenty
of dependent packages are required to install the environment (For instance 
Flask, psycopg2 and etc).

Our database is operated by postgresql, hence a database role "postgres" should
be set and create a database name as "testdb".
Additionally, when we finally move to AWS platform, we saved user avatars inside
our S3 bucket.

Then we need to import the data into databases. Those data files (not included
in the zip file) are "yelp_academic_dataset_business.json",
"yelp_academic_dataset_review.json", "yelp_academic_dataset_user.json". Running
the following scripts to import those files into the database.
Also, these files should be in the same path with python scripts.

```
python import_business_file.py
python import_review_file.py
python import_user_file.py
```

To store the recommendation matrix:
"mkdir /var/lib/postgresql/user_matrix"

To complete setup, we still need to run the following scripts:

```
python matrix_write.py
python rest_setup.py
```
NOTICE: these 5 scripts need to run in this order, since there are 
	foreign key dependencies among the related tables.


How to run the software
=======================

First we need to switch to the database user

```
sudo su - postgres
```

Then under the application folder, type the following script to start

```
nohup python app.py &
```

The nohup is used to keep the program running even if the user logout.
The application will listen to port 5000 in current machine.

How to run a demo
=================

Open a browser, type the IP address of the server with ":5000", you will
see the welcome page of our application. Click sign up / log in to start.


Introduction of all files
==========================
1. demo video is a representative workflow of a match and recommendation process.
2. template and static file include javascript files for webpage design.
3. json files are provided by Yelp challenge dataset.
4. a) app.py is the main function of web application.
   b) app_config.py is for secrete key configuration.
   c) app_util.py is for cookie check function.
   d) call_by_app.py is a container of functions that called by app.py, database query
      or reaction to UI activities are handled in this script.
   e) import_business_file.py, import_review_file.py and import_user_file.py
      are need to run only once after first create the database. They import data from
      Yelp dataset.
   f) matrix_write.py and rest_setup.py are for recommendation matrix initialization 
      need to run only once after import.
   g) append_predict_matrix.py is called by call_by_app.py each time their comes a new
      user; get_recommendation.py is called by call_by_app.py to generate recommendation
      list for accepted matches; is_match.py return whether two post info matches.
5. user avatar files are fetched by using Gravatar.com random avatars and they are moved
   to our S3 bucket. We have made these images public.


Contact
=========
If there’s any problem when you try to implement this application, please contact:
zluo60@gatech.edu
