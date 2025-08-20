"""
Business Flask Application - Handles all business-related operations
"""
from common_utils import *
import base64
from flask import Response

# Import Appwrite utilities
from appwrite_utils import AppwriteDB
from appwrite.query import Query

# Initialize Appwrite DB
appwrite_db = AppwriteDB()

# Create the business Flask app
business_app = create_app('Khatape-Business')

@business_app.route('/bill_image/<transaction_id>')
@login_required
@business_required
def bill_image(transaction_id):
    """Serve bill image from base64 string in receipt_image_url column"""
    try:
        business_id = safe_uuid(session.get('business_id'))
        transaction_id = safe_uuid(transaction_id)
        
        # Get the base64 image data from Appwrite
<<<<<<< HEAD
        from appwrite_utils import get_transaction_by_id
        transaction = get_transaction_by_id(transaction_id)
        
        if not transaction or transaction.get('business_id') != business_id or not transaction.get('receipt_image_url'):
            return Response("Bill image not found", status=404)
        
        img_data = transaction['receipt_image_url']
=======
        from appwrite_utils import db
        
        # Get transaction document
        transaction = db.get_document('transactions', transaction_id)
        
        if not transaction or transaction.get('business_id') != business_id:
            return Response("Bill image not found", status=404)
        
        receipt_image_url = transaction.get('receipt_image_url')
        if not receipt_image_url:
            return Response("Bill image not found", status=404)
        
        img_data = receipt_image_url
