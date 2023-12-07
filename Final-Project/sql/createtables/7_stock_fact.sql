CREATE TABLE IF NOT EXISTS stock_fact (
    stock_id INT PRIMARY KEY,
    date_id INT,
    branch_id INT,
    product_id INT,
    opening_stock INT,
    closing_stock INT,
    quantity_sold INT,
    FOREIGN KEY (date_id) REFERENCES date_dimension(date_id),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);