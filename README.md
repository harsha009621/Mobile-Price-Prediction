# Dynamic Price Prediction

This project is a Django-based web application for mobile price prediction. It includes:

- User registration and login
- Admin approval for users
- Model training using mobile dataset data
- Price prediction for smartphones
- SQLite database support

## Technologies Used

- Python
- Django
- SQLite
- Pandas
- NumPy
- scikit-learn
- XGBoost
- Joblib
- Google Generative AI (`google-generativeai`)
- HTML templates

## Software Required

Install the following software before running the project:

- Python 3.10 or later
- `pip` (comes with Python)
- A code editor such as VS Code
- A web browser such as Chrome or Edge

## Python Packages Required

Install these packages:

```bash
pip install django pandas numpy scikit-learn xgboost joblib google-generativeai
```

## Project Structure

- `manage.py` - Django project runner
- `Dynamic_Price_Prediction/` - Django project settings and URLs
- `users/` - user module, training logic, and prediction logic
- `admins/` - admin approval module
- `templates/` - HTML pages
- `media/mobiles_ (1).csv` - dataset used for training
- `db.sqlite3` - SQLite database
- `mobile_price_model.pkl` - trained model file

## How to Run the Project

### 1. Open terminal in the project folder

Make sure you are inside the project directory:

```bash
cd Dynamic_Price_Prediction
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install django pandas numpy scikit-learn xgboost joblib google-generativeai
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Run the server

```bash
python manage.py runserver
```

### 6. Open in browser

Visit:

```text
http://127.0.0.1:8000/
```

## Main Routes

- `/` - home page
- `/register/` - user registration
- `/login/` - user login
- `/admin_view` - custom admin login page
- `/admin_approval/` - user approval page
- `/training/` - train the ML model
- `/prediction/` - predict mobile price

## Default Admin Login

The custom admin page currently uses:

- Username: `admin`
- Password: `admin`

## Notes

- The project uses `db.sqlite3`, so no separate database server is needed.
- The dataset file `media/mobiles_ (1).csv` must remain available.
- XGBoost must be installed for model training to work.
- The prediction feature also uses Google Generative AI.
- The current code contains a hardcoded API key. For real use, replace it with your own API key and load it from an environment variable.

## Recommended Improvement

For easier setup, you can also create a `requirements.txt` file later with:

```bash
pip freeze > requirements.txt
```
