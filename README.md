# Inventory Tracking System

A complete web-based inventory management application built with Flask backend and vanilla JavaScript frontend. Track stock levels, manage categories, monitor transactions, and get real-time inventory insights.

## Features

✅ **User Authentication** - Secure registration and login with JWT tokens
✅ **Inventory Management** - Add, edit, delete, and search inventory items
✅ **Stock Tracking** - Add/remove stock with transaction history
✅ **Category Management** - Organize items by categories
✅ **Dashboard** - Real-time statistics and low stock alerts
✅ **Transaction History** - Complete audit trail of all inventory movements
✅ **Responsive Design** - Works on desktop and mobile devices
✅ **RESTful API** - Complete API documentation

## Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - JWT authentication
- **SQLite** - Database (easily scalable to PostgreSQL)

### Frontend
- **Vanilla JavaScript** - No dependencies
- **HTML5**
- **CSS3** - Modern styling
- **Responsive Design**

## Project Structure

```
inventory-tracker/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── index.html            # Frontend HTML
├── app.js                # Frontend JavaScript
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/inventory-tracker.git
cd inventory-tracker
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create environment file**
```bash
cp .env.example .env
```

Edit `.env` and change the `JWT_SECRET_KEY` to a secure random string:
```bash
# Generate a secure key (in Python)
python -c "import secrets; print(secrets.token_hex(32))"
```

5. **Run the Flask app**
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

The frontend is a static HTML/JS application. Simply open `index.html` in your browser or serve it with a simple HTTP server:

```bash
# Using Python 3
python -m http.server 8000

# Using Node.js (if you have http-server installed)
http-server

# Using Live Server (VS Code extension)
# Just right-click and "Open with Live Server"
```

The frontend will be available at `http://localhost:8000`

## API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "message": "User registered successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "is_admin": false,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

#### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "password123"
}
```

### Category Endpoints

#### Get All Categories
```http
GET /api/categories
Authorization: Bearer {access_token}
```

#### Create Category
```http
POST /api/categories
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Electronics",
  "description": "Electronic devices and components"
}
```

#### Update Category
```http
PUT /api/categories/{category_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

#### Delete Category
```http
DELETE /api/categories/{category_id}
Authorization: Bearer {access_token}
```

### Inventory Endpoints

#### Get All Items
```http
GET /api/inventory
Authorization: Bearer {access_token}

# Query parameters:
# ?category_id=1        - Filter by category
# ?search=phone         - Search by name or SKU
# ?low_stock=true       - Show only low stock items
```

#### Create Item
```http
POST /api/inventory
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Laptop",
  "sku": "LAP-001",
  "category_id": 1,
  "unit_price": 999.99,
  "quantity": 10,
  "reorder_level": 5,
  "description": "Dell XPS Laptop"
}
```

#### Get Item Details
```http
GET /api/inventory/{item_id}
Authorization: Bearer {access_token}
```

#### Update Item
```http
PUT /api/inventory/{item_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Updated Name",
  "unit_price": 1099.99,
  "reorder_level": 3
}
```

#### Delete Item
```http
DELETE /api/inventory/{item_id}
Authorization: Bearer {access_token}
```

#### Add Stock
```http
POST /api/inventory/{item_id}/add
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "quantity": 50,
  "reason": "New shipment received"
}
```

#### Remove Stock
```http
POST /api/inventory/{item_id}/remove
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "quantity": 5,
  "reason": "Sold to customer"
}
```

### Transaction Endpoints

#### Get All Transactions
```http
GET /api/transactions
Authorization: Bearer {access_token}

# Query parameters:
# ?item_id=1            - Filter by item
# ?type=add             - Filter by type (add, remove, adjustment)
```

### Dashboard Endpoints

#### Get Dashboard Stats
```http
GET /api/dashboard/stats
Authorization: Bearer {access_token}
```

Response:
```json
{
  "total_items": 25,
  "total_value": 15000.50,
  "low_stock_count": 3,
  "low_stock_items": [
    {
      "id": 1,
      "name": "Item Name",
      "quantity": 2,
      "reorder_level": 10
    }
  ]
}
```

#### Get Category Breakdown
```http
GET /api/dashboard/category-breakdown
Authorization: Bearer {access_token}
```

## Usage Guide

### Login/Register
1. Open the application in your browser
2. Create a new account or log in with existing credentials
3. You'll be taken to the dashboard

### Dashboard
- View total inventory value
- See number of items
- Check items that need reordering
- Quick access to low stock items

### Managing Inventory
1. Go to **Inventory Items** page
2. Click **+ Add Item** to create a new item
3. Fill in the required fields (Name, SKU, Category, Price)
4. Use + / - buttons to add/remove stock
5. Search or filter items as needed

### Managing Categories
1. Go to **Categories** page
2. Click **+ Add Category** to create a new category
3. Edit or delete existing categories
4. Use categories to organize your inventory

### Viewing Transactions
1. Go to **Transactions** page
2. View complete history of all stock movements
3. Filter by transaction type
4. See who made each change and when

## Deployment

### Deploy to Heroku

1. **Create Heroku account** and install Heroku CLI

2. **Create Procfile**
```
web: gunicorn app:app
```

3. **Update requirements.txt** to include gunicorn
```bash
pip install gunicorn
pip freeze > requirements.txt
```

4. **Deploy**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Deploy Frontend to GitHub Pages

1. Create a `docs` folder in your repository
2. Copy `index.html` and `app.js` to the `docs` folder
3. Update `API_URL` in `app.js` to point to your deployed backend
4. Enable GitHub Pages in repository settings (Source: `docs` folder)

### Using PostgreSQL (Production)

1. Install PostgreSQL
2. Update `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/inventory_db
```

3. Update `requirements.txt`:
```
psycopg2-binary==2.9.9
```

4. Run migrations if needed

## Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
# Flask
FLASK_ENV=production
FLASK_DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@host/dbname

# Security
JWT_SECRET_KEY=your-super-secret-key-here-change-in-production

# CORS
CORS_ORIGINS=https://yourdomain.com
```

## Database Schema

### Users Table
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- password (Hashed)
- is_admin (Boolean)
- created_at (DateTime)
```

### Categories Table
```sql
- id (Primary Key)
- name (Unique)
- description
- created_at (DateTime)
```

### Inventory Items Table
```sql
- id (Primary Key)
- name
- sku (Unique)
- description
- quantity
- reorder_level
- unit_price
- category_id (Foreign Key)
- user_id (Foreign Key)
- created_at (DateTime)
- updated_at (DateTime)
```

### Transactions Table
```sql
- id (Primary Key)
- item_id (Foreign Key)
- user_id (Foreign Key)
- transaction_type (add, remove, adjustment)
- quantity_changed
- reason
- created_at (DateTime)
```

## Troubleshooting

### CORS Error
Make sure the backend is running on `http://localhost:5000` and the frontend is accessing it correctly. The Flask app has CORS enabled for all origins in development.

### Database Errors
Delete `inventory.db` and restart the app to reinitialize the database.

### JWT Token Errors
Make sure you're sending the `Authorization: Bearer {token}` header with all API requests that require authentication.

### Port Already in Use
If port 5000 is already in use, modify the last line in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## Future Enhancements

- [ ] Barcode scanning
- [ ] CSV import/export
- [ ] Email notifications for low stock
- [ ] Multi-warehouse support
- [ ] Advanced reporting and analytics
- [ ] Mobile app
- [ ] API rate limiting
- [ ] Scheduled backups
- [ ] Two-factor authentication
- [ ] Role-based access control

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Open an issue on GitHub
3. Contact the maintainer

## Author

Created with ❤️ for inventory management

---

**Happy Tracking!** 📦
