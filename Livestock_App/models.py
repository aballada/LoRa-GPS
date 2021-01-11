from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from Login import db


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

