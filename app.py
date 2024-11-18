from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from email_validator import validate_email, EmailNotValidError

# Ініціалізація додатка
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Обов'язково змініть на більш надійний ключ у реальному проекті
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///example.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Функція завантаження користувача
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from datetime import datetime

# Модель користувача
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    number = db.Column(db.String(15), nullable=True)  

    def __repr__(self):
        return f"<User {self.name}>"

# Ініціалізація бази даних
with app.app_context():
    db.create_all()

# Форма реєстрації
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    number = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
    submit = SubmitField('Sign Up')

# Форма входу
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Маршрут для реєстрації
@app.route("/registration", methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Перевірка наявності імені користувача
            existing_user = User.query.filter_by(name=form.username.data).first()
            if existing_user:
                flash('Username already exists. Please choose another one.', 'danger')
                return redirect(url_for('registration'))
            
            # Перевірка наявності email
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash('Email already registered. Please use another one.', 'danger')
                return redirect(url_for('registration'))
            
            # Створення нового користувача
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(name=form.username.data, email=form.email.data, password=hashed_password, number=form.number.data)
            db.session.add(user)
            db.session.commit()

            # Автоматичний вхід
            login_user(user)
            flash('Account created and you are now logged in!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            flash(f'An error occurred during registration: {str(e)}', 'danger')
            return redirect(url_for('registration'))
    else:
        # Якщо форма не пройшла валідацію
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    
    return render_template('registration.html', form=form)

# Маршрут для профілю
@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_email = request.form.get('email')
        new_password = request.form.get('password')
        new_number = request.form.get('number')

        # Перевірка унікальності імені користувача
        if new_name and new_name != current_user.name:
            existing_user = User.query.filter_by(name=new_name).first()
            if existing_user:
                flash('Username already exists. Please choose another one.', 'danger')
                return redirect(url_for('profile'))
            current_user.name = new_name
        
        # Перевірка унікальності email
        if new_email and new_email != current_user.email:
            existing_email = User.query.filter_by(email=new_email).first()
            if existing_email:
                flash('Email already registered. Please use another one.', 'danger')
                return redirect(url_for('profile'))
            
            try:
                # Перевірка коректності email
                valid = validate_email(new_email)
                new_email = valid.email  # нормалізована (стандартизована) адреса
                current_user.email = new_email
            except EmailNotValidError as e:
                flash(str(e), 'danger')
                return redirect(url_for('profile'))
        
        # Оновлення пароля
        if new_password:
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        # Оновлення номера телефону
        if new_number:
            current_user.number = new_number
        
        db.session.commit()
        flash('Profile information updated!', 'success')
        return redirect(url_for('profile'))

    return render_template("profile.html", user=current_user)

# Ініціалізація бази даних при першому запуску
with app.app_context():
    db.create_all()

# Маршрут для входу
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Login unsuccessful. Please check username and password', 'danger')
    else:
        # Повідомлення про помилки валідації форми під час входу
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')
    
    return render_template('login.html', form=form)

# Маршрут для виходу
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# Головна сторінка
@app.route("/")
def home():
    return render_template("index.html")

# Запуск додатка
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
