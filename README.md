# 📊 KhataSystem

KhataSystem is a **desktop-based shop management system** built using **Python, Tkinter, and MySQL**. It provides a simple yet powerful graphical interface for managing daily shop operations such as customers, products, sales, and reports.

The system follows a **modular architecture**, separating UI, business logic, and database operations for better maintainability and scalability.

---

# 🚀 Features

- 🔐 Secure admin authentication system  
- 👤 Customer management (add, update, delete, view)  
- 📦 Product inventory management  
- 💰 Sales transaction recording  
- 📊 Reports generation  
- 🗄️ MySQL database integration  
- 🖥️ Tkinter-based desktop GUI  

---

# 🏗️ Architecture

KhataSystem is designed using a **layered modular structure**:

- **UI Layer (Tkinter):** Handles all user interaction  
- **Logic Layer (Python modules):** Business operations  
- **Database Layer (`db.py`):** MySQL communication layer  

This separation ensures clean code organization and easy scalability.

---

# 📁 Project Structure

```
KhataSystem/
│
├── main.py              # Entry point
├── login.py            # Authentication system
├── dashboard.py        # Main dashboard UI
│
├── customers.py        # Customer management
├── products.py         # Product management
├── sales.py            # Sales module
├── reports.py          # Reports module
│
├── db.py               # Database handler
├── seed_admin.py       # Creates admin user
├── requirements.txt    # Dependencies
│
├── database/           # SQL schema files
└── __pycache__/        # Cache files
```

---

# ⚙️ Tech Stack

| Technology | Purpose |
|------------|--------|
| Python     | Core logic |
| Tkinter    | GUI framework |
| MySQL      | Database |

---

# 📦 Installation

## 1. Clone Repository
```
git clone https://github.com/Shahzeb121-oss/KhataSystem.git
cd KhataSystem
```

## 2. Install Dependencies
```
pip install -r requirements.txt
```

---

# 🗄️ Database Setup

## Create Database
```sql
CREATE DATABASE shop_khata;
```

## Import Schema
Import SQL files from the `database/` folder into MySQL.

---

# 🔐 Configuration

Update MySQL credentials in `db.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD",
    "database": "shop_khata"
}
```

---

# 👤 Admin Setup

Run the admin seed script:

```
python seed_admin.py
```

This creates the default admin account.

---

# ▶️ Run Application

```
python main.py
```

---

# 🧠 How It Works

1. User starts app via `main.py`
2. Login handled in `login.py`
3. Dashboard loads after authentication
4. Modules interact with `db.py`
5. MySQL stores and retrieves data
6. Results displayed in GUI

---

# ⚠️ Common Issues

## MySQL Error
- Ensure MySQL is running
- Check credentials in `db.py`
- Confirm database exists

## Login Issue
```
python seed_admin.py
```

---

# 📌 Design Highlights

- Modular architecture
- Centralized database handling
- Clear separation of concerns
- Easy to extend and maintain

---

# 📄 License

This project is for **educational purposes only**.

