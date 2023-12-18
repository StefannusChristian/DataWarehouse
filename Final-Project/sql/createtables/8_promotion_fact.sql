CREATE TABLE promotion_fact (
    promotion_id INT PRIMARY KEY,
    date_id INT,
    branch_id INT,
    FOREIGN KEY (date_id) REFERENCES date_dimension(date_id),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);