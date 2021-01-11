from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length


class SignupForm(FlaskForm):
    name = StringField('Nombre:', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Contraseña:', validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired(), Email()])
    submit = SubmitField('Registrar')
    

class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired()])
    password = PasswordField('Contraseña:', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Iniciar sesión')
