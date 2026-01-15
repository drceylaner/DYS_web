"""
Akademik Dergi Yönetim Sistemi - Web Uygulaması
Flask tabanlı web uygulaması
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import json

# Veritabanı ve AI modüllerini import et
import sys
sys.path.append('Dergi_Yonetim_Sistemi')
from database import Database
from ai_classifier import AIArticleClassifier

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Production'da değiştirin!

# Yapılandırma
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'odt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Klasörleri oluştur
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'reviews'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'recommendations'), exist_ok=True)

# Veritabanı ve AI sınıflandırıcı
# Veritabanını root dizininde oluştur
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dergi_sistemi.db')
db = Database(db_name=db_path)
ai_classifier = AIArticleClassifier()

# Yardımcı fonksiyonlar
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator for routes that require login"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Bu sayfaya erişmek için giriş yapmalısınız.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator for routes that require specific roles"""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('Bu sayfaya erişmek için giriş yapmalısınız.', 'warning')
                return redirect(url_for('login'))
            
            user = db.get_user(session['username'])
            if not user:
                flash('Kullanıcı bulunamadı.', 'error')
                return redirect(url_for('login'))
            
            user_roles = user.get('roles', [])
            if not any(role in user_roles for role in roles):
                flash('Bu sayfaya erişim yetkiniz yok.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def init_database_data():
    """Veritabanını test verileriyle doldur"""
    test_users = [
        ("admin", "DYS.2025", "admin", ["Admin", "Editör", "Alan Editörü", "Hakem", "Yazar"]),
        ("editor1", "pass", "Editör 1", ["Editör", "Yazar"]),
        ("editor2", "pass", "Editör 2", ["Editör", "Yazar"]),
        ("fe1", "pass", "Alan Editörü 1", ["Alan Editörü", "Yazar"], "Bilgisayar Mühendisliği"),
        ("fe2", "pass", "Alan Editörü 2", ["Alan Editörü", "Yazar"], "Elektrik-Elektronik Mühendisliği"),
        ("fe3", "pass", "Alan Editörü 3", ["Alan Editörü", "Yazar"], "Makine Mühendisliği"),
        ("fe4", "pass", "Alan Editörü 4", ["Alan Editörü", "Yazar"], "Endüstri Mühendisliği"),
        ("fe5", "pass", "Alan Editörü 5", ["Alan Editörü", "Yazar"], "İnşaat Mühendisliği"),
        ("rev1", "pass", "Hakem 1", ["Hakem", "Yazar"]),
        ("rev2", "pass", "Hakem 2", ["Hakem", "Yazar"]),
        ("rev3", "pass", "Hakem 3", ["Hakem", "Yazar"]),
        ("rev4", "pass", "Hakem 4", ["Hakem", "Yazar"]),
        ("rev5", "pass", "Hakem 5", ["Hakem", "Yazar"]),
        ("author1", "pass", "Yazar 1", ["Yazar"]),
        ("author2", "pass", "Yazar 2", ["Yazar"]),
    ]
    
    for user_data in test_users:
        username, password, name, roles = user_data[0], user_data[1], user_data[2], user_data[3]
        expertise_field = user_data[4] if len(user_data) > 4 else None
        
        if not db.get_user(username):
            db.add_user(username, password, name, roles, expertise_field)
        else:
            # Mevcut kullanıcı varsa uzmanlık alanını güncelle
            user = db.get_user(username)
            if user and "Alan Editörü" in user.get("roles", []) and not user.get("expertise_field") and expertise_field:
                db.update_user_expertise_field(username, expertise_field)

# Veritabanını başlat
init_database_data()

# ========== PUBLIC ROUTES ==========

@app.route('/')
def home():
    """Ana sayfa"""
    # Son yayınlanmış sayıları getir
    published_issues = db.get_published_issues()
    
    # Son sayı makaleleri
    latest_articles = []
    if published_issues:
        latest = published_issues[0]
        # Debug: Son sayı bilgisini konsola yazdır
        print(f"DEBUG: Son sayı - Yıl: {latest['year']}, Cilt: {latest['volume']}, Sayı: {latest['issue']}")
        latest_articles = db.get_articles_by_volume_issue(
            latest['volume'], latest['issue'], latest['year']
        )
    
    return render_template('home.html', 
                         published_issues=published_issues,
                         latest_articles=latest_articles)

@app.route('/about')
def about():
    """Hakkında sayfası"""
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """İletişim sayfası"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if not all([name, email, subject, message]):
            flash('Lütfen tüm alanları doldurun.', 'error')
            return render_template('contact.html')
        
        if db.add_contact_message(name, email, subject, message):
            flash('Mesajınız başarıyla gönderildi. Teşekkürler!', 'success')
            return redirect(url_for('contact'))
        else:
            flash('Mesaj gönderilirken bir hata oluştu.', 'error')
    
    return render_template('contact.html')

@app.route('/archive')
def archive():
    """Arşiv sayfası"""
    published_issues = db.get_published_issues()
    return render_template('archive.html', issues=published_issues)

@app.route('/issue/<volume>/<issue>/<year>')
def issue_detail(volume, issue, year):
    """Sayı detay sayfası"""
    articles = db.get_articles_by_volume_issue(volume, issue, year)
    return render_template('issue_detail.html', 
                         volume=volume, issue=issue, year=year,
                         articles=articles)

# ========== AUTHENTICATION ROUTES ==========

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Giriş sayfası"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Lütfen kullanıcı adı ve şifreyi girin.', 'error')
            return render_template('login.html')
        
        user = db.get_user(username)
        if not user or user.get('password') != password:
            flash('Kullanıcı bulunamadı veya şifre hatalı.', 'error')
            return render_template('login.html')
        
        # Session oluştur
        session['username'] = username
        session['user_name'] = user.get('name', username)
        user_roles = user.get('roles', ['Yazar'])
        
        # Admin ise tüm rollere sahip ol
        if 'Admin' in user_roles:
            user_roles = ['Admin', 'Editör', 'Alan Editörü', 'Hakem', 'Yazar']
        
        session['user_roles'] = user_roles
        session['user_role'] = user_roles[0] if user_roles else 'Yazar'
        
        flash(f'Hoş geldiniz, {user.get("name", username)}!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Kayıt sayfası"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not all([name, username, password]):
            flash('Lütfen tüm alanları doldurun.', 'error')
            return render_template('register.html')
        
        if db.get_user(username):
            flash('Bu kullanıcı adı zaten kayıtlı.', 'error')
            return render_template('register.html')
        
        # Varsayılan olarak Yazar rolü ile kayıt et
        if db.add_user(username, password, name, ['Yazar']):
            flash('Kayıt başarılı! Giriş yapabilirsiniz.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Kayıt sırasında bir hata oluştu.', 'error')
    
    return render_template('register.html')

@app.route('/switch-role', methods=['POST'])
@login_required
def switch_role():
    """Rol değiştir"""
    new_role = request.form.get('role', '').strip()
    
    if not new_role:
        flash('Geçersiz rol seçimi.', 'error')
        return redirect(url_for('dashboard'))
    
    user = db.get_user(session['username'])
    if not user:
        flash('Kullanıcı bulunamadı.', 'error')
        return redirect(url_for('dashboard'))
    
    user_roles = user.get('roles', [])
    
    # Kullanıcının bu role sahip olduğunu kontrol et
    if new_role not in user_roles:
        flash('Bu role sahip değilsiniz.', 'error')
        return redirect(url_for('dashboard'))
    
    # Session'da rolü güncelle
    session['user_role'] = new_role
    
    flash(f'Rol değiştirildi: {new_role}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """Çıkış"""
    session.clear()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('home'))

# ========== DASHBOARD ROUTES ==========

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard ana sayfa"""
    user = db.get_user(session['username'])
    user_roles = user.get('roles', [])
    current_role = session.get('user_role', user_roles[0] if user_roles else 'Yazar')
    
    # İstatistikler - aktif role göre
    stats = {}
    if current_role == 'Admin' or current_role == 'Editör':
        all_articles = db.get_all_articles()
        stats['total'] = len(all_articles)
        stats['pending'] = len([a for a in all_articles if a['status'] in ['Gönderildi', 'Editör İncelemede', 'Alan Editörü İncelemede']])
        stats['review'] = len([a for a in all_articles if a['status'] in ['Değerlendirmede', 'Hakemde']])
        stats['accepted'] = len([a for a in all_articles if a['status'] in ['Kabul Edildi', 'Yayınlandı']])
        stats['rejected'] = len([a for a in all_articles if a['status'] == 'Reddedildi'])
    elif current_role == 'Yazar':
        all_articles = db.get_all_articles()
        my_articles = [a for a in all_articles if a['author'] == session['username']]
        stats['total'] = len(my_articles)
        stats['pending'] = len([a for a in my_articles if a['status'] in ['Gönderildi', 'Editör İncelemede']])
        stats['review'] = len([a for a in my_articles if a['status'] in ['Değerlendirmede', 'Hakemde']])
        stats['accepted'] = len([a for a in my_articles if a['status'] in ['Kabul Edildi', 'Yayınlandı']])
        stats['rejected'] = len([a for a in my_articles if a['status'] == 'Reddedildi'])
    elif current_role == 'Hakem':
        my_reviews = db.get_articles_by_reviewer(session['username'])
        stats['total'] = len(my_reviews)
        stats['pending'] = len([a for a in my_reviews if a['status'] == 'Değerlendirmede'])
        stats['review'] = len([a for a in my_reviews if a['status'] == 'Değerlendirmede'])
        stats['accepted'] = 0
        stats['rejected'] = 0
    elif current_role == 'Alan Editörü':
        all_articles = db.get_all_articles()
        my_articles = [a for a in all_articles if a.get('field_editor') == session['username']]
        stats['total'] = len(my_articles)
        stats['pending'] = len([a for a in my_articles if a['status'] == 'Alan Editörü İncelemede'])
        stats['review'] = len([a for a in my_articles if a['status'] == 'Hakemde'])
        stats['accepted'] = len([a for a in my_articles if a.get('field_editor_recommendation')])
        stats['rejected'] = 0
    
    # Son aktiviteler (son 5 makale)
    all_articles_for_recent = db.get_all_articles()
    recent_articles = sorted(all_articles_for_recent, key=lambda x: x.get('created_at', '') or '', reverse=True)[:5]
    
    # Sağ sidebar için hızlı istatistikler
    quick_stats = stats.copy()
    if current_role == 'Admin':
        all_users_list = db.get_all_users()
        quick_stats['total_users'] = len(all_users_list)
    
    # Okunmamış mesajlar
    user_messages = db.get_messages_by_user(session['username'])
    unread_messages = [m for m in user_messages if not m.get('is_read', False)][:3]
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         user=user, 
                         recent_articles=recent_articles,
                         quick_stats=quick_stats,
                         unread_messages=unread_messages)