>>>>>>> 64f183b76de57e07d1178b54e0a01fc6ea9fbb6a
        
        # Handle data URL format (data:image/jpeg;base64,...)
        if img_data.startswith('data:image/'):
            # Remove data URL prefix if present
            header, img_data = img_data.split(',', 1)
            if 'jpeg' in header or 'jpg' in header:
                mime_type = 'image/jpeg'
            elif 'png' in header:
                mime_type = 'image/png'
            elif 'webp' in header:
                mime_type = 'image/webp'
            else:
                mime_type = 'image/jpeg'  # Default fallback
        else:
            # Assume it's just base64 data without prefix
            mime_type = 'image/jpeg'  # Default to JPEG
        
        try:
            # Decode base64 string to bytes
            image_bytes = base64.b64decode(img_data)
            return Response(image_bytes, mimetype=mime_type)
        except Exception as decode_error:
            print(f"Error decoding base64 image: {str(decode_error)}")
            return Response("Invalid image data", status=415)
            
    except Exception as e:
        print(f"Error serving bill image: {str(e)}")
        return Response("Server error", status=500)
        conn.close()
        if not result or not result['receipt_image_url']:
            return Response(status=404)
        # Try to detect image type
        img_data = result['receipt_image_url']
        if img_data.startswith('data:image/'):
            # Remove data URL prefix if present
            header, img_data = img_data.split(',', 1)
            if 'jpeg' in header:
                mime = 'image/jpeg'
            elif 'png' in header:
                mime = 'image/png'
            else:
                mime = 'application/octet-stream'
        else:
            # Default to jpeg
            mime = 'image/jpeg'
        try:
            image_bytes = base64.b64decode(img_data)
        except Exception:
            return Response(status=415)
        return Response(image_bytes, mimetype=mime)
    except Exception as e:
        print(f"Error serving bill image: {str(e)}")
        return Response(status=500)

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
            
            # Try Appwrite authentication
            try:
                logger.info("Testing Appwrite connection for business login")
                
                # Use appwrite_db to find user
                appwrite_db._ensure_initialized()
                from appwrite.query import Query
                
                # Query business user
                users = appwrite_db.list_documents('users', [
                    Query.equal('phone_number', phone),
                    Query.equal('user_type', 'business'),
                    Query.limit(1)
                ])
                
                if users and len(users) > 0:
                    user_data = users[0]
                    if user_data.get('password') == password:
                        # ONLY set session after successful password verification
                        user_id = user_data['$id']
                        user_name = user_data.get('name', f"Business {phone[-4:]}" if phone and len(phone) > 4 else "Business User")
                        
                        session['user_id'] = user_id
                        session['user_name'] = user_name
                        session['user_type'] = 'business'
                        session['phone_number'] = phone
                        session.permanent = True
                        
                        # Get business details using Appwrite
                        businesses = appwrite_db.list_documents('businesses', [
                            Query.equal('user_id', user_id),
                            Query.limit(1)
                        ])
                        
                        if businesses and len(businesses) > 0:
                            business_data = businesses[0]
                            session['business_id'] = business_data['$id']
                            session['business_name'] = business_data['name']
                            session['access_pin'] = business_data['access_pin']
                        else:
                            # Create business record if it doesn't exist
                            business_id = str(uuid.uuid4())
                            access_pin = get_unique_business_pin()
                            business_doc = {
                                'user_id': user_id,
                                'name': f"{session['user_name']}'s Business",
                                'access_pin': access_pin,
                                'created_at': datetime.now().isoformat(),
                                'is_active': True
                            }
                            appwrite_db.create_document('businesses', business_doc, business_id)
                            session['business_id'] = business_id
                            session['business_name'] = f"{session['user_name']}'s Business"
                            session['access_pin'] = access_pin
                        
                        flash('Successfully logged in!', 'success')
                        return redirect(url_for('business_dashboard'))
                    else:
                        flash('Invalid phone number or password', 'error')
                        return render_template('login.html')
                else:
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
            # Check if phone number already exists using Appwrite
            appwrite_db._ensure_initialized()
            from appwrite.query import Query
            
            existing_users = appwrite_db.list_documents('users', [
                Query.equal('phone_number', phone),
                Query.limit(1)
            ])
            
            if existing_users and len(existing_users) > 0:
                flash('Phone number already registered', 'error')
                return render_template('register.html')
            
            # Create user and business records
            user_id = str(uuid.uuid4())
            business_id = str(uuid.uuid4())
            access_pin = get_unique_business_pin()
            
            # Create user record in Appwrite
            user_doc = {
                'name': name,
                'phone_number': phone,
                'user_type': 'business',
                'password': password,
                'created_at': datetime.now().isoformat(),
                'is_active': True
            }
            user_result = appwrite_db.create_document('users', user_doc, user_id)
            
            if user_result:
                # Create business record in Appwrite
                business_doc = {
                    'user_id': user_id,
                    'name': f"{name}'s Business",
                    'description': 'My business account',
                    'access_pin': access_pin,
                    'created_at': datetime.now().isoformat(),
                    'is_active': True
                }
                appwrite_db.create_document('businesses', business_doc, business_id)
                
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
        
        # Get business details using Appwrite
        appwrite_db._ensure_initialized()
        from appwrite.query import Query
        
        business = appwrite_db.get_document('businesses', business_id)
        
        if not business:
            # Create mock business object from session data
            business = {
                '$id': business_id,
                'name': session.get('business_name', 'Your Business'),
                'description': 'Business account',
                'access_pin': session.get('access_pin', '0000')
            }
        
        # Get summary data using Appwrite
        total_customers = 0
        total_credit = 0
        total_payments = 0
        transactions = []
        customers = []
        
        try:
            # Get customer credits for this business
            customer_credits = appwrite_db.list_documents('customer_credits', [
                Query.equal('business_id', business_id)
            ])
            total_customers = len(customer_credits)
            
            # Get all transactions for this business (limited for dashboard)
            all_transactions = appwrite_db.list_documents('transactions', [
                Query.equal('business_id', business_id),
                Query.order_desc('created_at'),
                Query.limit(50)
            ])
            
            # Calculate totals from transactions
            for transaction in all_transactions:
                amount = float(transaction.get('amount', 0))
                if transaction.get('transaction_type') == 'credit':
                    total_credit += amount
                elif transaction.get('transaction_type') == 'payment':
                    total_payments += amount
            
            # Get recent transactions for display (limited to 10)
            transactions = all_transactions[:10]
            
            # Get customer details for the customers with credits
            customers_list = []
            for credit in customer_credits[:10]:  # Limit to 10 for dashboard
                customer_id = credit.get('customer_id')
                if customer_id:
                    customer = appwrite_db.get_document('customers', customer_id)
                    if customer:
                        customer_data = {
                            'id': customer['$id'],
                            'name': customer.get('name', 'Unknown'),
                            'phone_number': customer.get('phone_number', ''),
                            'current_balance': credit.get('current_balance', 0)
                        }
                        customers_list.append(customer_data)
            customers = customers_list
            
            # Calculate total outstanding - sum all positive customer balances
            total_outstanding = sum([customer['current_balance'] for customer in customers if customer['current_balance'] > 0])
            
            # Limit to top 5 for display
            customers = customers[:5]
            
            print(f"DEBUG: Business Dashboard Calculations:")
            print(f"Total Outstanding (sum of positive customer balances): {total_outstanding}")
            
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
    
    try:
        # Get all customer credits for this business
        customer_credits = appwrite_db.list_documents('customer_credits', [
            Query.equal('business_id', business_id)
        ])
        
        # Gather all customer details
        customers = []
        for credit in customer_credits:
            customer_id = credit.get('customer_id')
            if customer_id:
                try:
                    customer = appwrite_db.get_document('customers', customer_id)
                    
                    # Calculate actual balance from transactions
                    transactions = appwrite_db.list_documents('transactions', [
                        Query.equal('business_id', business_id),
                        Query.equal('customer_id', customer_id)
                    ])
                    
                    # Calculate totals the same way as customer details page
                    credit_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'credit'])
                    payment_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'payment'])
                    current_balance = credit_total - payment_total
                    
                    customer_data = {
                        'id': customer['$id'],
                        'name': customer.get('name', 'Unknown'),
                        'phone_number': customer.get('phone_number', ''),
                        'current_balance': current_balance
                    }
                    customers.append(customer_data)
                except Exception as e:
                    print(f"Error getting customer {customer_id}: {str(e)}")
                    continue
        
        # Sort customers by current balance (highest first), then by name
        customers.sort(key=lambda x: (-x.get('current_balance', 0), x.get('name', '')))
        
    except Exception as e:
        print(f"Error in business customers: {str(e)}")
        flash('Error loading customers', 'error')
        customers = []
    
    return render_template('business/customers.html', customers=customers)

