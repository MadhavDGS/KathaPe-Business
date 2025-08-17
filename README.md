# Khatape Business App

A Flask-based business management application for handling customer credits and transactions.

## Features

- ✅ Business registration and authentication
- ✅ Customer management system
- ✅ Credit tracking and transactions
- ✅ QR code generation for business identification
- ✅ Dashboard with analytics
- ✅ Transaction history and reporting

## Deployment on Render

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository**
3. **Configure deployment settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:business_app --bind 0.0.0.0:$PORT`
   - **Environment**: `Python 3`

4. **Set Environment Variables**:
   ```
   RENDER=true
   DATABASE_URL=your_database_connection_string
   EXTERNAL_DATABASE_URL=your_external_database_connection_string
   SECRET_KEY=your_secret_key
   ```

5. **Deploy** and your business app will be live!

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at `http://localhost:5001`

## Database Schema

The app requires these PostgreSQL tables:
- `users` - Business user accounts
- `businesses` - Business profiles  
- `customers` - Customer information
- `customer_credits` - Business-customer credit relationships
- `transactions` - Transaction history

## Tech Stack

- **Backend**: Flask 2.2.3
- **Database**: PostgreSQL (via psycopg2-binary)
- **Deployment**: Render
- **Authentication**: Session-based
- **QR Codes**: qrcode + Pillow
