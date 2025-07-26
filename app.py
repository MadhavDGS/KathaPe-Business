"""
Business Flask Application - Handles all business-related operations
"""
from common_utils import *

# Create the business Flask app
business_app = create_app('KathaPe-Business')

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
                
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
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
                
                # Get recent customers - prioritize those with outstanding balances
                cursor.execute("""
                    SELECT c.*, cc.current_balance 
                    FROM customers c
                    JOIN customer_credits cc ON c.id = cc.customer_id
                    WHERE cc.business_id = %s
                    ORDER BY cc.current_balance DESC, cc.updated_at DESC
                    LIMIT 5
                """, [business_id])
                
                customers_data = cursor.fetchall()
                for customer in customers_data:
                    customers.append({
                        'id': customer['id'],
                        'name': customer['name'],
                        'phone_number': customer['phone_number'],
                        'current_balance': float(customer['current_balance']) if customer['current_balance'] else 0
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
                
                # Calculate totals - Use actual customer balance sums instead of transaction totals
                # This matches how the customer app calculates balances
                cursor.execute("SELECT COALESCE(SUM(current_balance), 0) FROM customer_credits WHERE business_id = %s AND current_balance > 0", [business_id])
                total_outstanding_raw = cursor.fetchone()[0]
                total_outstanding = float(total_outstanding_raw) if total_outstanding_raw else 0.0
                
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
                # Get current balance from credit record, default to 0 if not found
                try:
                    current_balance = float(credit.get('current_balance', 0)) if 'current_balance' in credit else 0.0
                except (ValueError, TypeError):
                    current_balance = 0.0
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
    
    # Get transaction history
    transactions_response = query_table('transactions', 
                                       filters=[('business_id', 'eq', business_id), 
                                               ('customer_id', 'eq', customer_id)])
    transactions = transactions_response.data if transactions_response and transactions_response.data else []
    
    # Calculate totals
    credit_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'credit'])
    payment_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'payment'])
    
    # Calculate the actual balance that customer should give
    calculated_balance = credit_total - payment_total
    
    # Sort transactions by date, newest first
    transactions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
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
                # Create new customer (but do NOT create a user account - that's only done during registration)
                customer_id = str(uuid.uuid4())
                customer_query = """
                    INSERT INTO customers (id, name, phone_number, created_at)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """
                result = execute_query(customer_query, [customer_id, name, phone, datetime.now().isoformat()], fetch_one=True)
                if not result:
                    raise Exception("Failed to create customer")
                print(f"DEBUG: Created new customer with ID: {customer_id}")
            
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
                    initial_balance, datetime.now().isoformat(), datetime.now().isoformat()
                ])
                print(f"DEBUG: Created credit relationship for customer {customer_id} with business {business_id}")
            
            flash('Customer added successfully!', 'success')
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
                'created_at': datetime.now().isoformat(),
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

@business_app.route('/remind_customer/<customer_id>')
@login_required
@business_required
def remind_customer(customer_id):
    """Basic reminder functionality - can be expanded later"""
    flash('Reminder feature will be implemented soon!', 'info')
    return redirect(url_for('business_customer_details', customer_id=customer_id))

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
