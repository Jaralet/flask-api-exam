from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Конфигурация подключения к базе данных PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@db:5432/mydatabase')
    
    # Отключаем отслеживание изменений объектов SQLAlchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализируем SQLAlchemy с приложением
    db.init_app(app)

    # Регистрируем Blueprint с маршрутами
    from .routes import api_bp
    app.register_blueprint(api_bp)

    return app