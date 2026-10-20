from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from flask import abort
from db_config import get_connection
import mysql.connector

app = Flask(__name__)
app.secret_key = 'InformationManagement'  # secret key

USERS = {
    'admin': {'password': 'adminpass', 'role': 'admin'},
    'visitor': {'password': 'visitorpass', 'role': 'visitor'},
}

def login_required(f):
    """Decorator to require login for certain routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You must be logged in to view that page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for certain routes."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = USERS.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            flash('Logged in successfully.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('index'))

@app.route('/')
def index():
    search_query = request.args.get('search_query', '')
    filter_status = request.args.get('filter_status', '')
    filter_role = request.args.get('filter_role', '')
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    valid_sort_columns = ['id', 'first_name', 'last_name', 'birthday', 'age', 'email', 'phone_number', 'role', 'status']
    valid_sort_order = ['asc', 'desc']

    if sort_by not in valid_sort_columns:
        sort_by = 'id'
    if sort_order.lower() not in valid_sort_order:
        sort_order = 'asc'

    conn = get_connection()
    records = []

    try:
        cursor = conn.cursor()
        base_sql = "SELECT id, first_name, last_name, birthday, age, email, phone_number, role, status FROM youthOfficials"
        where_clauses = []
        params = []

        if search_query:
            search_term = f"%{search_query}%"
            where_clauses.append("""(first_name LIKE %s OR 
                                     last_name LIKE %s OR 
                                     email LIKE %s OR 
                                     role LIKE %s)""")
            params.extend([search_term] * 4)

        if filter_status:
            where_clauses.append("status = %s")
            params.append(filter_status)

        if filter_role:
            where_clauses.append("role = %s")
            params.append(filter_role)

        if where_clauses:
            base_sql += " WHERE " + " AND ".join(where_clauses)

        base_sql += f" ORDER BY {sort_by} {sort_order.upper()}"

        cursor.execute(base_sql, tuple(params))
        records = cursor.fetchall()
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    return render_template('index.html', 
                           records=records,
                           search_query=search_query,
                           filter_status=filter_status,
                           filter_role=filter_role,
                           sort_by=sort_by,
                           sort_order=sort_order,
                           username=session.get('username'),
                           role=session.get('role'))

# Only admin can add officials
@app.route('/add', methods=['POST'])
@login_required
@admin_required
def add_student():
    # (Same as your current add_student code)
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    
    birthday_str = request.form.get('birthday')
    birthday = birthday_str if birthday_str else None

    age_str = request.form.get('age')
    age = int(age_str) if age_str and age_str.strip().isdigit() else None

    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    role = request.form.get('role')
    status_from_form = request.form.get('status')
    status_to_insert = 'Active' if not status_from_form or not status_from_form.strip() else status_from_form.strip()

    conn = get_connection()
    if not conn or not conn.is_connected():
        return "Error: Could not connect to the database for adding.", 500

    try:
        cursor = conn.cursor()
        sql = """INSERT INTO youthOfficials 
                 (first_name, last_name, birthday, age, email, phone_number, role, status) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (
            first_name, last_name, birthday, age,
            email if email else None,
            phone_number if phone_number else None,
            role if role else None,
            status_to_insert
        )
        cursor.execute(sql, values)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error adding student: {err}")
        conn.rollback()
        return f"Database error occurred: {err}", 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
    return redirect('/')

# Only admin can delete
@app.route('/delete/<int:id>')
@login_required
@admin_required
def delete_student(id):
    conn = get_connection()
    if not conn or not conn.is_connected():
        return "Error: Could not connect to the database for deletion.", 500
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM youthOfficials WHERE id=%s", (id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error deleting student: {err}")
        conn.rollback()
        return f"Database error occurred during deletion: {err}", 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
    return redirect('/')

# Only admin can edit
@app.route('/edit/<int:id>')
@login_required
@admin_required
def edit_student(id):
    conn = get_connection()
    if not conn or not conn.is_connected():
        return "Error: Could not connect to the database for editing.", 500

    student = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, birthday, age, email, phone_number, role, status FROM youthOfficials WHERE id=%s", (id,))
        student = cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error fetching student for edit: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

    if student is None:
        return "Official not found", 404
        
    return render_template('update.html', student=student)

# Only admin can update
@app.route('/update/<int:id>', methods=['POST'])
@login_required
@admin_required
def update_student(id):
    if session.get('role') != 'admin':
        abort(403)
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')

    birthday_str = request.form.get('birthday')
    birthday = birthday_str if birthday_str else None

    age_str = request.form.get('age')
    age = int(age_str) if age_str and age_str.strip().isdigit() else None
    
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    role = request.form.get('role')
    status = request.form.get('status')

    conn = get_connection()
    if not conn or not conn.is_connected():
        return "Error: Could not connect to the database for updating.", 500

    try:
        cursor = conn.cursor()
        sql = """UPDATE youthOfficials SET 
                 first_name=%s, last_name=%s, birthday=%s, age=%s, 
                 email=%s, phone_number=%s, role=%s, status=%s 
                 WHERE id=%s"""
        values = (
            first_name, last_name, birthday, age,
            email if email else None,
            phone_number if phone_number else None,
            role if role else None,
            status if status else None,
            id
        )
        cursor.execute(sql, values)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error updating student: {err}")
        conn.rollback()
        return f"Database error occurred during update: {err}", 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
    return redirect('/')

@app.route('/reset_ids', methods=['POST']) # Use POST for actions that modify data
@login_required
@admin_required
def reset_ids_route():
    if request.method == 'POST':
        conn = get_connection()
        if not conn or not conn.is_connected():
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500

        try:
            cursor = conn.cursor()
            # 1. Delete all records from the table
            cursor.execute("DELETE FROM youthOfficials;")
            # 2. Reset the AUTO_INCREMENT value
            cursor.execute("ALTER TABLE youthOfficials AUTO_INCREMENT = 1;")
            conn.commit()
            flash('All records deleted and IDs have been reset.', 'success')
            return jsonify({'status': 'success', 'message': 'IDs reset successfully. All records deleted.'})
        except mysql.connector.Error as err:
            print(f"Error resetting IDs: {err}")
            conn.rollback()
            flash(f'Error resetting IDs: {err}', 'danger')
            return jsonify({'status': 'error', 'message': str(err)}), 500
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    # Should not be reached via GET if only POST is allowed by decorator/route
    return jsonify({'status': 'error', 'message': 'Invalid request method.'}), 405

if __name__ == '__main__':
    app.run(debug=True)
