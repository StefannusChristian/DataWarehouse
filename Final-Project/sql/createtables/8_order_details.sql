CREATE TABLE IF NOT EXISTS order_details (
    order_detail_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    total_amount DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES order_fact(order_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);
