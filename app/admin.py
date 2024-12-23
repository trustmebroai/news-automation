from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, Article
from .utils import generate_article_with_claude

admin_bp = Blueprint('admin', __name__, url_prefix='/dashboard_x2f')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

@admin_bp.route('/')
def index():
    if current_user.is_authenticated:
        articles = Article.query.order_by(Article.created_at.desc()).all()
        return render_template('dashboard_x2f/dashboard.html', articles=articles)
    return redirect(url_for('admin.login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
        
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('admin.index'))
        flash('Invalid username or password')
    return render_template('dashboard_x2f/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@admin_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'POST':
        try:
            prompt = request.form['prompt']
            style = request.form['style']
            
            # Generate article with Claude
            result = generate_article_with_claude(
                topic=prompt,
                style=style,
                tone="engaging"
            )
            
            if result['success']:
                # Create new article
                article = Article(
                    title=result['title'],
                    content=result['content'],
                    image_url=result['image_url']
                )
                db.session.add(article)
                db.session.commit()
                flash('Article generated successfully!')
                return redirect(url_for('admin.index'))
            else:
                flash(f'Error generating article: {result["error"]}')
        except Exception as e:
            flash(f'Error: {str(e)}')
    
    return render_template('dashboard_x2f/create_article.html')

@admin_bp.route('/delete/<int:article_id>')
@login_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('Article deleted successfully!')
    return redirect(url_for('admin.index'))

@admin_bp.route('/change_password/<new_password>')
@login_required
def change_password(new_password):
    if current_user.username == 'admin':
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password updated successfully')
    return redirect(url_for('admin.index'))

@admin_bp.route('/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if request.method == 'POST':
        article.title = request.form['title']
        article.content = request.form['content']
        db.session.commit()
        flash('Article updated successfully!')
        return redirect(url_for('admin.index'))
    return render_template('dashboard_x2f/edit_article.html', article=article)