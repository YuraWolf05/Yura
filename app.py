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
from flask_compress import Compress # оптимізацію на смартофон
import random
import string
import os
import json

# Ініціалізація додатка
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'your_secret_key'  # Замініть на більш надійний ключ у реальному проекті
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///example.db"
app.config['UPLOAD_FOLDER'] = '/var/www/apexia/my-app/static/uploads'  #Linux host
#app.config['UPLOAD_FOLDER'] = "C:/Web/my-app/static/uploads"            #local Windows
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
Compress(app)

# Ініціалізація бібліотек
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# Функція перевірки дозволених форматів файлів
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

INFO_DIR = "/var/www/apexia/InfoList/"  # Папка, де лежать файли з промокодами Linux host
#INFO_DIR = "C:\Web\InfoList"  # Папка, де лежать файли з промокодами local Windows

def load_promo_codes(product_name):
    """ Завантажуємо промокоди для конкретного продукту """
    file_path = os.path.join(INFO_DIR, f"{product_name}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

def save_promo_codes(product_name, promo_codes):
    """ Зберігаємо оновлений список промокодів """
    file_path = os.path.join(INFO_DIR, f"{product_name}.json")
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(promo_codes, file, indent=4, ensure_ascii=False)

def get_unused_promo(product_name):
    """ Отримує перший доступний невикористаний промокод """
    promo_codes = load_promo_codes(product_name)
    for promo in promo_codes:
        if not promo["used"]:
            promo["used"] = True  # Позначаємо як використаний
            save_promo_codes(product_name, promo_codes)
            return promo["code"]
    return None  # Якщо всі коди використані

@app.route("/promo_stock", methods=['GET'])
def promo_stock():
    product_name = request.args.get("product")  # Отримуємо назву товару
    if not product_name:
        return jsonify({"success": False, "message": "Не вказано товар"}), 400

    promo_codes = load_promo_codes(product_name)
    remaining_codes = sum(1 for p in promo_codes if not p["used"])

    return jsonify({"success": True, "product": product_name, "remaining": remaining_codes})


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
    profile_image = db.Column(db.String(120), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)  # Додаємо атрибут is_admin
    is_banned = db.Column(db.Boolean, default=False)  # 📌 Додали поле бану

    def __repr__(self):
        return f"<User {self.name}>"
    def __repr__(self):
        return f"<User {self.name}, Admin={self.is_admin}>"
    @property
    def profile_image_url(self):
        """Якщо фото профілю немає, повертаємо default.png"""
        if self.profile_image:
            return f'static/{self.profile_image}'
        return 'static/uploads/default.png'  # Шлях до дефолтного фото

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
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=7, max=30)])
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
        # Перевіряємо, чи ім'я, email або номер вже зайняті
        existing_user = User.query.filter_by(name=form.username.data).first()
        if existing_user:
            flash('Це імʼя вже зайняте.', 'danger')
            return redirect(url_for('registration'))

        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email:
            flash('Цей email вже зайнятий.', 'danger')
            return redirect(url_for('registration'))

        existing_number = User.query.filter_by(number=form.number.data).first()
        if existing_number:
            flash('Цей номер вже зайнятий.', 'danger')
            return redirect(url_for('registration'))

        # Хешуємо пароль перед збереженням
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Додаємо нового користувача
        user = User(
            name=form.username.data, 
            email=form.email.data, 
            password=hashed_password, 
            number=form.number.data
        )
        
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Помилка реєстрації. Спробуйте ще раз.", "danger")
            return redirect(url_for('registration'))

        # Автоматично авторизуємо нового користувача
        login_user(user)
        flash('Ваш акаунт успішно створено!', 'success')
        return redirect(url_for('profile'))

    return render_template('registration.html', form=form)


