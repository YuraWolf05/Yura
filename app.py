from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from email_validator import validate_email, EmailNotValidError
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import random
import string
import os

# Ініціалізація додатка
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Замініть на більш надійний ключ у реальному проекті
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///example.db"
app.config['UPLOAD_FOLDER'] = 'my-app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ініціалізація бібліотек
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Функція перевірки дозволених форматів файлів
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Функція для генерації промокодів
def generate_promo_code():
    while True:
        promo_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        
        # Перевіряємо, чи код існує в базі
        existing_code = Order.query.filter_by(promo_code=promo_code).first()
        if not existing_code:
            return promo_code

# Завантаження користувача для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Product {self.name} - {self.price}>"

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Связь с моделью Product
    product = db.relationship('Product', backref='cart_items')

    def __repr__(self):
        return f"<Cart user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity}>"



# Модель користувача
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    number = db.Column(db.String(15), nullable=True)
    profile_image = db.Column(db.String(120), nullable=True, default='uploads/default.jpg')

    def __repr__(self):
        return f"<User {self.name}>"

# Модель замовлення
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    promo_code = db.Column(db.String(10), nullable=True)

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

# Реєстрація
@app.route("/registration", methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(name=form.username.data).first()
        if existing_user:
            flash('Це імʼя вже зайняте.', 'danger')
            return redirect(url_for('registration'))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.username.data, email=form.email.data, password=hashed_password, number=form.number.data)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Ваш акаунт успішно створено!', 'success')
        return redirect(url_for('profile'))
    return render_template('registration.html', form=form)

# Профіль
@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_email = request.form.get('email')
        new_password = request.form.get('password')
        new_number = request.form.get('number')

        if new_name and new_name != current_user.name:
            if User.query.filter_by(name=new_name).first():
                flash('Це імʼя вже зайняте.', 'danger')
                return redirect(url_for('profile'))
            current_user.name = new_name

        if new_email and new_email != current_user.email:
            try:
                validate_email(new_email)
                current_user.email = new_email
            except EmailNotValidError as e:
                flash(str(e), 'danger')
                return redirect(url_for('profile'))

        if new_password:
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        if new_number:
            current_user.number = new_number

        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_image = f'uploads/{filename}'

        db.session.commit()
        flash('Профіль оновлено!', 'success')
        return redirect(url_for('profile'))

    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template("profile.html", user=current_user, orders=orders)

# Кошик
@app.route('/cart', methods=['GET'])
@login_required
def get_cart():
    user_id = current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    cart_data = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            cart_data.append({
                'product_id': item.product_id,
                'quantity': item.quantity,
                'product_name': product.name,
                'price': product.price
            })
        else:
            cart_data.append({
                'product_id': item.product_id,
                'quantity': item.quantity,
                'product_name': "Продукт не знайдено",
                'price': 0
            })

    # Перевіряємо, чи клієнт хоче JSON
    if request.headers.get('Accept') == 'application/json':
        return jsonify(cart_data)

    # Для запиту HTML сторінки
    return render_template('cart.html', user=current_user, cart_data=cart_data)

# Оформлення замовлення
@app.route("/checkout", methods=['POST'])
@login_required
def checkout():
    cart = request.json.get('cart', {})
    promo_code = generate_promo_code()

    for item_id, item in cart.items():
        order = Order(
            user_id=current_user.id,
            product_name=item['name'],
            quantity=item['quantity'],
            total_price=item['quantity'] * float(item['price']),
            promo_code=promo_code
        )
        db.session.add(order)

    db.session.commit()
    return jsonify({'success': True, 'promo_code': promo_code})

#Коли користувач додає товари в кошик, зберігайте ці дані в базі, а не в localStorage
@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    user_id = current_user.id
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)

    # Перевірка коректності даних
    if not product_id or not isinstance(quantity, int) or quantity < 1:
        return jsonify({'success': False, 'message': 'Некоректні дані'}), 400

    # Перевірка існування продукту
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Продукт не знайдено'}), 404

    # Оновлення або створення запису в кошику
    cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        new_cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_cart_item)

    db.session.commit()
    return jsonify({'success': True, 'message': 'Товар додано до кошика'})


#Додавання товару в SQL базу, включати коли додаєш.
#@app.route('/product/add', methods=['POST'])
#@login_required
#def add_product():
    # Отримання даних із запиту
    product_name = request.json.get('name')
    product_price = request.json.get('price')

    # Перевірка коректності даних
    if not product_name or not isinstance(product_price, (int, float)) or product_price <= 0:
        return jsonify({'success': False, 'message': 'Некоректні дані'}), 400

    # Створення нового продукту
    new_product = Product(name=product_name, price=product_price)
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Товар успішно додано', 'product_id': new_product.id})

# Вхід
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Вхід успішний!', 'success')
            return redirect(url_for('profile'))
        flash('Невірний логін або пароль.', 'danger')
    return render_template('login.html', form=form)

# Вихід
@app.route("/logout")
def logout():
    logout_user()
    flash("Ви вийшли з акаунта.", 'info')
    return redirect(url_for('home'))

# Головна сторінка
@app.route("/")
def home():
    return render_template("index.html", user=current_user if current_user.is_authenticated else None)

# Donate
@app.route("/donate")
def donate():
    return render_template("donate.html", user=current_user if current_user.is_authenticated else None)

# Запуск додатка
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

# запуск фласка .\flask\Scripts\activate 

#запуска сайта python C:\Web\my-app\app.py









#from flask import Flask, render_template
#from flask_sqlalchemy import SQLAlchemy

# Створення екземпляра додатка Flask і конфігурація бази даних
#app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///example.db"
#db = SQLAlchemy(app)

# Визначення моделі User
#class User(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    #name = db.Column(db.String(80), unique=True, nullable=False)

   # def __repr__(self):
       # return f"<User {self.name}>"

# Створення таблиць у базі даних
#with app.app_context():
    #db.create_all()

# Маршрут для головної сторінки
#@app.route("/")
#def home():
   # return render_template("index.html")

#@app.route("/exit")
##def exit():
   # return render_template("exit.html")

#@app.route("/registration")
#def registration():
   # return render_template("registration.html")

# Запуск додатка
#if __name__ == "__main__":
    # Робимо додаток доступним за межами localhost
   # app.run(debug=True, host="0.0.0.0", port=5000)
#app.run(host='0.0.0.0', port=5000)
 #httpd -k restart
 #https://www.youtube.com/watch?v=a5UMDy0EeUU

#python C:\Web\my-app\app.py

