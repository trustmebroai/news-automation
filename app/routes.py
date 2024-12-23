from flask import Blueprint, render_template
from .models.article import Article

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured_article = Article.query.order_by(Article.created_at.desc()).first()
    other_articles = Article.query.order_by(Article.created_at.desc()).offset(1).limit(6).all()
    return render_template('index.html', featured_article=featured_article, other_articles=other_articles)

@main_bp.route('/article/<int:article_id>')
def article(article_id):
    article = Article.query.get_or_404(article_id)
    other_articles = Article.query.order_by(Article.created_at.desc()).all()
    return render_template('article.html', 
                         article=article,
                         content=article.content,
                         other_articles=other_articles)