# DaLokal Website

## Description

DaLokal is a project to connect customer with farms nearby. The user is able to see which farm is selling which goods,what categories, what the farm is about (description), where the farm can be find (adress) and at which time the farm is open.
Every farmer can sign up and can edited his farm every time. The farmer can give a description about his or her farm can give it opening and closing times and can add or delete products and more. 

## Get started

### Online page

Hosted with gcloud
[DaLokal](https://dalokal-website.ey.r.appspot.com/?)

The DB password is locked in a github secret

### For local run

Connect MySQL database with website.
For that if not already install [MySQL Community](https://www.mysql.com/products/community/) and [MySQL Workbench](https://www.mysql.com/products/workbench/) on your pc and create a connection.
After done this go to website.py and use connection for local host and remove all #
for gcloud connection add #
- host='localhost'
- user to your MySQL connection user name (default is root)
- and if used your password after password=''

To get started and run the website on a localhost enter the following three lines in your terminal:

export FLASK_APP=dalokal_website.website.py

export FLASK_DEBUG=1

flask run

If database not setted up automatically use this queries in MySQL Workbench to create the database:
This queries should normally be run in the function on website.py createDatabase() in line 28

## ER Diagram

Every user and every user data is connected to the database of MySQL.
![](images/ERD.png)
* farm_table has a one relationship to user_table
* adress_table has a one relationship to farm_table
* time_table has a zero or many relationship to farm_table
* product_table has a zero or many relationship to farm_table
* category_table has a zero to many relationship to farm_table
product_table has to triggers one for AFTER INSERT and one for AFTER DELETE.