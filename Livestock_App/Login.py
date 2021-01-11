from flask import Flask
from flask import render_template, request, redirect, url_for
from forms import SignupForm, LoginForm
from flask_login import LoginManager, logout_user, current_user, login_user, login_required
from werkzeug.urls import url_parse
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps, Map, icons
from dynaconf import FlaskDynaconf
import mysql.connector
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = '999eb4d7934d1cdc31ba81a98cb63d3f8c284c09'
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+mysqldb://aballada:raspberry@localhost:5000/Lora_BD'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

GoogleMaps(app)
FlaskDynaconf(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
db = SQLAlchemy(app)



mail = Mail(app)

base = mysql.connector.connect( 
        host = 'localhost',
        user = 'aballada',
        password = 'raspberry',
        db = 'Lora_BD'
        )
mycursor = base.cursor()

app.config.update(dict(
       DEBUG = True,
       MAIL_SERVER = 'smtp.gmail.com',
       MAIL_PORT = 587,
       MAIL_USE_TLS = True,
       MAIL_USE_SSL = False,
       MAIL_USERNAME = 'app.livestock@gmail.com',
       MAIL_PASSWORD = 'Nieve125',
))

mail = Mail(app) 


class User(db.Model, UserMixin):
        
    __tablename__ = 'Usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(80), nullable=False)
    email = db.Column(db.Text(256), unique=True, nullable=False)
    password = db.Column(db.Text(128), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'
        
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
        
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
        
    @staticmethod
    def get_by_id(id):
        return User.query.get(id)
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()


@app.route('/')
def index():
    return render_template("index.html")
    
    
@app.route('/sent_mail')
def show_send_mail():
    #mycursor.reset()
    mycursor = base.cursor(buffered=True)
    sql1 = "SELECT Latitud, Longitud FROM `GPS` WHERE Nodo = '1' ORDER BY Hora DESC LIMIT 1"
    sql2 = "SELECT Latitud, Longitud FROM `GPS` WHERE Nodo = '2' ORDER BY Hora DESC LIMIT 1"
    mycursor.execute(sql1)
    registro1= mycursor.fetchone()
    mycursor.execute(sql2)
    registro2= mycursor.fetchone()
    mycursor = base.cursor(buffered=True)
    #if registro1[0]=='Fail' or registro2[0]='Fail':
    msg = Message('App Livestock', sender ='app.livestock@gmail.com', recipients = ['aballada@espol.edu.ec'])
    #msg.body = f'Hola, \n\n Te informamos que el GPS está fallando.\nSaludos,\nApp Livestock'
    msg.body = f'Hola, \n\n Los datos solicitados son los siguientes: \n\n Datos del Nodo1 \n   - Latitud: {registro1[0]} \n   - Longitud: {registro1[1]} \n\n Datos del Nodo2 \n   - Latitud: {registro2[0]} \n   - Longitud: {registro2[1]} \n '
    mail.send(msg)
    return render_template("mail.html")

@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('location'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        # Comprobamos que no hay ya un usuario con ese email
        user = User.get_by_email(email)
        if user is not None:
            error = f'El email {email} ya está siendo utilizado por otro usuario'
        else:
            # Creamos el usuario y lo guardamos
            user = User(name=name, email=email)
            user.set_password(password)
            user.save()
            # Dejamos al usuario logueado
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('viewData')
            return redirect(next_page)
    return render_template("signup_form.html", form=form, error=error)
        


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('viewData')
            return redirect(next_page)

    return render_template('login_form.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    

@app.route("/View")
def viewData():
    if mycursor.fetchone()=='None':
        base.cursor()
    else:
        mycursor.reset()
    sql1 = "SELECT Latitud, Longitud, Temperatura, StatusGPS, StatusTemp FROM `GPS` WHERE Nodo = '1' ORDER BY Hora DESC LIMIT 1"
    sql2 = "SELECT Latitud, Longitud, Temperatura, StatusGPS, StatusTemp FROM `GPS` WHERE Nodo = '2' ORDER BY Hora DESC LIMIT 1"
    mycursor.execute(sql1)
    registro1= mycursor.fetchone()
    mycursor.execute(sql2)
    registro2= mycursor.fetchone()
    print(registro2)
    templateData = {
    #Datos del nodo 1
    'Latitud1' : registro1[0],
    'Longitud1' : registro1[1],
    'Temperatura1' : registro1[2],
    'StatusGPS1' : registro1[3],
    'StatusTemp' : registro1[4],
    #Datos del nodo2
    'Latitud2' : registro2[0],
    'Longitud2' : registro2[1],
    'Temperatura2' : registro2[2],
    'StatusGPS2' : registro2[3],
    'StatusTemp2' : registro2[4],
    }

    base.commit()
    if registro1[0]=='Fail' :
        lat=float(registro2[0])
        lng=float(registro2[1])
        #Msg1 = "Existe problemas de comunicación, revise la señal GPS!"
    elif registro1[1]=='Fail':
        lat=float(registro1[0])
        lng=float(registro1[1])
        #Msg1 = "Existe problemas de comunicación, revise la señal GPS!"
    elif registro1[0]=='Fail' and registro1[1]=='Fail':
        lat=41.572491
        lng=2.024105
        Msg1 = "Existe problemas de comunicación, revise la señal GPS!"
    else:
        lat=float(registro1[0])
        lng=float(registro1[1])
        #Msg="Geolocalización de res mediante comunicación Lora"
    gmap = Map(
        identifier="gmap",
        varname="gmap",
        zoom=16,
        lat=lat,
        lng=lng,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': registro1[0],
             'lng': registro1[1],
             'infobox': "<b>Soy el Nodo 1</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': registro2[0],
             'lng': registro2[1],
             'infobox': "<b>Soy el Nodo 2</b>"
          }
          ],
        style="height:400px; width:630px; position: relative; top: 20px; margin-left:auto; margin-right:auto",
    )
    print(registro1)
    print(registro2)
    base.commit()
    return render_template('View.html', **templateData, gmap=gmap)

if __name__=='__main__':
	app.run(host='0.0.0.0')
