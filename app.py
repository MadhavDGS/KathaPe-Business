"""
Business Flask Application - Handles all business-related operations
"""
from common_utils import *

# Create the business Flask app
business_app = create_app('KathaPe-Business')

# Initialize pending payments schema on startup
try:
    init_pending_payments_schema()
    logger.info("Database schema initialized for pending payments")
except Exception as e:
    logger.warning(f"Could not initialize pending payments schema: {str(e)}")

@business_app.template_filter('datetime')
def datetime_filter(value, format='%d %b %Y, %I:%M %p'):
    return format_datetime(value, format)

@business_app.template_filter('currency')
def currency_filter(value):
    """Format a number as currency with proper decimal places"""
    if value is None:
        return "₹0.00"
    try:
        # Convert to float and format with 2 decimal places
        amount = float(value)
        return f"₹{amount:,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"

# Business routes
@business_app.route('/')
def index():
    try:
        logger.info("Business app index route accessed")
        
        # If user is logged in as business, redirect to dashboard
        if 'user_id' in session and session.get('user_type') == 'business':
            return redirect(url_for('business_dashboard'))
        
        # Otherwise redirect to login
        return redirect(url_for('login'))
    except Exception as e:
        logger.error(f"Error in business index route: {str(e)}")
        return redirect(url_for('login'))

@business_app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            print(f"DEBUG: Business login attempt")
            logger.info("Business user attempting to login")
            phone = request.form.get('phone')
            password = request.form.get('password')
            
            if not phone or not password:
                flash('Please enter both phone number and password', 'error')
                return render_template('login.html')
            
            # Emergency login disabled for security - all logins must authenticate with database
            # Do NOT set session data before authentication!
            
            # Try database authentication
            try:
                logger.info("Testing database connection for business login")
                conn = psycopg2.connect(EXTERNAL_DATABASE_URL, connect_timeout=5)
                
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                    # Query business user
                    cursor.execute("SELECT id, name, password FROM users WHERE phone_number = %s AND user_type = 'business' LIMIT 1", [phone])
                    user_data = cursor.fetchone()
                    
                    if user_data and user_data['password'] == password:
                        # ONLY set session after successful password verification
                        user_id = user_data['id']
                        user_name = user_data.get('name', f"Business {phone[-4:]}" if phone and len(phone) > 4 else "Business User")
                        
                        session['user_id'] = user_id
                        session['user_name'] = user_name
                        session['user_type'] = 'business'
                        session['phone_number'] = phone
                        session.permanent = True
                        
                        # Get business details
                        cursor.execute("SELECT id, name, access_pin FROM businesses WHERE user_id = %s LIMIT 1", [user_id])
                        business_data = cursor.fetchone()
                        
                        if business_data:
                            session['business_id'] = business_data['id']
                            session['business_name'] = business_data['name']
                            session['access_pin'] = business_data['access_pin']
                        else:
                            # Create business record if it doesn't exist
                            business_id = str(uuid.uuid4())
                            access_pin = get_unique_business_pin()  # Use permanent PIN instead of timestamp
                            cursor.execute("""
                                INSERT INTO businesses (id, user_id, name, access_pin, created_at)
                                VALUES (%s, %s, %s, %s, %s)
                            """, [business_id, user_id, f"{session['user_name']}'s Business", access_pin, datetime.now().isoformat()])
                            conn.commit()
                            session['business_id'] = business_id
                            session['business_name'] = f"{session['user_name']}'s Business"
                            session['access_pin'] = access_pin
                        
                        conn.close()
                        flash('Successfully logged in!', 'success')
                        return redirect(url_for('business_dashboard'))
                    else:
                        conn.close()
                        flash('Invalid phone number or password', 'error')
                        return render_template('login.html')
                
            except Exception as e:
                logger.error(f"Database error in business login: {str(e)}")
                # Don't allow fallback login - database authentication required
                flash('Login service temporarily unavailable. Please try again.', 'error')
                return render_template('login.html')
        
        # GET request
        return render_template('login.html')
        
    except Exception as e:
        logger.critical(f"Critical error in business login: {str(e)}")
        # Don't allow emergency fallback - require proper authentication
        flash('Login error. Please try again.', 'error')
        return render_template('login.html')

