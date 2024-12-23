
## 🔑 Admin Dashboard

1. **Access:**
   - URL: `http://localhost:5000/dashboard_x2f`
   - Default username: `admin`
   - Password: (what you set in app/__init__.py)

2. **Features:**
   - Create new articles
   - Edit existing articles
   - Delete articles
   - View all articles

## ⚙️ Customization

1. **Modify Article Topics:**
   Edit `auto_generator.py` and update the `TOPIC_TEMPLATES` dictionary:
  
2. **Customize Article Style:**
   Edit the prompt template in `app/utils/article.py`

## 🐛 Troubleshooting

1. **Twitter API Issues:**
   - Verify API keys in .env
   - Check app permissions (read/write)
   - Ensure OAuth 1.0a is enabled

2. **Image Generation Fails:**
   - Verify Stability API key
   - Check error messages in console
   - Ensure prompt follows guidelines

3. **Database Issues:**
   - Delete app.db and reinitialize
   - Check file permissions

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
