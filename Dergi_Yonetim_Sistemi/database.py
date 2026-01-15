import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class Database:
    def __init__(self, db_name="dergi_sistemi.db"):
        # Veritabanı dosyasını Dergi_Yonetim_Sistemi klasöründe oluştur
        if not os.path.isabs(db_name):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_name = os.path.join(base_dir, db_name)
        else:
            self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Veritabanı bağlantısı oluştur"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Sözlük benzeri erişim için
        return conn
    
    def init_database(self):
        """Veritabanı tablolarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Kullanıcılar tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                roles TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Makaleler tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                authors TEXT,
                pages TEXT,
                status TEXT NOT NULL,
                volume TEXT,
                issue TEXT,
                year TEXT,
                editor TEXT,
                field_editor TEXT,
                reviewers TEXT,
                decisions TEXT,
                file_path TEXT,
                scheduled INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Eğer file_path sütunu yoksa ekle (migration)
        try:
            cursor.execute("ALTER TABLE articles ADD COLUMN file_path TEXT")
        except sqlite3.OperationalError:
            pass  # Sütun zaten varsa
        
        # Eğer field_editor_recommendation sütunu yoksa ekle (migration)
        try:
            cursor.execute("ALTER TABLE articles ADD COLUMN field_editor_recommendation TEXT")
        except sqlite3.OperationalError:
            pass  # Sütun zaten varsa
        
        # Eğer expertise_field sütunu yoksa ekle (migration - alan editörü uzmanlık alanı)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN expertise_field TEXT")
        except sqlite3.OperationalError:
            pass  # Sütun zaten varsa
        
        # Hakem kararları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT NOT NULL,
                reviewer_username TEXT NOT NULL,
                decision TEXT NOT NULL,
                comment TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles(id),
                FOREIGN KEY (reviewer_username) REFERENCES users(username)
            )
        """)
        
        # Eğer file_path sütunu yoksa ekle (migration)
        try:
            cursor.execute("ALTER TABLE reviews ADD COLUMN file_path TEXT")
        except sqlite3.OperationalError:
            pass  # Sütun zaten varsa
        
        # Mesajlaşma tablosu (yazarlarla iletişim için)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id TEXT NOT NULL,
                from_user TEXT NOT NULL,
                to_user TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles(id),
                FOREIGN KEY (from_user) REFERENCES users(username),
                FOREIGN KEY (to_user) REFERENCES users(username)
            )
        """)
        
        # Dergi sayıları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                volume TEXT NOT NULL,
                issue TEXT NOT NULL,
                year TEXT NOT NULL,
                published_date TEXT,
                is_published INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(volume, issue, year)
            )
        """)
        
        # İletişim mesajları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    # Kullanıcı işlemleri
    def add_user(self, username: str, password: str, name: str, roles: List[str], expertise_field: Optional[str] = None):
        """Yeni kullanıcı ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        roles_str = ",".join(roles)
        try:
            cursor.execute("""
                INSERT INTO users (username, password, name, roles, expertise_field)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password, name, roles_str, expertise_field))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Kullanıcı bilgilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # expertise_field sütunu var mı kontrol et
            expertise_field = None
            try:
                if "expertise_field" in row.keys():
                    expertise_field = row["expertise_field"]
            except (KeyError, AttributeError):
                pass
            return {
                "username": row["username"],
                "password": row["password"],
                "name": row["name"],
                "roles": row["roles"].split(",") if row["roles"] else [],
                "expertise_field": expertise_field
            }
        return None
    
    def get_all_users(self) -> List[Dict]:
        """Tüm kullanıcıları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            # expertise_field sütunu var mı kontrol et
            expertise_field = None
            try:
                if "expertise_field" in row.keys():
                    expertise_field = row["expertise_field"]
            except (KeyError, AttributeError):
                pass
            users.append({
                "username": row["username"],
                "password": row["password"],
                "name": row["name"],
                "roles": row["roles"].split(",") if row["roles"] else [],
                "expertise_field": expertise_field
            })
        return users
    
    def update_user_roles(self, username: str, roles: List[str]):
        """Kullanıcı rollerini güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        roles_str = ",".join(roles)
        cursor.execute("""
            UPDATE users SET roles = ? WHERE username = ?
        """, (roles_str, username))
        conn.commit()
        conn.close()
    
    def update_user_expertise_field(self, username: str, expertise_field: Optional[str]):
        """Alan editörünün uzmanlık alanını güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET expertise_field = ? WHERE username = ?
        """, (expertise_field, username))
        conn.commit()
        conn.close()
    
    def update_user_password(self, username: str, new_password: str):
        """Kullanıcı şifresini güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET password = ? WHERE username = ?
        """, (new_password, username))
        conn.commit()
        conn.close()
    
    def update_user_name(self, username: str, new_name: str):
        """Kullanıcı adını güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET name = ? WHERE username = ?
        """, (new_name, username))
        conn.commit()
        conn.close()
    
    def get_field_editors_by_expertise(self, field_name: str) -> List[Dict]:
        """Belirli bir alanda uzman olan alan editörlerini getir"""
        all_users = self.get_all_users()
        field_editors = []
        for user in all_users:
            if "Alan Editörü" in user.get("roles", []) and user["username"] != "admin":
                if user.get("expertise_field") == field_name:
                    field_editors.append(user)
        return field_editors
    
    def delete_user(self, username: str):
        """Kullanıcı sil"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
    
    # Makale işlemleri
    def add_article(self, article: Dict):
        """Yeni makale ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        reviewers_str = ",".join(article.get("reviewers", [])) if article.get("reviewers") else ""
        decisions_str = json.dumps(article.get("decisions", {})) if article.get("decisions") else "{}"
        
        try:
            cursor.execute("""
                INSERT INTO articles (id, title, author, authors, pages, status, volume, issue, year,
                                    editor, field_editor, reviewers, decisions, file_path, scheduled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article.get("id"),
                article.get("title"),
                article.get("author", ""),
                article.get("authors", ""),
                article.get("pages", ""),
                article.get("status"),
                article.get("volume", ""),
                article.get("issue", ""),
                article.get("year", ""),
                article.get("editor"),
                article.get("field_editor"),
                reviewers_str,
                decisions_str,
                article.get("file_path", ""),
                article.get("scheduled", 0)
            ))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Database IntegrityError in add_article: {e}")
            conn.close()
            return False
        except Exception as e:
            print(f"Unexpected error in add_article: {e}")
            import traceback
            traceback.print_exc()
            conn.close()
            return False
    
    def get_article(self, article_id: str) -> Optional[Dict]:
        """Makale bilgilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_article_dict(row)
        return None
    
    def get_all_articles(self) -> List[Dict]:
        """Tüm makaleleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in rows:
            articles.append(self._row_to_article_dict(row))
        return articles
    
    def get_articles_by_status(self, status: str) -> List[Dict]:
        """Duruma göre makaleleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE status = ? ORDER BY created_at DESC", (status,))
        rows = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in rows:
            articles.append(self._row_to_article_dict(row))
        return articles
    
    def get_articles_by_reviewer(self, reviewer_username: str) -> List[Dict]:
        """Hakeme atanan makaleleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # LIKE sorgusu kullanarak önce filtreleme yap, sonra tam eşleşme kontrol et
        cursor.execute("SELECT * FROM articles WHERE reviewers LIKE ?", (f"%{reviewer_username}%",))
        rows = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in rows:
            article = self._row_to_article_dict(row)
            # Tam eşleşme kontrolü - reviewers listesinde bu hakem var mı?
            reviewers_list = article.get("reviewers", [])
            if reviewer_username in reviewers_list:
                articles.append(article)
        return articles
    
    def update_article(self, article_id: str, updates: Dict):
        """Makale bilgilerini güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Güncellenebilir alanlar
        allowed_fields = ["title", "status", "editor", "field_editor", "reviewers", "decisions", "scheduled", "field_editor_recommendation", "volume", "issue", "year", "pages"]
        set_clauses = []
        values = []
        
        for field in allowed_fields:
            if field in updates:
                set_clauses.append(f"{field} = ?")
                if field == "reviewers":
                    values.append(",".join(updates[field]) if isinstance(updates[field], list) else updates[field])
                elif field == "decisions":
                    values.append(json.dumps(updates[field]) if isinstance(updates[field], dict) else updates[field])
                else:
                    values.append(updates[field])
        
        if set_clauses:
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(article_id)
            query = f"UPDATE articles SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            result = True
        else:
            result = False
        
        conn.close()
        return result
    
    def _row_to_article_dict(self, row) -> Dict:
        """SQLite row'u dictionary'ye çevir"""
        # SQLite Row objesi için güvenli alan erişimi
        def safe_get(row, key, default=""):
            try:
                return row[key] if row[key] is not None else default
            except (KeyError, IndexError):
                return default
        
        # Reviewers ve decisions alanlarını güvenli şekilde parse et
        reviewers_str = safe_get(row, "reviewers", "")
        reviewers_list = []
        if reviewers_str:
            reviewers_list = [r.strip() for r in reviewers_str.split(",") if r.strip()]
        
        decisions_str = safe_get(row, "decisions", "")
        decisions_dict = {}
        if decisions_str:
            try:
                decisions_dict = json.loads(decisions_str)
            except (json.JSONDecodeError, TypeError):
                decisions_dict = {}
        
        article = {
            "id": row["id"],
            "title": row["title"],
            "author": row["author"],
            "authors": safe_get(row, "authors"),
            "pages": safe_get(row, "pages"),
            "status": row["status"],
            "volume": safe_get(row, "volume"),
            "issue": safe_get(row, "issue"),
            "year": safe_get(row, "year"),
            "editor": safe_get(row, "editor"),
            "field_editor": safe_get(row, "field_editor"),
            "reviewers": reviewers_list,
            "decisions": decisions_dict,
            "file_path": safe_get(row, "file_path"),
            "field_editor_recommendation": safe_get(row, "field_editor_recommendation"),
            "scheduled": bool(row["scheduled"]) if safe_get(row, "scheduled") else False,
            "created_at": safe_get(row, "created_at"),
            "updated_at": safe_get(row, "updated_at")
        }
        return article
    
    # Hakem kararları işlemleri
    def add_review(self, article_id: str, reviewer_username: str, decision: str, comment: str = "", file_path: str = ""):
        """Hakem kararı ekle"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Review'ı ekle
            cursor.execute("""
                INSERT INTO reviews (article_id, reviewer_username, decision, comment, file_path)
                VALUES (?, ?, ?, ?, ?)
            """, (article_id, reviewer_username, decision, comment, file_path))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"HATA: add_review hatası: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return False
    
    def get_reviews_by_article(self, article_id: str) -> List[Dict]:
        """Makale için hakem kararlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM reviews WHERE article_id = ? ORDER BY created_at DESC
        """, (article_id,))
        rows = cursor.fetchall()
        conn.close()
        
        reviews = []
        for row in rows:
            reviews.append({
                "id": row["id"],
                "article_id": row["article_id"],
                "reviewer_username": row["reviewer_username"],
                "decision": row["decision"],
                "comment": row["comment"],
                "file_path": row["file_path"] if row["file_path"] else "",
                "created_at": row["created_at"]
            })
        return reviews
    
    # Mesajlaşma işlemleri
    def add_message(self, article_id: str, from_user: str, to_user: str, subject: str, message: str):
        """Yeni mesaj ekle"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (article_id, from_user, to_user, subject, message)
                VALUES (?, ?, ?, ?, ?)
            """, (article_id, from_user, to_user, subject, message))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"HATA: Mesaj eklenirken hata oluştu: {str(e)}")
            print(f"  article_id: {article_id}, from_user: {from_user}, to_user: {to_user}")
            if 'conn' in locals():
                conn.close()
            return False
    
    def get_messages_by_article(self, article_id: str) -> List[Dict]:
        """Makale için mesajları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM messages WHERE article_id = ? ORDER BY created_at DESC
        """, (article_id,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                "id": row["id"],
                "article_id": row["article_id"],
                "from_user": row["from_user"],
                "to_user": row["to_user"],
                "subject": row["subject"],
                "message": row["message"],
                "is_read": bool(row["is_read"]),
                "created_at": row["created_at"]
            })
        return messages
    
    def get_messages_by_user(self, username: str) -> List[Dict]:
        """Kullanıcıya gelen mesajları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM messages WHERE to_user = ? ORDER BY created_at DESC
        """, (username,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                "id": row["id"],
                "article_id": row["article_id"],
                "from_user": row["from_user"],
                "to_user": row["to_user"],
                "subject": row["subject"],
                "message": row["message"],
                "is_read": bool(row["is_read"]),
                "created_at": row["created_at"]
            })
        return messages
    
    def get_messages_by_from_user(self, username: str) -> List[Dict]:
        """Kullanıcının gönderdiği mesajları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM messages WHERE from_user = ? ORDER BY created_at DESC
        """, (username,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                "id": row["id"],
                "article_id": row["article_id"],
                "from_user": row["from_user"],
                "to_user": row["to_user"],
                "subject": row["subject"],
                "message": row["message"],
                "is_read": bool(row["is_read"]),
                "created_at": row["created_at"]
            })
        return messages
    
    def mark_message_read(self, message_id: int):
        """Mesajı okundu olarak işaretle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE messages SET is_read = 1 WHERE id = ?", (message_id,))
        conn.commit()
        conn.close()
    
    # Sayı işlemleri
    def get_articles_by_volume_issue(self, volume: str, issue: str, year: str) -> List[Dict]:
        """Belirli bir sayıdaki makaleleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM articles 
            WHERE volume = ? AND issue = ? AND year = ? 
            ORDER BY pages ASC
        """, (volume, issue, year))
        rows = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in rows:
            articles.append(self._row_to_article_dict(row))
        return articles
    
    def get_published_issues(self) -> List[Dict]:
        """Yayınlanmış sayıları getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        # Year'ı integer'a çevirerek sırala (daha güvenli)
        cursor.execute("""
            SELECT DISTINCT volume, issue, year 
            FROM articles 
            WHERE status = 'Yayınlandı' 
            AND year != '' AND year IS NOT NULL
            ORDER BY CAST(year AS INTEGER) DESC, CAST(volume AS INTEGER) DESC, CAST(issue AS INTEGER) DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        issues = []
        for row in rows:
            issues.append({
                "volume": row["volume"],
                "issue": row["issue"],
                "year": row["year"]
            })
        
        # Python tarafında da sırala (ekstra güvenlik)
        def sort_key(issue):
            try:
                year = int(issue["year"]) if issue["year"] else 0
                volume = int(issue["volume"]) if issue["volume"] else 0
                issue_num = int(issue["issue"]) if issue["issue"] else 0
                return (-year, -volume, -issue_num)  # Negatif çünkü DESC sıralama
            except (ValueError, TypeError):
                return (0, 0, 0)
        
        issues.sort(key=sort_key)
        return issues
    
    def get_max_volume_for_year(self, year: str) -> int:
        """Belirli bir yıl için en yüksek cilt numarasını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT volume
            FROM articles 
            WHERE year = ? AND status = 'Yayınlandı' AND volume != '' AND volume IS NOT NULL
        """, (year,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return 0
        
        # Volume değerlerini integer'a çevir ve maksimum değeri bul
        max_volume = 0
        for row in rows:
            try:
                volume_str = row["volume"]
                if volume_str:
                    volume_int = int(volume_str)
                    if volume_int > max_volume:
                        max_volume = volume_int
            except (ValueError, TypeError):
                continue
        
        return max_volume
    
    def get_global_max_volume(self) -> int:
        """Tüm yıllar için global maksimum cilt numarasını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT volume
            FROM articles 
            WHERE status = 'Yayınlandı' AND volume != '' AND volume IS NOT NULL
        """)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return 0
        
        # Volume değerlerini integer'a çevir ve maksimum değeri bul
        max_volume = 0
        for row in rows:
            try:
                volume_str = row["volume"]
                if volume_str:
                    volume_int = int(volume_str)
                    if volume_int > max_volume:
                        max_volume = volume_int
            except (ValueError, TypeError):
                continue
        
        return max_volume
    
    def get_max_volume_before_year(self, year: str) -> int:
        """Belirli bir yıldan önceki tüm yıllar için maksimum cilt numarasını getir"""
        try:
            year_int = int(year)
        except ValueError:
            return 0
        
        conn = self.get_connection()
        cursor = conn.cursor()
        # Tüm yayınlanmış makaleleri al ve Python'da filtrele
        cursor.execute("""
            SELECT DISTINCT volume, year
            FROM articles 
            WHERE status = 'Yayınlandı' AND volume != '' AND volume IS NOT NULL AND year != '' AND year IS NOT NULL
        """)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return 0
        
        # Volume değerlerini integer'a çevir ve maksimum değeri bul (belirtilen yıldan önceki yıllar için)
        max_volume = 0
        for row in rows:
            try:
                year_str = row["year"]
                volume_str = row["volume"]
                if year_str and volume_str:
                    row_year = int(year_str)
                    if row_year < year_int:
                        volume_int = int(volume_str)
                        if volume_int > max_volume:
                            max_volume = volume_int
            except (ValueError, TypeError):
                continue
        
        return max_volume
    
    def get_ready_to_publish_articles(self) -> List[Dict]:
        """Yayına hazır makaleleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM articles 
            WHERE status = 'Yayına Hazır' AND scheduled = 1
            ORDER BY created_at ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in rows:
            articles.append(self._row_to_article_dict(row))
        return articles
    
    # İletişim mesajları işlemleri
    def add_contact_message(self, name: str, email: str, subject: str, message: str):
        """Yeni iletişim mesajı ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        """, (name, email, subject, message))
        conn.commit()
        conn.close()
        return True
    
    def get_contact_messages(self, unread_only: bool = False) -> List[Dict]:
        """İletişim mesajlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if unread_only:
            cursor.execute("""
                SELECT * FROM contact_messages 
                WHERE is_read = 0 
                ORDER BY created_at DESC
            """)
        else:
            cursor.execute("""
                SELECT * FROM contact_messages 
                ORDER BY created_at DESC
            """)
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                "id": row["id"],
                "name": row["name"],
                "email": row["email"],
                "subject": row["subject"],
                "message": row["message"],
                "is_read": bool(row["is_read"]),
                "created_at": row["created_at"]
            })
        return messages
    
    def mark_contact_message_read(self, message_id: int):
        """İletişim mesajını okundu olarak işaretle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE contact_messages SET is_read = 1 WHERE id = ?", (message_id,))
        conn.commit()
        conn.close()