@business_app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        phone = request.form.get('phone')
        password = request.form.get('password')
        name = request.form.get('name', f"Business {phone[-4:]}")
        
        if not phone or not password:
            flash('Please enter both phone number and password', 'error')
            return render_template('register.html')
        
        try:
            # Check if phone number already exists
            check_query = "SELECT id FROM users WHERE phone_number = %s"
            existing_user = execute_query(check_query, [phone], fetch_one=True)
            
            if existing_user:
                flash('Phone number already registered', 'error')
                return render_template('register.html')
            
            # Create user and business records
            user_id = str(uuid.uuid4())
            business_id = str(uuid.uuid4())
            access_pin = get_unique_business_pin()  # Use permanent PIN instead of timestamp
            
            # Create user record
            user_query = """
                INSERT INTO users (id, name, phone_number, user_type, password, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            user_result = execute_query(user_query, [user_id, name, phone, 'business', password, datetime.now().isoformat()], fetch_one=True)
            
            if user_result:
                # Create business record
                business_query = """
                    INSERT INTO businesses (id, user_id, name, description, access_pin, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                execute_query(business_query, [business_id, user_id, f"{name}'s Business", 'My business account', access_pin, datetime.now().isoformat()])
                
                # Auto-login: Set session data (same as login function)
                session['user_id'] = user_id
                session['user_name'] = name
                session['user_type'] = 'business'
                session['phone_number'] = phone
                session['business_id'] = business_id
                session['business_name'] = f"{name}'s Business"
                session['access_pin'] = access_pin
                session.permanent = True
                
                flash('Registration successful! Welcome to your dashboard.', 'success')
                return redirect(url_for('business_dashboard'))
            else:
                flash('Registration failed. Please try again.', 'error')
                
        except Exception as e:
            print(f"Registration error: {str(e)}")
            flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('register.html')

@business_app.route('/dashboard')
@login_required
@business_required
def business_dashboard():
    try:
        user_id = safe_uuid(session.get('user_id'))
        business_id = safe_uuid(session.get('business_id'))
        
        # Get business details
        business_response = query_table('businesses', filters=[('id', 'eq', business_id)])
        
        if business_response and business_response.data:
            business = business_response.data[0]
        else:
            # Create mock business object from session data
            business = {
                'id': business_id,
                'name': session.get('business_name', 'Your Business'),
                'description': 'Business account',
                'access_pin': session.get('access_pin', '0000')
            }
        
        # Get summary data
        total_customers = 0
        total_credit = 0
        total_payments = 0
        transactions = []
        customers = []
        
        try:
            # Connect directly to database
            conn = psycopg2.connect(EXTERNAL_DATABASE_URL)
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Get total customers count
                cursor.execute("SELECT COUNT(*) FROM customer_credits WHERE business_id = %s", [business_id])
                total_customers = cursor.fetchone()[0]
                
                # Get recent customers - ordered by most recent transaction activity
                cursor.execute("""
                    SELECT c.id, c.name, c.phone_number, 
                           MAX(t.created_at) as last_transaction_date
                    FROM customers c
                    JOIN customer_credits cc ON c.id = cc.customer_id
                    LEFT JOIN transactions t ON c.id = t.customer_id AND t.business_id = %s
                    WHERE cc.business_id = %s
                    GROUP BY c.id, c.name, c.phone_number
                    ORDER BY last_transaction_date DESC NULLS LAST
                """, [business_id, business_id])
                
                customers_data = cursor.fetchall()
                for customer in customers_data:
                    customer_id = customer['id']
                    
                    # Calculate actual balance from transactions
                    cursor.execute("""
                        SELECT amount, transaction_type
                        FROM transactions
                        WHERE business_id = %s AND customer_id = %s
                    """, [business_id, customer_id])
                    
                    transactions_data = cursor.fetchall()
                    credit_total = sum([float(t['amount']) for t in transactions_data if t['transaction_type'] == 'credit'])
                    payment_total = sum([float(t['amount']) for t in transactions_data if t['transaction_type'] == 'payment'])
                    current_balance = credit_total - payment_total
                    
                    # Show all customers with transactions (not just positive balance)
                    if len(transactions_data) > 0:  # Only show customers who have transaction history
                        customers.append({
                            'id': customer['id'],
                            'name': customer['name'],
                            'phone_number': customer['phone_number'],
                            'current_balance': current_balance,
                            'last_transaction_date': customer['last_transaction_date']
                        })
                
                # Get recent transactions - increased to 15
                cursor.execute("""
                    SELECT t.*, c.name as customer_name
                    FROM transactions t
                    LEFT JOIN customers c ON t.customer_id = c.id
                    WHERE t.business_id = %s
                    ORDER BY t.created_at DESC
                    LIMIT 15
                """, [business_id])
                
                transactions_data = cursor.fetchall()
                for tx in transactions_data:
                    transactions.append({
                        'id': tx['id'],
                        'amount': float(tx['amount']) if tx['amount'] else 0,
                        'transaction_type': tx['transaction_type'],
                        'notes': tx.get('notes', ''),
                        'created_at': tx['created_at'],
                        'customer_name': tx.get('customer_name', 'Unknown')
                    })
                
                # Calculate total outstanding - sum all positive customer balances
                total_outstanding = sum([customer['current_balance'] for customer in customers if customer['current_balance'] > 0])
                
                # Customers are already ordered by recent transaction activity from the query
                # Limit to top 5 for display
                customers = customers[:5]
                
                print(f"DEBUG: Business Dashboard Calculations:")
                print(f"Total Outstanding (sum of positive customer balances): {total_outstanding}")
            
            conn.close()
            
        except Exception as e:
            print(f"Database error in business dashboard: {str(e)}")
            # Use fallback empty data
        
        # Generate QR code
        try:
            generate_business_qr_code(business_id, business['access_pin'])
        except Exception as e:
            print(f"QR code generation error: {str(e)}")
        
        summary = {
            'total_customers': total_customers,
            'total_outstanding': round(total_outstanding, 2)
        }
        
        return render_template('business/dashboard.html', 
                             business=business, 
                             summary=summary, 
                             transactions=transactions,
                             customers=customers)
                             
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('login'))

@business_app.route('/customers')
@login_required
@business_required
def business_customers():
    business_id = safe_uuid(session.get('business_id'))
    
    # Get all customer credits for this business
    customers_response = query_table('customer_credits', filters=[('business_id', 'eq', business_id)])
    customer_credits = customers_response.data if customers_response and customers_response.data else []
    
    # Gather all customer details
    customers = []
    for credit in customer_credits:
        customer_id = credit.get('customer_id')
        if customer_id:
            customer_detail = query_table('customers', filters=[('id', 'eq', customer_id)])
            if customer_detail and customer_detail.data:
                customer = dict(customer_detail.data[0])  # Convert to regular dict
                
                # Calculate actual balance from transactions instead of using stored balance
                transactions_response = query_table('transactions', 
                                                   filters=[('business_id', 'eq', business_id), 
                                                           ('customer_id', 'eq', customer_id)])
                transactions = transactions_response.data if transactions_response and transactions_response.data else []
                
                # Calculate totals the same way as customer details page
                credit_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'credit'])
                payment_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'payment'])
                current_balance = credit_total - payment_total
                
                customer['current_balance'] = current_balance
                customers.append(customer)
    
    # Sort customers by current balance (highest first), then by name
    customers.sort(key=lambda x: (-x.get('current_balance', 0), x.get('name', '')))
    
    return render_template('business/customers.html', customers=customers)