# ========== ARTICLE ROUTES ==========

@app.route('/submissions/new', methods=['GET', 'POST'])
@login_required
@role_required('Yazar', 'Admin')
def new_submission():
    """Yeni makale gönderme"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subtitle = request.form.get('subtitle', '').strip()
        keywords = request.form.get('keywords', '').strip()
        article_type = request.form.get('type', '').strip()
        field = request.form.get('field', '').strip()
        abstract_tr = request.form.get('abstract_tr', '').strip()
        abstract_en = request.form.get('abstract_en', '').strip()
        
        if not title:
            flash('Lütfen makale başlığını girin.', 'error')
            return render_template('new_submission.html')
        
        if 'file' not in request.files:
            flash('Lütfen makale dosyasını seçin.', 'error')
            return render_template('new_submission.html')
        
        file = request.files['file']
        if file.filename == '':
            flash('Lütfen makale dosyasını seçin.', 'error')
            return render_template('new_submission.html')
        
        if file and allowed_file(file.filename):
            # Makale ID oluştur
            all_articles = db.get_all_articles()
            article_id = f"MAK-{datetime.now().year}-{len(all_articles)+1:04d}"
            
            # Dosyayı kaydet
            filename = secure_filename(f"{article_id}{os.path.splitext(file.filename)[1]}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Editör ataması
            all_editors = [u['username'] for u in db.get_all_users() if 'Editör' in u.get('roles', []) and u['username'] != 'admin']
            assigned_editor = all_editors[0] if all_editors else None
            
            # AI ile alan editörü ataması
            assigned_field_editor = None
            if abstract_tr or abstract_en or keywords:
                detected_field = ai_classifier.classify_article(
                    title=title,
                    abstract_tr=abstract_tr,
                    abstract_en=abstract_en,
                    keywords=keywords,
                    field=field
                )
                
                if detected_field:
                    all_field_editors = [u['username'] for u in db.get_all_users() 
                                        if 'Alan Editörü' in u.get('roles', []) and u['username'] != 'admin']
                    
                    if all_field_editors:
                        editor_expertise = {}
                        for fe_username in all_field_editors:
                            fe_user = db.get_user(fe_username)
                            if fe_user and fe_user.get('expertise_field'):
                                editor_expertise[fe_username] = fe_user['expertise_field']
                        
                        assigned_field_editor = ai_classifier.assign_field_editor(
                            detected_field, all_field_editors, editor_expertise
                        )
            
            # Durum belirleme
            if assigned_field_editor:
                article_status = "Alan Editörü İncelemede"
            elif assigned_editor:
                article_status = "Editör İncelemede"
            else:
                article_status = "Beklemede"
            
            # Makale oluştur
            user = db.get_user(session['username'])
            article = {
                "id": article_id,
                "title": title,
                "author": session['username'],
                "authors": user.get('name', session['username']) if user else session['username'],
                "status": article_status,
                "editor": assigned_editor,
                "field_editor": assigned_field_editor,
                "reviewers": [],
                "decisions": {},
                "file_path": file_path,
                "scheduled": False
            }
            
            try:
                if db.add_article(article):
                    flash(f'Makale başarıyla gönderildi! Makale ID: {article_id}', 'success')
                    if assigned_field_editor:
                        flash(f'Alan Editörü {assigned_field_editor} otomatik atandı.', 'info')
                    return redirect(url_for('my_articles'))
                else:
                    flash('Makale gönderilirken bir hata oluştu. Lütfen tekrar deneyin.', 'error')
            except Exception as e:
                print(f"Error in new_submission: {e}")
                import traceback
                traceback.print_exc()
                flash(f'Makale gönderilirken bir hata oluştu: {str(e)}', 'error')
        else:
            flash('Geçersiz dosya formatı. Lütfen Word, PDF veya TXT dosyası yükleyin.', 'error')
    
    return render_template('new_submission.html')

@app.route('/submissions')
@login_required
@role_required('Admin', 'Editör')
def submissions():
    """Tüm gönderilen makaleler"""
    articles = db.get_all_articles()
    return render_template('submissions.html', articles=articles)

@app.route('/submissions/my')
@login_required
@role_required('Yazar', 'Admin')
def my_articles():
    """Kullanıcının makaleleri"""
    all_articles = db.get_all_articles()
    articles = [a for a in all_articles if a['author'] == session['username']]
    return render_template('my_articles.html', articles=articles)

@app.route('/article/<article_id>', methods=['GET', 'POST'])
@login_required
def article_detail(article_id):
    """Makale detay sayfası"""
    article = db.get_article(article_id)
    if not article:
        flash('Makale bulunamadı.', 'error')
        return redirect(url_for('dashboard'))
    
    # Yetki kontrolü
    user_roles = session.get('user_roles', [])
    if article['author'] != session['username'] and 'Admin' not in user_roles and 'Editör' not in user_roles:
        if 'Alan Editörü' in user_roles and article.get('field_editor') != session['username']:
            if 'Hakem' in user_roles and session['username'] not in article.get('reviewers', []):
                flash('Bu makaleye erişim yetkiniz yok.', 'error')
                return redirect(url_for('dashboard'))
    
    # POST işlemleri
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'assign_field_editor' and ('Admin' in user_roles or 'Editör' in user_roles):
            field_editor = request.form.get('field_editor', '').strip()
            if field_editor:
                db.update_article(article_id, {
                    'field_editor': field_editor,
                    'editor': session['username'],
                    'status': 'Alan Editörü İncelemede'
                })
                flash(f'Alan editörü atandı: {field_editor}', 'success')
                return redirect(url_for('article_detail', article_id=article_id))
        
        elif action == 'assign_reviewers' and 'Alan Editörü' in user_roles:
            reviewers = request.form.getlist('reviewers')
            if len(reviewers) == 2:
                db.update_article(article_id, {
                    'reviewers': reviewers,
                    'status': 'Hakemde'
                })
                # Hakemlere mesaj gönder
                for reviewer in reviewers:
                    db.add_message(
                        article_id,
                        session['username'],
                        reviewer,
                        f'Hakemlik Görevi: {article.get("title", article_id)}',
                        f'Sayın {reviewer},\n\nMakale değerlendirmesi için size görev atanmıştır.\n\nMakale: {article.get("title", article_id)}\nMakale ID: {article_id}\n\nLütfen makaleyi inceleyip değerlendirmenizi yapınız.'
                    )
                flash('Hakemler başarıyla atandı.', 'success')
                return redirect(url_for('article_detail', article_id=article_id))
            else:
                flash('Lütfen tam olarak 2 hakem seçin.', 'error')
        
        elif action == 'assign_third_reviewer' and 'Alan Editörü' in user_roles:
            third_reviewer = request.form.get('third_reviewer', '').strip()
            if third_reviewer:
                reviewers = article.get('reviewers', [])
                if third_reviewer not in reviewers:
                    reviewers.append(third_reviewer)
                    db.update_article(article_id, {'reviewers': reviewers})
                    flash(f'3. hakem atandı: {third_reviewer}', 'success')
                return redirect(url_for('article_detail', article_id=article_id))
        
        elif action == 'reject_article' and ('Admin' in user_roles or 'Editör' in user_roles):
            reason = request.form.get('rejection_reason', '').strip()
            if reason:
                db.update_article(article_id, {
                    'status': 'Reddedildi',
                    'editor': session['username']
                })
                # Yazara mesaj gönder
                db.add_message(
                    article_id,
                    session['username'],
                    article['author'],
                    f'Makale Reddedildi: {article.get("title", article_id)}',
                    f'Sayın Yazar,\n\nMakaleniz ön inceleme aşamasında reddedilmiştir.\n\nReddetme Nedeni:\n{reason}\n\nSaygılarımızla,\nEditör'
                )
                flash('Makale reddedildi ve yazara bildirildi.', 'success')
                return redirect(url_for('article_detail', article_id=article_id))
        
        elif action == 'update_status' and ('Admin' in user_roles or 'Editör' in user_roles):
            new_status = request.form.get('new_status', '').strip()
            if new_status:
                db.update_article(article_id, {'status': new_status})
                flash(f'Makale durumu güncellendi: {new_status}', 'success')
                return redirect(url_for('article_detail', article_id=article_id))
        
        elif action == 'field_editor_recommendation' and 'Alan Editörü' in user_roles:
            recommendation = request.form.get('recommendation', '').strip()
            if recommendation:
                db.update_article(article_id, {'field_editor_recommendation': recommendation})
                flash('Alan editörü önerisi kaydedildi.', 'success')
                return redirect(url_for('article_detail', article_id=article_id))
    
    reviews = db.get_reviews_by_article(article_id)
    messages = db.get_messages_by_article(article_id)
    
    # Kullanıcı listeleri
    field_editors = [u for u in db.get_all_users() if 'Alan Editörü' in u.get('roles', []) and u['username'] != 'admin']
    reviewers_list = [u for u in db.get_all_users() if 'Hakem' in u.get('roles', [])]
    
    return render_template('article_detail.html', 
                         article=article, 
                         reviews=reviews, 
                         messages=messages,
                         field_editors=field_editors,
                         reviewers_list=reviewers_list)

@app.route('/review/<review_id>/download')
@login_required
def download_review(review_id):
    """Hakem değerlendirme dosyasını indir"""
    # Review bilgisini almak için tüm makaleleri kontrol et
    all_articles = db.get_all_articles()
    review = None
    article_obj = None
    
    try:
        review_id_int = int(review_id)
    except ValueError:
        flash('Geçersiz değerlendirme ID.', 'error')
        return redirect(url_for('dashboard'))
    
    for article in all_articles:
        reviews = db.get_reviews_by_article(article['id'])
        for r in reviews:
            if r['id'] == review_id_int:
                review = r
                article_obj = article
                break
        if review:
            break
    
    if not review:
        flash('Değerlendirme bulunamadı.', 'error')
        return redirect(url_for('dashboard'))
    
    # Yetki kontrolü
    user_roles = session.get('user_roles', [])
    if review['reviewer_username'] != session['username'] and 'Admin' not in user_roles:
        if 'Editör' not in user_roles and 'Alan Editörü' not in user_roles:
            flash('Bu dosyaya erişim yetkiniz yok.', 'error')
            return redirect(url_for('dashboard'))
    
    if review.get('file_path') and os.path.exists(review['file_path']):
        return send_file(review['file_path'], as_attachment=True)
    else:
        flash('Dosya bulunamadı.', 'error')
        if article_obj:
            return redirect(url_for('article_detail', article_id=article_obj['id']))
        else:
            return redirect(url_for('dashboard'))

@app.route('/article/<article_id>/download')
@login_required
def download_article(article_id):
    """Makale dosyasını indir"""
    article = db.get_article(article_id)
    if not article:
        flash('Makale bulunamadı.', 'error')
        return redirect(url_for('dashboard'))
    
    # Yetki kontrolü
    user_roles = session.get('user_roles', [])
    if article['author'] != session['username'] and 'Admin' not in user_roles and 'Editör' not in user_roles:
        if 'Alan Editörü' in user_roles and article.get('field_editor') != session['username']:
            if 'Hakem' in user_roles and session['username'] not in article.get('reviewers', []):
                flash('Bu dosyaya erişim yetkiniz yok.', 'error')
                return redirect(url_for('dashboard'))
    
    if article.get('file_path') and os.path.exists(article['file_path']):
        return send_file(article['file_path'], as_attachment=True)
    else:
        flash('Dosya bulunamadı.', 'error')
        return redirect(url_for('article_detail', article_id=article_id))

# ========== REVIEWER ROUTES ==========

@app.route('/reviews/assigned')
@login_required
@role_required('Hakem')
def assigned_reviews():
    """Hakeme atanan makaleler"""
    articles = db.get_articles_by_reviewer(session['username'])
    return render_template('assigned_reviews.html', articles=articles)

@app.route('/reviews/evaluated')
@login_required
@role_required('Hakem')
def evaluated_reviews():
    """Hakemin değerlendirdiği makaleler"""
    articles = db.get_articles_by_reviewer(session['username'])
    evaluated = []
    for article in articles:
        reviews = db.get_reviews_by_article(article['id'])
        if any(r['reviewer_username'] == session['username'] for r in reviews):
            evaluated.append(article)
    return render_template('evaluated_reviews.html', articles=evaluated)

@app.route('/article/<article_id>/review', methods=['GET', 'POST'])
@login_required
@role_required('Hakem')
def submit_review(article_id):
    """Hakem değerlendirmesi gönder"""
    article = db.get_article(article_id)
    if not article:
        flash('Makale bulunamadı.', 'error')
        return redirect(url_for('dashboard'))
    
    if session['username'] not in article.get('reviewers', []):
        flash('Bu makale size atanmamış.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        decision = request.form.get('decision', '').strip()
        comment = request.form.get('comment', '').strip()
        
        if not decision:
            flash('Lütfen bir karar seçin.', 'error')
            return render_template('submit_review.html', article=article)
        
        # Dosya yükleme
        file_path = ""
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{article_id}_rev{len(db.get_reviews_by_article(article_id))+1}_{decision}.{os.path.splitext(file.filename)[1][1:]}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'reviews', filename)
                file.save(file_path)
        
        if db.add_review(article_id, session['username'], decision, comment, file_path):
            flash('Değerlendirme başarıyla gönderildi.', 'success')
            return redirect(url_for('assigned_reviews'))
        else:
            flash('Değerlendirme gönderilirken bir hata oluştu.', 'error')
    
    return render_template('submit_review.html', article=article)

# ========== EDITOR ROUTES ==========

@app.route('/articles/pending')
@login_required
@role_required('Editör', 'Admin')
def pending_articles():
    """Onay bekleyen makaleler"""
    articles = db.get_articles_by_status('Gönderildi')
    articles += db.get_articles_by_status('Editör İncelemede')
    return render_template('pending_articles.html', articles=articles)

@app.route('/articles/review')
@login_required
@role_required('Editör', 'Admin')
def review_articles():
    """Değerlendirmede olan makaleler"""
    articles = db.get_articles_by_status('Değerlendirmede')
    articles += db.get_articles_by_status('Alan Editörü İncelemede')
    return render_template('review_articles.html', articles=articles)

@app.route('/articles/accepted')
@login_required
@role_required('Editör', 'Admin')
def accepted_articles():
    """Kabul edilen makaleler"""
    articles = db.get_articles_by_status('Kabul Edildi')
    return render_template('accepted_articles.html', articles=articles)

@app.route('/articles/rejected')
@login_required
@role_required('Editör', 'Admin')
def rejected_articles():
    """Reddedilen makaleler"""
    articles = db.get_articles_by_status('Reddedildi')
    return render_template('rejected_articles.html', articles=articles)

@app.route('/reviewers')
@login_required
@role_required('Editör', 'Admin')
def reviewers():
    """Hakem listesi"""
    reviewers = [u for u in db.get_all_users() if 'Hakem' in u.get('roles', [])]
    return render_template('reviewers.html', reviewers=reviewers)

# ========== USER MANAGEMENT ROUTES ==========

@app.route('/users', methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def user_management():
    """Kullanıcı yönetimi"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'assign_role':
            username = request.form.get('username', '').strip()
            role = request.form.get('role', '').strip()
            expertise_field = request.form.get('expertise_field', '').strip() or None
            
            if username and role:
                user = db.get_user(username)
                if user:
                    roles = user.get('roles', []).copy()
                    if role == 'Admin':
                        roles = ['Admin', 'Editör', 'Alan Editörü', 'Hakem', 'Yazar']
                    else:
                        if role not in roles:
                            roles.append(role)
                        if role in ['Editör', 'Alan Editörü', 'Hakem', 'Admin'] and 'Yazar' not in roles:
                            roles.append('Yazar')
                    
                    db.update_user_roles(username, roles)
                    if role == 'Alan Editörü' and expertise_field:
                        db.update_user_expertise_field(username, expertise_field)
                    flash(f'Rol başarıyla atandı: {username} -> {role}', 'success')
        
        elif action == 'remove_role':
            username = request.form.get('username', '').strip()
            role_to_remove = request.form.get('role_to_remove', '').strip()
            
            if username and role_to_remove:
                user = db.get_user(username)
                if user:
                    roles = user.get('roles', []).copy()
                    if role_to_remove in roles and role_to_remove != 'Admin':
                        roles.remove(role_to_remove)
                        db.update_user_roles(username, roles)
                        flash(f'Rol başarıyla kaldırıldı: {username} -> {role_to_remove}', 'success')
        
        elif action == 'create_user':
            name = request.form.get('new_name', '').strip()
            username = request.form.get('new_username', '').strip()
            password = request.form.get('new_password', '').strip()
            role = request.form.get('new_role', '').strip()
            expertise_field = request.form.get('new_expertise_field', '').strip() or None
            
            if all([name, username, password, role]):
                if db.get_user(username):
                    flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
                else:
                    roles = [role]
                    if role in ['Editör', 'Alan Editörü', 'Hakem', 'Admin']:
                        roles.append('Yazar')
                    
                    try:
                        if db.add_user(username, password, name, roles, expertise_field):
                            flash(f'Kullanıcı başarıyla oluşturuldu: {username}', 'success')
                        else:
                            flash('Kullanıcı oluşturulurken hata oluştu. Kullanıcı adı zaten kullanılıyor olabilir.', 'error')
                    except Exception as e:
                        print(f"Error in create_user: {e}")
                        import traceback
                        traceback.print_exc()
                        flash(f'Kullanıcı oluşturulurken hata oluştu: {str(e)}', 'error')
            else:
                flash('Lütfen tüm alanları doldurun.', 'error')
        
        elif action == 'reset_password':
            username = request.form.get('reset_username', '').strip()
            new_password = request.form.get('reset_password', '').strip()
            
            if username and new_password:
                db.update_user_password(username, new_password)
                flash(f'Şifre başarıyla sıfırlandı: {username}', 'success')
            else:
                flash('Lütfen kullanıcı adı ve yeni şifreyi girin.', 'error')
        
        elif action == 'delete_user':
            username = request.form.get('delete_username', '').strip()
            
            if username and username != 'admin':
                db.delete_user(username)
                flash(f'Kullanıcı başarıyla silindi: {username}', 'success')
            else:
                flash('Admin kullanıcısı silinemez.', 'error')
        
        return redirect(url_for('user_management'))
    
    users = db.get_all_users()
    return render_template('user_management.html', users=users)

