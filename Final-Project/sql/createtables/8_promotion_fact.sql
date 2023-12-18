CREATE TABLE IF NOT EXISTS promotion_fact (
    promotion_fact_id INT PRIMARY KEY,
    promotion_id INT,
    product_id INT,
    date_id INT,
    branch_id INT,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (date_id) REFERENCES date_dimension(date_id),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id),
    FOREIGN KEY (promotion_id) REFERENCES promotion_dimension(promotion_id)
);
