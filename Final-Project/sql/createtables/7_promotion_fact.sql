CREATE TABLE promotion_fact (
    promotion_id CHAR(36) PRIMARY KEY,
    product_id INT,
    date_id INT,
    branch_id INT,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (date_id) REFERENCES date_dimension(date_id),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);
