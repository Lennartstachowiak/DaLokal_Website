CREATE SCHEMA IF NOT EXISTS dalokalschema;
USE dalokalschema;

CREATE TABLE IF NOT EXISTS user_table (
    user_id INT(11) NOT NULL AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(500) NOT NULL,
    firstname VARCHAR(45),
    lastname VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE KEY unique_email (email),
    UNIQUE KEY unique_user_id (user_id)
);

CREATE TABLE IF NOT EXISTS farm_table (
    farm_id INT(11) NOT NULL AUTO_INCREMENT,
    user_id INT(11) NOT NULL,
    farmname VARCHAR(100) NOT NULL,
    farm_img VARCHAR(100) NOT NULL,
    description VARCHAR(1000) NOT NULL,
    total_products INT(11) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (farm_id),
    UNIQUE KEY unique_farm_id (farm_id),
    UNIQUE KEY unique_farmname (farmname),
    CONSTRAINT farmToTable FOREIGN KEY (user_id)
    REFERENCES user_table(user_id)
);

CREATE TABLE IF NOT EXISTS product_table (
    product_id INT(11) NOT NULL AUTO_INCREMENT,
    farm_id INT(11) NOT NULL,
    category VARCHAR(45) NOT NULL,
    product_name VARCHAR(45) NOT NULL,
    product_img VARCHAR(100) NOT NULL,
    product_description VARCHAR(500) NOT NULL,
    product_price DECIMAL (10,2) NOT NULL,
    product_weight DECIMAL (10,3) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id),
    UNIQUE KEY unique_product_id (product_id),
    CONSTRAINT productToFarm FOREIGN KEY (farm_id)
    REFERENCES farm_table(farm_id)
);

CREATE TABLE IF NOT EXISTS time_table (
    farm_id INT(11) NOT NULL,
    day VARCHAR(45),
    opening TIME,
    closing TIME,
    CONSTRAINT timeToFarm FOREIGN KEY (farm_id)
    REFERENCES farm_table(farm_id)
);

CREATE TABLE IF NOT EXISTS category_table (
    farm_id INT(11) NOT NULL,
    veg_check TINYINT(4) NOT NULL DEFAULT '0',
    milk_check TINYINT(4) NOT NULL DEFAULT '0',
    wheat_check TINYINT(4) NOT NULL DEFAULT '0',
    meat_check TINYINT(4) NOT NULL DEFAULT '0',
    CONSTRAINT categoryToFarm FOREIGN KEY (farm_id)
    REFERENCES farm_table(farm_id)
);

CREATE TABLE IF NOT EXISTS adress_table (
    farm_id INT(11) NOT NULL,
    street VARCHAR(100) NOT NULL,
    postalcode INT(11) NOT NULL,
    city VARCHAR(45) NOT NULL,
    CONSTRAINT adressToFarm FOREIGN KEY (farm_id)
    REFERENCES farm_table(farm_id)
);

To do:
- If running locally create schema and tables if not exists
- Finish the readme