@app.route("/profile", methods=['GET', 'POST']) 
@login_required
def profile():
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_email = request.form.get('email')
        new_password = request.form.get('password')
        new_number = request.form.get('number')
        
        user = current_user

        if new_name and new_name != user.name:
            if User.query.filter_by(name=new_name).first():
                flash('Це імʼя вже зайняте.', 'danger')
                return redirect(url_for('profile'))
            user.name = new_name

        if new_email and new_email != user.email:
            try:
                validate_email(new_email)
                user.email = new_email
            except EmailNotValidError as e:
                flash(str(e), 'danger')
                return redirect(url_for('profile'))

        if new_password:
            user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        if new_number:
            user.number = new_number

        # Обробка завантаження фото
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_image = f'uploads/{filename}'

        db.session.commit()
        flash('Профіль оновлено!', 'success')
        return redirect(url_for('profile'))

    
    # Додаємо всі заявки користувача
    receipt_requests = ReceiptRequest.query.filter_by(user_id=current_user.id).all()
    orders = Order.query.filter_by(user_id=current_user.id).all()
    orders = db.session.query(ReceiptRequest).filter_by(user_id=current_user.id).all()
    return render_template("profile.html", user=current_user, orders=orders, receipt_requests=receipt_requests)
   
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
    response_data = {"success": True, "promo_codes": []}

    for item_id, item in cart.items():
        product_name = item["name"]
        promo_code = get_unused_promo(product_name)

        if promo_code:
            response_data["promo_codes"].append({
                "product": product_name,
                "promo_code": promo_code
            })
        else:
            response_data["success"] = False
            response_data["promo_codes"].append({
                "product": product_name,
                "message": "Немає доступних промокодів"
            })

    return jsonify(response_data)


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


# Глобальна змінна для контролю режиму додавання  SQL базу
add_product_mode = {}

@app.route('/admin/activate_add_mode', methods=['POST'])
@login_required
def activate_add_mode():
    if current_user.is_admin:
        add_product_mode[current_user.id] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Недостатньо прав'}), 403


@app.route('/product/add', methods=['POST'])
@login_required
def add_product():
    if not current_user.is_admin or not add_product_mode.get(current_user.id):
        return jsonify({'success': False,}),

    product_name = request.json.get('name')
    product_price = request.json.get('price')

    if not product_name or not isinstance(product_price, (int, float)) or product_price <= 0:
        return jsonify({'success': False, 'message': 'Некоректні дані'}), 400

    # Захист від дублювання
    existing = Product.query.filter_by(name=product_name).first()
    if existing:
        return jsonify({'success': False, 'message': 'Такий товар вже існує'}), 409

    new_product = Product(name=product_name, price=product_price)
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'success': True, 'message': '✅ Товар додано', 'product_id': new_product.id})


@app.route('/admin/deactivate_add_mode', methods=['POST'])
@login_required
def deactivate_add_mode():
    if current_user.is_admin:
        add_product_mode[current_user.id] = False
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Недостатньо прав'}), 403


# Вхід
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()

        if not user:
            flash('Користувача не знайдено.', 'danger')
            return redirect(url_for('login'))  # URL існує

        if user.is_banned:
            flash('Ваш акаунт заблоковано. Зверніться до адміністрації.', 'danger')
            return redirect(url_for('login'))  # URL існує

        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Вхід успішний!', 'success')
            return redirect(url_for('profile'))  # Правильний URL

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

@app.route("/news")
def news():
    news_list = News.query.order_by(News.date.desc()).all()
    return render_template("news.html", news_list=news_list, user=current_user if current_user.is_authenticated else None)

# Модель новин
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    image_path = db.Column(db.String(255), nullable=True) 

# Додавання новини (тільки для адміністраторів)
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/add_news", methods=["POST"])
@login_required
def add_news():
    if not current_user.is_admin:
        flash("У вас немає прав для додавання новин!", "danger")
        return redirect(url_for('news'))

    title = request.form.get("title")
    content = request.form.get("content")
    image = request.files.get("image")

    image_filename = None

    if image and allowed_file(image.filename):
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

    if title and content:
        new_news = News(title=title, content=content, author=current_user.name, image_path=image_filename)
        db.session.add(new_news)
        db.session.commit()
        flash("Новина успішно додана!", "success")

    return redirect(url_for("news"))

