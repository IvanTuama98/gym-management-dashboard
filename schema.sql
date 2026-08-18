-- Delete the tables who have Foreign keys
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS users;

-- Creation of the tables
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    monthly_fee NUMERIC DEFAULT 0,
    due_day INTEGER DEFAULT 10,
    late_fee NUMERIC DEFAULT 0
);

CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    registration_date TEXT NOT NULL,
    status TEXT DEFAULT 'Active',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    amount NUMERIC NOT NULL,
    payment_date TEXT NOT NULL,
    month_covered TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);
