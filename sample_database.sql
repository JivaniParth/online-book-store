USE bookstore;

-- Drop existing tables in reverse order of dependencies
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS book_order;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS book_details;
DROP TABLE IF EXISTS author;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS publisher;
DROP TABLE IF EXISTS user;

-- User entity
CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    user_type ENUM('customer', 'admin') NOT NULL DEFAULT 'customer',
    address TEXT,
    city VARCHAR(100),
    registration_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_user_type (user_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Publisher entity
CREATE TABLE publisher (
    publisher_name VARCHAR(255) PRIMARY KEY,
    address TEXT,
    city VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(255),
    established_date DATE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Category entity
CREATE TABLE category (
    category_name VARCHAR(255) PRIMARY KEY,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Author entity
CREATE TABLE author (
    author_name VARCHAR(255) PRIMARY KEY,
    biography TEXT,
    nationality VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Book entity (with proper cascading)
CREATE TABLE book_details (
    isbn VARCHAR(13) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_name VARCHAR(255) NOT NULL,
    publisher_name VARCHAR(255) NOT NULL,
    category_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    publication_date DATE,
    pages INT,
    stock_quantity INT NOT NULL DEFAULT 0,
    description TEXT,
    image VARCHAR(255),
    INDEX idx_title (title),
    INDEX idx_author (author_name),
    INDEX idx_category (category_name),
    INDEX idx_publisher (publisher_name),
    FOREIGN KEY (author_name) REFERENCES author(author_name) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (publisher_name) REFERENCES publisher(publisher_name) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (category_name) REFERENCES category(category_name) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cart entity (with CASCADE delete when user is deleted)
CREATE TABLE cart (
    cart_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    book_id VARCHAR(13) NOT NULL,
    quantity INT NOT NULL DEFAULT 1 CHECK (quantity > 0),
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_cart (user_id),
    INDEX idx_book_cart (book_id),
    UNIQUE KEY unique_user_book (user_id, book_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_details(isbn) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Order entity (with CASCADE delete when user is deleted)
CREATE TABLE book_order (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    shipping_address TEXT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    INDEX idx_user_order (user_id),
    INDEX idx_order_date (order_date),
    INDEX idx_payment_status (payment_status),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Order_Item entity (with CASCADE delete when order is deleted)
CREATE TABLE order_item (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    book_id VARCHAR(13) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    INDEX idx_order_items (order_id),
    INDEX idx_book_items (book_id),
    FOREIGN KEY (order_id) REFERENCES book_order(order_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_details(isbn) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Review entity (with CASCADE delete when user is deleted)
CREATE TABLE review (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    book_id VARCHAR(13) NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_review (user_id),
    INDEX idx_book_review (book_id),
    UNIQUE KEY unique_user_book_review (user_id, book_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES book_details(isbn) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO category (category_name, description) VALUES
('Classics', 'Timeless literary works that have stood the test of time'),
('Science Fiction', 'Futuristic and sci-fi novels exploring technology and space'),
('Fantasy', 'Magic, dragons, and fantasy adventures in imaginary worlds'),
('Romance', 'Love stories and romantic novels for the heart'),
('Thriller', 'Suspenseful and thrilling stories that keep you on edge'),
('Dystopian', 'Dystopian and post-apocalyptic fiction'),
('Mystery', 'Crime, detective, and mystery novels'),
('Biography', 'Life stories of notable people'),
('Self Help', 'Books for personal development and improvement'),
('History', 'Historical events and periods');

INSERT INTO author (author_name, biography, nationality) VALUES
('F. Scott Fitzgerald', 'American novelist known for The Great Gatsby', 'American'),
('Harper Lee', 'American novelist best known for To Kill a Mockingbird', 'American'),
('George Orwell', 'English novelist, essayist, and critic', 'British'),
('Frank Herbert', 'American science fiction author', 'American'),
('J.R.R. Tolkien', 'English writer and philologist', 'British'),
('Jane Austen', 'English novelist known for romantic fiction', 'British'),
('Gillian Flynn', 'American author known for psychological thrillers', 'American'),
('Stieg Larsson', 'Swedish journalist and writer', 'Swedish'),
('Agatha Christie', 'English writer known for detective novels', 'British'),
('Stephen King', 'American author of horror and supernatural fiction', 'American');

INSERT INTO publisher (publisher_name, address, city, phone, email, established_date) VALUES
('Penguin Books', '80 Strand, London', 'London', '+44-20-7139-3000', 'info@penguin.co.uk', '1935-07-01'),
('HarperCollins', '195 Broadway', 'New York', '+1-212-207-7000', 'info@harpercollins.com', '1989-01-01'),
('Random House', '1745 Broadway', 'New York', '+1-212-782-9000', 'info@randomhouse.com', '1927-01-01'),
('Simon & Schuster', '1230 Avenue of the Americas', 'New York', '+1-212-698-7000', 'info@simonandschuster.com', '1924-01-01'),
('Macmillan Publishers', 'The Macmillan Building', 'London', '+44-20-7833-4000', 'info@macmillan.com', '1843-01-01');

INSERT INTO book_details (isbn, title, author_name, publisher_name, category_name, price, publication_date, pages, stock_quantity, description, image) VALUES
('9780743273565', 'The Great Gatsby', 'F. Scott Fitzgerald', 'Penguin Books', 'Classics', 12.99, '1925-04-10', 180, 50, 'A classic American novel set in the Jazz Age, exploring themes of wealth, love, and the American Dream.', 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&h=400&fit=crop'),
('9780061120084', 'To Kill a Mockingbird', 'Harper Lee', 'HarperCollins', 'Classics', 13.99, '1960-07-11', 324, 45, 'A gripping tale of racial injustice and childhood innocence in the American South.', 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=400&fit=crop'),
('9780451524935', '1984', 'George Orwell', 'Penguin Books', 'Dystopian', 13.99, '1949-06-08', 328, 60, 'A dystopian masterpiece about totalitarianism, surveillance, and the power of language.', 'https://images.unsplash.com/photo-1495640452828-3df6795cf69b?w=300&h=400&fit=crop'),
('9780441013593', 'Dune', 'Frank Herbert', 'Penguin Books', 'Science Fiction', 16.99, '1965-08-01', 688, 40, 'Epic science fiction saga set on the desert planet Arrakis, featuring politics, religion, and ecology.', 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=300&h=400&fit=crop'),
('9780547928227', 'The Hobbit', 'J.R.R. Tolkien', 'HarperCollins', 'Fantasy', 14.99, '1937-09-21', 310, 55, 'An unexpected journey to the Lonely Mountain with Bilbo Baggins and thirteen dwarves.', 'https://images.unsplash.com/photo-1621351183012-e2f9972dd9bf?w=300&h=400&fit=crop'),
('9780141439518', 'Pride and Prejudice', 'Jane Austen', 'Penguin Books', 'Romance', 10.99, '1813-01-28', 432, 48, 'A timeless romance and social commentary about Elizabeth Bennet and Mr. Darcy.', 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=300&h=400&fit=crop'),
('9780307588364', 'Gone Girl', 'Gillian Flynn', 'Random House', 'Thriller', 15.99, '2012-06-05', 432, 35, 'A psychological thriller about a marriage gone wrong, full of twists and unreliable narrators.', 'https://images.unsplash.com/photo-1589998059171-988d887df646?w=300&h=400&fit=crop'),
('9780307949486', 'The Girl with the Dragon Tattoo', 'Stieg Larsson', 'Random House', 'Mystery', 16.99, '2005-08-01', 465, 30, 'A gripping mystery thriller featuring journalist Mikael Blomkvist and hacker Lisbeth Salander.', 'https://images.unsplash.com/photo-1589998059171-988d887df646?w=300&h=400&fit=crop'),
('9780062073501', 'And Then There Were None', 'Agatha Christie', 'HarperCollins', 'Mystery', 11.99, '1939-11-06', 272, 42, 'Ten strangers are invited to an island, where they are killed off one by one.', 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=300&h=400&fit=crop'),
('9781501142970', 'The Shining', 'Stephen King', 'Simon & Schuster', 'Thriller', 14.99, '1977-01-28', 447, 38, 'A family heads to an isolated hotel for the winter where a sinister presence influences the father.', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop');

-- Insert Users (password for all users: password123)
INSERT INTO user (name, email, phone, password, user_type, address, city, registration_date) VALUES
('Parth Jivani', 'parth@bookhaven.com', '+1-555-0100', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5V7LMxM1VDR.a', 'admin', '123 Admin Street', 'New York', '2024-01-15 10:00:00'),
('Nirjari Sheth', 'nirjari@bookhaven.com', '+1-555-0200', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5V7LMxM1VDR.a', 'admin', '123 Admin Street', 'New York', '2024-01-15 10:00:00'),
('John Doe', 'john.doe@example.com', '+1-555-0101', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5V7LMxM1VDR.a', 'customer', '456 Customer Ave', 'Los Angeles', '2024-02-20 14:30:00'),
('Jane Smith', 'jane.smith@example.com', '+1-555-0102', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5V7LMxM1VDR.a', 'customer', '789 Reader Blvd', 'Chicago', '2024-03-10 09:15:00'),
('Bob Wilson', 'bob.wilson@example.com', '+1-555-0103', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5V7LMxM1VDR.a', 'customer', '321 Book Lane', 'Houston', '2024-03-25 16:45:00'),
('Alice Johnson', 'alice.j@example.com', '+1-555-0104', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5V7LMxM1VDR.a', 'customer', '654 Library St', 'Phoenix', '2024-04-05 11:20:00');

INSERT INTO cart (user_id, book_id, quantity, date_added) VALUES
(2, '9780743273565', 1, '2024-10-01 10:00:00'),
(2, '9780451524935', 2, '2024-10-02 14:30:00'),
(3, '9780547928227', 1, '2024-10-03 09:15:00');

INSERT INTO book_order (user_id, customer_name, customer_email, phone, payment_method, shipping_address, total_amount, order_date, payment_status) VALUES
(2, 'John Doe', 'john.doe@example.com', '+1-555-0101', 'cod', '456 Customer Ave, Los Angeles, CA 90001', 29.97, '2024-09-15 10:30:00', 'completed'),
(3, 'Jane Smith', 'jane.smith@example.com', '+1-555-0102', 'online', '789 Reader Blvd, Chicago, IL 60601', 43.96, '2024-09-20 14:15:00', 'completed'),
(4, 'Bob Wilson', 'bob.wilson@example.com', '+1-555-0103', 'cod', '321 Book Lane, Houston, TX 77001', 16.49, '2024-09-25 16:45:00', 'pending');

INSERT INTO order_item (order_id, book_id, quantity, unit_price) VALUES
(1, '9780743273565', 1, 12.99),
(1, '9780061120084', 1, 13.99);

INSERT INTO order_item (order_id, book_id, quantity, unit_price) VALUES
(2, '9780451524935', 2, 13.99),
(2, '9780547928227', 1, 14.99);

INSERT INTO order_item (order_id, book_id, quantity, unit_price) VALUES
(3, '9780141439518', 1, 10.99),
(3, '9780062073501', 1, 11.99);

INSERT INTO review (user_id, book_id, rating, review_text, review_date) VALUES
(2, '9780743273565', 5, 'An absolute masterpiece! Fitzgerald\'s prose is beautiful and the story is timeless.', '2024-09-16 10:00:00'),
(2, '9780061120084', 5, 'A must-read classic. Harper Lee tackles important themes with grace and power.', '2024-09-16 10:30:00'),
(3, '9780451524935', 5, 'Terrifyingly relevant even today. Orwell\'s vision is both dystopian and prophetic.', '2024-09-21 15:00:00'),
(3, '9780547928227', 5, 'A delightful adventure that started it all. Perfect for all ages.', '2024-09-21 15:30:00'),
(4, '9780141439518', 4, 'Witty, romantic, and thoroughly entertaining. Austen at her best.', '2024-09-26 09:00:00'),
(4, '9780062073501', 5, 'Christie is the queen of mystery. This book keeps you guessing until the very end.', '2024-09-26 09:30:00');

-- Verify Data
SELECT 'Categories:' AS Table_Name, COUNT(*) AS Count FROM category
UNION ALL
SELECT 'Authors:', COUNT(*) FROM author
UNION ALL
SELECT 'Publishers:', COUNT(*) FROM publisher
UNION ALL
SELECT 'Books:', COUNT(*) FROM book_details
UNION ALL
SELECT 'Users:', COUNT(*) FROM user
UNION ALL
SELECT 'Cart Items:', COUNT(*) FROM cart
UNION ALL
SELECT 'Orders:', COUNT(*) FROM book_order
UNION ALL
SELECT 'Order Items:', COUNT(*) FROM order_item
UNION ALL
SELECT 'Reviews:', COUNT(*) FROM review;

-- Verify table creation
SELECT 'Database schema created successfully!' AS status;

COMMIT;