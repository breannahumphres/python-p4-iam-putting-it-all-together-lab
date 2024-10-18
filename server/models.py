from sqlalchemy.orm import validates, synonym
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    # Attributes
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column("password_hash", db.String, nullable=True)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    password_hash = synonym('_password_hash', map_column=True)

    # Relationships
    recipes = db.relationship('Recipe', back_populates='user', cascade='all, delete-orphan')

    # Password property
    @property
    def password_hash(self):
        raise AttributeError('password_hash is not a readable attribute.')

    @password_hash.setter
    def password_hash(self, password):
        if password:
            self._password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
                    
        else: 
            self._password_hash = None

    # Password verification
    def authenticate(self, password):
        if self._password_hash is None:
            return False
        return bcrypt.check_password_hash(self._password_hash, password)

    # Validators
    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('Username is required.')
        return username

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    # Attributes
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='recipes')

    # Validators
    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError('Title is required.')
        return title

    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if not instructions or len(instructions) < 50:
            raise ValueError('Instructions must be at least 50 characters long.')
        return instructions
