from flask import Flask, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Email, Length
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from services import services_dictionary

# ---------------------------- CREDENTIALS ------------------------------- #
MY_EMAIL = "pythontest32288@gmail.com"
MY_PASSWORD = "gsrfzucledwimgqp"


# ---------------------------- WTForms ------------------------------- #
class ContactMe(FlaskForm):
    name = StringField("الاسم", validators=[DataRequired(message='هذا الحقل مطلوب.')])
    email = StringField("البريد الإلكتروني", validators=[DataRequired(message='هذا الحقل مطلوب.'), Email(message='يرجى إدخال عنوان بريد إلكتروني صالح.')])
    phone_number = StringField("رقم الهاتف", validators=[DataRequired(message='هذا الحقل مطلوب.')])
    message = TextAreaField("الرسالة", validators=[DataRequired(message='هذا الحقل مطلوب.')], render_kw={"rows": 10})
    submit = SubmitField("إرسال")


class LoginForm(FlaskForm):
    email = StringField("البريد الإلكتروني", validators=[DataRequired(message='هذا الحقل مطلوب.'), Email()])
    password = PasswordField("كلمة السر", validators=[DataRequired(message='هذا الحقل مطلوب.'), Length(min=8, max=50)])
    submit = SubmitField("تسجيل الدخول")


# ------------------ Initializing A Flask App With Some Extensions --------------------- #
# Initialize the Flask app and set a secret key
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6derzWlSihBXox7C0sKR6b'

# Initialize the Bootstrap extension
Bootstrap(app)

# Initialize the Flask-Login extension
login_manager = LoginManager()
login_manager.init_app(app)

# Set up the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ammar-team.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# # Set up the database connection
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://omarblog:mysqlpassword@omarblog.mysql.pythonanywhere-services.com:3306/omarblog$default'
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280, 'pool_timeout': 10}
# app.config['SQLALCHEMY_POOL_SIZE'] = 5
# app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# # Use SQLite as a fallback if the MySQL URL fails
# app.config['SQLALCHEMY_FALLBACK_URI'] = 'sqlite://///home/omarblog/Day-59-60-67-69-blog--5th-capstone-/instance/blog.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)


# ---------------------------- DB Tables ------------------------------- #
# Users table in db
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __repr__(self):
        return f'<User {self.name}>'


# # Projects table in db
# class Project(db.Model):
#     __tablename__ = "projects"
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(250), unique=True, nullable=False)
#     subtitle = db.Column(db.String(250), nullable=False)
#     date = db.Column(db.String(250), nullable=False)
#     body = db.Column(db.Text, nullable=False)
#     img_url = db.Column(db.String(250), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     comments = db.relationship('PostComments', backref='blog_post', lazy=True)
#
#     def __repr__(self):
#         return f'<Project {self.title}>'


# with app.app_context():
#     db.create_all()


# ---------------------------- Custom Functions ------------------------------- #
def send_mail(name, email, phone, message):
    # create message object instance
    msg = MIMEMultipart()

    # set up the parameters of the message
    password = MY_PASSWORD
    msg['From'] = MY_EMAIL
    msg['To'] = "omarmobarak53@gmail.com"
    msg['Subject'] = "New message from 'Omar's Blog' user"

    # add in the message body
    body = f"Name: {name}\nEmail: {email}\nPhone Number: {phone}\nMessage: {message}"
    msg.attach(MIMEText(body, 'plain'))

    # create server instance
    server = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for secure connection
    server.starttls()

    # Login to the server
    server.login(msg['From'], password)

    # send the message via the server
    server.sendmail(msg['From'], msg['To'], msg.as_string())

    # close the server connection
    server.quit()


# Create a custom decorator to restrict access to non-logged-in users
def logout_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash('يجب عليك تسجيل الخروج أولا لتستطيع الوصول لهذه الصفحة.')
            return redirect(url_for('home'))
        return func(*args, **kwargs)

    return decorated_function


# Set up the user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------- Main Pages Routes ------------------------------- #
@app.route("/", methods=["GET", "POST"])
def home():
    contact_form = ContactMe()
    sent_successfully = ""
    if contact_form.validate_on_submit():
        name = contact_form.name.data
        email = contact_form.email.data
        phone = contact_form.phone_number.data
        message = contact_form.message.data
        try:
            send_mail(name, email, phone, message)
            sent_successfully = "تم إرسال رسالتك بنجاح! سنحرص على التواصل معك في أقرب وقت ممكن."

        except (smtplib.SMTPException, socket.gaierror):
            flash("عذرا, حصل خطأ أثناء إرسالة رسالتك. الرجاء المحاولة لاحقا.")

    return render_template("index.html", contact_form=contact_form, sent_successfully=sent_successfully)


@app.route("/portfolio-details")
def portfolio_details():
    return render_template("portfolio-details.html")


@app.route('/services/<int:service_id>', methods=["GET", "POST"])
def services(service_id):

    service = services_dictionary[service_id]
    contact_form = ContactMe()
    sent_successfully = ""
    if contact_form.validate_on_submit():
        name = contact_form.name.data
        email = contact_form.email.data
        phone = contact_form.phone_number.data
        message = contact_form.message.data
        try:
            send_mail(name, email, phone, message)
            sent_successfully = "تم إرسال رسالتك بنجاح! سنحرص على التواصل معك في أقرب وقت ممكن."

        except (smtplib.SMTPException, socket.gaierror):
            flash("عذرا, حصل خطأ أثناء إرسالة رسالتك. الرجاء المحاولة لاحقا.")

    return render_template(
        "services.html",
        contact_form=contact_form,
        sent_successfully=sent_successfully,
        service=service,
        service_id=service_id
    )


@app.route('/inner-page')
def inner_page():
    return render_template("inner-page.html")


# ---------------------------- Admin Pages Routes ------------------------------- #
@app.route("/login-admin", methods=["GET", "POST"])
@logout_required
def login_admin():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        print("hi")
        email = login_form.email.data
        password = login_form.password.data
        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('كلمة السر غير صحيحة, الرجاء المحاولة مرة أخرى.')
        else:
            flash('البريد الإلكتروني غير موجود, الرجاء المحاولة مرة أخرى.')

    return render_template("login-admin.html", login_form=login_form)


@app.route('/logout-admin')
@login_required
def logout_admin():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