# ========== MESSAGE ROUTES ==========

@app.route('/messages')
@login_required
def messages():
    """Mesajlar"""
    user_messages = db.get_messages_by_user(session['username'])
    return render_template('messages.html', messages=user_messages)

@app.route('/messages/sent')
@login_required
def sent_messages():
    """Gönderilen mesajlar"""
    sent = db.get_messages_by_from_user(session['username'])
    return render_template('sent_messages.html', messages=sent)

@app.route('/messages/send', methods=['GET', 'POST'])
@login_required
def send_message():
    """Mesaj gönder"""
    if request.method == 'POST':
        article_id = request.form.get('article_id', '').strip()
        to_user = request.form.get('to_user', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if all([article_id, to_user, subject, message]):
            if db.add_message(article_id, session['username'], to_user, subject, message):
                flash('Mesaj başarıyla gönderildi.', 'success')
                return redirect(url_for('article_detail', article_id=article_id))
            else:
                flash('Mesaj gönderilirken hata oluştu.', 'error')
        else:
            flash('Lütfen tüm alanları doldurun.', 'error')
    
    article_id = request.args.get('article_id', '')
    to_user = request.args.get('to_user', '')
    return render_template('send_message.html', article_id=article_id, to_user=to_user)

@app.route('/contact-messages')
@login_required
@role_required('Admin')
def contact_messages():
    """İletişim mesajları"""
    messages = db.get_contact_messages()
    return render_template('contact_messages.html', messages=messages)

# ========== STATISTICS ROUTE ==========

@app.route('/statistics')
@login_required
def statistics():
    """İstatistikler sayfası"""
    user = db.get_user(session['username'])
    user_roles = user.get('roles', [])
    all_articles = db.get_all_articles()
    all_users = db.get_all_users()
    
    stats = {}
    if 'Admin' in user_roles:
        stats['total_users'] = len(all_users)
        stats['total_articles'] = len(all_articles)
        stats['published'] = len([a for a in all_articles if a.get('status') == 'Yayınlandı'])
        stats['pending'] = len([a for a in all_articles if a.get('status') in ['Editör İncelemede', 'Alan Editörü İncelemede']])
        stats['in_review'] = len([a for a in all_articles if a.get('status') == 'Hakemde'])
        stats['rejected'] = len([a for a in all_articles if 'Red' in a.get('status', '')])
        
        # Rol dağılımı
        role_dist = {}
        for u in all_users:
            for role in u.get('roles', []):
                if role != 'Yazar':
                    role_dist[role] = role_dist.get(role, 0) + 1
        stats['role_distribution'] = role_dist
    elif 'Editör' in user_roles:
        stats['total_articles'] = len(all_articles)
        stats['pending'] = len([a for a in all_articles if a.get('status') in ['Editör İncelemede', 'Alan Editörü İncelemede']])
        stats['in_review'] = len([a for a in all_articles if a.get('status') in ['Hakemde', 'Alan Editörü İncelemede']])
        stats['accepted'] = len([a for a in all_articles if 'Kabul' in a.get('status', '')])
        stats['published'] = len([a for a in all_articles if a.get('status') == 'Yayınlandı'])
        stats['rejected'] = len([a for a in all_articles if 'Red' in a.get('status', '')])
    elif 'Yazar' in user_roles:
        my_articles = [a for a in all_articles if a.get('author') == session['username']]
        stats['total_articles'] = len(my_articles)
        stats['submitted'] = len([a for a in my_articles if a.get('status') in ['Editör İncelemede', 'Alan Editörü İncelemede']])
        stats['in_review'] = len([a for a in my_articles if a.get('status') == 'Hakemde'])
        stats['accepted'] = len([a for a in my_articles if 'Kabul' in a.get('status', '')])
        stats['published'] = len([a for a in my_articles if a.get('status') == 'Yayınlandı'])
        stats['rejected'] = len([a for a in my_articles if 'Red' in a.get('status', '')])
    elif 'Hakem' in user_roles:
        assigned_articles = db.get_articles_by_reviewer(session['username'])
        evaluated = []
        for a in assigned_articles:
            reviews = db.get_reviews_by_article(a['id'])
            if any(r['reviewer_username'] == session['username'] for r in reviews):
                evaluated.append(a)
        
        stats['assigned'] = len(assigned_articles)
        stats['evaluated'] = len(evaluated)
        stats['pending'] = len(assigned_articles) - len(evaluated)
        
        # Karar dağılımı
        accepted_count = 0
        correction_count = 0
        rejected_count = 0
        for a in evaluated:
            reviews = db.get_reviews_by_article(a['id'])
            for r in reviews:
                if r['reviewer_username'] == session['username']:
                    if r['decision'] == 'Kabul':
                        accepted_count += 1
                    elif r['decision'] == 'Düzeltme':
                        correction_count += 1
                    elif r['decision'] == 'Red':
                        rejected_count += 1
        
        stats['accepted_decisions'] = accepted_count
        stats['correction_decisions'] = correction_count
        stats['rejected_decisions'] = rejected_count
    elif 'Alan Editörü' in user_roles:
        my_articles = [a for a in all_articles if a.get('field_editor') == session['username']]
        stats['total_articles'] = len(my_articles)
        stats['pending'] = len([a for a in my_articles if a.get('status') == 'Alan Editörü İncelemede'])
        stats['in_review'] = len([a for a in my_articles if a.get('status') == 'Hakemde'])
        stats['reviewer_decision'] = len([a for a in my_articles if a.get('status') == 'Hakem Kararı'])
        stats['recommended'] = len([a for a in my_articles if a.get('field_editor_recommendation')])
        stats['completed'] = len([a for a in my_articles if a.get('status') == 'Yayınlandı'])
    
    return render_template('statistics.html', stats=stats, user=user)

# ========== SETTINGS ROUTE ==========

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Ayarlar sayfası"""
    user = db.get_user(session['username'])
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_name':
            new_name = request.form.get('name', '').strip()
            if new_name:
                db.update_user_name(session['username'], new_name)
                session['user_name'] = new_name
                flash('İsim başarıyla güncellendi.', 'success')
            else:
                flash('İsim boş olamaz.', 'error')
        
        elif action == 'update_password':
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not current_password or not new_password or not confirm_password:
                flash('Lütfen tüm alanları doldurun.', 'error')
            elif user.get('password') != current_password:
                flash('Mevcut şifre hatalı.', 'error')
            elif new_password != confirm_password:
                flash('Yeni şifreler eşleşmiyor.', 'error')
            else:
                db.update_user_password(session['username'], new_password)
                flash('Şifre başarıyla güncellendi.', 'success')
        
        return redirect(url_for('settings'))
    
    return render_template('settings.html', user=user)

# ========== OTHER ROUTES ==========
# (about, archive, issue_detail routes are already defined in PUBLIC ROUTES section)

@app.route('/publish-issue', methods=['GET', 'POST'])
@login_required
@role_required('Editör', 'Admin')
def publish_issue():
    """Sayı oluştur ve yayınla"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create_issue':
            volume = request.form.get('volume', '').strip()
            issue = request.form.get('issue', '').strip()
            year = request.form.get('year', '').strip()
            article_ids = request.form.getlist('article_ids')
            
            # Eğer cilt numarası boşsa, yıl için otomatik hesapla
            # Yıl arttıkça cilt numarası da artmalı: önceki yılların maksimum cilt numarasına +1
            if not volume and year:
                # Önce o yıl için maksimum cilt numarasını kontrol et
                max_volume_for_year = db.get_max_volume_for_year(year)
                if max_volume_for_year > 0:
                    # O yıl için zaten cilt varsa, o yılın maksimum cilt numarasına +1
                    volume = str(max_volume_for_year + 1)
                else:
                    # O yıl için cilt yoksa, önceki yılların maksimum cilt numarasına +1
                    max_volume_before = db.get_max_volume_before_year(year)
                    volume = str(max_volume_before + 1) if max_volume_before > 0 else "1"
            
            if all([volume, issue, year]) and article_ids:
                # Makaleleri sayıya ata ve sayfa numaraları ver
                start_page = 1
                for idx, article_id in enumerate(article_ids):
                    article = db.get_article(article_id)
                    if article:
                        # Sayfa numarası hesapla (her makale için varsayılan 10 sayfa)
                        pages_per_article = 10
                        end_page = start_page + pages_per_article - 1
                        pages = f"{start_page}-{end_page}"
                        start_page = end_page + 1
                        
                        db.update_article(article_id, {
                            'volume': volume,
                            'issue': issue,
                            'year': year,
                            'status': 'Yayınlandı',
                            'scheduled': 1,
                            'pages': pages
                        })
                
                flash(f'Sayı başarıyla oluşturuldu: Cilt {volume}, Sayı {issue} ({year}) - {len(article_ids)} makale yayınlandı', 'success')
                return redirect(url_for('publish_issue'))
            else:
                flash('Lütfen tüm alanları doldurun ve en az bir makale seçin.', 'error')
        
        elif action == 'schedule_article':
            article_id = request.form.get('article_id', '').strip()
            if article_id:
                db.update_article(article_id, {'scheduled': 1})
                flash('Makale yayına hazır olarak işaretlendi.', 'success')
                return redirect(url_for('publish_issue'))
    
    ready_articles = db.get_ready_to_publish_articles()
    all_accepted = [a for a in db.get_all_articles() if a.get('status') == 'Kabul Edildi']
    
    # Mevcut yıl için maksimum cilt numarasını hesapla (varsayılan yıl için)
    # Yıl arttıkça cilt numarası da artmalı
    current_year = str(datetime.now().year)
    max_volume_for_year = db.get_max_volume_for_year(current_year)
    if max_volume_for_year > 0:
        # Bu yıl için zaten cilt varsa, o yılın maksimum cilt numarasına +1
        suggested_volume = str(max_volume_for_year + 1)
    else:
        # Bu yıl için cilt yoksa, önceki yılların maksimum cilt numarasına +1
        max_volume_before = db.get_max_volume_before_year(current_year)
        suggested_volume = str(max_volume_before + 1) if max_volume_before > 0 else "1"
    
    return render_template('publish_issue.html', 
                         ready_articles=ready_articles,
                         all_accepted=all_accepted,
                         suggested_volume=suggested_volume,
                         current_year=current_year)

@app.route('/assigned-articles-fe')
@login_required
@role_required('Alan Editörü')
def assigned_articles_fe():
    """Alan editörüne atanan makaleler"""
    all_articles = db.get_all_articles()
    articles = [a for a in all_articles if a.get('field_editor') == session['username']]
    return render_template('assigned_articles_fe.html', articles=articles)

@app.route('/reviewer-decisions-fe')
@login_required
@role_required('Alan Editörü')
def reviewer_decisions_fe():
    """Alan editörü için hakem kararları"""
    all_articles = db.get_all_articles()
    articles = [a for a in all_articles if a.get('field_editor') == session['username']]
    return render_template('reviewer_decisions_fe.html', articles=articles)

@app.route('/my-publications')
@login_required
@role_required('Yazar', 'Admin')
def my_publications():
    """Yazarın yayınları"""
    all_articles = db.get_all_articles()
    articles = [a for a in all_articles if a['author'] == session['username'] and a['status'] == 'Yayınlandı']
    return render_template('my_publications.html', articles=articles)

# ========== KEŞFET SAYFALARI ==========

@app.route('/discover/aim-and-scope')
def discover_aim_and_scope():
    """Amaç ve Kapsam sayfası"""
    return render_template('discover_aim_and_scope.html')

@app.route('/discover/writing-guidelines')
def discover_writing_guidelines():
    """Yazım Kuralları sayfası"""
    return render_template('discover_writing_guidelines.html')

@app.route('/discover/ethics-policy')
def discover_ethics_policy():
    """Etik İlkeler ve Yayın Politikası sayfası"""
    return render_template('discover_ethics_policy.html')

@app.route('/discover/fee-policy')
def discover_fee_policy():
    """Ücret Politikası sayfası"""
    return render_template('discover_fee_policy.html')

@app.route('/discover/editorial-boards')
def discover_editorial_boards():
    """Dergi Kurulları sayfası"""
    return render_template('discover_editorial_boards.html')

@app.route('/discover/indexes')
def discover_indexes():
    """Dizinler sayfası"""
    return render_template('discover_indexes.html')

# ========== HAKEMLİK İSTEĞİ ==========

@app.route('/reviewer-request', methods=['GET', 'POST'])
def reviewer_request():
    """Hakemlik isteği formu"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        institution = request.form.get('institution', '').strip()
        expertise = request.form.get('expertise', '').strip()
        cv = request.form.get('cv', '').strip()
        notes = request.form.get('notes', '').strip()
        
        if not all([name, email, institution, expertise, cv]):
            flash('Lütfen zorunlu alanları doldurun (* işaretli alanlar).', 'error')
            return render_template('reviewer_request.html')
        
        if "@" not in email:
            flash('Lütfen geçerli bir e-posta adresi girin.', 'error')
            return render_template('reviewer_request.html')
        
        # Admin kullanıcısını bul
        admin_user = db.get_user("admin")
        if not admin_user:
            flash('Admin kullanıcısı bulunamadı.', 'error')
            return render_template('reviewer_request.html')
        
        # Mesaj içeriği oluştur
        message_content = f"""Hakemlik İsteği

Ad Soyad: {name}
E-posta: {email}
Kurum/Üniversite: {institution}
Uzmanlık Alanları: {expertise}

Özgeçmiş ve Deneyim:
{cv}
"""
        if notes:
            message_content += f"\nEk Notlar:\n{notes}"
        
        # Admin'e mesaj gönder
        general_id = "GENEL-HAKEMLIK-ISTEKLERI"
        db.add_message(
            general_id,
            email,
            "admin",
            f"Hakemlik İsteği - {name}",
            message_content
        )
        
        flash('Hakemlik isteğiniz admin\'e gönderildi. İsteğiniz değerlendirildikten sonra size dönüş yapılacaktır.', 'success')
        return redirect(url_for('home'))
    
    return render_template('reviewer_request.html')

# ========== GÖNDERİLEN KARARLAR (HAKEM) ==========

@app.route('/sent-decisions')
@login_required
@role_required('Hakem', 'Admin')
def sent_decisions():
    """Hakemlerin gönderdiği kararları göster"""
    all_articles = db.get_all_articles()
    my_decisions = []
    
    # Reviews tablosundan bu hakemin tüm kararlarını al
    for art in all_articles:
        reviews = db.get_reviews_by_article(art["id"])
        for review in reviews:
            if review["reviewer_username"] == session['username']:
                my_decisions.append({
                    "article": art,
                    "review": review,
                    "decision": review.get("decision", "")
                })
    
    # Tarihe göre sırala (en yeni önce)
    my_decisions.sort(key=lambda x: x["review"].get("created_at", ""), reverse=True)
    
    return render_template('sent_decisions.html', decisions=my_decisions)

# ========== API ROUTES ==========

@app.route('/api/max-volume/<year>')
@login_required
def api_max_volume(year):
    """Belirli bir yıl için önerilen cilt numarasını döndür (yıl arttıkça cilt de artar)"""
    try:
        # Önce o yıl için maksimum cilt numarasını kontrol et
        max_volume_for_year = db.get_max_volume_for_year(year)
        if max_volume_for_year > 0:
            # O yıl için zaten cilt varsa, o yılın maksimum cilt numarasına +1
            suggested_volume = max_volume_for_year + 1
        else:
            # O yıl için cilt yoksa, önceki yılların maksimum cilt numarasına +1
            max_volume_before = db.get_max_volume_before_year(year)
            suggested_volume = max_volume_before + 1 if max_volume_before > 0 else 1
        return jsonify({'max_volume': suggested_volume - 1, 'suggested_volume': suggested_volume})
    except Exception as e:
        return jsonify({'error': str(e), 'max_volume': 0, 'suggested_volume': 1}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
