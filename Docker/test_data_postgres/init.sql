-- Create kafka table
CREATE TABLE public.kafka (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT NOT NULL
);

-- Insert data into kafka table
INSERT INTO public.kafka (name, age) VALUES
    ('Bahram', 28),
    ('Nima', 34),
    ('Alireza', 24);

-- Create customer table
CREATE TABLE public.customer (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE public.product (
    ProductID SERIAL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Description TEXT,
    Price DECIMAL(10, 2) NOT NULL,
    StockQuantity INT NOT NULL
);

-- Insert data into customer table
INSERT INTO public.customer (first_name, last_name, email, phone) VALUES
    ('John', 'Doe', 'john.doe@example.com', '555-1234'),
    ('Jane', 'Smith', 'jane.smith@example.com', '555-5678'),
    ('Alice', 'Johnson', 'alice.johnson@example.com', '555-8765'),
    ('Bob', 'Brown', 'bob.brown@example.com', '555-4321');

INSERT INTO public.product (Name, Description, Price, StockQuantity)
VALUES
    ('T-Shirt', 'Cotton short sleeve T-shirt', 15.99, 100),
    ('Jeans', 'Denim blue jeans', 49.99, 50),
    ('Sweater', 'Woolen winter sweater', 35.99, 30),
    ('Jacket', 'Leather jacket', 89.99, 20),
    ('Sneakers', 'Comfortable running sneakers', 59.99, 80),
    ('Dress', 'Summer floral dress', 45.99, 25),
    ('Hat', 'Baseball cap', 12.99, 200),
    ('Scarf', 'Silk scarf', 25.99, 60);
