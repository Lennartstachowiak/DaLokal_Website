CREATE SCHEMA IF NOT EXISTS dalokalschema;

CREATE TABLE IF NOT EXISTS test_table (
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

CREATE TABLE IF NOT EXISTS test_table (
    farm_id INT(11) NOT NULL AUTO_INCREMENT,
    user_id INT(11) NOT NULL,
    farmname VARCHAR(100) NOT NULL,
    farm_img VARCHAR(100) NOT NULL,
    description VARCHAR(1000) NOT NULL,
    total_products INT(11) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (farm_id),
    UNIQUE KEY unique_farm_id (farm_id),
    UNIQUE KEY unique_farmname (farmname)
);

CREATE TABLE IF NOT EXISTS product_table (
    product_id INT(11) NOT NULL,
    farm_id INT(11) NOT NULL,
    category VARCHAR(45) NOT NULL,
    product_name VARCHAR(45) NOT NULL,

)

To do:
- Delete can't work if farm doesn't have details in table so it doesn't find a row.
- Create a error page
- Delete product and delete profile need security
- If running locally create schema and tables if not exists
- Finish the readme