CREATE TABLE IF NOT EXISTS promotion_dimension (
    promotion_id INT PRIMARY KEY,
    promotion_name VARCHAR(255),
    start_date DATE,
    end_date DATE,
    description TEXT
);
