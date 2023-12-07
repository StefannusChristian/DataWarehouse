CREATE TABLE IF NOT EXISTS product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(50),
    price DECIMAL(10, 2),
    cost_price DECIMAL(10, 2)
);