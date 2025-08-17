-- Khatape Business Application Database Schema
-- PostgreSQL Database Creation Script
-- This file contains all the necessary tables and indexes for the Khatape Business application

-- Drop existing tables (if you want to recreate from scratch)
-- Uncomment the lines below if you want to drop existing tables
-- WARNING: This will delete all existing data!
/*
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS customer_credits CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS businesses CASCADE;
DROP TABLE IF EXISTS users CASCADE;
*/

-- Create Users Table
-- Stores both business owners and customers
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(255),
    user_type VARCHAR(50) NOT NULL CHECK (user_type IN ('business', 'customer')),
    password VARCHAR(255) NOT NULL,
    profile_photo_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Businesses Table
-- Stores business information linked to business users
CREATE TABLE IF NOT EXISTS businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    business_type VARCHAR(100),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    access_pin VARCHAR(10) NOT NULL,
    qr_code_data TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Customers Table  
-- Stores customer information
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    profile_photo_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Customer Credits Table
-- Links customers to businesses and tracks their credit relationships
CREATE TABLE IF NOT EXISTS customer_credits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    current_balance DECIMAL(12,2) DEFAULT 0.00,
    credit_limit DECIMAL(12,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique relationship between business and customer
    UNIQUE(business_id, customer_id)
);

-- Create Transactions Table
-- Stores all financial transactions between businesses and customers
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('credit', 'payment')),
    notes TEXT,
    media_url TEXT,
    receipt_image_url TEXT,
    transaction_reference VARCHAR(100),
    payment_method VARCHAR(50),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create QR Code Images Table (Optional - for storing QR code images)
CREATE TABLE IF NOT EXISTS qr_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    qr_data TEXT NOT NULL,
    image_data BYTEA,
    image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(business_id)
);