#Маршрут для редагування новини
@app.route("/edit_news/<int:news_id>", methods=["GET", "POST"])
@login_required
def edit_news(news_id):
    if not current_user.is_admin:
        flash("У вас немає прав для редагування новин!", "danger")
        return redirect(url_for('news'))
    
    news = News.query.get_or_404(news_id)

    if request.method == "POST":
        news.title = request.form.get("title")
        news.content = request.form.get("content")
        db.session.commit()
        flash("Новина успішно оновлена!", "success")
        return redirect(url_for("news"))

    return render_template("edit_news.html", news=news, user=current_user)
#Маршрут для видалення новини
@app.route("/delete_news/<int:news_id>", methods=["POST"])
@login_required
def delete_news(news_id):
    if not current_user.is_admin:
        flash("У вас немає прав для видалення новин!", "danger")
        return redirect(url_for('news'))

    news = News.query.get_or_404(news_id)
    db.session.delete(news)
    db.session.commit()
    flash("Новина видалена!", "success")

    return redirect(url_for("news"))

@app.route("/delete_news_image/<int:news_id>", methods=["POST"])
@login_required
def delete_news_image(news_id):
    if not current_user.is_admin:
        flash("У вас немає прав для видалення фото!", "danger")
        return redirect(url_for('news'))

    news = News.query.get_or_404(news_id)

    if news.image_path:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], news.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)  # Видаляємо файл з сервера
        news.image_path = None
        db.session.commit()
        flash("Фото видалено!", "success")

    return redirect(url_for("news"))

#Правила точка входу
@app.route("/regulations")
def regulations():
    return render_template("regulations.html", user=current_user if current_user.is_authenticated else None)

@app.route("/donate")
def donate():
    return render_template("donate.html", user=current_user if current_user.is_authenticated else None)

@app.route("/carsChernorus")
def carsChernorus():
    return render_template("cars-shop-Chernorus.html", user=current_user if current_user.is_authenticated else None)

@app.route("/trucksChernorus")
def trucksChernorus():
    return render_template("trucks-shop-Chernorus.html", user=current_user if current_user.is_authenticated else None)

@app.route("/helicoptersChernorus")
def helicoptersChernorus():
    return render_template("helicopters-shop-Chernorus.html", user=current_user if current_user.is_authenticated else None)

@app.route("/basesChernorus")
def basesChernorus():
    return render_template("bases-shop-Chernorus.html", user=current_user if current_user.is_authenticated else None)

@app.route("/clothingChernorus")
def clothingChernorus():
    return render_template("clothing-shop-Chernorus.html", user=current_user if current_user.is_authenticated else None)

@app.route("/carsDeerisle")
def carsDeerisle():
    return render_template("cars-shop-Deerisle.html", user=current_user if current_user.is_authenticated else None)

@app.route("/trucksDeerisle")
def trucksDeerisle():
    return render_template("trucks-shop-Deerisle.html", user=current_user if current_user.is_authenticated else None)

@app.route("/helicoptersDeerisle")
def helicoptersDeerisle():
    return render_template("helicopters-shop-Deerisle.html", user=current_user if current_user.is_authenticated else None)

@app.route("/basesDeerisle")
def basesDeerisle():
    return render_template("bases-shop-Deerisle.html", user=current_user if current_user.is_authenticated else None)

@app.route("/clothingDeerisle")
def clothingDeerisle():
    return render_template("clothing-shop-Deerisle.html", user=current_user if current_user.is_authenticated else None)

@app.route("/info")
def info():
    return render_template("info.html", user=current_user if current_user.is_authenticated else None)

@app.route("/Territories")
def Territories():
    return render_template("Territories-and-places.html", user=current_user if current_user.is_authenticated else None)

@app.route("/Systems")
def Systems():
    return render_template("Systems-and-mechanics.html", user=current_user if current_user.is_authenticated else None)
         ############################# Початок Система та механіка #############################
@app.route("/CraftingSystem")
def CraftingSystem():
    return render_template("Crafting system.html", user=current_user if current_user.is_authenticated else None)

@app.route("/MiningOfOresAndPreciousStones")
def MiningOfOresAndPreciousStones():
    return render_template("Mining of ores and precious stones.html", user=current_user if current_user.is_authenticated else None)

@app.route("/BrewingMoonshine")
def BrewingMoonshine():
    return render_template("Brewing moonshine.html", user=current_user if current_user.is_authenticated else None)

