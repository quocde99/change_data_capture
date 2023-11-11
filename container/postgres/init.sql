-- create a commerce schema
CREATE SCHEMA commerce;

-- Use commerce schema
SET
    search_path TO commerce;

-- create a table named products
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price REAL NOT NULL
);

-- create a users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    PASSWORD VARCHAR(255) NOT NULL
);

-- create an orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



ALTER TABLE
    products REPLICA IDENTITY FULL;

ALTER TABLE
    users REPLICA IDENTITY FULL;

-- Set REPLICA IDENTITY to FULL for orders table
ALTER TABLE orders REPLICA IDENTITY FULL;



create schema revenue_report;
SET
    search_path TO revenue_report;


CREATE TABLE report(
    date_id varchar(8) primary key,
    revenue real
);