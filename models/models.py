from datetime import datetime
from config import db
from flask_login import UserMixin

class Goods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_id = db.Column(db.Integer, db.ForeignKey("ip.id"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(100), nullable=False)
    article = db.Column(db.String(100), nullable=False)
    wb_article = db.Column(db.String(100), nullable=False)
    create_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    edit_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    compound = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer,nullable=False)
    ip = db.relationship("Ip", backref="goods")

class Ip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)









from config import db

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Reception(db.Model):
    __tablename__ = 'receptions'
    id = db.Column(db.Integer, primary_key=True)
    priemka_date = db.Column(db.Date, nullable=False)

class ProjectReception(db.Model):
    __tablename__ = 'project_receptions'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    priemka_id = db.Column(db.Integer, db.ForeignKey('receptions.id'), nullable=False)



class GoodsReception(db.Model):
    __tablename__ = 'goods_receptions'
    id = db.Column(db.Integer, primary_key=True)
    priemka_id = db.Column(db.Integer, db.ForeignKey('receptions.id'), nullable=False)
    tovar_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    kol_vo = db.Column(db.Integer, nullable=False)



class Defect(db.Model):
    __tablename__ = 'defects'
    id = db.Column(db.Integer, primary_key=True)
    tovar_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    priemka_id = db.Column(db.Integer, db.ForeignKey('receptions.id'), nullable=False)
    kol_vo = db.Column(db.Integer, nullable=False)

class Action(db.Model):
    __tablename__ = 'actions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    quantity=db.Column(db.Integer,nullable=True)

class UserAction(db.Model):
    __tablename__ = 'user_actions'
    id = db.Column(db.Integer, primary_key=True)
    deistvie_id = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    kol_vo = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    action = db.relationship('Action', backref='user_actions')

class Empoyeer(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class ReceptionAction(db.Model):
    __tablename__ = 'reception_actions'
    id = db.Column(db.Integer, primary_key=True)
    priemka_id = db.Column(db.Integer, db.ForeignKey('receptions.id'), nullable=False)
    deistvie_id = db.Column(db.Integer, db.ForeignKey ('actions.id'), nullable=False)