@app.route("/GrowingCannabis")
def GrowingCannabis():
    return render_template("Growing cannabis.html", user=current_user if current_user.is_authenticated else None)

@app.route("/LiveMarket")
def LiveMarket():
    return render_template("Live market.html", user=current_user if current_user.is_authenticated else None)

@app.route("/BankAndGarage")
def BankAndGarage():
    return render_template("Bank and garage.html", user=current_user if current_user.is_authenticated else None)

@app.route("/AdvancedMedicine")
def AdvancedMedicine():
    return render_template("Advanced Medicine.html", user=current_user if current_user.is_authenticated else None)

@app.route("/DivingSystem")
def DivingSystem():
    return render_template("Diving system.html", user=current_user if current_user.is_authenticated else None)

@app.route("/RadiationZones")
def RadiationZones():
    return render_template("Radiation zones.html", user=current_user if current_user.is_authenticated else None)

@app.route("/AchievementSystem")
def AchievementSystem():
    return render_template("Achievement system.html", user=current_user if current_user.is_authenticated else None)

@app.route("/QuestSystem")
def QuestSystem():
    return render_template("Quest system.html", user=current_user if current_user.is_authenticated else None)

@app.route("/BitcoinMining")
def BitcoinMining():
    return render_template("Bitcoin mining.html", user=current_user if current_user.is_authenticated else None)

@app.route("/KnifeCases")
def KnifeCases():
    return render_template("Knife cases.html", user=current_user if current_user.is_authenticated else None)

@app.route("/LootBoxes")
def LootBoxes():
    return render_template("Loot boxes.html", user=current_user if current_user.is_authenticated else None)

@app.route("/CarTuning")
def CarTuning():
    return render_template("Car tuning.html", user=current_user if current_user.is_authenticated else None)

############################ Кінець секції Система та механіка #############################

@app.route("/Aboutus")
def Aboutus():
    return render_template("About-us.html", user=current_user if current_user.is_authenticated else None)

# Адмін-панель для перегляду заявок
@app.route('/admin/receipts', methods=['GET'])
@login_required
def admin_receipts():
    if not current_user.is_admin:
        flash("Доступ заборонено. Ви не адміністратор.", "danger")
        return redirect(url_for('home'))

    # Отримання списку заявок із бази даних
    receipt_requests = ReceiptRequest.query.all()

    # Рендер сторінки адміністратора з даними
    return render_template('admin_receipts.html', requests=receipt_requests, user=current_user)

