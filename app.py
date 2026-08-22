from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)
jwt = JWTManager(app)

# ==================== Database Models ====================

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    inventory_items = db.relationship('InventoryItem', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('InventoryItem', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }


class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=10)
    unit_price = db.Column(db.Float, default=0.0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    transactions = db.relationship('Transaction', backref='item', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'description': self.description,
            'quantity': self.quantity,
            'reorder_level': self.reorder_level,
            'unit_price': self.unit_price,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'total_value': self.quantity * self.unit_price,
            'needs_reorder': self.quantity <= self.reorder_level,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'add', 'remove', 'adjustment'
    quantity_changed = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_name': self.item.name if self.item else None,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'transaction_type': self.transaction_type,
            'quantity_changed': self.quantity_changed,
            'reason': self.reason,
            'created_at': self.created_at.isoformat()
        }


# ==================== Authentication Routes ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


# ==================== Category Routes ====================

@app.route('/api/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get all categories"""
    categories = Category.query.all()
    return jsonify([cat.to_dict() for cat in categories]), 200


@app.route('/api/categories', methods=['POST'])
@jwt_required()
def create_category():
    """Create a new category"""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Category name is required'}), 400
    
    if Category.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Category already exists'}), 400
    
    category = Category(
        name=data['name'],
        description=data.get('description', '')
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'message': 'Category created successfully',
        'category': category.to_dict()
    }), 201


@app.route('/api/categories/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """Update a category"""
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Category updated successfully',
        'category': category.to_dict()
    }), 200


@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """Delete a category"""
    category = Category.query.get(category_id)
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Category deleted successfully'}), 200


# ==================== Inventory Routes ====================

@app.route('/api/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    """Get all inventory items for current user"""
    user_id = get_jwt_identity()
    
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '')
    low_stock = request.args.get('low_stock', 'false').lower() == 'true'
    
    query = InventoryItem.query.filter_by(user_id=user_id)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(
            db.or_(
                InventoryItem.name.ilike(f'%{search}%'),
                InventoryItem.sku.ilike(f'%{search}%')
            )
        )
    
    if low_stock:
        query = query.filter(InventoryItem.quantity <= InventoryItem.reorder_level)
    
    items = query.all()
    
    return jsonify([item.to_dict() for item in items]), 200


@app.route('/api/inventory', methods=['POST'])
@jwt_required()
def create_inventory_item():
    """Create a new inventory item"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required_fields = ['name', 'sku', 'category_id', 'unit_price']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
    
    if InventoryItem.query.filter_by(sku=data['sku']).first():
        return jsonify({'error': 'SKU already exists'}), 400
    
    item = InventoryItem(
        name=data['name'],
        sku=data['sku'],
        description=data.get('description', ''),
        quantity=data.get('quantity', 0),
        reorder_level=data.get('reorder_level', 10),
        unit_price=data['unit_price'],
        category_id=data['category_id'],
        user_id=user_id
    )
    
    db.session.add(item)
    db.session.commit()
    
    # Create initial transaction if quantity > 0
    if item.quantity > 0:
        transaction = Transaction(
            item_id=item.id,
            user_id=user_id,
            transaction_type='add',
            quantity_changed=item.quantity,
            reason='Initial stock'
        )
        db.session.add(transaction)
        db.session.commit()
    
    return jsonify({
        'message': 'Inventory item created successfully',
        'item': item.to_dict()
    }), 201


@app.route('/api/inventory/<int:item_id>', methods=['GET'])
@jwt_required()
def get_inventory_item(item_id):
    """Get a specific inventory item"""
    user_id = get_jwt_identity()
    item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify(item.to_dict()), 200


@app.route('/api/inventory/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_inventory_item(item_id):
    """Update an inventory item"""
    user_id = get_jwt_identity()
    item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        item.name = data['name']
    if 'description' in data:
        item.description = data['description']
    if 'reorder_level' in data:
        item.reorder_level = data['reorder_level']
    if 'unit_price' in data:
        item.unit_price = data['unit_price']
    if 'category_id' in data:
        item.category_id = data['category_id']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Item updated successfully',
        'item': item.to_dict()
    }), 200


@app.route('/api/inventory/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_inventory_item(item_id):
    """Delete an inventory item"""
    user_id = get_jwt_identity()
    item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'message': 'Item deleted successfully'}), 200


# ==================== Transaction Routes ====================

@app.route('/api/inventory/<int:item_id>/add', methods=['POST'])
@jwt_required()
def add_stock(item_id):
    """Add stock to an inventory item"""
    user_id = get_jwt_identity()
    item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('quantity'):
        return jsonify({'error': 'Quantity is required'}), 400
    
    quantity = int(data['quantity'])
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be positive'}), 400
    
    item.quantity += quantity
    
    transaction = Transaction(
        item_id=item.id,
        user_id=user_id,
        transaction_type='add',
        quantity_changed=quantity,
        reason=data.get('reason', 'Stock addition')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Stock added successfully',
        'item': item.to_dict(),
        'transaction': transaction.to_dict()
    }), 200


@app.route('/api/inventory/<int:item_id>/remove', methods=['POST'])
@jwt_required()
def remove_stock(item_id):
    """Remove stock from an inventory item"""
    user_id = get_jwt_identity()
    item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('quantity'):
        return jsonify({'error': 'Quantity is required'}), 400
    
    quantity = int(data['quantity'])
    if quantity <= 0:
        return jsonify({'error': 'Quantity must be positive'}), 400
    
    if item.quantity < quantity:
        return jsonify({'error': 'Insufficient stock'}), 400
    
    item.quantity -= quantity
    
    transaction = Transaction(
        item_id=item.id,
        user_id=user_id,
        transaction_type='remove',
        quantity_changed=quantity,
        reason=data.get('reason', 'Stock removal')
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Stock removed successfully',
        'item': item.to_dict(),
        'transaction': transaction.to_dict()
    }), 200


@app.route('/api/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get all transactions for current user"""
    user_id = get_jwt_identity()
    
    item_id = request.args.get('item_id', type=int)
    transaction_type = request.args.get('type', '')
    
    query = Transaction.query.filter_by(user_id=user_id)
    
    if item_id:
        query = query.filter_by(item_id=item_id)
    
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    transactions = query.order_by(Transaction.created_at.desc()).all()
    
    return jsonify([trans.to_dict() for trans in transactions]), 200


# ==================== Dashboard Routes ====================

@app.route('/api/dashboard/stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get dashboard statistics"""
    user_id = get_jwt_identity()
    
    items = InventoryItem.query.filter_by(user_id=user_id).all()
    low_stock_items = [item for item in items if item.quantity <= item.reorder_level]
    
    total_value = sum(item.quantity * item.unit_price for item in items)
    
    return jsonify({
        'total_items': len(items),
        'total_value': total_value,
        'low_stock_count': len(low_stock_items),
        'low_stock_items': [item.to_dict() for item in low_stock_items]
    }), 200


@app.route('/api/dashboard/category-breakdown', methods=['GET'])
@jwt_required()
def get_category_breakdown():
    """Get inventory breakdown by category"""
    user_id = get_jwt_identity()
    
    categories = Category.query.all()
    breakdown = []
    
    for category in categories:
        items = InventoryItem.query.filter_by(category_id=category.id, user_id=user_id).all()
        if items:
            breakdown.append({
                'category': category.name,
                'item_count': len(items),
                'total_quantity': sum(item.quantity for item in items),
                'total_value': sum(item.quantity * item.unit_price for item in items)
            })
    
    return jsonify(breakdown), 200


# ==================== Health Check ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
