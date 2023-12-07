CREATE TABLE IF NOT EXISTS date_dimension (
    date_id INT PRIMARY KEY,
    full_date DATE,
    day_of_week VARCHAR(10),
    calendar_month VARCHAR(20),
    calendar_quarter VARCHAR(10),
    calendar_year INT
);