@business_app.route('/customer/<customer_id>')
@login_required
@business_required
def business_customer_details(customer_id):
    business_id = safe_uuid(session.get('business_id'))
    customer_id = safe_uuid(customer_id)
    
    # Get credit relationship
    credit_response = query_table('customer_credits', 
                               filters=[('business_id', 'eq', business_id), 
                                       ('customer_id', 'eq', customer_id)])
    credit = credit_response.data[0] if credit_response and credit_response.data else {}
    
    # Get customer details
    customer_response = query_table('customers', filters=[('id', 'eq', customer_id)])
    customer = customer_response.data[0] if customer_response and customer_response.data else {}
    
    # Merge customer details with credit information
    if customer and credit:
        customer = {**customer, 'current_balance': credit.get('current_balance', 0)}
    
    # Get transaction history - Force fresh query from database
    try:
        # Use direct database query to ensure we get the latest transactions
        conn = psycopg2.connect(EXTERNAL_DATABASE_URL)
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE business_id = %s AND customer_id = %s 
                ORDER BY created_at DESC
            """, [business_id, customer_id])
            
            transactions_data = cursor.fetchall()
            transactions = []
            for tx in transactions_data:
                transactions.append({
                    'id': tx['id'],
                    'amount': float(tx['amount']) if tx['amount'] else 0,
                    'transaction_type': tx['transaction_type'],
                    'notes': tx.get('notes', ''),
                    'created_at': tx['created_at'],
                    'created_by': tx.get('created_by', '')
                })
        conn.close()
        
        print(f"DEBUG: Found {len(transactions)} transactions for customer {customer_id}")
        
    except Exception as e:
        print(f"Error fetching transactions: {str(e)}")
        # Fallback to query_table method
        transactions_response = query_table('transactions', 
                                           filters=[('business_id', 'eq', business_id), 
                                                   ('customer_id', 'eq', customer_id)])
        transactions = transactions_response.data if transactions_response and transactions_response.data else []
    
    # Calculate totals
    credit_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'credit'])
    payment_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'payment'])
    
    # Calculate the actual balance that customer should give
    calculated_balance = credit_total - payment_total
    
    # Update the stored balance in customer_credits table to match calculated balance
    try:
        execute_query(
            "UPDATE customer_credits SET current_balance = %s, updated_at = %s WHERE business_id = %s AND customer_id = %s",
            [calculated_balance, get_ist_now().isoformat(), business_id, customer_id],
            commit=True
        )
        print(f"DEBUG: Updated stored balance to {calculated_balance} for customer {customer_id}")
    except Exception as e:
        print(f"WARNING: Could not update stored balance: {str(e)}")
    
    return render_template('business/customer_details.html', 
                          customer=customer, 
                          transactions=transactions,
                          credit_total=credit_total,
                          payment_total=payment_total,
                          calculated_balance=calculated_balance)

@business_app.route('/add_customer', methods=['GET', 'POST'])
@login_required
@business_required
def add_customer():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        initial_balance = float(request.form.get('initial_balance', 0))
        
        if not name or not phone:
            flash('Name and phone number are required', 'error')
            return render_template('business/add_customer.html')
        
        try:
            business_id = safe_uuid(session.get('business_id'))
            
            # Check if customer already exists by phone number
            existing_customer = execute_query("SELECT id FROM customers WHERE phone_number = %s LIMIT 1", [phone], fetch_one=True)
            
            if existing_customer:
                customer_id = existing_customer['id']
                print(f"DEBUG: Found existing customer with ID: {customer_id}")
            else:
                # Create new customer record
                customer_id = str(uuid.uuid4())
                customer_query = """
                    INSERT INTO customers (id, name, phone_number, created_at)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """
                result = execute_query(customer_query, [customer_id, name, phone, get_ist_now().isoformat()], fetch_one=True)
                if not result:
                    raise Exception("Failed to create customer")
                print(f"DEBUG: Created new customer with ID: {customer_id}")
                
                # Create customer user account with default password "devi123"
                try:
                    # Check if user account already exists for this phone number
                    existing_user = execute_query("SELECT id FROM users WHERE phone_number = %s LIMIT 1", [phone], fetch_one=True)
                    
                    if not existing_user:
                        user_id = str(uuid.uuid4())
                        user_query = """
                            INSERT INTO users (id, name, phone_number, user_type, password, created_at) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                            RETURNING id
                        """
                        user_result = execute_query(user_query, [
                            user_id, name, phone, 'customer', 'devi123', get_ist_now().isoformat()
                        ], fetch_one=True)
                        
                        if user_result:
                            print(f"DEBUG: Created customer user account for {phone} with password 'devi123'")
                        else:
                            print(f"WARNING: Failed to create user account for customer {phone}")
                    else:
                        print(f"DEBUG: User account already exists for phone {phone}")
                        
                except Exception as user_error:
                    print(f"WARNING: Could not create user account for customer: {str(user_error)}")
                    # Don't fail the whole operation if user creation fails
            
            # Check if credit relationship already exists
            existing_credit = execute_query(
                "SELECT id FROM customer_credits WHERE business_id = %s AND customer_id = %s LIMIT 1", 
                [business_id, customer_id], fetch_one=True
            )
            
            if existing_credit:
                flash('Customer already exists in your business!', 'warning')
                return redirect(url_for('business_customers'))
            else:
                # Create new credit relationship
                credit_query = """
                    INSERT INTO customer_credits (id, business_id, customer_id, current_balance, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                execute_query(credit_query, [
                    str(uuid.uuid4()), business_id, customer_id, 
                    initial_balance, get_ist_now().isoformat(), get_ist_now().isoformat()
                ])
                print(f"DEBUG: Created credit relationship for customer {customer_id} with business {business_id}")
            
            flash('Customer added successfully! Customer can now login with phone number and password: devi123', 'success')
            return redirect(url_for('business_customers'))
            
        except Exception as e:
            flash(f'Error adding customer: {str(e)}', 'error')
    
    return render_template('business/add_customer.html')

@business_app.route('/transactions/<customer_id>', methods=['GET', 'POST'])
@login_required
@business_required
def business_transactions(customer_id):
    business_id = safe_uuid(session.get('business_id'))
    customer_id = safe_uuid(customer_id)
    
    if request.method == 'POST':
        amount = request.form.get('amount')
        transaction_type = request.form.get('transaction_type')
        notes = request.form.get('notes', '')
        
        if not amount or not transaction_type:
            flash('Please enter amount and transaction type', 'error')
            return redirect(url_for('business_transactions', customer_id=customer_id))
        
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be greater than 0', 'error')
                return redirect(url_for('business_transactions', customer_id=customer_id))
        except ValueError:
            flash('Invalid amount', 'error')
            return redirect(url_for('business_transactions', customer_id=customer_id))
        
        try:
            # Create transaction
            transaction_data = {
                'id': str(uuid.uuid4()),
                'business_id': business_id,
                'customer_id': customer_id,
                'amount': amount,
                'transaction_type': transaction_type,
                'notes': notes,
                'created_at': get_ist_now().isoformat(),
                'created_by': session.get('user_id')
            }
            
            columns = list(transaction_data.keys())
            placeholders = ["%s"] * len(columns)
            values = [transaction_data[col] for col in columns]
            
            query = f"INSERT INTO transactions ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING id"
            result = execute_query(query, values, fetch_one=True, commit=True)
            
            if result:
                # Update customer balance in customer_credits table
                try:
                    # Get current balance
                    current_credit = execute_query(
                        "SELECT current_balance FROM customer_credits WHERE business_id = %s AND customer_id = %s", 
                        [business_id, customer_id], 
                        fetch_one=True
                    )
                    
                    if current_credit:
                        current_balance = float(current_credit['current_balance']) if current_credit['current_balance'] else 0.0
                        
                        # Calculate new balance based on transaction type
                        if transaction_type == 'credit':
                            new_balance = current_balance + amount  # Customer owes more
                        else:  # payment
                            new_balance = current_balance - amount  # Customer owes less
                        
                        # Update the balance
                        execute_query(
                            "UPDATE customer_credits SET current_balance = %s, updated_at = %s WHERE business_id = %s AND customer_id = %s",
                            [new_balance, datetime.now().isoformat(), business_id, customer_id],
                            commit=True
                        )
                        
                        print(f"Updated customer balance: {current_balance} -> {new_balance} (transaction: {transaction_type} {amount})")
                    else:
                        # Create customer credit record if it doesn't exist
                        initial_balance = amount if transaction_type == 'credit' else -amount
                        execute_query(
                            "INSERT INTO customer_credits (id, business_id, customer_id, current_balance, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
                            [str(uuid.uuid4()), business_id, customer_id, initial_balance, datetime.now().isoformat(), datetime.now().isoformat()],
                            commit=True
                        )
                        print(f"Created new customer credit record with balance: {initial_balance}")
                
                except Exception as balance_error:
                    print(f"Error updating customer balance: {str(balance_error)}")
                    # Don't fail the whole transaction, just log the error
                
                flash('Transaction added successfully', 'success')
            else:
                flash('Failed to add transaction. Please try again.', 'error')
                
        except Exception as e:
            print(f"Error adding transaction: {str(e)}")
            flash(f'Error adding transaction: {str(e)}', 'error')
        
        return redirect(url_for('business_customer_details', customer_id=customer_id))
    
    # GET request - show transaction form
    customer_response = query_table('customers', filters=[('id', 'eq', customer_id)])
    customer = dict(customer_response.data[0]) if customer_response and customer_response.data else {}
    
    # Get current balance
    credit_response = query_table('customer_credits', 
                                 filters=[('business_id', 'eq', business_id),
                                         ('customer_id', 'eq', customer_id)])
    credit_info = credit_response.data[0] if credit_response and credit_response.data else {}
    
    customer['current_balance'] = credit_info.get('current_balance', 0)
    
    return render_template('business/add_transaction.html', customer=customer)

@business_app.route('/profile', methods=['GET', 'POST'])
@login_required
@business_required
def business_profile():
    business_id = safe_uuid(session.get('business_id'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        try:
            update_data = {}
            if name:
                update_data['name'] = name
                session['business_name'] = name
            if description:
                update_data['description'] = description
            
            if update_data:
                query_table('businesses', query_type='update', 
                           data=update_data, filters=[('id', 'eq', business_id)])
                flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
    
    # Get current business details
    business_response = query_table('businesses', filters=[('id', 'eq', business_id)])
    business = business_response.data[0] if business_response and business_response.data else {
        'name': session.get('business_name', 'Your Business'),
        'description': 'Business account',
        'access_pin': session.get('access_pin', '0000')
    }
    
    return render_template('business/profile.html', business=business)

@business_app.route('/regenerate_pin', methods=['POST'])
@login_required
@business_required
def regenerate_business_pin():
    """Regenerate the business PIN"""
    business_id = safe_uuid(session.get('business_id'))
    
    try:
        # Generate a new unique PIN
        new_pin = get_unique_business_pin()
        
        # Update the business PIN in the database
        execute_query(
            "UPDATE businesses SET access_pin = %s, updated_at = %s WHERE id = %s",
            [new_pin, datetime.now().isoformat(), business_id],
            commit=True
        )
        
        # Update the session
        session['access_pin'] = new_pin
        
        # Regenerate QR code with new PIN
        generate_business_qr_code(business_id, new_pin)
        
        flash(f'New PIN generated successfully: {new_pin}', 'success')
        
    except Exception as e:
        print(f"Error regenerating PIN: {str(e)}")
        flash('Error generating new PIN. Please try again.', 'error')
    
    return redirect(url_for('business_profile'))

@business_app.route('/qr_image/<business_id>')
@login_required
@business_required  
def business_qr_image(business_id):
    try:
        business_id = safe_uuid(business_id)
        qr_filename = f"static/qr_codes/{business_id}.png"
        
        if os.path.exists(qr_filename):
            return send_from_directory('static/qr_codes', f"{business_id}.png")
        else:
            # Generate QR code if it doesn't exist
            access_pin = session.get('access_pin', '0000')
            generate_business_qr_code(business_id, access_pin)
            
            if os.path.exists(qr_filename):
                return send_from_directory('static/qr_codes', f"{business_id}.png")
            else:
                # Return placeholder
                return send_from_directory('static/images', 'placeholder_qr.png')
    except Exception as e:
        print(f"Error serving QR image: {str(e)}")
        return send_from_directory('static/images', 'placeholder_qr.png')

@business_app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@business_app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Error handling
@business_app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@business_app.route('/all_transactions')
@login_required
@business_required
def all_transactions():
    """View all transactions for the business"""
    try:
        business_id = safe_uuid(session.get('business_id'))
        page = int(request.args.get('page', 1))
        per_page = 50  # Show 50 transactions per page
        offset = (page - 1) * per_page
        
        transactions = []
        total_count = 0
        
        try:
            # Connect directly to database
            conn = psycopg2.connect(EXTERNAL_DATABASE_URL)
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Get total count for pagination
                cursor.execute("SELECT COUNT(*) FROM transactions WHERE business_id = %s", [business_id])
                total_count = cursor.fetchone()[0]
                
                # Get transactions with pagination
                cursor.execute("""
                    SELECT t.*, c.name as customer_name
                    FROM transactions t
                    LEFT JOIN customers c ON t.customer_id = c.id
                    WHERE t.business_id = %s
                    ORDER BY t.created_at DESC
                    LIMIT %s OFFSET %s
                """, [business_id, per_page, offset])
                
                transactions_data = cursor.fetchall()
                for tx in transactions_data:
                    transactions.append({
                        'id': tx['id'],
                        'amount': float(tx['amount']) if tx['amount'] else 0,
                        'transaction_type': tx['transaction_type'],
                        'notes': tx.get('notes', ''),
                        'created_at': tx['created_at'],
                        'customer_name': tx.get('customer_name', 'Unknown')
                    })
            
            conn.close()
            
        except Exception as e:
            print(f"Database error in business transactions: {str(e)}")
            flash('Error loading transactions', 'error')
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('business/transactions.html',
                             transactions=transactions,
                             page=page,
                             total_pages=total_pages,
                             has_prev=has_prev,
                             has_next=has_next,
                             total_count=total_count)
                             
    except Exception as e:
        flash(f'Error loading transactions: {str(e)}', 'error')
        return redirect(url_for('business_dashboard'))

@business_app.route('/sync_customer/<customer_id>')
@login_required
@business_required
def sync_customer_data(customer_id):
    """Manually sync customer transaction data"""
    business_id = safe_uuid(session.get('business_id'))
    customer_id = safe_uuid(customer_id)
    
    try:
        # Force refresh all transaction data for this customer
        conn = psycopg2.connect(EXTERNAL_DATABASE_URL)
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Get all transactions for this customer-business relationship
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE business_id = %s AND customer_id = %s 
                ORDER BY created_at DESC
            """, [business_id, customer_id])
            
            transactions = cursor.fetchall()
            
            # Recalculate balance
            credit_total = sum([float(t['amount']) for t in transactions if t['transaction_type'] == 'credit'])
            payment_total = sum([float(t['amount']) for t in transactions if t['transaction_type'] == 'payment'])
            new_balance = credit_total - payment_total
            
            # Update the stored balance
            cursor.execute("""
                UPDATE customer_credits 
                SET current_balance = %s, updated_at = %s 
                WHERE business_id = %s AND customer_id = %s
            """, [new_balance, get_ist_now().isoformat(), business_id, customer_id])
            
            conn.commit()
            
        conn.close()
        
        flash(f'Customer data synced successfully! Found {len(transactions)} transactions. Balance: ₹{new_balance:.2f}', 'success')
        print(f"DEBUG: Synced customer {customer_id} - {len(transactions)} transactions, balance: {new_balance}")
        
    except Exception as e:
        print(f"Error syncing customer data: {str(e)}")
        flash('Error syncing customer data. Please try again.', 'error')
    
    return redirect(url_for('business_customer_details', customer_id=customer_id))

@business_app.route('/remind_customer/<customer_id>')
@login_required
@business_required
def remind_customer(customer_id):
    """Send WhatsApp reminder to customer"""
    try:
        business_id = safe_uuid(session.get('business_id'))
        customer_id = safe_uuid(customer_id)
        
        # Get business details
        business_response = query_table('businesses', filters=[('id', 'eq', business_id)])
        business = business_response.data[0] if business_response and business_response.data else {}
        
        # Get customer details
        customer_response = query_table('customers', filters=[('id', 'eq', customer_id)])
        customer = customer_response.data[0] if customer_response and customer_response.data else {}
        
        # Get credit relationship for balance
        credit_response = query_table('customer_credits', 
                                   filters=[('business_id', 'eq', business_id), 
                                           ('customer_id', 'eq', customer_id)])
        credit = credit_response.data[0] if credit_response and credit_response.data else {}
        
        if not customer or not business:
            flash('Customer or business not found', 'error')
            return redirect(url_for('business_customers'))
        
        # Get current balance
        balance = credit.get('current_balance', 0)
        customer_name = customer.get('name', 'Customer')
        business_name = business.get('name', 'Business')
        phone_number = customer.get('phone_number', '')
        
        # Remove any non-digit characters from phone number
        import re
        clean_phone = re.sub(r'\D', '', phone_number)
        
        # Add country code if not present (assuming Indian numbers)
        if clean_phone and not clean_phone.startswith('91'):
            if clean_phone.startswith('0'):
                clean_phone = '91' + clean_phone[1:]
            elif len(clean_phone) == 10:
                clean_phone = '91' + clean_phone
        
        if not clean_phone:
            flash('Customer phone number not found or invalid', 'error')
            return redirect(url_for('business_customer_details', customer_id=customer_id))
        
        # Generate reminder message based on your format
        if balance > 0:
            message = f"""Hello {customer_name},
Just a gentle reminder about your outstanding balance of ₹{balance:,.2f} with us at {business_name}
You can check your balance and history here: https://www.khatape.tech/business/{business_id}
We'd appreciate it if you could pay soon!
{business_name}"""
        else:
            message = f"""Hello {customer_name},
Thank you for keeping your account up to date with {business_name}!
Your current balance is ₹{balance:,.2f}
You can check your balance and history here: https://www.khatape.tech/business/{business_id}
We appreciate your business!
{business_name}"""
        
        # Create WhatsApp URL
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_message}"
        
        # Log the reminder
        logger.info(f"WhatsApp reminder generated for customer {customer_id}: {clean_phone}")
        
        # Redirect to WhatsApp
        return redirect(whatsapp_url)
        
    except Exception as e:
        logger.error(f"Error generating WhatsApp reminder: {str(e)}")
        flash('Error generating reminder. Please try again.', 'error')
        return redirect(url_for('business_customer_details', customer_id=customer_id))

@business_app.route('/remind_all_customers')
@login_required
@business_required
def remind_all_customers():
    """Show page with all customers that need WhatsApp reminders"""
    try:
        business_id = safe_uuid(session.get('business_id'))
        
        # Get business details
        business_response = query_table('businesses', filters=[('id', 'eq', business_id)])
        business = business_response.data[0] if business_response and business_response.data else {}
        business_name = business.get('name', 'Business')
        
        # Get all customers with balances
        conn = psycopg2.connect(EXTERNAL_DATABASE_URL)
        customers_to_remind = []
        
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Get all customers with their phone numbers and balances
            cursor.execute("""
                SELECT c.id, c.name, c.phone_number
                FROM customers c
                JOIN customer_credits cc ON c.id = cc.customer_id
                WHERE cc.business_id = %s AND c.phone_number IS NOT NULL AND c.phone_number != ''
                ORDER BY c.name
            """, [business_id])
            
            customers_data = cursor.fetchall()
            
            for customer in customers_data:
                try:
                    customer_id = customer['id']
                    customer_name = customer.get('name', 'Customer')
                    phone_number = customer.get('phone_number', '')
                    
                    # Calculate balance from transactions
                    cursor.execute("""
                        SELECT amount, transaction_type
                        FROM transactions
                        WHERE business_id = %s AND customer_id = %s
                    """, [business_id, customer_id])
                    
                    transactions_data = cursor.fetchall()
                    if not transactions_data:
                        continue  # Skip customers with no transactions
                    
                    credit_total = sum([float(t['amount']) for t in transactions_data if t['transaction_type'] == 'credit'])
                    payment_total = sum([float(t['amount']) for t in transactions_data if t['transaction_type'] == 'payment'])
                    balance = credit_total - payment_total
                    
                    # Only include customers with positive balances
                    if balance <= 0:
                        continue
                    
                    # Clean phone number
                    import re
                    clean_phone = re.sub(r'\D', '', phone_number)
                    
                    # Add country code if not present (assuming Indian numbers)
                    if clean_phone and not clean_phone.startswith('91'):
                        if clean_phone.startswith('0'):
                            clean_phone = '91' + clean_phone[1:]
                        elif len(clean_phone) == 10:
                            clean_phone = '91' + clean_phone
                    
                    if not clean_phone:
                        continue
                    
                    # Generate reminder message
                    message = f"""Hi {customer_name}! 🙏

Your current balance with {business_name} is ₹{balance:,.2f}. 
You can view your transaction history and make payments here: 
https://www.khatape.tech/business/{business_id}

Thank you for your business! 😊

- {business_name} Team"""
                    
                    # Create WhatsApp URL
                    import urllib.parse
                    encoded_message = urllib.parse.quote(message)
                    whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_message}"
                    
                    customers_to_remind.append({
                        'id': customer_id,
                        'name': customer_name,
                        'phone': f"+{clean_phone}",
                        'balance': f"{balance:,.2f}",
                        'whatsapp_url': whatsapp_url
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing customer {customer.get('name', 'Unknown')}: {str(e)}")
                    continue
        
        conn.close()
        
        return render_template('business/bulk_reminders.html', 
                             customers=customers_to_remind,
                             business=business)
            
    except Exception as e:
        logger.error(f"Error generating bulk reminders: {str(e)}")
        flash('Error loading reminder page. Please try again.', 'error')
        return redirect(url_for('business_customers'))

# PhonePe Payment Approval System Routes

@business_app.route('/pending_payments')
@login_required
@business_required
def pending_payments():
    """Display all payments awaiting business approval"""
    try:
        business_id = safe_uuid(session.get('business_id'))
        
        # Query pending payments from the database
        pending_payments_query = """
            SELECT pp.*, c.name as customer_name, c.phone_number as customer_phone
            FROM pending_payments pp
            JOIN customers c ON pp.customer_id = c.id
            WHERE pp.business_id = %s AND pp.status = 'pending'
            ORDER BY pp.created_at DESC
        """
        
        pending_payments_data = execute_query(pending_payments_query, [business_id])
        
        # Format the data for display
        formatted_payments = []
        if pending_payments_data:
            for payment in pending_payments_data:
                formatted_payments.append({
                    'transaction_id': payment['transaction_id'],
                    'customer_name': payment['customer_name'],
                    'customer_phone': payment['customer_phone'],
                    'amount': float(payment['amount']),
                    'payment_method': payment.get('payment_method', 'PhonePe'),
                    'notes': payment.get('notes', ''),
                    'created_at': payment['created_at'],
                    'timestamp': format_datetime(payment['created_at'])
                })
        
        return render_template('business/pending_payments.html', 
                             pending_payments=formatted_payments,
                             business={'name': session.get('business_name', 'Your Business')})
        
    except Exception as e:
        logger.error(f"Error loading pending payments: {str(e)}")
        flash('Error loading pending payments. Please try again.', 'error')
        return redirect(url_for('business_dashboard'))

@business_app.route('/approve_payment/<transaction_id>', methods=['POST'])
@login_required
@business_required
def approve_payment(transaction_id):
    """Approve a pending payment and create actual transaction record"""
    try:
        business_id = safe_uuid(session.get('business_id'))
        transaction_id = safe_uuid(transaction_id)
        
        # Get pending payment details
        pending_payment_query = """
            SELECT pp.*, c.name as customer_name
            FROM pending_payments pp
            JOIN customers c ON pp.customer_id = c.id
            WHERE pp.transaction_id = %s AND pp.business_id = %s AND pp.status = 'pending'
        """
        
        pending_payment = execute_query(pending_payment_query, [transaction_id, business_id], fetch_one=True)
        
        if not pending_payment:
            flash('Payment not found or already processed.', 'error')
            return redirect(url_for('pending_payments'))
        
        # Create actual transaction record
        transaction_data = {
            'id': str(uuid.uuid4()),
            'business_id': business_id,
            'customer_id': pending_payment['customer_id'],
            'amount': pending_payment['amount'],
            'transaction_type': 'payment',  # PhonePe payments are always payments (reducing customer debt)
            'payment_method': 'PhonePe',
            'notes': f"PhonePe Payment: {pending_payment.get('notes', '')}",
            'created_at': get_ist_now().isoformat(),
            'created_by': session.get('user_id'),
            'approved_at': get_ist_now().isoformat(),
            'original_pending_id': transaction_id
        }
        
        # Insert transaction into transactions table
        columns = list(transaction_data.keys())
        placeholders = ["%s"] * len(columns)
        values = [transaction_data[col] for col in columns]
        
        insert_query = f"INSERT INTO transactions ({', '.join(columns)}) VALUES ({', '.join(placeholders)}) RETURNING id"
        result = execute_query(insert_query, values, fetch_one=True, commit=True)
        
        if result:
            # Update customer balance
            amount = float(pending_payment['amount'])
            customer_id = pending_payment['customer_id']
            
            # Get current balance
            current_credit = execute_query(
                "SELECT current_balance FROM customer_credits WHERE business_id = %s AND customer_id = %s", 
                [business_id, customer_id], 
                fetch_one=True
            )
            
            if current_credit:
                current_balance = float(current_credit['current_balance']) if current_credit['current_balance'] else 0.0
                new_balance = current_balance - amount  # Payment reduces customer debt
                
                execute_query(
                    "UPDATE customer_credits SET current_balance = %s, updated_at = %s WHERE business_id = %s AND customer_id = %s",
                    [new_balance, datetime.now().isoformat(), business_id, customer_id],
                    commit=True
                )
            else:
                # Create customer credit record if it doesn't exist
                initial_balance = -amount  # Negative because it's a payment
                execute_query(
                    "INSERT INTO customer_credits (id, business_id, customer_id, current_balance, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)",
                    [str(uuid.uuid4()), business_id, customer_id, initial_balance, datetime.now().isoformat(), datetime.now().isoformat()],
                    commit=True
                )
            
            # Update pending payment status to approved
            execute_query(
                "UPDATE pending_payments SET status = 'approved', approved_at = %s, approved_by = %s WHERE transaction_id = %s",
                [get_ist_now().isoformat(), session.get('user_id'), transaction_id],
                commit=True
            )
            
            # Send confirmation to customer app (cross-app communication)
            try:
                customer_app_url = "http://localhost:5002"  # Customer app port
                confirmation_data = {
                    'transaction_id': transaction_id,
                    'status': 'approved',
                    'business_id': business_id,
                    'customer_id': customer_id,
                    'amount': amount,
                    'approved_at': get_ist_now().isoformat()
                }
                
                requests.post(f"{customer_app_url}/payment_status_update", 
                             json=confirmation_data, timeout=5)
            except Exception as comm_error:
                logger.warning(f"Could not notify customer app: {str(comm_error)}")
            
            flash(f'Payment of ₹{amount:,.2f} from {pending_payment["customer_name"]} approved successfully!', 'success')
        else:
            flash('Failed to approve payment. Please try again.', 'error')
        
    except Exception as e:
        logger.error(f"Error approving payment: {str(e)}")
        flash('Error approving payment. Please try again.', 'error')
    
    return redirect(url_for('pending_payments'))

@business_app.route('/reject_payment/<transaction_id>', methods=['POST'])
@login_required
@business_required
def reject_payment(transaction_id):
    """Reject a pending payment"""
    try:
        business_id = safe_uuid(session.get('business_id'))
        transaction_id = safe_uuid(transaction_id)
        rejection_reason = request.form.get('rejection_reason', 'No reason provided')
        
        # Get pending payment details
        pending_payment_query = """
            SELECT pp.*, c.name as customer_name
            FROM pending_payments pp
            JOIN customers c ON pp.customer_id = c.id
            WHERE pp.transaction_id = %s AND pp.business_id = %s AND pp.status = 'pending'
        """
        
        pending_payment = execute_query(pending_payment_query, [transaction_id, business_id], fetch_one=True)
        
        if not pending_payment:
            flash('Payment not found or already processed.', 'error')
            return redirect(url_for('pending_payments'))
        
        # Update pending payment status to rejected
        execute_query(
            "UPDATE pending_payments SET status = 'rejected', rejected_at = %s, rejected_by = %s, rejection_reason = %s WHERE transaction_id = %s",
            [get_ist_now().isoformat(), session.get('user_id'), rejection_reason, transaction_id],
            commit=True
        )
        
        # Notify customer app of rejection
        try:
            customer_app_url = "http://localhost:5002"  # Customer app port
            rejection_data = {
                'transaction_id': transaction_id,
                'status': 'rejected',
                'business_id': business_id,
                'customer_id': pending_payment['customer_id'],
                'amount': pending_payment['amount'],
                'rejection_reason': rejection_reason,
                'rejected_at': get_ist_now().isoformat()
            }
            
            requests.post(f"{customer_app_url}/payment_status_update", 
                         json=rejection_data, timeout=5)
        except Exception as comm_error:
            logger.warning(f"Could not notify customer app: {str(comm_error)}")
        
        flash(f'Payment of ₹{float(pending_payment["amount"]):,.2f} from {pending_payment["customer_name"]} rejected.', 'warning')
        
    except Exception as e:
        logger.error(f"Error rejecting payment: {str(e)}")
        flash('Error rejecting payment. Please try again.', 'error')
    
    return redirect(url_for('pending_payments'))

@business_app.route('/payment_status_update', methods=['POST'])
def payment_status_update():
    """Endpoint for receiving payment status updates from customer app"""
    try:
        data = request.get_json()
        transaction_id = data.get('transaction_id')
        status = data.get('status')
        
        logger.info(f"Received payment status update: {transaction_id} -> {status}")
        
        # Log the update for debugging
        if transaction_id and status:
            logger.info(f"Payment {transaction_id} status updated to {status}")
            return jsonify({'success': True, 'message': 'Status update received'})
        else:
            return jsonify({'success': False, 'message': 'Invalid data'}), 400
            
    except Exception as e:
        logger.error(f"Error processing payment status update: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal error'}), 500

@business_app.route('/test_pending_payment', methods=['POST'])
@login_required
@business_required
def test_pending_payment():
    """Test endpoint to create a mock pending payment for testing"""
    try:
        business_id = safe_uuid(session.get('business_id'))
        
        # Get the first customer for this business
        customer_query = "SELECT id, name FROM customers WHERE business_id = %s LIMIT 1"
        customer = execute_query(customer_query, [business_id], fetch_one=True)
        
        if not customer:
            flash('No customers found. Add a customer first.', 'error')
            return redirect(url_for('business_dashboard'))
        
        # Create a test pending payment
        test_payment = {
            'transaction_id': str(uuid.uuid4()),
            'business_id': business_id,
            'customer_id': customer['id'],
            'amount': 500.00,
            'payment_method': 'PhonePe',
            'notes': 'Test payment via PhonePe',
            'status': 'pending',
            'created_at': get_ist_now().isoformat()
        }
        
        columns = list(test_payment.keys())
        placeholders = ["%s"] * len(columns)
        values = [test_payment[col] for col in columns]
        
        insert_query = f"INSERT INTO pending_payments ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        result = execute_query(insert_query, values, commit=True)
        
        if result is not None:
            flash(f'Test pending payment of ₹500.00 created for {customer["name"]}!', 'success')
        else:
            flash('Failed to create test payment.', 'error')
            
    except Exception as e:
        logger.error(f"Error creating test pending payment: {str(e)}")
        flash('Error creating test payment.', 'error')
    
    return redirect(url_for('pending_payments'))

@business_app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@business_app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# Run the application
if __name__ == '__main__':
    port = int(os.environ.get('BUSINESS_PORT', 5001))
    business_app.run(debug=False, host='0.0.0.0', port=port)
