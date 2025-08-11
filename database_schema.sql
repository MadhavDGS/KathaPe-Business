-- SQL script to create pending_payments table for PhonePe payment approval system

CREATE TABLE IF NOT EXISTS pending_payments (
    transaction_id UUID PRIMARY KEY,
    business_id UUID NOT NULL REFERENCES businesses(id),
    customer_id UUID NOT NULL REFERENCES customers(id),
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'PhonePe',
    notes TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL,
    approved_by UUID NULL REFERENCES users(id),
    rejected_at TIMESTAMP NULL,
    rejected_by UUID NULL REFERENCES users(id),
    rejection_reason TEXT NULL,
    metadata JSONB NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_pending_payments_business_id ON pending_payments(business_id);
CREATE INDEX IF NOT EXISTS idx_pending_payments_customer_id ON pending_payments(customer_id);
CREATE INDEX IF NOT EXISTS idx_pending_payments_status ON pending_payments(status);
CREATE INDEX IF NOT EXISTS idx_pending_payments_created_at ON pending_payments(created_at);

-- Add payment_method column to transactions table if it doesn't exist
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50) DEFAULT 'manual';

-- Add approved_at column to transactions table if it doesn't exist  
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP NULL;

-- Add original_pending_id column to transactions table if it doesn't exist
ALTER TABLE transactions 
ADD COLUMN IF NOT EXISTS original_pending_id UUID NULL;

-- Create index on payment_method
CREATE INDEX IF NOT EXISTS idx_transactions_payment_method ON transactions(payment_method);
