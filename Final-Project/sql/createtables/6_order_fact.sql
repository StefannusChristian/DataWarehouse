CREATE TABLE IF NOT EXISTS order_fact (
    order_id INT PRIMARY KEY,
    date_id INT,
    branch_id INT,
    customer_id INT,
    product_id INT,
    supplier_id INT,
    quantity INT,
    total_amount DECIMAL(10, 2),
    FOREIGN KEY (date_id) REFERENCES date_dimension(date_id),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id)
);