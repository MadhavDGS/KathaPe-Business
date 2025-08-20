# Migration from PostgreSQL to Appwrite

This guide helps you migrate your KathaPe Business application from PostgreSQL to Appwrite.

## 🎯 Benefits of Migration

- ✅ **No Network Issues**: Cloud-hosted database eliminates college server network problems
- ✅ **Free with GitHub Student Pack**: No cost for students
- ✅ **Automatic Scaling**: Handles traffic spikes automatically
- ✅ **Built-in Authentication**: Additional security features
- ✅ **Real-time Updates**: Support for real-time data sync
- ✅ **Better Performance**: Optimized for web applications

## 📋 Pre-Migration Steps

### 1. Create Appwrite Account
1. Go to [Appwrite Cloud](https://cloud.appwrite.io/)
2. Sign up with your GitHub account
3. Apply for [GitHub Student Developer Pack](https://education.github.com/pack) if you haven't

### 2. Create Appwrite Project
1. Create a new project in Appwrite console
2. Note down your **Project ID**
3. Go to **Settings** → **API Keys**
4. Create a new API Key with full permissions
5. Note down your **API Key**

### 3. Setup Local Environment
1. Copy `.env.example` to `.env`
2. Fill in your Appwrite credentials:
```env
APPWRITE_PROJECT_ID=your_project_id_here
APPWRITE_API_KEY=your_api_key_here
```

## 🚀 Migration Steps

### Step 1: Setup Appwrite Collections
```bash
python setup_appwrite.py
```

This will create all necessary collections in your Appwrite database.

### Step 2: Export Existing Data (Optional)
If you have existing PostgreSQL data to migrate:

```bash
# Connect to your PostgreSQL database and export data
pg_dump your_database_url > backup.sql

# Create a custom migration script if needed
python migrate_data.py
```

### Step 3: Update Environment Variables in Render

In your Render dashboard, update these environment variables:

```
APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your_project_id
APPWRITE_API_KEY=your_api_key
APPWRITE_DATABASE_ID=kathape_business
SECRET_KEY=fc36290a52f89c1c92655b7d22b198e4
RENDER=true
```

### Step 4: Deploy Updated Application

```bash
git add .
git commit -m "Migrate from PostgreSQL to Appwrite"
git push origin main
```

Render will automatically redeploy your application.

## 🔄 What Changed

### Database Operations
- **Before**: SQL queries with psycopg2
- **After**: Appwrite SDK with document-based operations

### Data Structure
- **Before**: Relational tables with foreign keys
- **After**: Document collections with referenced IDs

### Connection Management
- **Before**: Connection pooling with PostgreSQL
- **After**: HTTP-based API calls to Appwrite

## 📊 Collection Schema

### Users Collection
- `name` (string): User's full name
- `phone_number` (string): User's phone number
- `email` (string): User's email address
- `user_type` (string): 'business' or 'customer'
- `password` (string): Hashed password
- `is_active` (boolean): Account status

### Businesses Collection
- `user_id` (string): Reference to user document
- `name` (string): Business name
- `address` (string): Business address
- `access_pin` (string): Business access PIN
- `qr_code_data` (string): QR code information

### Customers Collection
- `business_id` (string): Reference to business document
- `name` (string): Customer name
- `phone` (string): Customer phone
- `balance` (double): Outstanding balance

### Transactions Collection
- `business_id` (string): Reference to business
- `customer_id` (string): Reference to customer
- `amount` (double): Transaction amount
- `transaction_type` (string): 'credit' or 'debit'
- `description` (string): Transaction description
- `receipt_image_url` (string): Base64 encoded image

## 🛠️ Troubleshooting

### Common Issues

**1. Collection Creation Fails**
- Check your API key permissions
- Ensure project ID is correct

**2. Connection Timeout**
- Check your internet connection
- Verify Appwrite endpoint URL

**3. Data Not Appearing**
- Check collection permissions
- Verify document IDs are correct

**4. Migration from Existing Data**
- Export PostgreSQL data first
- Create custom migration scripts for bulk data transfer

### Getting Help

1. Check Appwrite documentation: https://appwrite.io/docs
2. Join Appwrite Discord community
3. Check GitHub issues in this repository

## 📈 Performance Considerations

- Appwrite has rate limits (check your plan)
- Optimize queries to reduce API calls
- Use pagination for large datasets
- Consider caching for frequently accessed data

## 🔐 Security Notes

- API keys should be kept secret
- Use environment variables for all credentials
- Consider using Appwrite's built-in authentication
- Regularly rotate API keys

## 🎉 Post-Migration Testing

1. Test user registration and login
2. Create test customers and transactions
3. Verify balance calculations
4. Test WhatsApp reminder functionality
5. Check bill image upload/display

Your application should now be running on Appwrite! 🚀
