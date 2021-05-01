# DaLokal Website

## Desription

DaLokal is a project to connect customer with farms nearby. The user is able to see which farm is selling which goods,what categories, what the farm is about (description), where the farm can be find (adress) and at which time the farm is open.
Every farmer can sign up and can edited his farm every time. The farmer can give a description about his or her farm can give it opening and closing times and can add or delete products and more. 

## Get started

To get started and run the website on a localhost with ->

<export FLASK_APP=dalokal_website
export FLASK_DEBUG=1
flask run>

## ER Diagram

Every user and every user data is connected to the database of MySQL.
![](images/ERD.png)
* farm_table has a one relationship to user_table
* adress_table has a one relationship to farm_table
* time_table has a zero or many relationship to farm_table
* product_table has a zero or many relationship to farm_table
* category_table has a zero to many relationship to farm_table
product_table has to triggers one for AFTER INSERT and one for AFTER DELETE.