@business_app.route('/customer/<customer_id>')
@login_required
@business_required
def business_customer_details(customer_id):
    business_id = safe_uuid(session.get('business_id'))
    customer_id = safe_uuid(customer_id)
    
    try:
        # Get credit relationship
        credit_response = appwrite_db.list_documents('customer_credits', [
            Query.equal('business_id', business_id),
            Query.equal('customer_id', customer_id)
        ])
        credit = credit_response[0] if credit_response else {}
        
        # Get customer details
        customer = appwrite_db.get_document('customers', customer_id)
        
        if not customer:
            flash('Customer not found', 'error')
            return redirect(url_for('business_customers'))
        
        # Merge customer details with credit information
        customer_data = {
            'id': customer['$id'],
            'name': customer.get('name', 'Unknown'),
            'phone_number': customer.get('phone_number', ''),
            'current_balance': credit.get('current_balance', 0)
        }
        
        # Get transaction history using Appwrite
        transactions = appwrite_db.list_documents('transactions', [
            Query.equal('business_id', business_id),
            Query.equal('customer_id', customer_id),
            Query.order_desc('created_at')
        ])
        
        # Format transactions for display
        transactions_list = []
        for tx in transactions:
            transactions_list.append({
                'id': tx['$id'],
                'amount': float(tx.get('amount', 0)),
                'transaction_type': tx.get('transaction_type', ''),
                'notes': tx.get('notes', ''),
                'created_at': tx.get('created_at', ''),
                'created_by': tx.get('created_by', ''),
                'receipt_image_url': tx.get('receipt_image_url', '')
            })
        
        print(f"DEBUG: Found {len(transactions_list)} transactions for customer {customer_id}")
        
        # Calculate totals
        credit_total = sum([float(t.get('amount', 0)) for t in transactions_list if t.get('transaction_type') == 'credit'])
        payment_total = sum([float(t.get('amount', 0)) for t in transactions_list if t.get('transaction_type') == 'payment'])
        
        # Calculate the actual balance that customer should give
        calculated_balance = credit_total - payment_total
        
        # Update the stored balance in customer_credits table to match calculated balance
        if credit:
            try:
                appwrite_db.update_document('customer_credits', credit['$id'], {
                    'current_balance': calculated_balance,
                    'updated_at': datetime.now().isoformat()
                })
                customer_data['current_balance'] = calculated_balance
            except Exception as e:
                print(f"Error updating customer balance: {str(e)}")
        
    except Exception as e:
        print(f"Error in customer details: {str(e)}")
        flash('Error loading customer details', 'error')
        return redirect(url_for('business_customers'))
    
    return render_template('business/customer_details.html', 
                         customer=customer_data, 
                         transactions=transactions_list,
                         credit_total=credit_total,
                         payment_total=payment_total)

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
            existing_customers = appwrite_db.list_documents('customers', [
                Query.equal('phone_number', phone),
                Query.limit(1)
            ])
            
            if existing_customers:
                customer_id = existing_customers[0]['$id']
                customer = existing_customers[0]
                print(f"DEBUG: Found existing customer with ID: {customer_id}")
            else:
                # Create new customer record
                customer_data = {
                    'name': name,
                    'phone_number': phone,
                    'created_at': datetime.now().isoformat()
                }
                customer = appwrite_db.create_document('customers', 'unique()', customer_data)
                customer_id = customer['$id']
                print(f"DEBUG: Created new customer with ID: {customer_id}")
                
                # Create customer user account with default password "devi123"
                try:
                    # Check if user account already exists for this phone number
                    existing_users = appwrite_db.list_documents('users', [
                        Query.equal('phone_number', phone),
                        Query.limit(1)
                    ])
                    
                    if not existing_users:
                        user_data = {
                            'name': name,
                            'phone_number': phone,
                            'user_type': 'customer',
                            'password': 'devi123',
                            'created_at': datetime.now().isoformat()
                        }
                        user_result = appwrite_db.create_document('users', 'unique()', user_data)
                        
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
            existing_credits = appwrite_db.list_documents('customer_credits', [
                Query.equal('business_id', business_id),
                Query.equal('customer_id', customer_id),
                Query.limit(1)
            ])
            
            if existing_credits:
                flash('Customer already exists in your business!', 'warning')
                return redirect(url_for('business_customers'))
            else:
                # Create new credit relationship
                credit_data = {
                    'business_id': business_id,
                    'customer_id': customer_id,
                    'current_balance': initial_balance,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                appwrite_db.create_document('customer_credits', 'unique()', credit_data)
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
                'business_id': business_id,
                'customer_id': customer_id,
                'amount': amount,
                'transaction_type': transaction_type,
                'notes': notes,
                'created_at': datetime.now().isoformat(),
                'created_by': session.get('user_id')
            }
            
            result = appwrite_db.create_document('transactions', 'unique()', transaction_data)
            
            if result:
                # Update customer balance in customer_credits table
                try:
                    # Get current balance
                    credit_records = appwrite_db.list_documents('customer_credits', [
                        Query.equal('business_id', business_id),
                        Query.equal('customer_id', customer_id),
                        Query.limit(1)
                    ])
                    
                    if credit_records:
                        credit_record = credit_records[0]
                        current_balance = float(credit_record.get('current_balance', 0))
                        
                        # Calculate new balance based on transaction type
                        if transaction_type == 'credit':
                            new_balance = current_balance + amount  # Customer owes more
                        else:  # payment
                            new_balance = current_balance - amount  # Customer owes less
                        
                        # Update the balance
                        appwrite_db.update_document('customer_credits', credit_record['$id'], {
                            'current_balance': new_balance,
                            'updated_at': datetime.now().isoformat()
                        })
                        
                        print(f"Updated customer balance: {current_balance} -> {new_balance} (transaction: {transaction_type} {amount})")
                    else:
                        # Create customer credit record if it doesn't exist
                        initial_balance = amount if transaction_type == 'credit' else -amount
                        credit_data = {
                            'business_id': business_id,
                            'customer_id': customer_id,
                            'current_balance': initial_balance,
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat()
                        }
                        appwrite_db.create_document('customer_credits', 'unique()', credit_data)
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
        business = appwrite_db.get_document('businesses', business_id)
        appwrite_db.update_document('businesses', business_id, {
            'access_pin': new_pin,
            'updated_at': datetime.now().isoformat()
        })
        
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

