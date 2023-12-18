CREATE TABLE yearly_sales_snapshot (
    snapshot_id INT PRIMARY KEY,
    date_id INT,
    branch_id INT,
    total_sales DECIMAL(10, 2),
    profit DECIMAL(10, 2),
    FOREIGN KEY (date_id) REFERENCES date_dimension(date_id),
    FOREIGN KEY (branch_id) REFERENCES branch(branch_id)
);