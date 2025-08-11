# PhonePe Payment Approval System

## Overview

The PhonePe Payment Approval System allows customers to make payments via PhonePe that require business confirmation before being recorded as transactions. This provides an extra layer of verification for digital payments.

## How It Works

### Customer Side (Port 5002)
1. Customer initiates a PhonePe payment
2. Payment details are stored in customer session as `pending_payment_{transaction_id}`
3. Payment data includes: transaction_id, business_id, customer_id, amount, notes, status
4. Customer app periodically checks payment status via `/check_payment_status/<transaction_id>`

### Business Side (Port 5001) 
1. Business views pending payments at `/pending_payments`
2. Business can approve or reject each payment
3. Approved payments create actual transaction records
4. Customer app is notified of status changes

## Implementation Details

### Database Schema

#### pending_payments table
```sql
CREATE TABLE pending_payments (
    transaction_id UUID PRIMARY KEY,
    business_id UUID NOT NULL,
    customer_id UUID NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'PhonePe',
    notes TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL,
    approved_by UUID NULL,
    rejected_at TIMESTAMP NULL,
    rejected_by UUID NULL,
    rejection_reason TEXT NULL,
    metadata JSONB NULL
);
```

#### transactions table additions
- `payment_method` VARCHAR(50) DEFAULT 'manual'
- `approved_at` TIMESTAMP NULL  
- `original_pending_id` UUID NULL

### Business Routes

#### `/pending_payments` (GET)
- Display all payments awaiting business approval
- Shows customer name, amount, payment method, timestamp, notes
- Provides approve/reject buttons for each payment

#### `/approve_payment/<transaction_id>` (POST)
- Creates actual transaction record in database
- Updates customer credit balance
- Sends confirmation to customer app
- Removes from pending payments

#### `/reject_payment/<transaction_id>` (POST)
- Notifies customer of rejection
- Removes from pending payments
- Logs rejection reason

#### `/payment_status_update` (POST)
- Endpoint for receiving status updates from customer app
- Used for cross-app communication

#### `/test_pending_payment` (POST)
- Development endpoint to create mock pending payments
- Useful for testing the approval workflow

### Customer Integration

The customer app should implement:

1. **Payment Creation**: Store payment details in session
2. **Status Checking**: Periodic checks via `/check_payment_status/<transaction_id>`
3. **Status Updates**: Handle approval/rejection notifications
4. **Cleanup**: Remove approved/rejected payments from session

### Cross-App Communication

Communication between customer (port 5002) and business (port 5001) apps:

```python
# Business app notifies customer app
customer_app_url = "http://localhost:5002"
confirmation_data = {
    'transaction_id': transaction_id,
    'status': 'approved',  # or 'rejected'
    'business_id': business_id,
    'customer_id': customer_id,
    'amount': amount,
    'approved_at': timestamp
}
requests.post(f"{customer_app_url}/payment_status_update", json=confirmation_data)
```

## Features

### Business Dashboard Integration
- **Pending Payments Button**: Direct access from dashboard
- **Statistics**: Count and total amount of pending payments
- **Test Payment Button**: Create mock payments for development

### User Interface
- **Responsive Design**: Works on mobile and desktop
- **Confirmation Dialogs**: Prevent accidental approvals/rejections
- **Modal Rejection**: Collect rejection reasons
- **Real-time Updates**: Status changes reflected immediately

### Security & Validation
- **User Authentication**: Login required for all operations
- **Business Validation**: Users can only access their business data
- **Transaction Integrity**: Atomic operations for approvals
- **Error Handling**: Comprehensive error management

## Testing

### Manual Testing
1. Use the "Test Payment" button on dashboard to create mock payments
2. Navigate to "Pending Payments" to view them
3. Test approve/reject workflows
4. Verify transaction creation and balance updates

### Development Endpoints
- `/test_pending_payment` - Creates test payments
- `/pending_payments` - View pending payments dashboard

## Future Enhancements

1. **Bulk Operations**: Approve/reject multiple payments at once
2. **Payment Limits**: Set auto-approval thresholds
3. **Notifications**: Email/SMS notifications for payment status
4. **Audit Trail**: Detailed logging of all payment actions
5. **API Integration**: Direct PhonePe webhook integration
6. **Mobile App**: Dedicated mobile app for payment management

## Error Handling

The system handles various error scenarios:
- Database connection failures
- Invalid payment data
- Network communication errors
- User permission issues
- Concurrent modification conflicts

All errors are logged and user-friendly messages are displayed.

## Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `CUSTOMER_APP_URL`: Customer app URL for notifications (default: http://localhost:5002)
- `BUSINESS_APP_URL`: Business app URL (default: http://localhost:5001)

### Database Initialization
The system automatically creates required tables and indexes on startup.

## Deployment Notes

### Render.com Deployment
- Database schema is automatically initialized
- Cross-app communication URLs need to be updated for production
- Ensure both apps have access to the same PostgreSQL database

### Local Development
- Customer app on port 5002
- Business app on port 5001  
- Shared PostgreSQL database required