# PWA routes
@business_app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/json')

@business_app.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'
    return response

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
            # Get total count for pagination - Appwrite doesn't have direct count, we'll get all and count
            all_transactions = appwrite_db.list_documents('transactions', [
                Query.equal('business_id', business_id)
            ])
            total_count = len(all_transactions)
            
            # Get transactions with pagination and sorting
            paginated_transactions = appwrite_db.list_documents('transactions', [
                Query.equal('business_id', business_id),
                Query.order_desc('created_at'),
                Query.limit(per_page),
                Query.offset(offset)
            ])
            
            # Format transactions for display
            for tx in paginated_transactions:
                customer_name = 'Unknown'
                customer_id = tx.get('customer_id')
                if customer_id:
                    try:
                        customer = appwrite_db.get_document('customers', customer_id)
                        customer_name = customer.get('name', 'Unknown')
                    except:
                        pass
                
                transactions.append({
                    'id': tx['$id'],
                    'amount': float(tx.get('amount', 0)),
                    'transaction_type': tx.get('transaction_type', ''),
                    'notes': tx.get('notes', ''),
                    'created_at': tx.get('created_at', ''),
                    'customer_name': customer_name,
                    'receipt_image_url': tx.get('receipt_image_url', '')
                })
            
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

@business_app.route('/view_bill/<transaction_id>')
@login_required
@business_required
def view_bill_image(transaction_id):
    """View bill/receipt image for a transaction"""
    try:
        business_id = safe_uuid(session.get('business_id'))
        transaction_id = safe_uuid(transaction_id)
        
        print(f"DEBUG: View bill request for transaction {transaction_id}")
        
        # Verify transaction belongs to the business and get details
        try:
            transaction = appwrite_db.get_document('transactions', transaction_id)
            
            # Verify it belongs to this business
            if transaction.get('business_id') != business_id:
                print(f"DEBUG: Transaction {transaction_id} doesn't belong to business {business_id}")
                flash('Transaction not found', 'error')
                return redirect(url_for('all_transactions'))
            
            # Get customer name
            customer_name = 'Unknown'
            customer_id = transaction.get('customer_id')
            if customer_id:
                try:
                    customer = appwrite_db.get_document('customers', customer_id)
                    customer_name = customer.get('name', 'Unknown')
                except:
                    pass
        
        except Exception as e:
            print(f"DEBUG: Transaction {transaction_id} not found: {str(e)}")
            flash('Transaction not found', 'error')
            return redirect(url_for('all_transactions'))
        
        print(f"DEBUG: Transaction found, has receipt_image_url: {bool(transaction.get('receipt_image_url'))}")
        
        transaction_data = {
            'id': transaction_id,
            'receipt_image_url': transaction.get('receipt_image_url', ''),
            'notes': transaction.get('notes', ''),
            'amount': float(transaction.get('amount', 0)),
            'transaction_type': transaction.get('transaction_type', ''),
            'created_at': transaction.get('created_at', ''),
            'customer_name': customer_name
        }
        
        print(f"DEBUG: Rendering view_bill template for transaction {transaction_id}")
        return render_template('business/view_bill.html', transaction=transaction_data)
        
    except Exception as e:
        flash(f'Error loading bill: {str(e)}', 'error')
        return redirect(url_for('all_transactions'))

