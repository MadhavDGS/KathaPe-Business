# Performance Optimization Configuration

# Database query limits to prevent timeouts
MAX_TRANSACTIONS_PER_PAGE = 25  # Reduced from 50
MAX_CUSTOMERS_DASHBOARD = 5     # Dashboard customers
MAX_CUSTOMERS_PAGE = 100        # Customers page limit  
MAX_TRANSACTIONS_DASHBOARD = 10 # Dashboard transactions

# Caching configuration
CACHE_TTL_SECONDS = 60         # 1 minute cache
ENABLE_REQUEST_CACHING = True  # Enable per-request caching

# Connection optimization
CONNECTION_TIMEOUT = 10        # 10 second timeout
REQUEST_TIMEOUT = 15          # 15 second request timeout

# Pagination settings
DEFAULT_PAGE_SIZE = 25        # Smaller page sizes for better performance
MAX_PAGE_SIZE = 50           # Maximum allowed page size
