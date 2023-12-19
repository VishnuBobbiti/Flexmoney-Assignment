from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False, unique=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    preferred_batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    payments = db.relationship('Payment', backref='user', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

    # Add batches to the Batch table only if they don't exist
    batch_names = ['6-7AM', '7-8AM', '8-9AM', '5-6PM']
    for name in batch_names:
        existing_batch = Batch.query.filter_by(name=name).first()
        if not existing_batch:
            batch = Batch(name=name)
            db.session.add(batch)

    db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')  # Assuming your HTML file is named index.html

def has_submitted_form_this_month(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return False

    current_month_submissions = Payment.query.filter_by(user=user).filter(
        Payment.created_at >= datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        Payment.created_at <= datetime.now().replace(day=1, month=datetime.now().month + 1, hour=0, minute=0, second=0,
                                                     microsecond=0) - timedelta(microseconds=1)
    ).all()

    return bool(current_month_submissions)

def calculate_monthly_fee():
    # Assuming the monthly fee is 500 INR
    return 500


@app.route('/process_payment', methods=['POST'])
def process_payment():
    try:
        data = request.get_json()

        # Validate age
        age = data.get('age', 0)
        if not (18 <= age <= 65):
            raise ValueError('Invalid age')

        # Validate preferred batch
        preferred_batch = data.get('preferred_batch', '')
        valid_batches = ['6-7AM', '7-8AM', '8-9AM', '5-6PM']
        if preferred_batch not in valid_batches:
            raise ValueError('Invalid preferred batch. Choose from: 6-7AM, 7-8AM, 8-9AM, 5-6PM')

        # Other validations...

        username = data['username']

        # Check if the user has already submitted the form this month
        if has_submitted_form_this_month(username):
            return jsonify({'error': 'You have already enrolled for this month.'}), 400

        # Calculate monthly fee
        amount = calculate_monthly_fee()

        # Other payment processing logic...

        return jsonify({'message': 'Payment processed successfully', 'status': 'Success'})

    except ValueError as ve:
        app.logger.warning(f'Bad Request: {str(ve)}')
        return jsonify({'error': str(ve)}), 400

    except Exception as e:
        app.logger.error(f'Internal Server Error: {str(e)}')
        return jsonify({'error': str(e)}), 500

def has_completed_payment_this_month(user):
    # Check if the user has completed a payment this month
    current_month_payments = Payment.query.filter_by(user=user).filter(
        Payment.status == 'Success',
        Payment.created_at >= datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        Payment.created_at <= datetime.now().replace(day=1, month=datetime.now().month + 1, hour=0, minute=0, second=0,
                                                     microsecond=0) - timedelta(microseconds=1)
    ).all()

    return bool(current_month_payments)

def is_valid_email(email):
    # Basic email validation
    return '@' in email and '.' in email.split('@')[1]

# Mock function, replace with actual implementation
def complete_payment(user, payment):
    # Perform actual payment processing here
    # This is just a placeholder, you should replace it with the logic for your payment gateway
    return 'Success'

@app.route('/get_users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{'username': user.username, 'email': user.email} for user in users]
    return jsonify({'users': user_list})

@app.route('/user_payment_details/<username>', methods=['GET'])

def user_payment_details(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    payments = Payment.query.filter_by(user=user).all()

    payment_details = []
    for payment in payments:
        payment_details.append({
            'amount': payment.amount,
            'status': payment.status,
            'created_at': payment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({'username': user.username, 'payment_details': payment_details})

if __name__ == '__main__':
    with app.app_context():
        # Drop the batch table and recreate it
        db.drop_all()
        db.create_all()

        # Add batches to the Batch table
        batch_names = ['6-7AM', '7-8AM', '8-9AM', '5-6PM']
        for name in batch_names:
            batch = Batch(name=name)
            db.session.add(batch)

        db.session.commit()

    app.run(debug=True)