@business_app.route('/sync_customer/<customer_id>')
@login_required
@business_required
def sync_customer_data(customer_id):
    """Manually sync customer transaction data"""
    business_id = safe_uuid(session.get('business_id'))
    customer_id = safe_uuid(customer_id)
    
    try:
        # Force refresh all transaction data for this customer using Appwrite
        transactions = appwrite_db.list_documents('transactions', [
            Query.equal('business_id', business_id),
            Query.equal('customer_id', customer_id),
            Query.order_desc('created_at')
        ])
        
        # Recalculate balance
        credit_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'credit'])
        payment_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'payment'])
        new_balance = credit_total - payment_total
        
        # Update the stored balance
        credit_records = appwrite_db.list_documents('customer_credits', [
            Query.equal('business_id', business_id),
            Query.equal('customer_id', customer_id),
            Query.limit(1)
        ])
        
        if credit_records:
            appwrite_db.update_document('customer_credits', credit_records[0]['$id'], {
                'current_balance': new_balance,
                'updated_at': datetime.now().isoformat()
            })
        
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
        business = appwrite_db.get_document('businesses', business_id)
        business_name = business.get('name', 'Business')
        
        # Get all customers with balances
        customers_to_remind = []
        
        # Get all customer credits for this business
        customer_credits = appwrite_db.list_documents('customer_credits', [
            Query.equal('business_id', business_id)
        ])
        
        for credit in customer_credits:
            try:
                customer_id = credit.get('customer_id')
                if not customer_id:
                    continue
                
                # Get customer details
                customer = appwrite_db.get_document('customers', customer_id)
                customer_name = customer.get('name', 'Customer')
                phone_number = customer.get('phone_number', '')
                
                if not phone_number:
                    continue  # Skip customers without phone numbers
                
                # Calculate balance from transactions
                transactions = appwrite_db.list_documents('transactions', [
                    Query.equal('business_id', business_id),
                    Query.equal('customer_id', customer_id)
                ])
                
                if not transactions:
                    continue  # Skip customers with no transactions
                
                credit_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'credit'])
                payment_total = sum([float(t.get('amount', 0)) for t in transactions if t.get('transaction_type') == 'payment'])
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
                print(f"Error processing customer {customer.get('name', 'Unknown')}: {str(e)}")
                continue
        
        return render_template('business/bulk_reminders.html', 
                             customers=customers_to_remind,
                             business=business)
            
    except Exception as e:
        print(f"Error generating bulk reminders: {str(e)}")
        flash('Error loading reminder page. Please try again.', 'error')
        return redirect(url_for('business_customers'))

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
