-- ============================================================
--  KhataSystem Database Schema  |  MySQL 8+
--  FIXED VERSION
-- ============================================================
-- IMPORTANT: Do NOT manually insert the admin user from this file.
--            Run seed_admin.py AFTER importing this schema — it
--            generates a proper bcrypt hash automatically.
-- ============================================================

CREATE DATABASE IF NOT EXISTS shop_khata;
USE shop_khata;

CREATE TABLE IF NOT EXISTS users (
    user_id    INT PRIMARY KEY AUTO_INCREMENT,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    role       VARCHAR(20)  DEFAULT 'admin',
    created_at DATETIME     DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name        VARCHAR(100) NOT NULL,
    phone       VARCHAR(20),
    address     TEXT,
    balance     DECIMAL(12,2) DEFAULT 0.00,
    created_at  DATE DEFAULT (CURRENT_DATE)
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name       VARCHAR(150) NOT NULL,
    price      DECIMAL(10,2) NOT NULL,
    stock      INT DEFAULT 0,
    unit       VARCHAR(30)  DEFAULT 'Piece'
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id     INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    product_id  INT NOT NULL,
    qty         INT NOT NULL,
    price       DECIMAL(10,2) NOT NULL,
    total       DECIMAL(12,2) NOT NULL,
    paid        DECIMAL(12,2) DEFAULT 0.00,
    status      ENUM('credit','partial','paid') DEFAULT 'credit',
    sale_date   DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id)  REFERENCES products(product_id)   ON DELETE CASCADE
);

-- Sample data
INSERT INTO customers (name, phone, address, balance) VALUES
    ('Ahmed Khan',     '0300-1234567', 'Main Bazar, Karachi', 4500.00),
    ('Zainab Traders', '0321-9876543', 'Saddar, Karachi',    12000.00),
    ('Raza Brothers',  '0333-5554444', 'Lyari, Karachi',         0.00);

INSERT INTO products (name, price, stock, unit) VALUES
    ('Basmati Rice 5kg', 850.00, 120, 'Bag'),
    ('Cooking Oil 1L',   490.00, 200, 'Bottle'),
    ('Flour 10kg',      1100.00,  80, 'Bag'),
    ('Sugar 1kg',        175.00, 350, 'Kg');

INSERT INTO sales (customer_id, product_id, qty, price, total, paid, status) VALUES
    (1, 1, 2,  850.00, 1700.00,    0, 'credit'),
    (2, 2, 10, 490.00, 4900.00,    0, 'credit'),
    (1, 3, 3, 1100.00, 3300.00,  500, 'partial');
