#!/usr/bin/env python
from app import db, app
from config import SECRET_KEY
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    level = db.Column(db.Integer)
    parent = db.Column(db.String(64))
    title = db.Column(db.String(64))
    start = db.Column(db.String(64))
    over = db.Column(db.String(64))
    items = db.Column(db.String(64))
    status = db.Column(db.Integer)  # 增删改
    timestamp = db.Column(db.Integer)
    username = db.Column(db.String(32), db.ForeignKey('user.username'))

    def __init__(self, level, parent, title, start, over, timestamp, status, items, username):
        self.level = level
        self.parent = parent
        self.title = title
        self.start = start
        self.over = over
        self.timestamp = timestamp
        self.status = status
        self.items = items
        self.username = username

    def __repr__(self):
        return '<Goal %r>' % self.title

    def serialize(self):
        return {
            'level': self.level,
            'parent': self.parent,
            'title': self.title,
            'start': self.start,
            'over': self.over,
            'timestamp': self.timestamp,
            'status': self.status,
            'items': self.items,
            'username': self.username
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        # s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        # s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    note = db.Column(db.String(128))
    date = db.Column(db.String(64))

    def __init__(self, username, note, date):
        self.date = date
        self.note = note
        self.username = username