-- Create Sessions Table (Optional - for better session management)
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Activity Logs Table (Optional - for audit trail)
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    business_id UUID REFERENCES businesses(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    description TEXT,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for better performance
-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Business indexes
CREATE INDEX IF NOT EXISTS idx_businesses_user_id ON businesses(user_id);
CREATE INDEX IF NOT EXISTS idx_businesses_access_pin ON businesses(access_pin);
CREATE INDEX IF NOT EXISTS idx_businesses_created_at ON businesses(created_at);

-- Customer indexes
CREATE INDEX IF NOT EXISTS idx_customers_phone_number ON customers(phone_number);
CREATE INDEX IF NOT EXISTS idx_customers_created_at ON customers(created_at);

-- Customer Credits indexes
CREATE INDEX IF NOT EXISTS idx_customer_credits_business_id ON customer_credits(business_id);
CREATE INDEX IF NOT EXISTS idx_customer_credits_customer_id ON customer_credits(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_credits_balance ON customer_credits(current_balance);
CREATE INDEX IF NOT EXISTS idx_customer_credits_created_at ON customer_credits(created_at);

-- Transaction indexes
CREATE INDEX IF NOT EXISTS idx_transactions_business_id ON transactions(business_id);
CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_transactions_business_customer ON transactions(business_id, customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_business_created_at ON transactions(business_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_customer_credits_business_balance ON customer_credits(business_id, current_balance DESC);

-- Session indexes
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);

-- Activity log indexes
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_business_id ON activity_logs(business_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at);

-- Create Functions and Triggers

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers to automatically update updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_businesses_updated_at BEFORE UPDATE ON businesses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customer_credits_updated_at BEFORE UPDATE ON customer_credits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate customer balance
CREATE OR REPLACE FUNCTION calculate_customer_balance(
    p_business_id UUID,
    p_customer_id UUID
) RETURNS DECIMAL AS $$
DECLARE
    credit_total DECIMAL(12,2) := 0;
    payment_total DECIMAL(12,2) := 0;
BEGIN
    -- Calculate total credits (what customer took/owes)
    SELECT COALESCE(SUM(amount), 0) INTO credit_total
    FROM transactions 
    WHERE business_id = p_business_id 
    AND customer_id = p_customer_id 
    AND transaction_type = 'credit';
    
    -- Calculate total payments (what customer paid)
    SELECT COALESCE(SUM(amount), 0) INTO payment_total
    FROM transactions 
    WHERE business_id = p_business_id 
    AND customer_id = p_customer_id 
    AND transaction_type = 'payment';
    
    -- Return net balance (positive means customer owes money)
    RETURN credit_total - payment_total;
END;
$$ LANGUAGE plpgsql;

-- Function to update customer credit balance after transaction
CREATE OR REPLACE FUNCTION update_customer_balance()
RETURNS TRIGGER AS $$
DECLARE
    new_balance DECIMAL(12,2);
BEGIN
    -- Calculate the new balance
    SELECT calculate_customer_balance(NEW.business_id, NEW.customer_id) INTO new_balance;
    
    -- Update the customer_credits table
    UPDATE customer_credits 
    SET current_balance = new_balance,
        updated_at = CURRENT_TIMESTAMP
    WHERE business_id = NEW.business_id 
    AND customer_id = NEW.customer_id;
    
    -- If no record exists in customer_credits, create one
    IF NOT FOUND THEN
        INSERT INTO customer_credits (business_id, customer_id, current_balance)
        VALUES (NEW.business_id, NEW.customer_id, new_balance);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger to automatically update customer balance after transactions
CREATE TRIGGER update_balance_after_transaction 
    AFTER INSERT ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_customer_balance();

-- Create Views for common queries

-- View for customer summary with balance
CREATE OR REPLACE VIEW customer_summary AS
SELECT 
    c.id,
    c.name,
    c.phone_number,
    c.email,
    c.address,
    cc.business_id,
    cc.current_balance,
    cc.created_at as relationship_created_at,
    COUNT(t.id) as total_transactions,
    MAX(t.created_at) as last_transaction_date
FROM customers c
JOIN customer_credits cc ON c.id = cc.customer_id
LEFT JOIN transactions t ON cc.business_id = t.business_id AND cc.customer_id = t.customer_id
GROUP BY c.id, c.name, c.phone_number, c.email, c.address, cc.business_id, cc.current_balance, cc.created_at;

-- View for business summary
CREATE OR REPLACE VIEW business_summary AS
SELECT 
    b.id,
    b.name,
    b.description,
    u.name as owner_name,
    u.phone_number as owner_phone,
    COUNT(DISTINCT cc.customer_id) as total_customers,
    COUNT(t.id) as total_transactions,
    COALESCE(SUM(CASE WHEN t.transaction_type = 'credit' THEN t.amount ELSE 0 END), 0) as total_credit_given,
    COALESCE(SUM(CASE WHEN t.transaction_type = 'payment' THEN t.amount ELSE 0 END), 0) as total_payments_received,
    COALESCE(SUM(cc.current_balance), 0) as total_outstanding
FROM businesses b
JOIN users u ON b.user_id = u.id
LEFT JOIN customer_credits cc ON b.id = cc.business_id
LEFT JOIN transactions t ON b.id = t.business_id
GROUP BY b.id, b.name, b.description, u.name, u.phone_number;

-- Insert some sample data (Optional - for testing)
-- Uncomment if you want sample data for testing

/*
-- Sample business user
INSERT INTO users (id, name, phone_number, user_type, password) VALUES 
('550e8400-e29b-41d4-a716-446655440001', 'John Doe', '9876543210', 'business', 'business123');

-- Sample business
INSERT INTO businesses (id, user_id, name, description, access_pin) VALUES 
('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', 'John''s Store', 'General Store', '1234');

-- Sample customers
INSERT INTO customers (id, name, phone_number) VALUES 
('550e8400-e29b-41d4-a716-446655440003', 'Alice Smith', '9876543211'),
('550e8400-e29b-41d4-a716-446655440004', 'Bob Johnson', '9876543212');

-- Sample customer credit relationships
INSERT INTO customer_credits (business_id, customer_id, current_balance) VALUES 
('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440003', 500.00),
('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440004', 250.00);

-- Sample transactions
INSERT INTO transactions (business_id, customer_id, amount, transaction_type, notes) VALUES 
('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440003', 500.00, 'credit', 'Groceries purchase'),
('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440004', 300.00, 'credit', 'Monthly supplies'),
('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440004', 50.00, 'payment', 'Partial payment');
*/

-- Cleanup old sessions (run this periodically)
-- DELETE FROM sessions WHERE expires_at < CURRENT_TIMESTAMP;

COMMIT;

-- Grant permissions (adjust as needed for your database user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- Database setup complete!
-- You can now connect your Khatape Business application to this database.
