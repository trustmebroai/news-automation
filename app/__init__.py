from flask import Flask
from flask_login import LoginManager
from config import Config
from .models import db

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    
    # Import and register blueprints
    from .routes import main_bp
    from .admin import admin_bp, User
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        # Remove this line that drops all tables
        # db.drop_all()  
        
        # Only create tables if they don't exist
        db.create_all()
        
        # Create or update admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin')
        admin.set_password('your_new_password_here')  # Change this to your desired password
        db.session.add(admin)
        db.session.commit()
    
    return app