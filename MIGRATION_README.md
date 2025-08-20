# KathaPe Business - Database Migration to Appwrite

This application has been migrated from PostgreSQL to Appwrite NoSQL database while maintaining all existing functionality.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Appwrite
1. Create an account at [Appwrite Cloud](https://cloud.appwrite.io) or set up self-hosted Appwrite
2. Create a new project
3. Copy `.env.template` to `.env` and fill in your Appwrite credentials:
   ```bash
   cp .env.template .env
   ```
4. Edit `.env` file with your Appwrite details:
   ```env
   APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
   APPWRITE_PROJECT_ID=your_project_id_here
   APPWRITE_API_KEY=your_api_key_here
   ```

### 3. Setup Database Collections
Run the setup script to create all necessary collections:
```bash
python setup_appwrite_collections.py
```

This will create the following collections:
- `users` - User accounts (business owners and customers)
- `businesses` - Business profiles
- `customers` - Customer information
- `customer_credits` - Customer credit relationships
- `transactions` - All financial transactions

### 4. Run the Application
```bash
python run.py
```

## Migration Details

### What Changed
- **Database**: PostgreSQL → Appwrite NoSQL
- **Dependencies**: Removed `psycopg2-binary`, added `appwrite==11.1.0`
- **Database Operations**: SQL queries replaced with Appwrite document operations
- **Connection Management**: Connection pooling replaced with Appwrite SDK

### What Stayed the Same
- **All functionality**: Complete feature parity maintained
- **User Interface**: No changes to templates or UI
- **Business Logic**: All workflows remain identical
- **File Structure**: Same route handling and organization

### Key Files Modified
- `requirements.txt` - Updated dependencies
- `appwrite_config.py` - New Appwrite configuration
- `appwrite_utils.py` - Database utility functions
- `common_utils.py` - Removed PostgreSQL, added Appwrite
- `app.py` - Database calls migrated to Appwrite
- `db_migration_helper.py` - SQL to NoSQL translation layer

### Database Schema Mapping

| PostgreSQL Table | Appwrite Collection | Notes |
|------------------|-------------------|-------|
| users | users | Direct mapping |
| businesses | businesses | Direct mapping |
| customers | customers | Direct mapping |
| customer_credits | customer_credits | Direct mapping |
| transactions | transactions | Direct mapping |

### Migration Benefits
- **No Network Issues**: Eliminates college network connectivity problems
- **Cloud Native**: Fully cloud-based database solution
- **Scalability**: Better horizontal scaling capabilities
- **Modern Stack**: Updated to modern NoSQL architecture
- **Same Experience**: All user-facing functionality preserved

## Troubleshooting

### Common Issues
1. **Environment Variables**: Ensure all required variables are set in `.env`
2. **API Key Permissions**: Verify API key has appropriate database permissions
3. **Collection Setup**: Run setup script if collections are missing
4. **Import Errors**: Ensure `appwrite==11.1.0` is installed correctly

### Getting Help
If you encounter issues:
1. Check the `.env` file configuration
2. Verify Appwrite project settings
3. Review console output for specific error messages
4. Ensure all dependencies are installed

## Development Notes
- The migration preserves all PostgreSQL functionality using a translation layer
- Complex SQL queries are converted to equivalent Appwrite operations
- UUID generation and management remains consistent
- Session handling and authentication unchanged