# Модель заявки на чек
class ReceiptRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    buyer_name = db.Column(db.String(50), nullable=False)
    receipt_image = db.Column(db.String(120), nullable=False)
    promo_code = db.Column(db.String(10), nullable=True)
    promo_code_confirmed = db.Column(db.Boolean, default=False)  # Нове поле
    quantity = db.Column(db.Integer, nullable=False, default=1)  # Нове поле
    status = db.Column(db.String(20), nullable=False, default='pending')
    approved_by = db.Column(db.String(50), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Створення таблиць
with app.app_context():
    db.create_all()

# Роут для завантаження чека користувачем
@app.route('/upload_receipt_user', methods=['POST'])
@login_required
def upload_receipt_user():
    try:
        # Отримання даних кошика
        cart_data = request.form.get('cart_data')
        if not cart_data:
            app.logger.warning("Дані кошика відсутні у запиті")
            return jsonify({'success': False, 'message': 'Дані кошика відсутні'}), 400

        cart_data = json.loads(cart_data)
        file = request.files.get('receipt_image')  # Отримуємо файл

        if not file or not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Невірний формат файлу. Дозволені тільки зображення (png, jpg, jpeg).'}), 400

        # Збереження файлу
        filename = secure_filename(file.filename)
        upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
        file_path = os.path.join(upload_folder, filename)
        os.makedirs(upload_folder, exist_ok=True)  # Створюємо папку, якщо її немає
        file.save(file_path)

        # Оновлення бази даних для кожного товару в кошику
        for product_id, item in cart_data.items():
            product = Product.query.get(product_id)
            if not product:
                app.logger.warning(f"Товар із product_id {product_id} не знайдено")
                continue

            # Збереження заявки на кожен товар
            receipt_request = ReceiptRequest(
                user_id=current_user.id,
                user_name=current_user.name,
                product_name=item['name'],
                product_price=item['price'],
                buyer_name=current_user.name,
                receipt_image=f'uploads/{filename}',  # Шлях до файлу
                quantity=item['quantity'],
                status='pending'
            )
            db.session.add(receipt_request)

        db.session.commit()
        app.logger.info("Чек успішно завантажено")
        return redirect(url_for('profile'))  # Перенаправлення до профілю
    except Exception as e:
        app.logger.error(f"Помилка обробки запиту: {e}")
        return jsonify({'success': False, 'message': 'Сталася помилка на сервері'}), 500
    
#Роут для перегляду заявок адміністратором
@app.route('/admin/approve_receipt/<int:request_id>', methods=['POST'])
@login_required
def handle_approve_receipt(request_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Доступ заборонено'}), 403

    receipt_request = ReceiptRequest.query.get(request_id)
    if not receipt_request:
        return jsonify({'success': False, 'message': 'Заявку не знайдено'}), 404

    data = request.get_json()
    action = data.get('action')

    if action == 'approve':
        promo_code = get_unused_promo(receipt_request.product_name)
        if not promo_code:
            return jsonify({'success': False, 'message': 'Немає доступних промокодів'}), 400

        receipt_request.status = 'Затверджено'
        receipt_request.promo_code = promo_code
        receipt_request.promo_code_confirmed = True
        receipt_request.approved_by = current_user.name

        db.session.commit()
        return jsonify({'success': True, 'promo_code': promo_code})

    elif action == 'reject':
        receipt_request.status = 'Відхилено'
        receipt_request.approved_by = current_user.name
        db.session.commit()
        return jsonify({'success': True, 'message': 'Заявку відхилено'})

    else:
        return jsonify({'success': False, 'message': 'Невідома дія'}), 400

        
 #Маршрут у Flask для сторінки оплати
@app.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    bank_details = {
        'bank_name': 'ПриватБанк',
        'iban': 'UA123456789012345670000000',
        'mfo': '0',
        'edrpou': '0',
        'recipient': 'ТОВ "Apexia"'
    }
    # Обробка POST-запиту
    if request.method == 'POST':
        # Перевірка наявності файлу у формі
        file = request.files.get('receipt_image')
        if not file:
            flash('Будь ласка, завантажте файл.', 'danger')
            return redirect(url_for('payment'))

        # Перевірка формату файлу
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')  # Папка завантаження
            file_path = os.path.join(upload_folder, filename)

            # Збереження файлу
            try:
                file.save(file_path)

                # Збереження даних у базу
                receipt_request = ReceiptRequest(
                    user_id=current_user.id,
                    receipt_image=f'{upload_folder}/{filename}',  # Збереження шляху до файлу
                )
                db.session.add(receipt_request)
                db.session.commit()

                flash('Чек успішно завантажено. Очікуйте підтвердження.', 'success')
                return redirect(url_for('profile'))
            except Exception as e:
                app.logger.error(f"Помилка при збереженні чека: {e}")
                flash('Сталася помилка при завантаженні файлу. Спробуйте ще раз.', 'danger')
                return redirect(url_for('payment'))
        else:
            flash('Невірний формат файлу. Дозволені тільки зображення (png, jpg, jpeg).', 'danger')

    return render_template('payment.html', bank_details=bank_details)

# Завантаження чека
@app.route('/upload_receipt', methods=['POST'])
@login_required
def upload_receipt():
    if 'receipt_image' not in request.files:
        return jsonify({'success': False, 'message': 'Чек не завантажено'}), 400

    file = request.files['receipt_image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Створюємо заявку без промокоду
        receipt_request = ReceiptRequest(
        user_id=current_user.id,
        receipt_image=f'uploads/{filename}',
        status='approved'  # або 'pending' залежно від логіки
          )
        db.session.add(receipt_request)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Чек успішно завантажено. Очікуйте підтвердження.'})
    return jsonify({'success': False, 'message': 'Невірний формат файлу'}), 400


#Адмін затверджує чек
@app.route('/admin/approve_receipt/<int:request_id>', methods=['POST'])
@login_required
def approve_receipt(request_id):
    if not current_user.is_admin:        
        return redirect(url_for('home')) 

    receipt_request = ReceiptRequest.query.get(request_id)
    if not receipt_request:
        return jsonify({'success': False, 'message': 'Заявку не знайдено'}), 404

    action = request.json.get('action')
    if action == 'approve':
        receipt_request.status = 'Затверджено'
        promo_code = generate_promo_code()
        receipt_request.promo_code = promo_code
        receipt_request.approved_by = current_user.name  # Зберігаємо ім'я адміністратора
        db.session.commit()
        return jsonify({'success': True, 'promo_code': promo_code})
    elif action == 'reject':
        receipt_request.status = 'Відхилено'
        db.session.commit()
        return jsonify({'success': True, 'message': 'Заявку відхилено'})
    return jsonify({'success': False, 'message': 'Некоректна дія'}), 400

# Маршрут для отримання списку товарів
@app.route('/api/products', methods=['GET'])
@login_required
def get_products():
    products = Product.query.all()
    product_list = [{'id': p.id, 'name': p.name, 'price': p.price} for p in products]
    return jsonify(product_list)

# Додаємо маршрут для надання прав адміністратора 
@app.route('/admin/grant_admin', methods=['GET', 'POST'])
@login_required
def grant_admin():
    if not current_user.is_admin:                              #Удалить тимчасово для надання прав адміна коли його не існує
        flash("Ви не маєте прав для цієї операції.", "danger") #Удалить тимчасово для надання прав адміна коли його не існує
        return redirect(url_for('home'))                       #Удалить тимчасово для надання прав адміна коли його не існує

    if request.method == 'POST':
        username = request.form.get('username')

        if not username:
            flash("Будь ласка, вкажіть ім'я користувача.", "danger")
            return redirect(url_for('admin_receipts'))

        # Шукаємо користувача по імені
        user = User.query.filter_by(name=username).first()

        if not user:
            flash(f"Користувача з ім'ям {username} не знайдено.", "danger")
            return redirect(url_for('admin_receipts'))

        if user.is_admin:
            flash(f"Користувач {username} вже є адміністратором.", "info")
            return redirect(url_for('admin_receipts'))

        # Надаємо права адміністратора
        user.is_admin = True
        db.session.commit()

        flash(f"Користувач {username} тепер є адміністратором.", "success")
        return redirect(url_for('admin_receipts'))

    return render_template('admin_receipts.html','admin_panel_secretly.html')

@app.route('/admin_panel_secretly', methods=['GET', 'POST'])
def admin_panel_secretly():
    return render_template("admin_panel_secretly.html", user=current_user if current_user.is_authenticated else None)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/admin/users', methods=['GET'])
@login_required
def admin_users():
    if not current_user.is_admin:
        flash("Доступ заборонено!", "danger")
        return redirect(url_for('home'))

    users = User.query.all()
    return render_template('admin_users.html', users=users)

# 📌 Роут для перегляду деталей конкретного користувача
@app.route('/admin/view_user/<int:user_id>', methods=['GET'])
@login_required
def view_user(user_id):
    if not current_user.is_admin:
        flash("Доступ заборонено!", "danger")
        return redirect(url_for('home'))

    user = User.query.get(user_id)
    if not user:
        flash("Користувача не знайдено!", "danger")
        return redirect(url_for('admin_users'))

    return render_template('view_user.html', user=user)

# 📌 Роут для блокування користувача
@app.route('/admin/ban_user/<int:user_id>', methods=['POST'])
@login_required
def ban_user(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Доступ заборонено'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Користувача не знайдено'}), 404

    user.is_banned = True
    db.session.commit()
    return jsonify({'success': True, 'message': f'Користувач {user.name} заблокований'})

# 📌 Роут для розблокування користувача
@app.route('/admin/unban_user/<int:user_id>', methods=['POST'])
@login_required
def unban_user(user_id):
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Доступ заборонено'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'Користувача не знайдено'}), 404

    user.is_banned = False
    db.session.commit()
    return jsonify({'success': True, 'message': f'Користувач {user.name} розблокований'})


#if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)