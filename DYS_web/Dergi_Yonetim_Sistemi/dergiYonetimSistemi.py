import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime
import json
import os
import shutil
import time
import traceback
from database import Database
from ai_classifier import AIArticleClassifier


class AkademikDergiSistemi:
    def __init__(self, root):
        self.root = root
        self.root.title("Akademik Dergi Yönetim Sistemi")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f5f5f5")

        # Kullanıcı bilgileri
        self.current_user = None
        self.user_role = None
        
        # Dosya seçimi için değişken
        self.selected_file_path = None
        
        # Veritabanı bağlantısı
        self.db = Database()
        
        # Yapay zeka sınıflandırıcı
        self.ai_classifier = AIArticleClassifier()
        
        # Stil ayarları (show_home_page'den önce çağrılmalı)
        self.setup_styles()
        
        # Veritabanını başlat ve test verilerini yükle
        self.init_database_data()
        
        # Ana container
        self.main_container = tk.Frame(root, bg="#f5f5f5")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Başlangıçta dergi ana sayfasını göster
        self.show_home_page()
    
    def init_database_data(self):
        """Veritabanını test verileriyle doldur"""
        # Test kullanıcıları ekle
        test_users = [
            ("admin", "DYS.2025", "admin", ["Admin", "Editör", "Alan Editörü", "Hakem", "Yazar"]),
            ("editor1", "pass", "Editör 1", ["Editör", "Yazar"]),
            ("editor2", "pass", "Editör 2", ["Editör", "Yazar"]),
            ("fe1", "pass", "Alan Editörü 1", ["Alan Editörü", "Yazar"]),
            ("fe2", "pass", "Alan Editörü 2", ["Alan Editörü", "Yazar"]),
            ("rev1", "pass", "Hakem 1", ["Hakem", "Yazar"]),
            ("rev2", "pass", "Hakem 2", ["Hakem", "Yazar"]),
            ("rev3", "pass", "Hakem 3", ["Hakem", "Yazar"]),
            ("author1", "pass", "Yazar 1", ["Yazar"]),
            ("author2", "pass", "Yazar 2", ["Yazar"]),
        ]
        
        for username, password, name, roles in test_users:
            if not self.db.get_user(username):
                # Alan editörlerine varsayılan uzmanlık alanları ata
                expertise_field = None
                if "Alan Editörü" in roles:
                    if username == "fe1":
                        expertise_field = "Bilgisayar Mühendisliği"
                    elif username == "fe2":
                        expertise_field = "Elektrik-Elektronik Mühendisliği"
                self.db.add_user(username, password, name, roles, expertise_field)
            else:
                # Mevcut alan editörlerine varsayılan alanlar ata (eğer yoksa)
                user = self.db.get_user(username)
                if user and "Alan Editörü" in user.get("roles", []) and not user.get("expertise_field"):
                    if username == "fe1":
                        self.db.update_user_expertise_field(username, "Bilgisayar Mühendisliği")
                    elif username == "fe2":
                        self.db.update_user_expertise_field(username, "Elektrik-Elektronik Mühendisliği")
        
        # 3 Yeni Alan Editörü Ekle
        new_field_editors = [
            ("fe3", "pass", "Alan Editörü 3", ["Alan Editörü", "Yazar"], "Makine Mühendisliği"),
            ("fe4", "pass", "Alan Editörü 4", ["Alan Editörü", "Yazar"], "Endüstri Mühendisliği"),
            ("fe5", "pass", "Alan Editörü 5", ["Alan Editörü", "Yazar"], "İnşaat Mühendisliği"),
        ]
        
        for username, password, name, roles, expertise_field in new_field_editors:
            if not self.db.get_user(username):
                self.db.add_user(username, password, name, roles, expertise_field)
            else:
                # Mevcut kullanıcı varsa uzmanlık alanını güncelle
                user = self.db.get_user(username)
                if user and not user.get("expertise_field"):
                    self.db.update_user_expertise_field(username, expertise_field)
        
        # 5 Yeni Hakem Ekle
        new_reviewers = [
            ("rev4", "pass", "Hakem 4", ["Hakem", "Yazar"], "Bilgisayar Mühendisliği"),
            ("rev5", "pass", "Hakem 5", ["Hakem", "Yazar"], "Elektrik-Elektronik Mühendisliği"),
            ("rev6", "pass", "Hakem 6", ["Hakem", "Yazar"], "Makine Mühendisliği"),
            ("rev7", "pass", "Hakem 7", ["Hakem", "Yazar"], "Endüstri Mühendisliği"),
            ("rev8", "pass", "Hakem 8", ["Hakem", "Yazar"], "İnşaat Mühendisliği"),
        ]
        
        for username, password, name, roles, expertise_field in new_reviewers:
            if not self.db.get_user(username):
                self.db.add_user(username, password, name, roles, expertise_field)
            else:
                # Mevcut kullanıcı varsa uzmanlık alanını güncelle
                user = self.db.get_user(username)
                if user and not user.get("expertise_field"):
                    self.db.update_user_expertise_field(username, expertise_field)
        
        # 10 Yeni Yazar Ekle
        new_authors = [
            ("author3", "pass", "Yazar 3", ["Yazar"]),
            ("author4", "pass", "Yazar 4", ["Yazar"]),
            ("author5", "pass", "Yazar 5", ["Yazar"]),
            ("author6", "pass", "Yazar 6", ["Yazar"]),
            ("author7", "pass", "Yazar 7", ["Yazar"]),
            ("author8", "pass", "Yazar 8", ["Yazar"]),
            ("author9", "pass", "Yazar 9", ["Yazar"]),
            ("author10", "pass", "Yazar 10", ["Yazar"]),
            ("author11", "pass", "Yazar 11", ["Yazar"]),
            ("author12", "pass", "Yazar 12", ["Yazar"]),
        ]
        
        for username, password, name, roles in new_authors:
            if not self.db.get_user(username):
                self.db.add_user(username, password, name, roles, None)
        
        # Test makaleleri ekle
        test_articles = [
            {
                "id": "MAK-2024-001",
                "title": "Yapay Zeka Destekli Kontrol Sistemleri ve Endüstriyel Uygulamaları",
                "authors": "H. Sarıçam, S. Yılmaz",
                "pages": "1-15",
                "status": "Yayınlandı",
                "volume": "1",
                "issue": "2",
                "year": "2025"
            },
            {
                "id": "MAK-2024-002",
                "title": "Sürdürülebilir Enerji Sistemlerinde Yeni Nesil Malzeme Teknolojileri",
                "authors": "M. Özkan, A. Demir",
                "pages": "16-28",
                "status": "Yayınlandı",
                "volume": "1",
                "issue": "2",
                "year": "2025"
            },
            {
                "id": "MAK-2024-003",
                "title": "Otonom Araçlarda Gömülü Sistemler ve Güvenlik Algoritmaları",
                "authors": "K. Yıldız, E. Kaya",
                "pages": "29-42",
                "status": "Yayınlandı",
                "volume": "1",
                "issue": "2",
                "year": "2025"
            },
            {
                "id": "MAK-2024-004",
                "title": "Makine Öğrenmesi ile Akıllı Şehir Uygulamaları",
                "authors": "B. Şahin, D. Arslan",
                "pages": "43-55",
                "status": "Yayınlandı",
                "volume": "1",
                "issue": "2",
                "year": "2025"
            },
            {
                "id": "MAK-2024-005",
                "title": "Robotik Üretimde Enerji Verimliliği Optimizasyonu ve Endüstri 4.0",
                "authors": "F. Çelik, G. Aydın",
                "pages": "56-68",
                "status": "Yayınlandı",
                "volume": "1",
                "issue": "2",
                "year": "2025"
            },
            {
                "id": "MAK-2010-001",
                "title": "Mühendislik Eğitiminde Temel Prensipler ve Uygulamalar",
                "authors": "A. Yılmaz, B. Demir",
                "pages": "1-12",
                "status": "Yayınlandı",
                "volume": "1",
                "issue": "1",
                "year": "2025"
            },
            {
                "id": "MAK-2010-002",
                "title": "Makine Mühendisliğinde Modern Tasarım Yaklaşımları",
                "authors": "C. Özkan, D. Şahin",
                "pages": "13-25",
                "status": "Yayınlandı",
                "volume": "1",
                "issue": "1",
                "year": "2025"
            },
            {
                "id": "MAK-2010-003",
                "title": "Elektrik-Elektronik Mühendisliğinde Devre Analizi Teknikleri",
                "authors": "E. Kaya, F. Arslan",
                "pages": "26-38",
                "status": "Yayınlandı",
                "volume": "1",
                "issue": "1",
                "year": "2025"
            },
            {
                "id": "MAK-2010-004",
                "title": "İnşaat Mühendisliğinde Yapısal Analiz ve Tasarım",
                "authors": "G. Çelik, H. Yıldız",
                "pages": "39-51",
                "status": "Yayınlandı",
                "volume": "1",
                "issue": "1",
                "year": "2025"
            },
            {
                "id": "MAK-2010-005",
                "title": "Bilgisayar Mühendisliğinde Yazılım Geliştirme Metodolojileri",
                "authors": "İ. Aydın, J. Öztürk",
                "pages": "52-64",
                "status": "Yayınlandı",
                "volume": "1",
                "issue": "1",
                "year": "2025"
            },
            {
                "id": "MAK-2025-001",
                "title": "Derin Öğrenme ile Görüntü İşleme ve Nesne Tanıma Sistemleri",
                "author": "author1",
                "authors": "N. Tekin, M. Yıldırım",
                "pages": "",
                "status": "Hakemde",
                "volume": "",
                "issue": "",
                "year": "2025",
                "editor": "editor1",
                "field_editor": "fe1",
                "reviewers": ["rev1", "rev2"],
                "decisions": {}
            },
            {
                "id": "MAK-2025-002",
                "title": "Nesnelerin İnterneti (IoT) Tabanlı Akıllı Tarım Sistemleri",
                "author": "author2",
                "authors": "Ö. Kaya, S. Demir",
                "pages": "",
                "status": "Hakemde",
                "volume": "",
                "issue": "",
                "year": "2025",
                "editor": "editor2",
                "field_editor": "fe2",
                "reviewers": ["rev2", "rev3"],
                "decisions": {}
            }
        ]
        
        for article in test_articles:
            if not self.db.get_article(article["id"]):
                self.db.add_article(article)

    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Bordo ve krem temalı renk paleti
        self.colors = {
            'primary': '#8B0000',  # Koyu bordo
            'primary_light': '#A52A2A',  # Açık bordo
            'secondary': '#9B2D30',  # Bordo tonu
            'secondary_light': '#B85450',  # Açık bordo tonu
            'success': '#2d8659',  # Koyu yeşil (bordo ile uyumlu)
            'success_light': '#3da76f',
            'danger': '#c9302c',  # Koyu kırmızı
            'danger_light': '#d9534f',
            'warning': '#d68910',  # Altın sarısı (bordo ile uyumlu)
            'warning_light': '#f4a460',
            'info': '#8B6F47',  # Kahverengi tonu (bordo ile uyumlu)
            'light': '#FFF8DC',  # Krem
            'light_bg': '#FAF9F6',  # Açık krem
            'dark': '#4A2C2A',  # Koyu bordo-kahve
            'dark_text': '#5C3A3A',  # Koyu bordo-kahve metin
            'white': '#FFFEF5',  # Beyaz-krem
            'accent': '#CD5C5C',  # Açık bordo vurgu
            'gradient_start': '#8B0000',  # Bordo gradyan başlangıç
            'gradient_end': '#A52A2A',  # Açık bordo gradyan bitiş
            'shadow': '#D3C5B5'  # Krem-gri gölge
        }

        # Modern fontlar
        self.fonts = {
            'title': ('Segoe UI', 24, 'bold'),
            'subtitle': ('Segoe UI', 14, 'normal'),
            'heading': ('Segoe UI', 18, 'bold'),
            'body': ('Segoe UI', 11, 'normal'),
            'button': ('Segoe UI', 11, 'bold'),
            'small': ('Segoe UI', 9, 'normal')
        }

        # Button stilleri
        style.configure('Primary.TButton',
                        background=self.colors['primary_light'],
                        foreground='white',
                        padding=(20, 12),
                        font=self.fonts['button'],
                        borderwidth=0,
                        focuscolor='none')

        style.configure('Success.TButton',
                        background=self.colors['success'],
                        foreground='white',
                        padding=(15, 10),
                        font=self.fonts['button'])

        style.configure('Danger.TButton',
                        background=self.colors['danger'],
                        foreground='white',
                        padding=(15, 10),
                        font=self.fonts['button'])

    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_home_page(self):
        """Modern 2 sütunlu düzen."""
        self.clear_screen()
        self.main_container.configure(bg=self.colors['light_bg'])

        # Üst navigasyon barı (ince krem)
        nav_bar = tk.Frame(self.main_container, bg=self.colors['white'], height=40)
        nav_bar.pack(fill=tk.X)
        nav_bar.pack_propagate(False)

        nav_left = tk.Frame(nav_bar, bg=self.colors['white'])
        nav_left.pack(side=tk.LEFT, padx=20, pady=8)
        
        nav_items = ["Ana Sayfa", "Arşiv", "Hakkında", "İletişim"]
        for item in nav_items:
            nav_link = tk.Label(nav_left, text=item, font=('Arial', 10),
                               bg=self.colors['white'], fg=self.colors['primary'], cursor='hand2', padx=8)
            nav_link.pack(side=tk.LEFT)
            nav_link.bind('<Enter>', lambda e, l=nav_link: l.config(fg=self.colors['secondary']))
            nav_link.bind('<Leave>', lambda e, l=nav_link: l.config(fg=self.colors['primary']))
            
            # Ana Sayfa linkine tıklama - Normal görünüme dön
            if item == "Ana Sayfa":
                nav_link.bind('<Button-1>', lambda e, it=item: self.show_home_page())
            
            # Arşiv linkine tıklama - Ana sayfada arşiv göster
            if item == "Arşiv":
                nav_link.bind('<Button-1>', lambda e, it=item: self.show_archive_in_home())
            
            # Hakkında linkine tıklama
            if item == "Hakkında":
                nav_link.bind('<Button-1>', lambda e, it=item: self.show_about_page())
            
            # İletişim linkine tıklama
            if item == "İletişim":
                nav_link.bind('<Button-1>', lambda e, it=item: self.show_contact_page())

        nav_right = tk.Frame(nav_bar, bg=self.colors['white'])
        nav_right.pack(side=tk.RIGHT, padx=20, pady=8)
        
        login_link = tk.Label(nav_right, text="Giriş Yap", font=('Arial', 10),
                              bg=self.colors['white'], fg=self.colors['primary'], cursor='hand2')
        login_link.pack(side=tk.RIGHT)
        login_link.bind('<Button-1>', lambda e: self.show_login_screen())
        login_link.bind('<Enter>', lambda e, l=login_link: l.config(fg=self.colors['secondary']))
        login_link.bind('<Leave>', lambda e, l=login_link: l.config(fg=self.colors['primary']))

        # Mavi banner
        banner = tk.Frame(self.main_container, bg=self.colors['primary'], height=200)
        banner.pack(fill=tk.X)
        banner.pack_propagate(False)

        banner_content = tk.Frame(banner, bg=self.colors['primary'])
        banner_content.pack(expand=True)

        journal_title = tk.Label(banner_content, text="İSTE Mühendislik Dergisi",
                                 font=('Arial', 28, 'bold'), bg=self.colors['primary'], fg='white')
        journal_title.pack(pady=(20, 8))

        subtitle = tk.Label(banner_content, text="Açık erişim, hakemli akademik dergi platformu",
                           font=('Arial', 12), bg=self.colors['primary'], fg='white')
        subtitle.pack(pady=(0, 20))

        info_frame = tk.Frame(banner_content, bg=self.colors['primary'])
        info_frame.pack()

        info_data = [
            ("📅", "Kuruluş: 2025"),
            ("📊", "Periyot: Yılda 3 Sayı"),
            ("🌐", "Dil: Türkçe / İngilizce")
        ]

        for icon, text in info_data:
            info_item = tk.Frame(info_frame, bg=self.colors['primary'])
            info_item.pack(side=tk.LEFT, padx=20)
            tk.Label(info_item, text=icon, font=('Arial', 12), bg=self.colors['primary'], fg='white').pack(side=tk.LEFT, padx=(0, 5))
            tk.Label(info_item, text=text, font=('Arial', 11), bg=self.colors['primary'], fg='white').pack(side=tk.LEFT)

        # Ana içerik - 2 sütunlu düzen
        self.main_content = tk.Frame(self.main_container, bg='#f5f5f5')
        self.main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Sol sütun: Makaleler (geniş)
        self.left_col = tk.Frame(self.main_content, bg=self.colors['white'], relief=tk.RAISED, borderwidth=1)
        self.left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        # Sol sütun içerik
        self.left_content = tk.Frame(self.left_col, bg=self.colors['white'])
        self.left_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Başlık - Son sayı bilgisi ile
        self.title_frame = tk.Frame(self.left_content, bg=self.colors['white'])
        self.title_frame.pack(fill=tk.X, pady=(0, 15))

        # Son sayı bilgisini al (ilk yayınlanmış makaleden)
        published_articles = self.db.get_articles_by_status("Yayınlandı")
        if published_articles:
            last_article = published_articles[0]
            volume = last_article.get("volume", "1")
            issue = last_article.get("issue", "2")
            title_text = f"Son Sayıdaki Makaleler (Cilt {volume}, Sayı {issue})"
        else:
            title_text = "Son Sayı"

        self.articles_title = tk.Label(self.title_frame, text=title_text,
                                 font=('Arial', 16, 'bold'), bg=self.colors['white'], fg=self.colors['primary'])
        self.articles_title.pack(side=tk.LEFT)

        # Makale listesi
        self.articles_list_frame = tk.Frame(self.left_content, bg=self.colors['white'])
        self.articles_list_frame.pack(fill=tk.BOTH, expand=True)

        # Son sayıdaki makaleleri veritabanından getir (Yayınlandı durumunda olanlar)
        published_articles = self.db.get_articles_by_status("Yayınlandı")
        
        if published_articles:
            # Canvas ve scrollbar için container
            canvas_container = tk.Frame(self.articles_list_frame, bg=self.colors['white'])
            canvas_container.pack(fill=tk.BOTH, expand=True)
            
            canvas = tk.Canvas(canvas_container, bg=self.colors['white'], highlightthickness=0)
            scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.colors['white'])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Makaleleri listele
            for idx, article in enumerate(published_articles[:5], 1):  # En fazla 5 makale
                article_frame = tk.Frame(scrollable_frame, bg=self.colors['white'], relief=tk.FLAT)
                article_frame.pack(fill=tk.X, pady=8, padx=5)
                
                # Makale numarası ve başlık
                title_frame = tk.Frame(article_frame, bg=self.colors['white'])
                title_frame.pack(fill=tk.X, pady=(0, 5))
                
                num_label = tk.Label(title_frame, text=f"{idx}.", font=('Arial', 11, 'bold'),
                                    bg=self.colors['white'], fg=self.colors['primary'], width=3, anchor='w')
                num_label.pack(side=tk.LEFT)
                
                title_label = tk.Label(title_frame, text=article["title"], font=('Arial', 11),
                                      bg=self.colors['white'], fg=self.colors['primary'], cursor='hand2',
                                      anchor='w', wraplength=600, justify='left')
                title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
                title_label.bind('<Enter>', lambda e, l=title_label: l.config(fg=self.colors['secondary'], font=('Arial', 11, 'underline')))
                title_label.bind('<Leave>', lambda e, l=title_label: l.config(fg=self.colors['primary'], font=('Arial', 11)))
                
                # Yazar bilgisi
                author_frame = tk.Frame(article_frame, bg=self.colors['white'])
                author_frame.pack(fill=tk.X, padx=(25, 0))
                
                author_label = tk.Label(author_frame, text=article["authors"], font=('Arial', 10),
                                       bg=self.colors['white'], fg=self.colors['dark_text'], anchor='w')
                author_label.pack(side=tk.LEFT)
                
                # Sayfa bilgisi
                pages_label = tk.Label(author_frame, text=f"Sayfa: {article['pages']}", font=('Arial', 10),
                                      bg=self.colors['white'], fg=self.colors['dark_text'])
                pages_label.pack(side=tk.LEFT, padx=(15, 0))
                
                # PDF butonu
                pdf_btn = tk.Label(author_frame, text="PDF", font=('Arial', 10, 'bold'),
                                  bg='white', fg=self.colors['danger'], cursor='hand2')
                pdf_btn.pack(side=tk.RIGHT)
                pdf_btn.bind('<Enter>', lambda e, l=pdf_btn: l.config(fg=self.colors['danger_light']))
                pdf_btn.bind('<Leave>', lambda e, l=pdf_btn: l.config(fg=self.colors['danger']))
                
                # Ayırıcı çizgi (son makale hariç)
                if idx < len(published_articles[:5]):
                    separator = tk.Frame(article_frame, bg='#e0e0e0', height=1)
                    separator.pack(fill=tk.X, pady=(8, 0), padx=(25, 0))
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        else:
            # Boş mesaj
            empty_msg = tk.Label(self.articles_list_frame, 
                                text="Henüz yayınlanmış makale bulunmamaktadır.",
                                font=('Arial', 11), bg=self.colors['white'], fg='#999999')
            empty_msg.pack(pady=30)

        # Sağ sütun: KEŞFET (dar)
        self.right_col = tk.Frame(self.main_content, bg=self.colors['white'], width=280, relief=tk.RAISED, borderwidth=1)
        self.right_col.pack(side=tk.LEFT, fill=tk.Y)
        self.right_col.pack_propagate(False)

        right_content = tk.Frame(self.right_col, bg=self.colors['white'])
        right_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=20)

        # KEŞFET başlığı
        discover_header = tk.Frame(right_content, bg='white')
        discover_header.pack(fill=tk.X, pady=(0, 10))
        
        # Küp ikonu ve başlık
        icon_label = tk.Label(discover_header, text="🔲", font=('Arial', 16),
                             bg='white', fg=self.colors['primary'])
        icon_label.pack(side=tk.LEFT, padx=(0, 8))
        
        discover_title = tk.Label(discover_header, text="KEŞFET",
                                 font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary'])
        discover_title.pack(side=tk.LEFT)

        # Ayırıcı çizgi
        separator = tk.Frame(right_content, bg='#e0e0e0', height=1)
        separator.pack(fill=tk.X, pady=(0, 10))

        # KEŞFET menü öğeleri
        discover_items = [
            "Amaç ve Kapsam",
            "Yazım Kuralları",
            "Etik İlkeler ve Yayın Politikası",
            "Ücret Politikası",
            "Dergi Kurulları",
            "Makale Gönder",
            "Hakemlik İsteği Gönder",
            "Dizinler",
            "İstatistikler"
            
        ]

        for idx, item in enumerate(discover_items):
            item_frame = tk.Frame(right_content, bg='white')
            item_frame.pack(fill=tk.X, pady=4)
            
            # Ok işareti - tüm öğeler için gri
            arrow_label = tk.Label(item_frame, text="→", font=('Arial', 12),
                                  bg='white', fg='#999999', width=2)
            arrow_label.pack(side=tk.LEFT)
            
            # Menü öğesi - tüm öğeler için aynı renk
            link_label = tk.Label(item_frame, text=item, font=('Arial', 10),
                                 bg='white', fg=self.colors['dark_text'],
                                 cursor='hand2', anchor='w')
            link_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Hover efekti - tüm öğelere uygula
            def make_hover_enter(label):
                return lambda e: label.config(fg=self.colors['secondary'])
            def make_hover_leave(label):
                return lambda e: label.config(fg=self.colors['dark_text'])
            
            link_label.bind('<Enter>', make_hover_enter(link_label))
            link_label.bind('<Leave>', make_hover_leave(link_label))
            
            # Makale Gönder'e tıklama
            if item == "Makale Gönder":
                link_label.bind('<Button-1>', lambda e, lbl=link_label: self.show_login_screen())
            
            # Hakemlik İsteği Gönder'e tıklama
            if item == "Hakemlik İsteği Gönder":
                link_label.bind('<Button-1>', lambda e: self.show_reviewer_request_form())
            
            # Amaç ve Kapsam
            if item == "Amaç ve Kapsam":
                link_label.bind('<Button-1>', lambda e, it=item: self.show_discover_page("Amaç ve Kapsam"))
            
            # Yazım Kuralları
            if item == "Yazım Kuralları":
                link_label.bind('<Button-1>', lambda e, it=item: self.show_discover_page("Yazım Kuralları"))
            
            # Etik İlkeler ve Yayın Politikası
            if item == "Etik İlkeler ve Yayın Politikası":
                link_label.bind('<Button-1>', lambda e, it=item: self.show_discover_page("Etik İlkeler ve Yayın Politikası"))
            
            # Ücret Politikası
            if item == "Ücret Politikası":
                link_label.bind('<Button-1>', lambda e, it=item: self.show_discover_page("Ücret Politikası"))
            
            # Dergi Kurulları
            if item == "Dergi Kurulları":
                link_label.bind('<Button-1>', lambda e, it=item: self.show_discover_page("Dergi Kurulları"))
            
            # Dizinler
            if item == "Dizinler":
                link_label.bind('<Button-1>', lambda e, it=item: self.show_discover_page("Dizinler"))
            
            # İstatistikler
            if item == "İstatistikler":
                link_label.bind('<Button-1>', lambda e, it=item: self.show_discover_page("İstatistikler"))

    def show_archive_in_home(self):
        """Ana sayfada arşiv görünümünü göster"""
        # Eğer ana sayfa yüklenmemişse, önce yükle
        if not hasattr(self, 'left_content'):
            self.show_home_page()
        
        # Widget'ın hala var olup olmadığını kontrol et
        try:
            if not self.left_content.winfo_exists():
                self.show_home_page()
        except tk.TclError:
            self.show_home_page()
            return
        
        # Sol sütun içeriğini temizle
        for widget in self.left_content.winfo_children():
            widget.destroy()
        
        # Arşiv başlığı
        archive_title = tk.Label(self.left_content, text="📖 Dergi Arşivi",
                                font=('Arial', 20, 'bold'), bg=self.colors['white'], fg=self.colors['primary'])
        archive_title.pack(pady=(10, 20))
        
        # Yayınlanmış sayıları getir
        published_issues = self.db.get_published_issues()
        
        if not published_issues:
            tk.Label(self.left_content, text="Henüz yayınlanmış sayı bulunmamaktadır.",
                    font=('Arial', 12), bg=self.colors['white'], fg=self.colors['secondary']).pack(pady=50)
            return
        
        # Canvas ve scrollbar
        canvas_container = tk.Frame(self.left_content, bg=self.colors['white'])
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_container, bg=self.colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['white'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Sayıları listele
        for issue in published_issues:
            # Sayı kartı
            issue_card = tk.Frame(scrollable_frame, bg=self.colors['white'], relief=tk.RAISED, borderwidth=2)
            issue_card.pack(fill=tk.X, pady=15, padx=5)
            
            # Sayı başlığı
            issue_header = tk.Frame(issue_card, bg=self.colors['primary'], height=60)
            issue_header.pack(fill=tk.X)
            issue_header.pack_propagate(False)
            
            issue_title = tk.Label(issue_header, 
                                  text=f"Cilt {issue['volume']}, Sayı {issue['issue']}, {issue['year']}",
                                  font=('Arial', 16, 'bold'), bg=self.colors['primary'], fg='white')
            issue_title.pack(pady=18)
            
            # Makaleler
            articles = self.db.get_articles_by_volume_issue(issue['volume'], issue['issue'], issue['year'])
            
            articles_frame = tk.Frame(issue_card, bg=self.colors['white'])
            articles_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
            
            if articles:
                tk.Label(articles_frame, text=f"{len(articles)} Makale", 
                        font=('Arial', 11, 'bold'), bg=self.colors['white'], fg=self.colors['dark']).pack(anchor='w', pady=(0, 15))
                
                for idx, art in enumerate(articles, 1):
                    article_item = tk.Frame(articles_frame, bg=self.colors['light'], relief=tk.FLAT)
                    article_item.pack(fill=tk.X, pady=5)
                    
                    # Makale numarası ve başlık
                    title_frame = tk.Frame(article_item, bg=self.colors['light'])
                    title_frame.pack(fill=tk.X, padx=15, pady=8)
                    
                    num_label = tk.Label(title_frame, text=f"{idx}.", font=('Arial', 11, 'bold'),
                                        bg=self.colors['light'], fg=self.colors['primary'], width=3, anchor='w')
                    num_label.pack(side=tk.LEFT)
                    
                    title_label = tk.Label(title_frame, text=art["title"], font=('Arial', 11),
                                          bg=self.colors['light'], fg=self.colors['primary'], cursor='hand2',
                                          anchor='w', wraplength=700, justify='left')
                    title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
                    title_label.bind('<Enter>', lambda e, l=title_label: l.config(fg=self.colors['secondary'], font=('Arial', 11, 'underline')))
                    title_label.bind('<Leave>', lambda e, l=title_label: l.config(fg=self.colors['primary'], font=('Arial', 11)))
                    
                    # Yazar ve sayfa bilgisi
                    info_frame = tk.Frame(title_frame, bg=self.colors['light'])
                    info_frame.pack(side=tk.RIGHT, padx=10)
                    
                    author_label = tk.Label(info_frame, 
                                           text=art.get('authors', art.get('author', '')),
                                           font=('Arial', 9), bg=self.colors['light'], fg=self.colors['dark_text'])
                    author_label.pack(side=tk.LEFT, padx=(0, 10))
                    
                    pages_label = tk.Label(info_frame, 
                                          text=f"Sayfa: {art.get('pages', 'N/A')}",
                                          font=('Arial', 9), bg=self.colors['light'], fg=self.colors['secondary'])
                    pages_label.pack(side=tk.LEFT)
            else:
                tk.Label(articles_frame, text="Bu sayıda makale bulunamadı.",
                        font=('Arial', 10), bg=self.colors['white'], fg=self.colors['secondary']).pack(pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_about_page(self):
        """Hakkında sayfasını göster"""
        # Eğer ana sayfa yüklenmemişse, önce yükle
        if not hasattr(self, 'left_content'):
            self.show_home_page()
        
        # Widget'ın hala var olup olmadığını kontrol et
        try:
            if not self.left_content.winfo_exists():
                self.show_home_page()
        except tk.TclError:
            self.show_home_page()
            return
        
        # Sol sütun içeriğini temizle
        for widget in self.left_content.winfo_children():
            widget.destroy()
        
        # Hakkında başlığı
        about_title = tk.Label(self.left_content, text="📚 Hakkında",
                              font=('Arial', 24, 'bold'), bg=self.colors['white'], fg=self.colors['primary'])
        about_title.pack(pady=(20, 20))
        
        # Canvas ve scrollbar container
        canvas_container = tk.Frame(self.left_content, bg=self.colors['white'])
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(canvas_container, bg=self.colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        
        # İçerik frame (canvas içinde)
        content_frame = tk.Frame(canvas, bg=self.colors['white'], padx=20)
        
        # Dergi hakkında bilgiler
        about_texts = [
            ("Dergi Hakkında", [
                "İSTE Mühendislik Dergisi, İskenderun Teknik Üniversitesi (İSTE) bünyesinde yayınlanan",
                "hakemli, açık erişimli bir akademik dergidir. Dergimiz, mühendislik alanındaki",
                "güncel araştırmaları, bilimsel gelişmeleri ve teknolojik yenilikleri akademik",
                "dünyaya sunmayı amaçlamaktadır."
            ]),
            ("Amaç ve Kapsam", [
                "Dergimiz, mühendislik bilimlerinin tüm alanlarında yapılan özgün araştırmaları",
                "yayınlamaktadır. Özellikle şu konularda makaleler kabul edilmektedir:",
                "• Bilgisayar Mühendisliği ve Yazılım",
                "• Elektrik-Elektronik Mühendisliği",
                "• Makine Mühendisliği",
                "• Endüstri Mühendisliği",
                "• İnşaat Mühendisliği",
                "• Kimya Mühendisliği",
                "• Diğer mühendislik disiplinleri"
            ]),
            ("Yayın Politikası", [
                "Dergimiz, açık erişim prensibini benimser ve tüm makaleler ücretsiz olarak",
                "erişilebilir durumdadır. Yayın sürecimiz şeffaf ve adil bir hakem değerlendirme",
                "sistemi üzerine kuruludur. Tüm makaleler en az iki hakem tarafından",
                "değerlendirilmektedir."
            ]),
            ("Yayın Periyodu", [
                "Dergimiz yılda 3 sayı olarak yayınlanmaktadır. Yayın takvimi:",
                "• 1. Sayı: Ocak-Nisan",
                "• 2. Sayı: Mayıs-Ağustos",
                "• 3. Sayı: Eylül-Aralık"
            ]),
            ("Dil", [
                "Dergimiz Türkçe ve İngilizce dillerinde makale kabul etmektedir."
            ]),
            ("Etik İlkeler", [
                "Dergimiz, akademik yayıncılıkta en yüksek etik standartları benimser.",
                "İntihal, veri sahteciliği ve diğer akademik suistimaller kesinlikle",
                "kabul edilmez. Tüm yazarlar, editörler ve hakemler etik kurallara",
                "uygun davranmakla yükümlüdür."
            ])
        ]
        
        for section_title, section_texts in about_texts:
            # Bölüm başlığı
            section_frame = tk.Frame(content_frame, bg=self.colors['white'])
            section_frame.pack(fill=tk.X, pady=(0, 20))
            
            title_label = tk.Label(section_frame, text=section_title,
                                  font=('Arial', 16, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['primary'], anchor='w')
            title_label.pack(fill=tk.X, pady=(0, 10))
            
            # Bölüm içeriği
            for text in section_texts:
                text_label = tk.Label(section_frame, text=text,
                                     font=('Arial', 11), bg=self.colors['white'],
                                     fg=self.colors['dark_text'], anchor='w', justify='left',
                                     wraplength=800)
                text_label.pack(fill=tk.X, pady=2)
        
        # Canvas'a içerik frame'i ekle
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Scrollbar ayarları
        def configure_scroll(event):
            # Canvas genişliğini içerik frame'e uygula
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
            # Scroll region'ı güncelle
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        content_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas ve scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_contact_page(self):
        """İletişim sayfasını göster"""
        # Eğer ana sayfa yüklenmemişse, önce yükle
        if not hasattr(self, 'left_content'):
            self.show_home_page()
        
        # Widget'ın hala var olup olmadığını kontrol et
        try:
            if not self.left_content.winfo_exists():
                self.show_home_page()
        except tk.TclError:
            self.show_home_page()
            return
        
        # Sol sütun içeriğini temizle
        for widget in self.left_content.winfo_children():
            widget.destroy()
        
        # İletişim başlığı
        contact_title = tk.Label(self.left_content, text="📧 İletişim",
                                font=('Arial', 24, 'bold'), bg=self.colors['white'], fg=self.colors['primary'])
        contact_title.pack(pady=(20, 20))
        
        # Canvas ve scrollbar container
        canvas_container = tk.Frame(self.left_content, bg=self.colors['white'])
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(canvas_container, bg=self.colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        
        # İçerik frame (canvas içinde)
        content_frame = tk.Frame(canvas, bg=self.colors['white'], padx=20)
        
        # İletişim bilgileri
        contact_info = [
            ("📧 E-posta", "iste.dergi@iste.edu.tr"),
            ("📞 Telefon", "+90 (326) 613 56 00"),
            ("📍 Adres", "İskenderun Teknik Üniversitesi\nMühendislik ve Doğa Bilimleri Fakültesi\n31200 İskenderun / Hatay / Türkiye"),
            ("🌐 Web Sitesi", "https://dergi.iste.edu.tr"),
            ("⏰ Çalışma Saatleri", "Pazartesi - Cuma: 09:00 - 17:00")
        ]
        
        # İletişim bilgileri kartları
        for icon_text, info_text in contact_info:
            info_card = tk.Frame(content_frame, bg=self.colors['light'], relief=tk.RAISED, borderwidth=1)
            info_card.pack(fill=tk.X, pady=10, padx=10)
            
            info_inner = tk.Frame(info_card, bg=self.colors['light'], padx=20, pady=15)
            info_inner.pack(fill=tk.BOTH, expand=True)
            
            icon_label = tk.Label(info_inner, text=icon_text,
                                 font=('Arial', 14, 'bold'), bg=self.colors['light'],
                                 fg=self.colors['primary'], anchor='w')
            icon_label.pack(fill=tk.X, pady=(0, 5))
            
            info_label = tk.Label(info_inner, text=info_text,
                                 font=('Arial', 11), bg=self.colors['light'],
                                 fg=self.colors['dark_text'], anchor='w', justify='left',
                                 wraplength=700)
            info_label.pack(fill=tk.X)
        
        # İletişim formu başlığı
        form_title = tk.Label(content_frame, text="Bize Ulaşın",
                             font=('Arial', 18, 'bold'), bg=self.colors['white'],
                             fg=self.colors['primary'], anchor='w')
        form_title.pack(fill=tk.X, pady=(30, 15))
        
        # İletişim formu
        form_card = tk.Frame(content_frame, bg=self.colors['light'], relief=tk.RAISED, borderwidth=2)
        form_card.pack(fill=tk.X, pady=10, padx=10)
        
        form_inner = tk.Frame(form_card, bg=self.colors['white'], padx=25, pady=25)
        form_inner.pack(fill=tk.BOTH, expand=True)
        
        # Form alanları
        tk.Label(form_inner, text="Ad Soyad *", font=('Arial', 11, 'bold'),
                bg=self.colors['white'], fg=self.colors['dark_text'], anchor='w').pack(fill=tk.X, pady=(0, 5))
        name_entry = tk.Entry(form_inner, font=('Arial', 11), bg=self.colors['light'],
                              relief=tk.FLAT, bd=2, highlightthickness=1,
                              highlightbackground=self.colors['shadow'],
                              highlightcolor=self.colors['primary'])
        name_entry.pack(fill=tk.X, ipady=8, pady=(0, 15))
        
        tk.Label(form_inner, text="E-posta *", font=('Arial', 11, 'bold'),
                bg=self.colors['white'], fg=self.colors['dark_text'], anchor='w').pack(fill=tk.X, pady=(0, 5))
        email_entry = tk.Entry(form_inner, font=('Arial', 11), bg=self.colors['light'],
                              relief=tk.FLAT, bd=2, highlightthickness=1,
                              highlightbackground=self.colors['shadow'],
                              highlightcolor=self.colors['primary'])
        email_entry.pack(fill=tk.X, ipady=8, pady=(0, 15))
        
        tk.Label(form_inner, text="Konu *", font=('Arial', 11, 'bold'),
                bg=self.colors['white'], fg=self.colors['dark_text'], anchor='w').pack(fill=tk.X, pady=(0, 5))
        subject_entry = tk.Entry(form_inner, font=('Arial', 11), bg=self.colors['light'],
                                relief=tk.FLAT, bd=2, highlightthickness=1,
                                highlightbackground=self.colors['shadow'],
                                highlightcolor=self.colors['primary'])
        subject_entry.pack(fill=tk.X, ipady=8, pady=(0, 15))
        
        tk.Label(form_inner, text="Mesajınız *", font=('Arial', 11, 'bold'),
                bg=self.colors['white'], fg=self.colors['dark_text'], anchor='w').pack(fill=tk.X, pady=(0, 5))
        message_text = scrolledtext.ScrolledText(form_inner, font=('Arial', 11),
                                                 bg=self.colors['light'], relief=tk.FLAT,
                                                 bd=2, highlightthickness=1,
                                                 highlightbackground=self.colors['shadow'],
                                                 highlightcolor=self.colors['primary'],
                                                 height=8, wrap=tk.WORD)
        message_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Gönder butonu
        def send_message():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            subject = subject_entry.get().strip()
            message = message_text.get("1.0", tk.END).strip()
            
            if not name or not email or not subject or not message:
                messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun.")
                return
            
            # E-posta formatını kontrol et
            if "@" not in email or "." not in email.split("@")[-1]:
                messagebox.showwarning("Uyarı", "Lütfen geçerli bir e-posta adresi girin.")
                return
            
            # Mesajı veritabanına kaydet
            try:
                self.db.add_contact_message(name, email, subject, message)
                messagebox.showinfo("Başarılı", "Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.")
                # Formu temizle
                name_entry.delete(0, tk.END)
                email_entry.delete(0, tk.END)
                subject_entry.delete(0, tk.END)
                message_text.delete("1.0", tk.END)
            except Exception as e:
                messagebox.showerror("Hata", f"Mesaj gönderilirken bir hata oluştu: {str(e)}")
        
        send_btn = tk.Button(form_inner, text="📤 Mesaj Gönder", font=('Arial', 12, 'bold'),
                             bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                             cursor='hand2', bd=0, activebackground=self.colors['primary_light'],
                             activeforeground='white', command=send_message,
                             padx=20, pady=12)
        send_btn.pack(pady=(10, 0))
        
        # Canvas'a içerik frame'i ekle
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Scrollbar ayarları
        def configure_scroll(event):
            # Canvas genişliğini içerik frame'e uygula
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
            # Scroll region'ı güncelle
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        content_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas ve scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_discover_page(self, page_type):
        """Keşfet bölümündeki sayfaları göster"""
        # Eğer ana sayfa yüklenmemişse, önce yükle
        if not hasattr(self, 'left_content'):
            self.show_home_page()
        
        # Widget'ın hala var olup olmadığını kontrol et
        try:
            if not self.left_content.winfo_exists():
                self.show_home_page()
        except tk.TclError:
            self.show_home_page()
            return
        
        # Sol sütun içeriğini temizle
        for widget in self.left_content.winfo_children():
            widget.destroy()
        
        # Sayfa başlığı
        page_title = tk.Label(self.left_content, text=f"📚 {page_type}",
                             font=('Arial', 24, 'bold'), bg=self.colors['white'], fg=self.colors['primary'])
        page_title.pack(pady=(20, 20))
        
        # Canvas ve scrollbar container
        canvas_container = tk.Frame(self.left_content, bg=self.colors['white'])
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(canvas_container, bg=self.colors['white'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        
        # İçerik frame (canvas içinde)
        content_frame = tk.Frame(canvas, bg=self.colors['white'], padx=20)
        
        # Sayfa türüne göre içerik oluştur
        if page_type == "Amaç ve Kapsam":
            self._show_aim_and_scope(content_frame)
        elif page_type == "Yazım Kuralları":
            self._show_writing_guidelines(content_frame)
        elif page_type == "Etik İlkeler ve Yayın Politikası":
            self._show_ethics_policy(content_frame)
        elif page_type == "Ücret Politikası":
            self._show_fee_policy(content_frame)
        elif page_type == "Dergi Kurulları":
            self._show_editorial_boards(content_frame)
        elif page_type == "Dizinler":
            self._show_indexes(content_frame)
        elif page_type == "İstatistikler":
            self._show_statistics(content_frame)
        
        # Canvas'a içerik frame'i ekle
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        # Scrollbar ayarları
        def configure_scroll(event):
            # Canvas genişliğini içerik frame'e uygula
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
            # Scroll region'ı güncelle
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        content_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas ve scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _show_aim_and_scope(self, parent):
        """Amaç ve Kapsam içeriği"""
        sections = [
            ("Amaç", [
                "İSTE Mühendislik Dergisi, mühendislik bilimlerinin tüm alanlarında yapılan özgün",
                "araştırmaları yayınlayarak bilimsel bilgi birikimine katkıda bulunmayı amaçlamaktadır.",
                "Dergimiz, akademisyenler, araştırmacılar ve uygulayıcılar arasında bilgi paylaşımını",
                "teşvik eder ve mühendislik alanındaki güncel gelişmeleri takip eder."
            ]),
            ("Kapsam", [
                "Dergimiz aşağıdaki mühendislik alanlarında makaleler kabul etmektedir:",
                "",
                "• Bilgisayar Mühendisliği: Yazılım mühendisliği, yapay zeka, veri bilimi, siber güvenlik,",
                "  bilgisayar ağları, algoritmalar ve veri yapıları",
                "",
                "• Elektrik-Elektronik Mühendisliği: Elektrik sistemleri, elektronik devreler, kontrol",
                "  sistemleri, sinyal işleme, güç elektroniği, telekomünikasyon",
                "",
                "• Makine Mühendisliği: Termodinamik, akışkanlar mekaniği, malzeme bilimi, üretim",
                "  teknolojileri, robotik, otomasyon",
                "",
                "• Endüstri Mühendisliği: Üretim planlama, optimizasyon, yöneylem araştırması,",
                "  kalite yönetimi, tedarik zinciri yönetimi",
                "",
                "• İnşaat Mühendisliği: Yapı mühendisliği, geoteknik, ulaştırma, su kaynakları,",
                "  yapı malzemeleri",
                "",
                "• Kimya Mühendisliği: Proses tasarımı, reaksiyon mühendisliği, ayırma işlemleri,",
                "  malzeme mühendisliği",
                "",
                "• Diğer Mühendislik Disiplinleri: Çevre mühendisliği, biyomedikal mühendislik,",
                "  mekatronik ve ilgili disiplinlerarası çalışmalar"
            ]),
            ("Makale Türleri", [
                "Dergimiz aşağıdaki türde makaleler kabul etmektedir:",
                "• Araştırma Makaleleri: Özgün araştırma sonuçlarını içeren makaleler",
                "• Derleme Makaleleri: Belirli bir konuda mevcut literatürün kapsamlı incelemesi",
                "• Kısa İleti: Kısa araştırma sonuçları veya teknik notlar",
                "• Vaka Çalışmaları: Gerçek uygulamalardan örnekler"
            ])
        ]
        
        for section_title, section_texts in sections:
            section_frame = tk.Frame(parent, bg=self.colors['white'])
            section_frame.pack(fill=tk.X, pady=(0, 25))
            
            title_label = tk.Label(section_frame, text=section_title,
                                  font=('Arial', 16, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['primary'], anchor='w')
            title_label.pack(fill=tk.X, pady=(0, 10))
            
            for text in section_texts:
                if text == "":
                    continue
                text_label = tk.Label(section_frame, text=text,
                                     font=('Arial', 11), bg=self.colors['white'],
                                     fg=self.colors['dark_text'], anchor='w', justify='left',
                                     wraplength=800)
                text_label.pack(fill=tk.X, pady=2)

    def _show_writing_guidelines(self, parent):
        """Yazım Kuralları içeriği"""
        sections = [
            ("Genel Kurallar", [
                "• Makaleler Türkçe veya İngilizce olarak yazılabilir.",
                "• Makale uzunluğu 5000-8000 kelime arasında olmalıdır.",
                "• Makaleler Microsoft Word formatında (.docx) gönderilmelidir.",
                "• Sayfa düzeni: A4, kenar boşlukları 2.5 cm, çift satır aralığı.",
                "• Font: Times New Roman, 12 punto (başlıklar için 14-16 punto)."
            ]),
            ("Makale Yapısı", [
                "1. Başlık: Kısa, açıklayıcı ve anlamlı olmalıdır.",
                "2. Özet: Türkçe ve İngilizce olarak 150-250 kelime arasında.",
                "3. Anahtar Kelimeler: 5-7 anahtar kelime.",
                "4. Giriş: Problem tanımı, literatür özeti ve çalışmanın amacı.",
                "5. Yöntem: Kullanılan metodoloji ve materyaller.",
                "6. Bulgular: Araştırma sonuçları, tablolar ve şekiller.",
                "7. Tartışma: Sonuçların değerlendirilmesi ve yorumlanması.",
                "8. Sonuç: Ana bulguların özeti ve öneriler.",
                "9. Kaynaklar: APA 7. sürüm formatında."
            ]),
            ("Tablo ve Şekiller", [
                "• Tüm tablolar ve şekiller numaralandırılmalı ve başlıklandırılmalıdır.",
                "• Tablolar ve şekiller metin içinde referans verilmelidir.",
                "• Şekiller yüksek çözünürlükte (300 dpi) olmalıdır.",
                "• Tablolar Word içinde oluşturulmalı, görsel olarak eklenmemelidir."
            ]),
            ("Kaynak Gösterimi", [
                "• Kaynaklar APA 7. sürüm formatında gösterilmelidir.",
                "• Metin içinde: (Yazar, Yıl) veya Yazar (Yıl) formatı kullanılmalıdır.",
                "• Kaynaklar listesi alfabetik sırada düzenlenmelidir.",
                "• DOI numaraları mümkünse eklenmelidir."
            ]),
            ("Etik Kurallar", [
                "• Makaleler daha önce yayınlanmamış olmalıdır.",
                "• İntihal yapılmamalıdır.",
                "• Tüm yazarlar makaleye katkıda bulunmuş olmalıdır.",
                "• Çıkar çatışması beyan edilmelidir."
            ])
        ]
        
        for section_title, section_texts in sections:
            section_frame = tk.Frame(parent, bg=self.colors['white'])
            section_frame.pack(fill=tk.X, pady=(0, 25))
            
            title_label = tk.Label(section_frame, text=section_title,
                                  font=('Arial', 16, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['primary'], anchor='w')
            title_label.pack(fill=tk.X, pady=(0, 10))
            
            for text in section_texts:
                text_label = tk.Label(section_frame, text=text,
                                     font=('Arial', 11), bg=self.colors['white'],
                                     fg=self.colors['dark_text'], anchor='w', justify='left',
                                     wraplength=800)
                text_label.pack(fill=tk.X, pady=2)

    def _show_ethics_policy(self, parent):
        """Etik İlkeler ve Yayın Politikası içeriği"""
        sections = [
            ("Yayın Etiği", [
                "İSTE Mühendislik Dergisi, akademik yayıncılıkta en yüksek etik standartları",
                "benimser. Tüm yazarlar, editörler ve hakemler aşağıdaki etik kurallara uymakla",
                "yükümlüdür."
            ]),
            ("Yazarların Sorumlulukları", [
                "• Makaleler özgün olmalı ve daha önce yayınlanmamış olmalıdır.",
                "• İntihal, veri sahteciliği ve diğer akademik suistimaller kesinlikle yasaktır.",
                "• Tüm yazarlar makaleye önemli katkıda bulunmuş olmalıdır.",
                "• Kaynaklar doğru ve eksiksiz şekilde gösterilmelidir.",
                "• Çıkar çatışması varsa beyan edilmelidir.",
                "• Araştırma etik kurul onayı gerektiriyorsa, onay belgesi sağlanmalıdır."
            ]),
            ("Editörlerin Sorumlulukları", [
                "• Editörler adil ve tarafsız değerlendirme yapmalıdır.",
                "• Editörler, makaleleri yalnızca bilimsel değerlerine göre değerlendirmelidir.",
                "• Editörler, yazarlar ve hakemler arasındaki iletişimi yönetmelidir.",
                "• Editörler, etik ihlalleri tespit ettiğinde gerekli önlemleri almalıdır."
            ]),
            ("Hakemlerin Sorumlulukları", [
                "• Hakemler, objektif ve yapıcı değerlendirme yapmalıdır.",
                "• Hakemler, gizlilik ilkesine uymalıdır.",
                "• Hakemler, zamanında değerlendirme yapmalıdır.",
                "• Hakemler, çıkar çatışması durumunda editöre bildirmelidir."
            ]),
            ("İntihal Politikası", [
                "Dergimiz, intihal tespit yazılımları kullanarak tüm gönderilen makaleleri",
                "kontrol eder. İntihal tespit edilen makaleler reddedilir ve yazarlar",
                "hakkında gerekli işlemler yapılır."
            ]),
            ("Ret ve İtiraz Politikası", [
                "• Reddedilen makaleler için yazarlar gerekçeli ret mektubu alır.",
                "• Yazarlar, ret kararına itiraz edebilir.",
                "• İtirazlar, editör kurulu tarafından değerlendirilir."
            ])
        ]
        
        for section_title, section_texts in sections:
            section_frame = tk.Frame(parent, bg=self.colors['white'])
            section_frame.pack(fill=tk.X, pady=(0, 25))
            
            title_label = tk.Label(section_frame, text=section_title,
                                  font=('Arial', 16, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['primary'], anchor='w')
            title_label.pack(fill=tk.X, pady=(0, 10))
            
            for text in section_texts:
                text_label = tk.Label(section_frame, text=text,
                                     font=('Arial', 11), bg=self.colors['white'],
                                     fg=self.colors['dark_text'], anchor='w', justify='left',
                                     wraplength=800)
                text_label.pack(fill=tk.X, pady=2)

    def _show_fee_policy(self, parent):
        """Ücret Politikası içeriği"""
        sections = [
            ("Genel Politika", [
                "İSTE Mühendislik Dergisi, açık erişim prensibini benimser ve tüm makaleler",
                "ücretsiz olarak erişilebilir durumdadır. Dergimiz, yazarlardan makale gönderme",
                "veya yayınlama ücreti talep etmemektedir."
            ]),
            ("Ücretsiz Hizmetler", [
                "Aşağıdaki hizmetler tamamen ücretsizdir:",
                "• Makale gönderme",
                "• Makale değerlendirme",
                "• Makale yayınlama",
                "• Açık erişim",
                "• DOI atama",
                "• PDF indirme"
            ]),
            ("Ek Hizmetler", [
                "Dergimiz, temel hizmetlerin yanı sıra aşağıdaki ek hizmetleri de sunmaktadır:",
                "• Hızlı değerlendirme (opsiyonel): Ek ücret gerektirmez",
                "• Renkli şekiller: Basılı versiyonda renkli şekiller ücretsizdir",
                "• Ek sayfa: İlk 10 sayfa ücretsiz, sonrası için ücret talep edilmez"
            ]),
            ("Finansman", [
                "Dergimiz, İskenderun Teknik Üniversitesi tarafından desteklenmektedir.",
                "Bu sayede yazarlardan herhangi bir ücret talep edilmemektedir."
            ])
        ]
        
        for section_title, section_texts in sections:
            section_frame = tk.Frame(parent, bg=self.colors['white'])
            section_frame.pack(fill=tk.X, pady=(0, 25))
            
            title_label = tk.Label(section_frame, text=section_title,
                                  font=('Arial', 16, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['primary'], anchor='w')
            title_label.pack(fill=tk.X, pady=(0, 10))
            
            for text in section_texts:
                text_label = tk.Label(section_frame, text=text,
                                     font=('Arial', 11), bg=self.colors['white'],
                                     fg=self.colors['dark_text'], anchor='w', justify='left',
                                     wraplength=800)
                text_label.pack(fill=tk.X, pady=2)

    def _show_editorial_boards(self, parent):
        """Dergi Kurulları içeriği"""
        sections = [
            ("Editör Kurulu", [
                "Baş Editör:",
                "Prof. Dr. Ahmet Yılmaz - İskenderun Teknik Üniversitesi, Mühendislik Fakültesi",
                "",
                "Yardımcı Editörler:",
                "• Prof. Dr. Mehmet Demir - Bilgisayar Mühendisliği Bölümü",
                "• Prof. Dr. Ayşe Kaya - Elektrik-Elektronik Mühendisliği Bölümü",
                "• Prof. Dr. Mustafa Özkan - Makine Mühendisliği Bölümü",
                "• Prof. Dr. Zeynep Şahin - Endüstri Mühendisliği Bölümü"
            ]),
            ("Alan Editörleri", [
                "Bilgisayar Mühendisliği:",
                "• Doç. Dr. Can Arslan - Yazılım Mühendisliği",
                "• Doç. Dr. Elif Yıldız - Yapay Zeka ve Makine Öğrenmesi",
                "",
                "Elektrik-Elektronik Mühendisliği:",
                "• Doç. Dr. Burak Çelik - Kontrol Sistemleri ve Otomasyon",
                "• Doç. Dr. Deniz Aydın - Güç Elektroniği ve Enerji Sistemleri",
                "",
                "Makine Mühendisliği:",
                "• Doç. Dr. Emre Koç - Termodinamik ve Enerji",
                "• Doç. Dr. Fatma Yılmaz - Malzeme Bilimi ve Mühendisliği",
                "",
                "Endüstri Mühendisliği:",
                "• Doç. Dr. Gökhan Özdemir - Üretim Sistemleri",
                "• Doç. Dr. Hülya Kılıç - Optimizasyon ve Yöneylem Araştırması"
            ]),
            ("Hakem Kurulu", [
                "Dergimiz, ulusal ve uluslararası alanında uzman akademisyenlerden oluşan",
                "geniş bir hakem kuruluna sahiptir. Hakemler, makaleleri objektif ve",
                "bilimsel kriterlere göre değerlendirmektedir."
            ]),
            ("Yayın Kurulu", [
                "Yayın kurulu, derginin yayın politikalarını belirler ve stratejik kararlar",
                "alır. Kurul, derginin bilimsel kalitesini ve etik standartlarını korumakla",
                "yükümlüdür."
            ])
        ]
        
        for section_title, section_texts in sections:
            section_frame = tk.Frame(parent, bg=self.colors['white'])
            section_frame.pack(fill=tk.X, pady=(0, 25))
            
            title_label = tk.Label(section_frame, text=section_title,
                                  font=('Arial', 16, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['primary'], anchor='w')
            title_label.pack(fill=tk.X, pady=(0, 10))
            
            for text in section_texts:
                if text == "":
                    continue
                text_label = tk.Label(section_frame, text=text,
                                     font=('Arial', 11), bg=self.colors['white'],
                                     fg=self.colors['dark_text'], anchor='w', justify='left',
                                     wraplength=800)
                text_label.pack(fill=tk.X, pady=2)

    def _show_indexes(self, parent):
        """Dizinler içeriği"""
        sections = [
            ("Ulusal Dizinler", [
                "Dergimiz aşağıdaki ulusal dizinlerde taranmaktadır:",
                "• TR Dizin (TÜBİTAK)",
                "• ULAKBİM Sosyal ve Beşeri Bilimler Veri Tabanı",
                "• Türk Eğitim İndeksi",
                "• ASOS İndeks"
            ]),
            ("Uluslararası Dizinler", [
                "Dergimiz aşağıdaki uluslararası dizinlerde taranmaktadır:",
                "• Google Scholar",
                "• EBSCO",
                "• Index Copernicus",
                "• DOAJ (Directory of Open Access Journals) - Başvuru aşamasında"
            ]),
            ("DOI ve ISSN", [
                "• DOI Öneki: 10.5555/iste-eng",
                "• e-ISSN: 2757-9876",
                "• Basılı ISSN: 2757-9868",
                "• Yayıncı: İskenderun Teknik Üniversitesi",
                "• Kuruluş Yılı: 2025"
            ]),
            ("Erişim", [
                "Tüm makaleler dergi web sitesinden ücretsiz olarak erişilebilir.",
                "Makaleler PDF formatında indirilebilir ve açık erişim lisansı altında",
                "yayınlanmaktadır."
            ])
        ]
        
        for section_title, section_texts in sections:
            section_frame = tk.Frame(parent, bg=self.colors['white'])
            section_frame.pack(fill=tk.X, pady=(0, 25))
            
            title_label = tk.Label(section_frame, text=section_title,
                                  font=('Arial', 16, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['primary'], anchor='w')
            title_label.pack(fill=tk.X, pady=(0, 10))
            
            for text in section_texts:
                text_label = tk.Label(section_frame, text=text,
                                     font=('Arial', 11), bg=self.colors['white'],
                                     fg=self.colors['dark_text'], anchor='w', justify='left',
                                     wraplength=800)
                text_label.pack(fill=tk.X, pady=2)

    def _show_statistics(self, parent):
        """İstatistikler içeriği"""
        # Veritabanından istatistikleri al
        all_articles = self.db.get_all_articles()
        published_articles = self.db.get_articles_by_status("Yayınlandı")
        pending_articles = self.db.get_articles_by_status("Beklemede")
        review_articles = self.db.get_articles_by_status("Değerlendirmede")
        
        # Yıllara göre dağılım
        years = {}
        for article in published_articles:
            year = article.get('year', 'Belirtilmemiş')
            years[year] = years.get(year, 0) + 1
        
        sections = [
            ("Genel İstatistikler", [
                f"• Toplam Makale Sayısı: {len(all_articles)}",
                f"• Yayınlanan Makale Sayısı: {len(published_articles)}",
                f"• Değerlendirme Aşamasındaki Makaleler: {len(review_articles)}",
                f"• Bekleyen Makaleler: {len(pending_articles)}"
            ]),
            ("Yıllara Göre Yayın Dağılımı", [
                "Yayınlanan makalelerin yıllara göre dağılımı:"
            ])
        ]
        
        for section_title, section_texts in sections:
            section_frame = tk.Frame(parent, bg=self.colors['white'])
            section_frame.pack(fill=tk.X, pady=(0, 25))
            
            title_label = tk.Label(section_frame, text=section_title,
                                  font=('Arial', 16, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['primary'], anchor='w')
            title_label.pack(fill=tk.X, pady=(0, 10))
            
            for text in section_texts:
                text_label = tk.Label(section_frame, text=text,
                                     font=('Arial', 11), bg=self.colors['white'],
                                     fg=self.colors['dark_text'], anchor='w', justify='left',
                                     wraplength=800)
                text_label.pack(fill=tk.X, pady=2)
            
            # Yıllara göre dağılımı göster
            if section_title == "Yıllara Göre Yayın Dağılımı":
                if years:
                    for year in sorted(years.keys(), reverse=True):
                        year_label = tk.Label(section_frame, 
                                             text=f"  • {year}: {years[year]} makale",
                                             font=('Arial', 11), bg=self.colors['white'],
                                             fg=self.colors['dark_text'], anchor='w',
                                             wraplength=800)
                        year_label.pack(fill=tk.X, pady=2, padx=(20, 0))
                else:
                    no_data_label = tk.Label(section_frame, 
                                            text="  Henüz yayınlanmış makale bulunmamaktadır.",
                                            font=('Arial', 11), bg=self.colors['white'],
                                            fg=self.colors['secondary'], anchor='w',
                                            wraplength=800)
                    no_data_label.pack(fill=tk.X, pady=2, padx=(20, 0))

    def show_login_screen(self):
        self.clear_screen()

        # Modern arka plan
        container = tk.Frame(self.main_container, bg=self.colors['light'])
        container.pack(fill=tk.BOTH, expand=True)

        # Modern başlık
        header_frame = tk.Frame(container, bg=self.colors['primary'], height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Geri dön butonu
        back_btn = tk.Button(header_frame, text="← Geri Dön", font=self.fonts['body'],
                            bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                            cursor='hand2', bd=0, activebackground=self.colors['secondary_light'],
                            activeforeground='white', command=self.show_home_page,
                            padx=15, pady=8)
        back_btn.pack(anchor='nw', padx=20, pady=15)
        
        title = tk.Label(header_frame, text="📚 Akademik Dergi Sistemi",
                         font=self.fonts['title'], bg=self.colors['primary'], fg='white')
        title.pack(pady=(5, 5))

        subtitle = tk.Label(header_frame, text="İSTE Mühendislik Dergisi • Giriş / Kayıt",
                            font=self.fonts['subtitle'], bg=self.colors['primary'], fg='white')
        subtitle.pack()

        forms_frame = tk.Frame(container, bg=self.colors['light'])
        forms_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        # Modern giriş kartı
        login_card = tk.Frame(forms_frame, bg=self.colors['white'], relief=tk.FLAT, borderwidth=0)
        login_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        login_inner = tk.Frame(login_card, bg=self.colors['white'], relief=tk.RAISED, borderwidth=2)
        login_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        tk.Label(login_inner, text="🔐 Kayıtlı Kullanıcı Girişi",
                 font=self.fonts['heading'], bg=self.colors['white'], fg=self.colors['primary']).pack(anchor='w', padx=25, pady=(25, 15))

        login_frame = tk.Frame(login_inner, bg=self.colors['white'])
        login_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))

        tk.Label(login_frame, text="E-posta / Kullanıcı Adı", font=self.fonts['body'], 
                 bg=self.colors['white'], fg=self.colors['dark_text']).pack(anchor='w', pady=(10, 6))
        self.email_entry = tk.Entry(login_frame, font=self.fonts['body'], relief=tk.FLAT,
                                    bg=self.colors['light'], bd=2, highlightthickness=1,
                                    highlightbackground=self.colors['shadow'],
                                    highlightcolor=self.colors['secondary'])
        self.email_entry.pack(fill=tk.X, ipady=10)
        self.email_entry.insert(0, "admin")

        tk.Label(login_frame, text="Şifre", font=self.fonts['body'], bg=self.colors['white'], 
                 fg=self.colors['dark_text']).pack(anchor='w', pady=(18, 6))
        self.password_entry = tk.Entry(login_frame, font=self.fonts['body'], show="*",
                                       relief=tk.FLAT, bg=self.colors['light'], bd=2,
                                       highlightthickness=1, highlightbackground=self.colors['shadow'],
                                       highlightcolor=self.colors['secondary'])
        self.password_entry.pack(fill=tk.X, ipady=10)
        self.password_entry.insert(0, "DYS.2025")

        login_btn = tk.Button(login_frame, text="🚀 GİRİŞ YAP", font=self.fonts['button'],
                              bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                              cursor='hand2', bd=0, activebackground=self.colors['secondary_light'],
                              activeforeground='white', command=self.login)
        login_btn.pack(fill=tk.X, pady=(28, 10), ipady=12)

        # Modern kayıt kartı
        register_card = tk.Frame(forms_frame, bg=self.colors['white'], relief=tk.FLAT, borderwidth=0)
        register_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        register_inner = tk.Frame(register_card, bg=self.colors['white'], relief=tk.RAISED, borderwidth=2)
        register_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        tk.Label(register_inner, text="✨ Yeni Kullanıcı Kaydı",
                 font=self.fonts['heading'], bg=self.colors['white'], fg=self.colors['primary']).pack(anchor='w', padx=25, pady=(25, 15))

        reg_frame = tk.Frame(register_inner, bg=self.colors['white'])
        reg_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))

        tk.Label(reg_frame, text="Ad Soyad", font=self.fonts['body'], bg=self.colors['white'], 
                 fg=self.colors['dark_text']).pack(anchor='w', pady=(10, 6))
        self.reg_name = tk.Entry(reg_frame, font=self.fonts['body'], relief=tk.FLAT,
                                 bg=self.colors['light'], bd=2, highlightthickness=1,
                                 highlightbackground=self.colors['shadow'],
                                 highlightcolor=self.colors['success'])
        self.reg_name.pack(fill=tk.X, ipady=10)

        tk.Label(reg_frame, text="E-posta / Kullanıcı Adı", font=self.fonts['body'], bg=self.colors['white'], 
                 fg=self.colors['dark_text']).pack(anchor='w', pady=(18, 6))
        self.reg_email = tk.Entry(reg_frame, font=self.fonts['body'], relief=tk.FLAT,
                                  bg=self.colors['light'], bd=2, highlightthickness=1,
                                  highlightbackground=self.colors['shadow'],
                                  highlightcolor=self.colors['success'])
        self.reg_email.pack(fill=tk.X, ipady=10)

        tk.Label(reg_frame, text="Şifre", font=self.fonts['body'], bg=self.colors['white'], 
                 fg=self.colors['dark_text']).pack(anchor='w', pady=(18, 6))
        self.reg_password = tk.Entry(reg_frame, font=self.fonts['body'], show="*",
                                     relief=tk.FLAT, bg=self.colors['light'], bd=2,
                                     highlightthickness=1, highlightbackground=self.colors['shadow'],
                                     highlightcolor=self.colors['success'])
        self.reg_password.pack(fill=tk.X, ipady=10)

        tk.Label(reg_frame, text="ℹ️ Rol admin tarafından atanacaktır.", font=self.fonts['small'],
                 bg=self.colors['white'], fg=self.colors['secondary']).pack(anchor='w', pady=(15, 8))

        register_btn = tk.Button(reg_frame, text="✅ KAYIT OLUŞTUR", font=self.fonts['button'],
                                 bg=self.colors['success'], fg='white', relief=tk.FLAT,
                                 cursor='hand2', bd=0, activebackground=self.colors['success_light'],
                                 activeforeground='white', command=self.register_user_request)
        register_btn.pack(fill=tk.X, pady=(12, 6), ipady=12)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showerror("Hata", "Lütfen e-posta ve şifreyi girin.")
            return

        user = self.db.get_user(email)
        if not user or user.get("password") != password:
            messagebox.showerror("Hata", "Kullanıcı bulunamadı veya şifre hatalı.")
            return

        self.current_user = email
        roles = user.get("roles", ["Yazar"])
        self.user_role = roles[0] if roles else "Yazar"
        self.show_main_dashboard()

    def register_user_request(self):
        name = self.reg_name.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get().strip()

        if not all([name, email, password]):
            messagebox.showerror("Hata", "Lütfen tüm kayıt alanlarını doldurun.")
            return

        if self.db.get_user(email):
            messagebox.showerror("Hata", "Bu kullanıcı zaten kayıtlı.")
            return

        # Rol admin tarafından atanacak; varsayılan yazar olarak ekle
        if self.db.add_user(email, password, name, ["Yazar"]):
            messagebox.showinfo("Bilgi", "Kayıt başarılı.")
            self.reg_name.delete(0, tk.END)
            self.reg_email.delete(0, tk.END)
            self.reg_password.delete(0, tk.END)
        else:
            messagebox.showerror("Hata", "Kayıt sırasında bir hata oluştu.")

    def show_main_dashboard(self):
        self.clear_screen()

        # Üst menü çubuğu
        self.create_top_menu()

        # Modern ana içerik alanı
        content_frame = tk.Frame(self.main_container, bg=self.colors['light'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Sol menü ve sağ içerik
        left_menu = self.create_left_menu(content_frame)
        left_menu.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        self.content_area = tk.Frame(content_frame, bg='white', relief=tk.FLAT, borderwidth=0)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # İçerik için gölge efekti
        content_inner = tk.Frame(self.content_area, bg='white', relief=tk.RAISED, borderwidth=2)
        content_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.content_area = content_inner  # Referansı güncelle

        # Varsayılan içeriği göster
        self.show_dashboard_content()

    def create_top_menu(self):
        # Modern üst menü çubuğu
        menu_bar = tk.Frame(self.main_container, bg=self.colors['primary'], height=75)
        menu_bar.pack(fill=tk.X)
        menu_bar.pack_propagate(False)

        # Logo ve başlık - Dergi adı
        logo_frame = tk.Frame(menu_bar, bg=self.colors['primary'])
        logo_frame.pack(side=tk.LEFT, padx=25, pady=20)

        logo = tk.Label(logo_frame, text="📚 İSTE Mühendislik Dergisi", font=self.fonts['heading'],
                        bg=self.colors['primary'], fg='white')
        logo.pack()

        # Boşluk için spacer (arama kutusu kaldırıldı)
        spacer = tk.Frame(menu_bar, bg=self.colors['primary'])
        spacer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Modern kullanıcı bilgisi paneli
        user_frame = tk.Frame(menu_bar, bg=self.colors['primary'])
        user_frame.pack(side=tk.RIGHT, padx=25, pady=18)

        user_info = f"👤 {self.user_role}: {self.current_user}" if self.current_user else "👤 Giriş yapılmadı"
        user_label = tk.Label(user_frame, text=user_info,
                              font=self.fonts['body'], bg=self.colors['primary'], fg='white')
        user_label.pack(side=tk.LEFT, padx=8)

        # Modern rol seçici
        if self.current_user:
            user = self.db.get_user(self.current_user)
            roles = user.get("roles", [self.user_role]) if user else [self.user_role]
            self.role_switch_var = tk.StringVar(value=self.user_role)
            role_combo = ttk.Combobox(user_frame, textvariable=self.role_switch_var,
                                      values=roles, state='readonly', width=14,
                                      font=self.fonts['body'])
            role_combo.pack(side=tk.LEFT, padx=8)

            role_combo.bind("<<ComboboxSelected>>", self.switch_role)

        logout_btn = tk.Button(user_frame, text="🚪 Çıkış", font=self.fonts['small'],
                               bg=self.colors['danger'], fg='white', relief=tk.FLAT,
                               cursor='hand2', padx=16, pady=6, bd=0,
                               activebackground=self.colors['danger_light'],
                               activeforeground='white',
                               command=self.show_home_page)
        logout_btn.pack(side=tk.LEFT, padx=(8, 0))

    def switch_role(self, event=None):
        selected = self.role_switch_var.get() if hasattr(self, "role_switch_var") else None
        if selected:
            self.user_role = selected
            self.show_main_dashboard()

    def create_left_menu(self, parent):
        # Modern sol menü
        menu_frame = tk.Frame(parent, bg='white', width=260, relief=tk.FLAT, borderwidth=0)
        menu_inner = tk.Frame(menu_frame, bg='white', relief=tk.RAISED, borderwidth=2)
        menu_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Modern menü başlığı
        menu_title = tk.Label(menu_inner, text="📋 Ana Menü", font=self.fonts['heading'],
                              bg=self.colors['primary'], fg='white', pady=18)
        menu_title.pack(fill=tk.X)

        # Menü öğeleri
        menu_items = []

        if self.user_role == "Admin":
            menu_items = [
                ("🏠 Ana Sayfa", self.show_dashboard_content),
                ("👥 Kullanıcı Yönetimi", self.show_user_management),
                ("📧 Gelen Mesajlar", self.show_messages),
                ("📨 İletişim Mesajları", self.show_contact_messages),
                ("📝 Gönderilenler", self.show_submissions),
                ("📋 Değerlendirmede", self.show_review),
                ("📊 İstatistikler", self.show_statistics),
                ("⚙ Ayarlar", self.show_settings)
            ]
        elif self.user_role == "Editör":
            menu_items = [
                ("🏠 Ana Sayfa", self.show_dashboard_content),
                ("📝 Gönderilenler", self.show_submissions),
                ("✅ Onay Bekleyenler", self.show_pending),
                ("📋 Değerlendirmede", self.show_review),
                ("✔ Kabul Edilenler", self.show_accepted),
                ("❌ Reddedilenler", self.show_rejected),
                ("📚 Sayı Oluştur ve Yayınla", self.show_publish_issue),
                ("📖 Arşiv", self.show_archive),
                ("👥 Hakemler", self.show_reviewers),
                ("📊 İstatistikler", self.show_statistics),
                ("⚙ Ayarlar", self.show_settings)
            ]
        elif self.user_role == "Yazar":
            menu_items = [
                ("🏠 Ana Sayfa", self.show_dashboard_content),
                ("➕ Yeni Makale Gönder", self.show_new_submission),
                ("📝 Makalelerim", self.show_my_articles),
                ("📊 Durum Takibi", self.show_status),
                ("📖 Yayınlarım", self.show_publications),
                ("⚙ Profil Ayarları", self.show_settings)
            ]
        elif self.user_role == "Hakem":
            menu_items = [
                ("🏠 Ana Sayfa", self.show_dashboard_content),
                ("📋 Atanan Makaleler", self.show_assigned),
                ("✅ Değerlendirilenler", self.show_evaluated),
                ("⏳ Bekleyen Görevler", self.show_pending_tasks),
                ("📧 Gelen Mesajlar", self.show_messages),
                ("📤 Gönderilen Kararlar", self.show_sent_decisions),
                ("⚙ Profil Ayarları", self.show_settings)
            ]
        elif self.user_role == "Alan Editörü":
            menu_items = [
                ("🏠 Ana Sayfa", self.show_dashboard_content),
                ("📌 Alanımdaki Makaleler", self.show_submissions),
                ("🧾 Ön İnceleme", self.show_pending),
                ("👥 Hakem Havuzu", self.show_reviewers),
                ("📧 Gelen Mesajlar", self.show_messages),
                ("📤 Gönderilen Mesajlar", self.show_sent_messages),
                ("📊 Alan İstatistikleri", self.show_statistics),
                ("⚙ Ayarlar", self.show_settings)
            ]
        else:
            menu_items = [
                ("🏠 Ana Sayfa", self.show_dashboard_content),
                ("⚙ Ayarlar", self.show_settings)
            ]

        # Modern menü butonları
        for text, command in menu_items:
            btn = tk.Button(menu_inner, text=text, font=self.fonts['body'],
                            bg='white', fg=self.colors['dark_text'], relief=tk.FLAT,
                            anchor='w', padx=22, pady=14, cursor='hand2',
                            bd=0, activebackground=self.colors['light'],
                            activeforeground=self.colors['primary'],
                            command=command)
            btn.pack(fill=tk.X, padx=2, pady=1)
            # Gelişmiş hover efekti
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.colors['light'], 
                                                           fg=self.colors['primary'],
                                                           font=(self.fonts['body'][0], self.fonts['body'][1], 'bold')))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='white', 
                                                          fg=self.colors['dark_text'],
                                                          font=self.fonts['body']))

        return menu_frame

    def show_dashboard_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Modern başlık
        header = tk.Label(self.content_area, text=f"🏠 Hoş Geldiniz, {self.user_role}",
                          font=self.fonts['title'], bg='white', fg=self.colors['primary'])
        header.pack(pady=25, padx=25, anchor='w')

        # Modern istatistik kartları
        stats_frame = tk.Frame(self.content_area, bg='white')
        stats_frame.pack(fill=tk.X, padx=25, pady=15)

        if self.user_role == "Admin":
            all_users = self.db.get_all_users()
            all_articles = self.db.get_all_articles()
            # Aktif roller sayısını hesapla (benzersiz roller)
            all_roles = set()
            for user in all_users:
                for role in user.get("roles", []):
                    if role not in ["Beklemede", "Yazar"]:  # Yazar herkeste var, Beklemede geçici durum
                        all_roles.add(role)
            active_roles_count = len(all_roles)
            stats = [
                ("Kullanıcı Sayısı", str(len(all_users)), self.colors['secondary']),
                ("Aktif Roller", str(active_roles_count), self.colors['success']),
                ("Bekleyen Kayıt", str(len([u for u in all_users if "Beklemede" in u.get('roles', [])])), self.colors['warning']),
                ("Toplam Makale", str(len(all_articles)), self.colors['dark'])
            ]
        elif self.user_role == "Editör":
            all_articles = self.db.get_all_articles()
            pending = len([a for a in all_articles if a.get("status") in ["Editör İncelemede", "Alan Editörü İncelemede", "Beklemede"]])
            in_review = len([a for a in all_articles if a.get("status") in ["Hakemde", "Alan Editörü İncelemede"]])
            accepted = len([a for a in all_articles if "Kabul" in a.get("status", "") or a.get("status") == "Yayınlandı"])
            total = len(all_articles)
            stats = [
                ("Bekleyen Makaleler", str(pending), self.colors['warning']),
                ("Değerlendirmede", str(in_review), self.colors['secondary']),
                ("Kabul Edilenler", str(accepted), self.colors['success']),
                ("Toplam Makale", str(total), self.colors['dark'])
            ]
        elif self.user_role == "Yazar":
            all_articles = self.db.get_all_articles()
            my_articles = [a for a in all_articles if a.get("author") == self.current_user]
            submitted = len(my_articles)
            in_review = len([a for a in my_articles if a.get("status") == "Hakemde"])
            accepted = len([a for a in my_articles if "Kabul" in a.get("status", "") or a.get("status") == "Yayınlandı"])
            published = len([a for a in my_articles if a.get("status") == "Yayınlandı"])
            stats = [
                ("Gönderilen", str(submitted), self.colors['secondary']),
                ("Değerlendirmede", str(in_review), self.colors['warning']),
                ("Kabul Edilen", str(accepted), self.colors['success']),
                ("Yayınlanan", str(published), self.colors['dark'])
            ]
        elif self.user_role == "Hakem":
            assigned_articles = self.db.get_articles_by_reviewer(self.current_user)
            evaluated = len([a for a in assigned_articles if self.current_user in a.get("decisions", {})])
            pending = len(assigned_articles) - evaluated
            total = len(assigned_articles)
            stats = [
                ("Atanan", str(total), self.colors['warning']),
                ("Değerlendirilen", str(evaluated), self.colors['success']),
                ("Bekleyen", str(pending), self.colors['danger']),
                ("Toplam", str(total), self.colors['dark'])
            ]
        elif self.user_role == "Alan Editörü":
            all_articles = self.db.get_all_articles()
            my_articles = [a for a in all_articles if a.get("field_editor") == self.current_user]
            total = len(my_articles)
            sent_to_reviewer = len([a for a in my_articles if a.get("status") == "Hakemde"])
            recommended = len([a for a in my_articles if a.get("field_editor_recommendation")])
            waiting_decision = len([a for a in my_articles if a.get("status") in ["Hakem Kararı", "3. Hakem Gerekli"]])
            stats = [
                ("Alanındaki Makaleler", str(total), self.colors['secondary']),
                ("Hakeme Gönderilen", str(sent_to_reviewer), self.colors['warning']),
                ("Kabul Önerisi", str(recommended), self.colors['success']),
                ("Bekleyen Karar", str(waiting_decision), self.colors['danger'])
            ]
        else:
            stats = [
                ("Aktif Roller", "4", self.colors['secondary']),
                ("Makaleler", "0", self.colors['success']),
                ("Bekleyen", "0", self.colors['warning']),
                ("Genel", "-", self.colors['dark'])
            ]

        for i, (title, value, color) in enumerate(stats):
            # Modern kart tasarımı
            card = tk.Frame(stats_frame, bg=color, relief=tk.FLAT, borderwidth=0)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8)
            card_inner = tk.Frame(card, bg=color, relief=tk.RAISED, borderwidth=3)
            card_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            value_label = tk.Label(card_inner, text=value, font=('Segoe UI', 36, 'bold'),
                                   bg=color, fg='white')
            value_label.pack(pady=(25, 8))

            title_label = tk.Label(card_inner, text=title, font=self.fonts['body'],
                                   bg=color, fg='white')
            title_label.pack(pady=(0, 25))

        # Modern aktiviteler bölümü
        activity_frame = tk.Frame(self.content_area, bg='white')
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        activity_title = tk.Label(activity_frame, text="📊 Son Aktiviteler",
                                  font=self.fonts['heading'], bg='white',
                                  fg=self.colors['primary'])
        activity_title.pack(anchor='w', pady=(0, 15))

        # Treeview için aktivite listesi
        columns = ('Tarih', 'Durum', 'Makale', 'İşlem')
        tree = ttk.Treeview(activity_frame, columns=columns, show='headings', height=10)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        # Örnek veriler
        activities = [
            ('07.12.2024', 'Gönderildi', 'Yapay Zeka ve Makine Öğrenmesi', 'Yazar: Dr. Ahmet Yılmaz'),
            ('06.12.2024', 'Kabul Edildi', 'Blockchain Teknolojisi', 'Editör onayı'),
            ('05.12.2024', 'Değerlendirmede', 'Kuantum Hesaplama', 'Hakem atandı'),
            ('04.12.2024', 'Revizyon', 'IoT ve Güvenlik', 'Düzeltme istendi'),
            ('03.12.2024', 'Yayınlandı', 'Big Data Analizi', 'Sayı 2'),
        ]

        for activity in activities:
            tree.insert('', tk.END, values=activity)

        # Scrollbar
        scrollbar = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # --- İş akışı metotları ---
    def show_submissions(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        title = "📝 Gönderilen Makaleler"
        header = tk.Label(self.content_area, text=title, font=('Arial', 20, 'bold'),
                          bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')

        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Yazarlar için hakem sütunu gösterilmez
        if self.user_role == "Yazar":
            columns = ("Kod", "Başlık", "Yazar", "Durum", "Editör", "Alan Editörü")
        else:
            columns = ("Kod", "Başlık", "Yazar", "Durum", "Editör", "Alan Editörü", "Hakemler")
        
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=160)

        def fmt_reviewers(article):
            reviewers = article.get("reviewers", [])
            names = []
            for r in reviewers:
                user = self.db.get_user(r)
                names.append(user.get("name", r) if user else r)
            return ", ".join(names)

        # Tüm makaleleri veritabanından getir
        all_articles = self.db.get_all_articles()
        
        for art in all_articles:
            # Filtreleme role göre
            if self.user_role == "Yazar" and art.get("author") != self.current_user:
                continue
            if self.user_role == "Alan Editörü" and art.get("field_editor") not in [None, self.current_user]:
                continue
            
            # Yazarlar için hakem bilgisi gösterilmez
            if self.user_role == "Yazar":
                values = (
                    art["id"],
                    art["title"],
                    art.get("authors", art.get("author", "")),
                    art["status"],
                    art.get("editor", ""),
                    art.get("field_editor", "")
                )
            else:
                values = (
                    art["id"],
                    art["title"],
                    art.get("authors", art.get("author", "")),
                    art["status"],
                    art.get("editor", ""),
                    art.get("field_editor", ""),
                    fmt_reviewers(art)
                )
            tree.insert('', tk.END, values=values)

        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        action_frame = tk.Frame(self.content_area, bg='white')
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        if self.user_role in ["Admin", "Editör"]:
            tk.Button(action_frame, text="📄 Dosyayı Aç", bg=self.colors['info'], fg='white',
                      relief=tk.FLAT, cursor='hand2', command=lambda: self.open_article_file(tree)).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Button(action_frame, text="❌ Ön İncelemede Reddet", bg=self.colors['danger'], fg='white',
                      relief=tk.FLAT, cursor='hand2', command=lambda: self.reject_article_early(tree)).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Button(action_frame, text="✅ Alan Editörüne Ata", bg=self.colors['secondary'], fg='white',
                      relief=tk.FLAT, cursor='hand2', command=lambda: self.assign_field_editor(tree)).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Button(action_frame, text="💬 Yazarla İletişim", bg=self.colors['primary'], fg='white',
                      relief=tk.FLAT, cursor='hand2', command=lambda: self.communicate_with_author(tree)).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Button(action_frame, text="📊 Karar Ver (Editör)", bg=self.colors['success'], fg='white',
                      relief=tk.FLAT, cursor='hand2', command=lambda: self.finalize_articles(tree)).pack(side=tk.LEFT, padx=5, pady=5)
        if self.user_role == "Alan Editörü":
            tk.Button(action_frame, text="📄 Dosyayı Aç", bg=self.colors['info'], fg='white',
                      relief=tk.FLAT, cursor='hand2', command=lambda: self.open_article_file(tree)).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Button(action_frame, text="👥 Hakem Havuzundan Seç", bg=self.colors['secondary'], fg='white',
                      relief=tk.FLAT, cursor='hand2', command=lambda: self.assign_reviewers(tree)).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Button(action_frame, text="➕ 3. Hakem Ata", bg=self.colors['warning'], fg='white',
                      relief=tk.FLAT, cursor='hand2', command=lambda: self.assign_third_reviewer(tree)).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Button(action_frame, text="💬 Hakemlerle İletişim", bg=self.colors['primary'], fg='white',
                      relief=tk.FLAT, cursor='hand2', command=lambda: self.communicate_with_reviewers(tree)).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Button(action_frame, text="📋 Hakem Kararlarını Görüntüle", bg=self.colors['info'], fg='white',
                      relief=tk.FLAT, cursor='hand2', command=lambda: self.show_reviewer_decisions_for_fe(tree)).pack(side=tk.LEFT, padx=5, pady=5)
            tk.Button(action_frame, text="📊 Editöre Öneri Gönder", bg=self.colors['success'], fg='white',
                      relief=tk.FLAT, cursor='hand2', command=lambda: self.send_recommendation_to_editor(tree)).pack(side=tk.LEFT, padx=5, pady=5)

    def show_new_submission(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Canvas ve scrollbar
        canvas = tk.Canvas(self.content_area, bg='white')
        scrollbar = ttk.Scrollbar(self.content_area, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Başlık
        header = tk.Label(scrollable_frame, text="➕ Yeni Makale Gönder",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')

        # Form
        form_frame = tk.Frame(scrollable_frame, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=10)

        # Form alanlarını saklamak için dictionary
        self.submission_fields = {}
        self.selected_file_path = None

        # Form alanları
        fields = [
            ('title', 'Makale Başlığı:', 'entry'),
            ('subtitle', 'Alt Başlık:', 'entry'),
            ('keywords', 'Anahtar Kelimeler:', 'entry'),
            ('type', 'Makale Türü:', 'combo', ['Araştırma Makalesi', 'Derleme', 'Olgu Sunumu', 'Kısa Bildiri']),
            ('field', 'Alan:', 'combo', ['Bilgisayar Mühendisliği', 'Elektrik-Elektronik Mühendisliği', 
                                         'Makine Mühendisliği', 'İnşaat Mühendisliği', 'Endüstri Mühendisliği']),
            ('abstract_tr', 'Özet (Türkçe):', 'text'),
            ('abstract_en', 'Özet (İngilizce):', 'text'),
        ]

        for field_data in fields:
            if len(field_data) == 3:
                field_key, label_text, field_type = field_data
                options = []
            else:
                field_key, label_text, field_type, options = field_data
            
            label = tk.Label(form_frame, text=label_text, font=('Arial', 11, 'bold'),
                             bg='white', fg=self.colors['dark'])
            label.pack(anchor='w', pady=(15, 5))

            if field_type == 'entry':
                entry = tk.Entry(form_frame, font=('Arial', 11), relief=tk.FLAT,
                                 bg=self.colors['light'], bd=2)
                entry.pack(fill=tk.X, ipady=8)
                self.submission_fields[field_key] = entry
            elif field_type == 'combo':
                combo = ttk.Combobox(form_frame, font=('Arial', 11), state='readonly', values=options)
                combo.pack(fill=tk.X, ipady=5)
                self.submission_fields[field_key] = combo
            elif field_type == 'text':
                text = scrolledtext.ScrolledText(form_frame, font=('Arial', 10),
                                                 height=5, relief=tk.FLAT,
                                                 bg=self.colors['light'], bd=2)
                text.pack(fill=tk.X)
                self.submission_fields[field_key] = text

        # Dosya yükleme
        file_frame = tk.Frame(form_frame, bg='white')
        file_frame.pack(fill=tk.X, pady=20)

        file_label = tk.Label(file_frame, text="Makale Dosyası (Word/PDF):",
                              font=('Arial', 11, 'bold'), bg='white', fg=self.colors['dark'])
        file_label.pack(anchor='w', pady=(0, 10))

        file_info_label = tk.Label(file_frame, text="Dosya seçilmedi",
                                   font=('Arial', 10), bg='white', fg=self.colors['secondary'])
        file_info_label.pack(anchor='w', pady=(0, 10))

        def select_file():
            file_path = filedialog.askopenfilename(
                title="Makale Dosyası Seç",
                filetypes=[
                    ("Word Belgesi", "*.docx *.doc"),
                    ("PDF Dosyası", "*.pdf"),
                    ("Tüm Dosyalar", "*.*")
                ]
            )
            if file_path:
                self.selected_file_path = file_path
                file_name = os.path.basename(file_path)
                file_info_label.config(text=f"✓ Seçilen: {file_name}", fg=self.colors['success'])

        upload_btn = tk.Button(file_frame, text="📎 Dosya Seç", font=('Arial', 10),
                               bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                               cursor='hand2', padx=20, pady=8, command=select_file)
        upload_btn.pack(anchor='w')

        # Gönder butonu
        submit_btn = tk.Button(form_frame, text="✉ MAKALEYİ GÖNDER",
                               font=('Arial', 12, 'bold'), bg=self.colors['success'],
                               fg='white', relief=tk.FLAT, cursor='hand2',
                               command=lambda: self.create_article_submission(file_info_label))
        submit_btn.pack(fill=tk.X, pady=(30, 20), ipady=12)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_list_view(self, title, data):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Başlık
        header = tk.Label(self.content_area, text=title,
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')

        # Liste
        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ('Kod', 'Başlık', 'Yazar', 'Tarih', 'Durum')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        for item in data:
            tree.insert('', tk.END, values=item)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Placeholder ve iş akışı ekranları
    def show_pending(self):
        # Editör karar ekranı
        self.finalize_articles_view()

    def show_review(self):
        messagebox.showinfo("Bilgi", "Hakem süreci listesi özet ekranıdır. Ayrıntı için Gönderilenler / Atanan Makaleler ekranını kullanın.")

    def show_accepted(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        header = tk.Label(self.content_area, text="✔ Kabul Edilenler",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        data = []
        all_articles = self.db.get_all_articles()
        for art in all_articles:
            if art.get("status") in ["Kabul", "Yayına Hazır"]:
                author = art.get("authors", art.get("author", ""))
                data.append((art["id"], art["title"], author, "", art["status"]))
        self.show_list_view_table(data, header_text=None)

    def show_rejected(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        header = tk.Label(self.content_area, text="❌ Reddedilenler",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        data = []
        all_articles = self.db.get_all_articles()
        for art in all_articles:
            if art.get("status") == "Reddedildi":
                author = art.get("authors", art.get("author", ""))
                data.append((art["id"], art["title"], author, "", art["status"]))
        self.show_list_view_table(data, header_text=None)

    def show_reviewers(self):
        """Hakem havuzunu göster - uzmanlık alanlarıyla birlikte"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = tk.Label(self.content_area, text="👥 Hakem Havuzu",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        
        # Hakemleri getir
        all_users = self.db.get_all_users()
        reviewers = [u for u in all_users if "Hakem" in u.get("roles", [])]
        
        if not reviewers:
            tk.Label(self.content_area, text="Sistemde hakem bulunmamaktadır.",
                    font=('Arial', 12), bg='white', fg=self.colors['secondary']).pack(pady=50)
            return
        
        # Hakem listesi
        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(list_frame, bg='white')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Uzmanlık alanı seçenekleri
        field_options = ["", "Bilgisayar Mühendisliği", "Elektrik-Elektronik Mühendisliği", 
                         "Makine Mühendisliği", "Endüstri Mühendisliği", 
                         "İnşaat Mühendisliği", "Kimya Mühendisliği"]
        
        for reviewer in reviewers:
            # Hakem kartı
            reviewer_card = tk.Frame(scrollable_frame, bg='white', relief=tk.RAISED, borderwidth=1)
            reviewer_card.pack(fill=tk.X, pady=8, padx=5)
            
            # İç frame
            inner_frame = tk.Frame(reviewer_card, bg='white')
            inner_frame.pack(fill=tk.X, padx=15, pady=15)
            
            # Sol taraf - Bilgiler
            info_frame = tk.Frame(inner_frame, bg='white')
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Ad ve kullanıcı adı
            name_label = tk.Label(info_frame, 
                                 text=f"👤 {reviewer.get('name', '')} ({reviewer['username']})",
                                 font=('Arial', 12, 'bold'), bg='white', fg=self.colors['primary'])
            name_label.pack(anchor='w', pady=(0, 5))
            
            # Uzmanlık alanı
            expertise = reviewer.get("expertise_field", "")
            if expertise:
                expertise_label = tk.Label(info_frame,
                                         text=f"📚 Uzmanlık Alanı: {expertise}",
                                         font=('Arial', 10), bg='white', fg=self.colors['secondary'])
                expertise_label.pack(anchor='w')
            else:
                no_expertise_label = tk.Label(info_frame,
                                             text="📚 Uzmanlık Alanı: Belirtilmemiş",
                                             font=('Arial', 10, 'italic'), bg='white', fg=self.colors['secondary'])
                no_expertise_label.pack(anchor='w')
            
            # Sağ taraf - Uzmanlık alanı düzenleme (sadece admin ve alan editörü için)
            if self.user_role in ["Admin", "Alan Editörü"]:
                edit_frame = tk.Frame(inner_frame, bg='white')
                edit_frame.pack(side=tk.RIGHT, padx=(10, 0))
                
                tk.Label(edit_frame, text="Uzmanlık Alanı:", 
                        font=('Arial', 9), bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(0, 2))
                
                expertise_var = tk.StringVar(value=expertise if expertise else "")
                expertise_combo = ttk.Combobox(edit_frame, textvariable=expertise_var,
                                              values=field_options, state='readonly',
                                              width=30)
                expertise_combo.pack(anchor='w')
                
                def update_expertise(username=reviewer['username'], var=expertise_var):
                    new_expertise = var.get().strip() if var.get().strip() else None
                    self.db.update_user_expertise_field(username, new_expertise)
                    messagebox.showinfo("Başarılı", f"{username} kullanıcısının uzmanlık alanı güncellendi.")
                    self.show_reviewers()  # Listeyi yenile
                
                update_btn = tk.Button(edit_frame, text="Güncelle", 
                                      font=('Arial', 9), bg=self.colors['secondary'], fg='white',
                                      relief=tk.FLAT, cursor='hand2', 
                                      command=update_expertise, padx=10, pady=3)
                update_btn.pack(anchor='w', pady=(5, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # İstatistik bilgisi
        stats_label = tk.Label(self.content_area, 
                               text=f"📊 Toplam {len(reviewers)} hakem kayıtlı",
                               font=('Arial', 11, 'bold'), bg='white', fg=self.colors['primary'])
        stats_label.pack(pady=10, padx=20, anchor='w')

    def show_statistics(self):
        """Detaylı istatistik sayfası"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = tk.Label(self.content_area, text="📊 Detaylı İstatistikler",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        
        # Scrollable frame
        main_container = tk.Frame(self.content_area, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(main_container, bg='white')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas.find_all()[0], width=canvas_width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        # İstatistikler
        all_articles = self.db.get_all_articles()
        all_users = self.db.get_all_users()
        
        if self.user_role == "Admin":
            # Admin istatistikleri
            stats_cards = [
                ("Toplam Kullanıcı", len(all_users), self.colors['primary']),
                ("Toplam Makale", len(all_articles), self.colors['secondary']),
                ("Yayınlanmış Makale", len([a for a in all_articles if a.get("status") == "Yayınlandı"]), self.colors['success']),
                ("Bekleyen Makale", len([a for a in all_articles if a.get("status") in ["Editör İncelemede", "Alan Editörü İncelemede"]]), self.colors['warning']),
                ("Hakemde", len([a for a in all_articles if a.get("status") == "Hakemde"]), self.colors['info']),
                ("Reddedilen", len([a for a in all_articles if "Red" in a.get("status", "")]), self.colors['danger'])
            ]
            
            # Rol dağılımı
            role_dist = {}
            for user in all_users:
                for role in user.get("roles", []):
                    if role != "Yazar":  # Yazar herkeste var
                        role_dist[role] = role_dist.get(role, 0) + 1
            
            role_frame = tk.Frame(scrollable_frame, bg=self.colors['light'], relief=tk.RAISED, borderwidth=1)
            role_frame.pack(fill=tk.X, padx=10, pady=10)
            tk.Label(role_frame, text="👥 Rol Dağılımı", font=('Arial', 14, 'bold'),
                    bg=self.colors['light'], fg=self.colors['primary']).pack(pady=10)
            for role, count in sorted(role_dist.items()):
                tk.Label(role_frame, text=f"{role}: {count} kullanıcı", font=('Arial', 11),
                        bg=self.colors['light'], fg=self.colors['dark']).pack(anchor='w', padx=20, pady=2)
        
        elif self.user_role == "Editör":
            stats_cards = [
                ("Toplam Makale", len(all_articles), self.colors['primary']),
                ("Bekleyen", len([a for a in all_articles if a.get("status") in ["Editör İncelemede", "Alan Editörü İncelemede"]]), self.colors['warning']),
                ("Değerlendirmede", len([a for a in all_articles if a.get("status") in ["Hakemde", "Alan Editörü İncelemede"]]), self.colors['info']),
                ("Kabul Edilen", len([a for a in all_articles if "Kabul" in a.get("status", "")]), self.colors['success']),
                ("Yayınlanan", len([a for a in all_articles if a.get("status") == "Yayınlandı"]), self.colors['dark']),
                ("Reddedilen", len([a for a in all_articles if "Red" in a.get("status", "")]), self.colors['danger'])
            ]
        
        elif self.user_role == "Yazar":
            my_articles = [a for a in all_articles if a.get("author") == self.current_user]
            stats_cards = [
                ("Toplam Makale", len(my_articles), self.colors['primary']),
                ("Gönderilen", len([a for a in my_articles if a.get("status") in ["Editör İncelemede", "Alan Editörü İncelemede"]]), self.colors['secondary']),
                ("Değerlendirmede", len([a for a in my_articles if a.get("status") == "Hakemde"]), self.colors['warning']),
                ("Kabul Edilen", len([a for a in my_articles if "Kabul" in a.get("status", "")]), self.colors['success']),
                ("Yayınlanan", len([a for a in my_articles if a.get("status") == "Yayınlandı"]), self.colors['dark']),
                ("Reddedilen", len([a for a in my_articles if "Red" in a.get("status", "")]), self.colors['danger'])
            ]
        
        elif self.user_role == "Hakem":
            assigned_articles = self.db.get_articles_by_reviewer(self.current_user)
            evaluated = [a for a in assigned_articles if self.current_user in a.get("decisions", {})]
            stats_cards = [
                ("Atanan Makale", len(assigned_articles), self.colors['primary']),
                ("Değerlendirilen", len(evaluated), self.colors['success']),
                ("Bekleyen", len(assigned_articles) - len(evaluated), self.colors['warning']),
                ("Kabul Verdiğim", len([a for a in evaluated if a.get("decisions", {}).get(self.current_user) == "Kabul"]), self.colors['success']),
                ("Düzeltme İstediğim", len([a for a in evaluated if a.get("decisions", {}).get(self.current_user) == "Düzeltme"]), self.colors['warning']),
                ("Reddettiğim", len([a for a in evaluated if a.get("decisions", {}).get(self.current_user) == "Ret"]), self.colors['danger'])
            ]
        
        elif self.user_role == "Alan Editörü":
            my_articles = [a for a in all_articles if a.get("field_editor") == self.current_user]
            stats_cards = [
                ("Alanımdaki Makale", len(my_articles), self.colors['primary']),
                ("Ön İncelemede", len([a for a in my_articles if a.get("status") == "Alan Editörü İncelemede"]), self.colors['warning']),
                ("Hakemde", len([a for a in my_articles if a.get("status") == "Hakemde"]), self.colors['info']),
                ("Hakem Kararı", len([a for a in my_articles if a.get("status") == "Hakem Kararı"]), self.colors['secondary']),
                ("Editöre Önerilen", len([a for a in my_articles if a.get("field_editor_recommendation")]), self.colors['success']),
                ("Tamamlanan", len([a for a in my_articles if a.get("status") == "Yayınlandı"]), self.colors['dark'])
            ]
        else:
            stats_cards = [
                ("Toplam Makale", len(all_articles), self.colors['primary']),
                ("Yayınlanan", len([a for a in all_articles if a.get("status") == "Yayınlandı"]), self.colors['success'])
            ]
        
        # İstatistik kartları
        stats_frame = tk.Frame(scrollable_frame, bg='white')
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        for i, (title, value, color) in enumerate(stats_cards):
            card = tk.Frame(stats_frame, bg=color, relief=tk.RAISED, borderwidth=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            tk.Label(card, text=str(value), font=('Arial', 28, 'bold'),
                    bg=color, fg='white').pack(pady=(15, 5))
            tk.Label(card, text=title, font=('Arial', 10),
                    bg=color, fg='white', wraplength=120).pack(pady=(0, 15))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel desteği
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def show_settings(self):
        """Kullanıcı ayarları sayfası - şifre değiştirme ve bilgi güncelleme"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = tk.Label(self.content_area, text="⚙️ Profil Ayarları",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        
        # Mevcut kullanıcı bilgilerini getir
        current_user_data = self.db.get_user(self.current_user)
        if not current_user_data:
            messagebox.showerror("Hata", "Kullanıcı bilgileri alınamadı.")
            return
        
        # Ana içerik frame
        main_frame = tk.Frame(self.content_area, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Sol panel - Bilgi güncelleme
        left_panel = tk.Frame(main_frame, bg='#f9fbff', relief=tk.RAISED, borderwidth=1)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        
        tk.Label(left_panel, text="📝 Bilgilerimi Güncelle", font=('Arial', 14, 'bold'),
                 bg='#f9fbff', fg=self.colors['primary']).pack(anchor='w', padx=20, pady=(20, 10))
        
        # Kullanıcı adı (değiştirilemez)
        tk.Label(left_panel, text="Kullanıcı Adı", font=('Arial', 10),
                 bg='#f9fbff', fg=self.colors['dark']).pack(anchor='w', padx=20, pady=(10, 2))
        username_entry = tk.Entry(left_panel, font=('Arial', 11), relief=tk.FLAT, 
                                 bg=self.colors['light'], state='readonly')
        username_entry.insert(0, current_user_data.get("username", ""))
        username_entry.pack(fill=tk.X, padx=20, ipady=6)
        
        # Ad Soyad
        tk.Label(left_panel, text="Ad Soyad", font=('Arial', 10),
                 bg='#f9fbff', fg=self.colors['dark']).pack(anchor='w', padx=20, pady=(10, 2))
        self.settings_name_var = tk.StringVar(value=current_user_data.get("name", ""))
        name_entry = tk.Entry(left_panel, textvariable=self.settings_name_var,
                             font=('Arial', 11), relief=tk.FLAT, bg=self.colors['light'])
        name_entry.pack(fill=tk.X, padx=20, ipady=6)
        
        # Roller (sadece görüntüleme)
        tk.Label(left_panel, text="Roller", font=('Arial', 10),
                 bg='#f9fbff', fg=self.colors['dark']).pack(anchor='w', padx=20, pady=(10, 2))
        roles_text = ", ".join(current_user_data.get("roles", []))
        roles_entry = tk.Entry(left_panel, font=('Arial', 11), relief=tk.FLAT,
                              bg=self.colors['light'], state='readonly')
        roles_entry.insert(0, roles_text)
        roles_entry.pack(fill=tk.X, padx=20, ipady=6)
        
        # Uzmanlık Alanı (sadece Alan Editörü için)
        if "Alan Editörü" in current_user_data.get("roles", []):
            tk.Label(left_panel, text="Uzmanlık Alanı", font=('Arial', 10),
                     bg='#f9fbff', fg=self.colors['dark']).pack(anchor='w', padx=20, pady=(10, 2))
            self.settings_expertise_var = tk.StringVar(value=current_user_data.get("expertise_field", ""))
            field_options = ["", "Bilgisayar Mühendisliği", "Elektrik-Elektronik Mühendisliği", 
                             "Makine Mühendisliği", "Endüstri Mühendisliği", 
                             "İnşaat Mühendisliği", "Kimya Mühendisliği"]
            expertise_combo = ttk.Combobox(left_panel, textvariable=self.settings_expertise_var,
                                           values=field_options, state='readonly')
            expertise_combo.pack(fill=tk.X, padx=20, ipady=2)
        
        # Güncelle butonu
        update_info_btn = tk.Button(left_panel, text="BİLGİLERİMİ GÜNCELLE", 
                                    font=('Arial', 11, 'bold'), bg=self.colors['secondary'], 
                                    fg='white', relief=tk.FLAT, cursor='hand2',
                                    command=self.update_user_info)
        update_info_btn.pack(fill=tk.X, padx=20, pady=(20, 20), ipady=8)
        
        # Sağ panel - Şifre değiştirme
        right_panel = tk.Frame(main_frame, bg='#fff9f9', relief=tk.RAISED, borderwidth=1)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        
        tk.Label(right_panel, text="🔒 Şifre Değiştir", font=('Arial', 14, 'bold'),
                 bg='#fff9f9', fg=self.colors['primary']).pack(anchor='w', padx=20, pady=(20, 10))
        
        # Mevcut şifre
        tk.Label(right_panel, text="Mevcut Şifre", font=('Arial', 10),
                 bg='#fff9f9', fg=self.colors['dark']).pack(anchor='w', padx=20, pady=(10, 2))
        self.settings_current_password_var = tk.StringVar()
        current_password_entry = tk.Entry(right_panel, textvariable=self.settings_current_password_var,
                                         font=('Arial', 11), relief=tk.FLAT, bg=self.colors['light'], show="*")
        current_password_entry.pack(fill=tk.X, padx=20, ipady=6)
        
        # Yeni şifre
        tk.Label(right_panel, text="Yeni Şifre", font=('Arial', 10),
                 bg='#fff9f9', fg=self.colors['dark']).pack(anchor='w', padx=20, pady=(10, 2))
        self.settings_new_password_var = tk.StringVar()
        new_password_entry = tk.Entry(right_panel, textvariable=self.settings_new_password_var,
                                     font=('Arial', 11), relief=tk.FLAT, bg=self.colors['light'], show="*")
        new_password_entry.pack(fill=tk.X, padx=20, ipady=6)
        
        # Yeni şifre tekrar
        tk.Label(right_panel, text="Yeni Şifre (Tekrar)", font=('Arial', 10),
                 bg='#fff9f9', fg=self.colors['dark']).pack(anchor='w', padx=20, pady=(10, 2))
        self.settings_confirm_password_var = tk.StringVar()
        confirm_password_entry = tk.Entry(right_panel, textvariable=self.settings_confirm_password_var,
                                          font=('Arial', 11), relief=tk.FLAT, bg=self.colors['light'], show="*")
        confirm_password_entry.pack(fill=tk.X, padx=20, ipady=6)
        
        # Şifre değiştir butonu
        change_password_btn = tk.Button(right_panel, text="ŞİFREMİ DEĞİŞTİR", 
                                       font=('Arial', 11, 'bold'), bg=self.colors['danger'], 
                                       fg='white', relief=tk.FLAT, cursor='hand2',
                                       command=self.change_password)
        change_password_btn.pack(fill=tk.X, padx=20, pady=(20, 20), ipady=8)
    
    def update_user_info(self):
        """Kullanıcı bilgilerini güncelle"""
        new_name = self.settings_name_var.get().strip()
        if not new_name:
            messagebox.showerror("Hata", "Lütfen ad soyad girin.")
            return
        
        # Ad soyad güncelle
        self.db.update_user_name(self.current_user, new_name)
        
        # Uzmanlık alanı güncelle (eğer Alan Editörü ise)
        if hasattr(self, 'settings_expertise_var'):
            expertise_field = self.settings_expertise_var.get().strip() if self.settings_expertise_var.get().strip() else None
            self.db.update_user_expertise_field(self.current_user, expertise_field)
        
        messagebox.showinfo("Başarılı", "Bilgileriniz başarıyla güncellendi.")
        # Sayfayı yenile
        self.show_settings()
    
    def change_password(self):
        """Kullanıcı şifresini değiştir"""
        current_password = self.settings_current_password_var.get()
        new_password = self.settings_new_password_var.get().strip()
        confirm_password = self.settings_confirm_password_var.get().strip()
        
        if not current_password or not new_password or not confirm_password:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
            return
        
        # Mevcut şifre kontrolü
        user = self.db.get_user(self.current_user)
        if not user or user.get("password") != current_password:
            messagebox.showerror("Hata", "Mevcut şifre hatalı.")
            return
        
        # Yeni şifre kontrolü
        if new_password != confirm_password:
            messagebox.showerror("Hata", "Yeni şifreler eşleşmiyor.")
            return
        
        if len(new_password) < 3:
            messagebox.showerror("Hata", "Şifre en az 3 karakter olmalıdır.")
            return
        
        # Şifreyi güncelle
        self.db.update_user_password(self.current_user, new_password)
        messagebox.showinfo("Başarılı", "Şifreniz başarıyla değiştirildi.")
        
        # Formu temizle
        self.settings_current_password_var.set("")
        self.settings_new_password_var.set("")
        self.settings_confirm_password_var.set("")

    def show_my_articles(self):
        self.show_submissions()

    def show_status(self):
        self.show_submissions()

    def show_publications(self):
        """Yazarların yayınlanmış makalelerini göster"""
        if self.user_role != "Yazar":
            messagebox.showerror("Hata", "Bu alana sadece yazar erişebilir.")
            return
        
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = tk.Label(self.content_area, text="📖 Yayınlanmış Makalelerim",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        
        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("Kod", "Başlık", "Cilt", "Sayı", "Yıl", "Sayfa", "Durum")
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Yazarın yayınlanmış makalelerini getir
        all_articles = self.db.get_all_articles()
        published_articles = [art for art in all_articles 
                             if art.get("author") == self.current_user and 
                             art.get("status") == "Yayınlandı"]
        
        for art in published_articles:
            values = (
                art["id"],
                art["title"],
                art.get("volume", "N/A"),
                art.get("issue", "N/A"),
                art.get("year", "N/A"),
                art.get("pages", "N/A"),
                art["status"]
            )
            tree.insert('', tk.END, values=values)
        
        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        if not published_articles:
            tk.Label(self.content_area, text="Henüz yayınlanmış makaleniz bulunmamaktadır.",
                    font=('Arial', 12), bg='white', fg=self.colors['secondary']).pack(pady=20)
        
        # İstatistikler
        stats_frame = tk.Frame(self.content_area, bg='white')
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        stats_card = tk.Frame(stats_frame, bg=self.colors['light'], relief=tk.RAISED, borderwidth=1)
        stats_card.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(stats_card, text="📊 Yayın İstatistikleri", 
                font=('Arial', 14, 'bold'), bg=self.colors['light'], fg=self.colors['primary']).pack(pady=10)
        
        stats_inner = tk.Frame(stats_card, bg=self.colors['light'])
        stats_inner.pack(fill=tk.X, padx=20, pady=10)
        
        total_published = len(published_articles)
        tk.Label(stats_inner, text=f"Toplam Yayınlanmış Makale: {total_published}",
                font=('Arial', 12), bg=self.colors['light'], fg=self.colors['dark']).pack(anchor='w', pady=5)
        
        if published_articles:
            # Yıllara göre dağılım
            years = {}
            for art in published_articles:
                year = art.get("year", "Bilinmiyor")
                years[year] = years.get(year, 0) + 1
            
            tk.Label(stats_inner, text="Yıllara Göre Dağılım:",
                    font=('Arial', 11, 'bold'), bg=self.colors['light'], fg=self.colors['dark']).pack(anchor='w', pady=(10, 5))
            for year, count in sorted(years.items(), reverse=True):
                tk.Label(stats_inner, text=f"  {year}: {count} makale",
                        font=('Arial', 10), bg=self.colors['light'], fg=self.colors['secondary']).pack(anchor='w', padx=20)

    def show_assigned(self):
        # Hakem atanan makaleler (sadece karar verilmemiş olanlar)
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Mevcut görünümü kaydet
        self.current_view = 'assigned'

        header = tk.Label(self.content_area, text="📋 Atanan Makaleler (Hakem)",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')

        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("Kod", "Başlık", "Yazar", "Durum")
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        # Hakeme atanan makaleleri veritabanından getir - sadece karar verilmemiş olanlar
        # Veritabanından güncel veriyi çek
        assigned_articles = self.db.get_articles_by_reviewer(self.current_user)
        
        for art in assigned_articles:
            # Makaleyi yeniden veritabanından al (güncel kararlar için)
            fresh_art = self.db.get_article(art["id"])
            if not fresh_art:
                continue
            
            decisions = fresh_art.get("decisions", {})
            my_decision = decisions.get(self.current_user, "Henüz karar verilmedi")
            
            # Sadece karar verilmemiş makaleleri göster
            if my_decision == "Henüz karar verilmedi":
                author_name = fresh_art.get("authors", fresh_art.get("author", "Bilinmiyor"))
                tree.insert('', tk.END, values=(fresh_art["id"], fresh_art["title"], author_name, fresh_art["status"]))

        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        action = tk.Frame(self.content_area, bg='white')
        action.pack(fill=tk.X, padx=20, pady=8)
        
        # Makale detaylarını görüntüle ve dosya indir butonları
        tk.Button(action, text="📄 Detayları Görüntüle", bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                  cursor='hand2', command=lambda: self.show_article_details_for_reviewer(tree)).pack(side=tk.LEFT, padx=5)
        tk.Button(action, text="📥 Dosyayı İndir", bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                  cursor='hand2', command=lambda: self.download_article_file_for_reviewer(tree)).pack(side=tk.LEFT, padx=5)
        
        # Ayırıcı
        separator = tk.Frame(action, bg='#ddd', width=2)
        separator.pack(side=tk.LEFT, padx=10, fill=tk.Y, pady=5)

        tk.Button(action, text="KABUL", bg=self.colors['success'], fg='white', relief=tk.FLAT,
                  cursor='hand2', command=lambda: self.reviewer_decision(tree, "Kabul")).pack(side=tk.LEFT, padx=5)
        tk.Button(action, text="DÜZELTME", bg=self.colors['warning'], fg='white', relief=tk.FLAT,
                  cursor='hand2', command=lambda: self.reviewer_decision(tree, "Düzeltme")).pack(side=tk.LEFT, padx=5)
        tk.Button(action, text="RET", bg=self.colors['danger'], fg='white', relief=tk.FLAT,
                  cursor='hand2', command=lambda: self.reviewer_decision(tree, "Ret")).pack(side=tk.LEFT, padx=5)

    def show_evaluated(self):
        """Hakemlerin değerlendirdiği makaleleri göster"""
        if self.user_role != "Hakem":
            messagebox.showerror("Hata", "Bu alana sadece hakem erişebilir.")
            return
        
        # Mevcut görünümü kaydet
        self.current_view = 'evaluated'
        
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = tk.Label(self.content_area, text="✅ Değerlendirdiğim Makaleler",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        
        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("Kod", "Başlık", "Yazar", "Alan Editörü", "Verdiğim Karar", "Durum", "Tarih")
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        for col in columns:
            tree.heading(col, text=col)
            if col == "Başlık":
                tree.column(col, width=250)
            elif col in ["Kod", "Yazar", "Alan Editörü"]:
                tree.column(col, width=120)
            else:
                tree.column(col, width=150)
        
        # Hakeme atanan ve karar verdiği makaleleri getir
        # Veritabanından güncel veriyi çek
        assigned_articles = self.db.get_articles_by_reviewer(self.current_user)
        evaluated_count = 0
        
        for art in assigned_articles:
            # Makaleyi yeniden veritabanından al (güncel kararlar için)
            fresh_art = self.db.get_article(art["id"])
            if not fresh_art:
                continue
            
            decisions = fresh_art.get("decisions", {})
            my_decision = decisions.get(self.current_user, "Henüz karar verilmedi")
            
            # Karar verilmiş makaleleri göster
            if my_decision != "Henüz karar verilmedi":
                evaluated_count += 1
                # Hakem kararını veritabanından al
                reviews = self.db.get_reviews_by_article(fresh_art["id"])
                review_date = ""
                review_comment = ""
                review_file = ""
                for review in reviews:
                    if review["reviewer_username"] == self.current_user:
                        review_date = review.get("created_at", "")[:10] if review.get("created_at") else ""
                        review_comment = review.get("comment", "")[:50] + "..." if len(review.get("comment", "")) > 50 else review.get("comment", "")
                        review_file = "Var" if review.get("file_path") else "Yok"
                        break
                
                # Alan editörü bilgisini al
                field_editor = fresh_art.get("field_editor", "Atanmamış")
                if field_editor and field_editor != "Atanmamış":
                    fe_user = self.db.get_user(field_editor)
                    if fe_user:
                        field_editor = fe_user.get("name", field_editor)
                
                decision_color = self.colors['success'] if my_decision == "Kabul" else \
                               self.colors['danger'] if my_decision == "Ret" else \
                               self.colors['warning']
                
                values = (
                    fresh_art["id"],
                    fresh_art["title"][:50] + "..." if len(fresh_art["title"]) > 50 else fresh_art["title"],
                    fresh_art.get("authors", fresh_art.get("author", ""))[:30] + "..." if len(fresh_art.get("authors", fresh_art.get("author", ""))) > 30 else fresh_art.get("authors", fresh_art.get("author", "")),
                    field_editor[:30] + "..." if len(field_editor) > 30 else field_editor,
                    my_decision,
                    fresh_art["status"],
                    review_date
                )
                tree.insert('', tk.END, values=values, tags=(my_decision,))
        
        # Renk etiketleri
        tree.tag_configure("Kabul", background='#e8f5e9')
        tree.tag_configure("Ret", background='#ffebee')
        tree.tag_configure("Düzeltme", background='#fff3e0')
        
        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # İstatistik bilgisi
        if evaluated_count > 0:
            stats_label = tk.Label(self.content_area, 
                                   text=f"📊 Toplam {evaluated_count} makale değerlendirdiniz.",
                                   font=('Arial', 11, 'bold'), bg='white', fg=self.colors['primary'])
            stats_label.pack(pady=10, padx=20, anchor='w')
        
        # Detay görüntüleme
        action_frame = tk.Frame(self.content_area, bg='white')
        action_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(action_frame, text="📄 Detayları Görüntüle", bg=self.colors['secondary'], fg='white',
                  relief=tk.FLAT, cursor='hand2', command=lambda: self.show_review_details(tree)).pack(side=tk.LEFT, padx=5)
        
        # Mesaj durumu kontrolü
        def check_message_status():
            selected = tree.selection()
            if not selected:
                messagebox.showinfo("Bilgi", "Lütfen bir makale seçin.")
                return
            art_id = tree.item(selected[0])["values"][0]
            art = self.db.get_article(art_id)
            if not art:
                messagebox.showerror("Hata", "Makale bulunamadı.")
                return
            
            field_editor = art.get("field_editor")
            if not field_editor:
                messagebox.showwarning("Uyarı", "Bu makale için alan editörü atanmamış.")
                return
            
            # Mesajları kontrol et
            messages = self.db.get_messages_by_user(field_editor)
            my_messages = [m for m in messages if m.get("article_id") == art_id and m.get("from_user") == self.current_user]
            
            if my_messages:
                messagebox.showinfo("Mesaj Durumu", 
                    f"✅ Mesajınız alan editörüne ({field_editor}) başarıyla ulaştı.\n\n"
                    f"Gönderilen mesaj sayısı: {len(my_messages)}\n"
                    f"Son mesaj: {my_messages[0].get('created_at', 'Bilinmiyor')}")
            else:
                messagebox.showwarning("Uyarı", 
                    f"⚠️ Bu makale için alan editörüne ({field_editor}) mesaj gönderilmemiş görünüyor.\n\n"
                    f"Lütfen sistem yöneticisine bildirin.")
        
        tk.Button(action_frame, text="📧 Mesaj Durumunu Kontrol Et", bg=self.colors['info'], fg='white',
                  relief=tk.FLAT, cursor='hand2', command=check_message_status).pack(side=tk.LEFT, padx=5)
        
        if not assigned_articles or evaluated_count == 0:
            tk.Label(self.content_area, text="Henüz değerlendirdiğiniz makale bulunmamaktadır.",
                    font=('Arial', 12), bg='white', fg=self.colors['secondary']).pack(pady=20)
    
    def show_review_details(self, tree):
        """Hakem için değerlendirme detaylarını göster"""
        if self.user_role != "Hakem":
            return
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        art_id = tree.item(selected[0])["values"][0]
        art = self.db.get_article(art_id)
        if not art:
            messagebox.showerror("Hata", "Makale bulunamadı.")
            return
        
        # Hakem kararını getir
        reviews = self.db.get_reviews_by_article(art_id)
        my_review = None
        for review in reviews:
            if review["reviewer_username"] == self.current_user:
                my_review = review
                break
        
        if not my_review:
            messagebox.showerror("Hata", "Bu makale için değerlendirme bulunamadı.")
            return
        
        # Detay penceresi
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Değerlendirme Detayları - {art_id}")
        detail_window.geometry("700x600")
        detail_window.configure(bg='white')
        
        # Scrollable frame
        main_container = tk.Frame(detail_window, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_container, bg='white')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # İçerik
        content_frame = tk.Frame(scrollable_frame, bg='white', padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content_frame, text="Değerlendirme Detayları", 
                font=('Arial', 18, 'bold'), bg='white', fg=self.colors['primary']).pack(anchor='w', pady=(0, 20))
        
        # Makale bilgileri
        info_items = [
            ("Makale ID:", art_id),
            ("Başlık:", art.get("title", "Belirtilmemiş")),
            ("Yazar:", art.get("authors", art.get("author", "Belirtilmemiş"))),
            ("Verdiğiniz Karar:", my_review["decision"]),
            ("Değerlendirme Tarihi:", my_review.get("created_at", "Belirtilmemiş")[:10]),
        ]
        
        for label, value in info_items:
            row_frame = tk.Frame(content_frame, bg='white')
            row_frame.pack(fill=tk.X, pady=5)
            tk.Label(row_frame, text=label, font=('Arial', 11, 'bold'), 
                    bg='white', fg=self.colors['dark'], width=20, anchor='w').pack(side=tk.LEFT)
            decision_color = self.colors['success'] if my_review["decision"] == "Kabul" else \
                           self.colors['danger'] if my_review["decision"] == "Ret" else \
                           self.colors['warning']
            color = decision_color if label == "Verdiğiniz Karar:" else self.colors['dark']
            tk.Label(row_frame, text=str(value), font=('Arial', 11), 
                    bg='white', fg=color, anchor='w').pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Açıklama/Gerekçe
        tk.Label(content_frame, text="Açıklama/Gerekçe:", font=('Arial', 11, 'bold'), 
                bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(15, 5))
        comment_text = scrolledtext.ScrolledText(content_frame, height=8, width=60,
                                                font=('Arial', 10), relief=tk.FLAT,
                                                bg=self.colors['light'], bd=2, wrap=tk.WORD)
        comment_text.insert("1.0", my_review.get("comment", "Açıklama yok"))
        comment_text.config(state='disabled')
        comment_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Dosya bilgisi
        if my_review.get("file_path"):
            file_frame = tk.Frame(content_frame, bg='white')
            file_frame.pack(fill=tk.X, pady=(10, 0))
            tk.Label(file_frame, text="Ek Dosya:", font=('Arial', 11, 'bold'), 
                    bg='white', fg=self.colors['dark']).pack(anchor='w')
            file_path = my_review["file_path"]
            tk.Label(file_frame, text=f"  {os.path.basename(file_path)}", 
                    font=('Arial', 10), bg='white', fg=self.colors['secondary']).pack(anchor='w', padx=20)
            
            def download_file():
                if os.path.exists(file_path):
                    save_path = filedialog.asksaveasfilename(
                        title="Dosyayı Kaydet",
                        defaultextension=os.path.splitext(file_path)[1],
                        initialfile=os.path.basename(file_path)
                    )
                    if save_path:
                        try:
                            shutil.copy2(file_path, save_path)
                            messagebox.showinfo("Başarılı", f"Dosya başarıyla indirildi:\n{save_path}")
                        except Exception as e:
                            messagebox.showerror("Hata", f"Dosya indirilemedi: {str(e)}")
                else:
                    messagebox.showerror("Hata", "Dosya bulunamadı.")
            
            tk.Button(file_frame, text="📥 Dosyayı İndir", bg=self.colors['secondary'], fg='white',
                     relief=tk.FLAT, cursor='hand2', command=download_file,
                     padx=15, pady=5).pack(anchor='w', padx=20, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Kapat butonu
        tk.Button(detail_window, text="Kapat", bg=self.colors['secondary'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=detail_window.destroy,
                 padx=20, pady=10).pack(pady=10)

    def show_pending_tasks(self):
        # Bekleyen görevler - sadece karar verilmemiş makaleler
        self.current_view = 'pending_tasks'
        self.show_assigned()

    # --- Admin: kullanıcı yönetimi ---
    def show_user_management(self):
        if self.user_role != "Admin":
            messagebox.showerror("Hata", "Bu alana sadece admin erişebilir.")
            return

        for widget in self.content_area.winfo_children():
            widget.destroy()

        header = tk.Label(self.content_area, text="👥 Kullanıcı Yönetimi",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')

        # Liste
        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        columns = ('Kullanıcı', 'Rol', 'Ad Soyad')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=220)

        all_users = self.db.get_all_users()
        for user in all_users:
            roles = ", ".join(user.get("roles", []))
            tree.insert('', tk.END, values=(user["username"], roles, user.get("name", "")))

        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Rol atama ve yeni kullanıcı
        action_frame = tk.Frame(self.content_area, bg='white')
        action_frame.pack(fill=tk.X, padx=20, pady=10)

        # Rol güncelleme
        update_card = tk.Frame(action_frame, bg='#f9fbff', relief=tk.RAISED, borderwidth=1)
        update_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=4)

        tk.Label(update_card, text="Rol Güncelle", font=('Arial', 12, 'bold'),
                 bg='#f9fbff', fg=self.colors['primary']).pack(anchor='w', padx=14, pady=(10, 4))

        tk.Label(update_card, text="Kullanıcı", font=('Arial', 10),
                 bg='#f9fbff', fg=self.colors['dark']).pack(anchor='w', padx=14, pady=(6, 2))
        self.role_user_var = tk.StringVar()
        all_users = self.db.get_all_users()
        user_combo = ttk.Combobox(update_card, textvariable=self.role_user_var,
                                  values=[u["username"] for u in all_users], state='readonly')
        user_combo.pack(fill=tk.X, padx=14, ipady=2)

        tk.Label(update_card, text="Rol", font=('Arial', 10),
                 bg='#f9fbff', fg=self.colors['dark']).pack(anchor='w', padx=14, pady=(10, 2))
        self.role_assign_var = tk.StringVar(value="Editör")
        role_options = ["Admin", "Editör", "Yazar", "Hakem", "Alan Editörü", "Beklemede"]
        role_combo = ttk.Combobox(update_card, textvariable=self.role_assign_var,
                                  values=role_options, state='readonly')
        role_combo.pack(fill=tk.X, padx=14, ipady=2)
        
        # Alan Editörü için uzmanlık alanı seçimi
        self.role_expertise_var = tk.StringVar()
        role_expertise_frame = tk.Frame(update_card, bg='#f9fbff')
        role_expertise_frame.pack(fill=tk.X, padx=14, pady=(10, 0))
        tk.Label(role_expertise_frame, text="Uzmanlık Alanı (Sadece Alan Editörü için)", 
                 font=('Arial', 10), bg='#f9fbff', fg=self.colors['dark']).pack(anchor='w')
        field_options = ["", "Bilgisayar Mühendisliği", "Elektrik-Elektronik Mühendisliği", 
                         "Makine Mühendisliği", "Endüstri Mühendisliği", 
                         "İnşaat Mühendisliği", "Kimya Mühendisliği"]
        role_expertise_combo = ttk.Combobox(role_expertise_frame, textvariable=self.role_expertise_var,
                                             values=field_options, state='readonly')
        role_expertise_combo.pack(fill=tk.X, pady=(2, 0), ipady=2)
        
        # Rol değiştiğinde uzmanlık alanı görünürlüğünü güncelle
        def on_role_assign_change(event=None):
            if self.role_assign_var.get() == "Alan Editörü":
                role_expertise_frame.pack(fill=tk.X, padx=14, pady=(10, 0))
            else:
                role_expertise_frame.pack_forget()
        role_combo.bind('<<ComboboxSelected>>', on_role_assign_change)
        
        # Rol silme için mevcut roller
        tk.Label(update_card, text="Mevcut Rollerden Sil", font=('Arial', 10, 'bold'),
                 bg='#f9fbff', fg=self.colors['dark']).pack(anchor='w', padx=14, pady=(15, 5))
        self.role_remove_var = tk.StringVar()
        role_remove_combo = ttk.Combobox(update_card, textvariable=self.role_remove_var,
                                         values=[], state='readonly')
        role_remove_combo.pack(fill=tk.X, padx=14, ipady=2)
        
        # Kullanıcı seçildiğinde mevcut uzmanlık alanını ve rollerini göster
        def on_user_select(event=None):
            username = self.role_user_var.get()
            if username:
                user = self.db.get_user(username)
                if user:
                    # Uzmanlık alanını göster
                    if user.get("expertise_field"):
                        self.role_expertise_var.set(user["expertise_field"])
                    else:
                        self.role_expertise_var.set("")
                    
                    # Mevcut rollerini göster
                    current_roles = user.get("roles", [])
                    # Admin rolünü silme listesinden çıkar (güvenlik)
                    removable_roles = [r for r in current_roles if r != "Admin"]
                    role_remove_combo['values'] = removable_roles
                    if removable_roles:
                        self.role_remove_var.set(removable_roles[0])
                    else:
                        self.role_remove_var.set("")
        user_combo.bind('<<ComboboxSelected>>', on_user_select)

        # Butonlar için frame
        button_frame = tk.Frame(update_card, bg='#f9fbff')
        button_frame.pack(fill=tk.X, padx=14, pady=(12, 12))
        
        update_btn = tk.Button(button_frame, text="ROL ATA", font=('Arial', 11, 'bold'),
                               bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                               cursor='hand2', command=lambda: self.assign_role(tree))
        update_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=8)
        
        remove_btn = tk.Button(button_frame, text="ROL SİL", font=('Arial', 11, 'bold'),
                               bg=self.colors['danger'], fg='white', relief=tk.FLAT,
                               cursor='hand2', command=lambda: self.remove_role(tree))
        remove_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=8)

        # Yeni kullanıcı oluşturma
        create_card = tk.Frame(action_frame, bg='#f9fffa', relief=tk.RAISED, borderwidth=1)
        create_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=4)

        tk.Label(create_card, text="Yeni Kullanıcı Oluştur (Admin)", font=('Arial', 12, 'bold'),
                 bg='#f9fffa', fg=self.colors['primary']).pack(anchor='w', padx=14, pady=(10, 4))

        tk.Label(create_card, text="Ad Soyad", font=('Arial', 10),
                 bg='#f9fffa', fg=self.colors['dark']).pack(anchor='w', padx=14, pady=(6, 2))
        self.new_name_var = tk.StringVar()
        tk.Entry(create_card, textvariable=self.new_name_var, font=('Arial', 11),
                 relief=tk.FLAT, bg=self.colors['light']).pack(fill=tk.X, padx=14, ipady=6)

        tk.Label(create_card, text="Kullanıcı / E-posta", font=('Arial', 10),
                 bg='#f9fffa', fg=self.colors['dark']).pack(anchor='w', padx=14, pady=(10, 2))
        self.new_email_var = tk.StringVar()
        tk.Entry(create_card, textvariable=self.new_email_var, font=('Arial', 11),
                 relief=tk.FLAT, bg=self.colors['light']).pack(fill=tk.X, padx=14, ipady=6)

        tk.Label(create_card, text="Şifre", font=('Arial', 10),
                 bg='#f9fffa', fg=self.colors['dark']).pack(anchor='w', padx=14, pady=(10, 2))
        self.new_pass_var = tk.StringVar()
        tk.Entry(create_card, textvariable=self.new_pass_var, font=('Arial', 11),
                 relief=tk.FLAT, bg=self.colors['light'], show="*").pack(fill=tk.X, padx=14, ipady=6)

        tk.Label(create_card, text="Rol", font=('Arial', 10),
                 bg='#f9fffa', fg=self.colors['dark']).pack(anchor='w', padx=14, pady=(10, 2))
        self.new_role_var = tk.StringVar(value="Yazar")
        new_role_combo = ttk.Combobox(create_card, textvariable=self.new_role_var,
                                      values=role_options, state='readonly')
        new_role_combo.pack(fill=tk.X, padx=14, ipady=2)
        
        # Alan Editörü için uzmanlık alanı seçimi
        self.new_expertise_var = tk.StringVar()
        expertise_frame = tk.Frame(create_card, bg='#f9fffa')
        expertise_frame.pack(fill=tk.X, padx=14, pady=(10, 0))
        tk.Label(expertise_frame, text="Uzmanlık Alanı (Sadece Alan Editörü için)", 
                 font=('Arial', 10), bg='#f9fffa', fg=self.colors['dark']).pack(anchor='w')
        field_options = ["", "Bilgisayar Mühendisliği", "Elektrik-Elektronik Mühendisliği", 
                         "Makine Mühendisliği", "Endüstri Mühendisliği", 
                         "İnşaat Mühendisliği", "Kimya Mühendisliği"]
        new_expertise_combo = ttk.Combobox(expertise_frame, textvariable=self.new_expertise_var,
                                           values=field_options, state='readonly')
        new_expertise_combo.pack(fill=tk.X, pady=(2, 0), ipady=2)
        
        # Rol değiştiğinde uzmanlık alanı görünürlüğünü güncelle
        def on_role_change(event=None):
            if self.new_role_var.get() == "Alan Editörü":
                expertise_frame.pack(fill=tk.X, padx=14, pady=(10, 0))
            else:
                expertise_frame.pack_forget()
        new_role_combo.bind('<<ComboboxSelected>>', on_role_change)

        create_btn = tk.Button(create_card, text="KULLANICI OLUŞTUR", font=('Arial', 11, 'bold'),
                               bg=self.colors['success'], fg='white', relief=tk.FLAT,
                               cursor='hand2', command=lambda: self.admin_create_user(tree))
        create_btn.pack(fill=tk.X, padx=14, pady=(12, 12), ipady=8)

        # Şifre sıfırlama
        password_reset_card = tk.Frame(action_frame, bg='#fff9f9', relief=tk.RAISED, borderwidth=1)
        password_reset_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=4)
        
        tk.Label(password_reset_card, text="Şifre Sıfırlama", font=('Arial', 12, 'bold'),
                 bg='#fff9f9', fg=self.colors['primary']).pack(anchor='w', padx=14, pady=(10, 4))
        
        tk.Label(password_reset_card, text="Kullanıcı", font=('Arial', 10),
                 bg='#fff9f9', fg=self.colors['dark']).pack(anchor='w', padx=14, pady=(6, 2))
        self.password_reset_user_var = tk.StringVar()
        password_reset_user_combo = ttk.Combobox(password_reset_card, textvariable=self.password_reset_user_var,
                                                 values=[u["username"] for u in all_users], state='readonly')
        password_reset_user_combo.pack(fill=tk.X, padx=14, ipady=2)
        
        tk.Label(password_reset_card, text="Yeni Şifre", font=('Arial', 10),
                 bg='#fff9f9', fg=self.colors['dark']).pack(anchor='w', padx=14, pady=(10, 2))
        self.password_reset_new_var = tk.StringVar()
        password_reset_entry = tk.Entry(password_reset_card, textvariable=self.password_reset_new_var,
                                        font=('Arial', 11), relief=tk.FLAT, bg=self.colors['light'], show="*")
        password_reset_entry.pack(fill=tk.X, padx=14, ipady=6)
        
        reset_btn = tk.Button(password_reset_card, text="ŞİFRE SIFIRLA", font=('Arial', 11, 'bold'),
                              bg=self.colors['danger'], fg='white', relief=tk.FLAT,
                              cursor='hand2', command=lambda: self.admin_reset_password(tree))
        reset_btn.pack(fill=tk.X, padx=14, pady=(12, 12), ipady=8)
        
        # Kullanıcı silme
        delete_card = tk.Frame(action_frame, bg='#fff9f9', relief=tk.RAISED, borderwidth=1)
        delete_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=4)
        tk.Label(delete_card, text="Kullanıcı Sil (Admin)", font=('Arial', 12, 'bold'),
                 bg='#fff9f9', fg=self.colors['danger']).pack(anchor='w', padx=14, pady=(10, 4))
        tk.Label(delete_card, text="Kullanıcı", font=('Arial', 10),
                 bg='#fff9f9', fg=self.colors['dark']).pack(anchor='w', padx=14, pady=(6, 2))
        self.del_user_var = tk.StringVar()
        all_users = self.db.get_all_users()
        del_combo = ttk.Combobox(delete_card, textvariable=self.del_user_var,
                                 values=[u["username"] for u in all_users], state='readonly')
        del_combo.pack(fill=tk.X, padx=14, ipady=2)
        tk.Button(delete_card, text="SİL", font=('Arial', 11, 'bold'),
                  bg=self.colors['danger'], fg='white', relief=tk.FLAT,
                  cursor='hand2', command=lambda: self.admin_delete_user(tree)).pack(fill=tk.X, padx=14, pady=(12, 12), ipady=8)

    def assign_role(self, tree):
        if self.user_role != "Admin":
            messagebox.showerror("Hata", "Bu işlem için admin olmalısınız.")
            return
        username = self.role_user_var.get()
        role = self.role_assign_var.get()
        user = self.db.get_user(username)
        if not username or not user:
            messagebox.showerror("Hata", "Lütfen kullanıcı seçin.")
            return
        roles = user.get("roles", []).copy()
        if role == "Admin":
            roles = ["Admin", "Editör", "Alan Editörü", "Hakem", "Yazar"]
            expertise_field = None
        else:
            if role not in roles:
                roles.append(role)
            if role in ["Editör", "Alan Editörü", "Hakem", "Admin"] and "Yazar" not in roles:
                roles.append("Yazar")
            # Alan Editörü için uzmanlık alanı
            if role == "Alan Editörü":
                expertise_field = self.role_expertise_var.get().strip() if self.role_expertise_var.get().strip() else None
                if expertise_field:
                    self.db.update_user_expertise_field(username, expertise_field)
            else:
                # Eğer rol Alan Editörü değilse ve kullanıcı artık Alan Editörü değilse, uzmanlık alanını temizle
                if "Alan Editörü" not in roles:
                    self.db.update_user_expertise_field(username, None)
        self.db.update_user_roles(username, roles)
        messagebox.showinfo("Bilgi", f"{username} için roller güncellendi: {', '.join(roles)}")
        self.show_user_management()
    
    def remove_role(self, tree):
        """Kullanıcıdan rol sil"""
        if self.user_role != "Admin":
            messagebox.showerror("Hata", "Bu işlem için admin olmalısınız.")
            return
        
        username = self.role_user_var.get()
        role_to_remove = self.role_remove_var.get()
        
        if not username:
            messagebox.showerror("Hata", "Lütfen kullanıcı seçin.")
            return
        
        if not role_to_remove:
            messagebox.showerror("Hata", "Lütfen silinecek rolü seçin.")
            return
        
        user = self.db.get_user(username)
        if not user:
            messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
            return
        
        # Admin rolünü silmeyi engelle
        if role_to_remove == "Admin":
            messagebox.showerror("Hata", "Admin rolü silinemez. Güvenlik nedeniyle bu işlem engellenmiştir.")
            return
        
        # Kullanıcının son rolünü silmeyi engelle
        current_roles = user.get("roles", []).copy()
        if len(current_roles) <= 1:
            messagebox.showerror("Hata", "Kullanıcının en az bir rolü olmalıdır. Son rolü silemezsiniz.")
            return
        
        # Rolü listeden çıkar
        if role_to_remove in current_roles:
            current_roles.remove(role_to_remove)
            
            # Eğer silinen rol "Alan Editörü" ise, uzmanlık alanını da temizle
            if role_to_remove == "Alan Editörü":
                self.db.update_user_expertise_field(username, None)
            
            # Rolleri güncelle
            self.db.update_user_roles(username, current_roles)
            messagebox.showinfo("Başarılı", f"{username} kullanıcısından '{role_to_remove}' rolü silindi.")
            self.refresh_user_tree(tree)
        else:
            messagebox.showerror("Hata", f"Kullanıcının '{role_to_remove}' rolü bulunmamaktadır.")

    def admin_create_user(self, tree):
        if self.user_role != "Admin":
            messagebox.showerror("Hata", "Bu işlem için admin olmalısınız.")
            return
        name = self.new_name_var.get().strip()
        email = self.new_email_var.get().strip()
        password = self.new_pass_var.get().strip()
        role = self.new_role_var.get()
        if not all([name, email, password, role]):
            messagebox.showerror("Hata", "Tüm alanları doldurun.")
            return
        if self.db.get_user(email):
            messagebox.showerror("Hata", "Bu kullanıcı zaten mevcut.")
            return
        if role == "Admin":
            roles = ["Admin", "Editör", "Alan Editörü", "Hakem", "Yazar"]
            expertise_field = None
        else:
            roles = [role]
            if role in ["Editör", "Alan Editörü", "Hakem"] and "Yazar" not in roles:
                roles.append("Yazar")
            # Alan Editörü için uzmanlık alanı
            if role == "Alan Editörü":
                expertise_field = self.new_expertise_var.get().strip() if self.new_expertise_var.get().strip() else None
            else:
                expertise_field = None
        if self.db.add_user(email, password, name, roles, expertise_field):
            messagebox.showinfo("Bilgi", "Kullanıcı oluşturuldu.")
            self.new_name_var.set("")
            self.new_email_var.set("")
            self.new_pass_var.set("")
            self.new_role_var.set("Yazar")
            self.new_expertise_var.set("")
            self.role_user_var.set("")
            self.refresh_user_tree(tree)
        else:
            messagebox.showerror("Hata", "Kullanıcı oluşturulamadı.")

    def admin_reset_password(self, tree):
        """Admin şifre sıfırlama"""
        if self.user_role != "Admin":
            messagebox.showerror("Hata", "Bu işlem için admin olmalısınız.")
            return
        username = self.password_reset_user_var.get()
        new_password = self.password_reset_new_var.get().strip()
        if not username:
            messagebox.showerror("Hata", "Lütfen kullanıcı seçin.")
            return
        if not new_password:
            messagebox.showerror("Hata", "Lütfen yeni şifreyi girin.")
            return
        if not self.db.get_user(username):
            messagebox.showerror("Hata", "Kullanıcı bulunamadı.")
            return
        
        # Onay al
        confirm = messagebox.askyesno("Onay", 
                                     f"{username} kullanıcısının şifresini sıfırlamak istediğinize emin misiniz?")
        if confirm:
            self.db.update_user_password(username, new_password)
            messagebox.showinfo("Başarılı", f"{username} kullanıcısının şifresi başarıyla güncellendi.")
            self.password_reset_user_var.set("")
            self.password_reset_new_var.set("")
            self.refresh_user_tree(tree)
    
    def admin_delete_user(self, tree):
        if self.user_role != "Admin":
            messagebox.showerror("Hata", "Bu işlem için admin olmalısınız.")
            return
        username = self.del_user_var.get()
        if not username or not self.db.get_user(username):
            messagebox.showerror("Hata", "Kullanıcı seçin.")
            return
        if username == "admin":
            messagebox.showerror("Hata", "Admin silinemez.")
            return
        self.db.delete_user(username)
        messagebox.showinfo("Bilgi", f"{username} silindi.")
        self.del_user_var.set("")
        self.refresh_user_tree(tree)

    def refresh_user_tree(self, tree):
        for row in tree.get_children():
            tree.delete(row)
        all_users = self.db.get_all_users()
        for user in all_users:
            roles = ", ".join(user.get("roles", []))
            tree.insert('', tk.END, values=(user["username"], roles, user.get("name", "")))

    # --- Yardımcı ve iş akışı fonksiyonları ---
    def get_users_by_role(self, role_name):
        all_users = self.db.get_all_users()
        return [u["username"] for u in all_users if role_name in u.get("roles", [])]

    def create_article_submission(self, file_info_label=None):
        user = self.db.get_user(self.current_user)
        user_roles = user.get("roles", [self.user_role]) if user else [self.user_role]
        if "Yazar" not in user_roles and self.user_role != "Admin":
            messagebox.showerror("Hata", "Makale göndermek için Yazar veya Admin olun.")
            return
        
        # Form alanlarını kontrol et
        if not hasattr(self, 'submission_fields'):
            messagebox.showerror("Hata", "Lütfen makale gönderme formunu kullanın.")
            return
        
        title = self.submission_fields.get('title', tk.Entry()).get().strip()
        if not title:
            messagebox.showerror("Hata", "Lütfen makale başlığını girin.")
            return
        
        # Dosya kontrolü
        if not self.selected_file_path:
            messagebox.showerror("Hata", "Lütfen makale dosyasını seçin.")
            return
        
        # Dosya yükleme klasörü oluştur (root dizinine göre)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        uploads_dir = os.path.join(base_dir, "uploads")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Yeni makale ID oluştur
        all_articles = self.db.get_all_articles()
        article_id = f"MAK-{datetime.now().year}-{len(all_articles)+1:04d}"
        
        # Dosyayı kopyala
        file_ext = os.path.splitext(self.selected_file_path)[1]
        new_file_name = f"{article_id}{file_ext}"
        destination_path = os.path.join(uploads_dir, new_file_name)
        
        try:
            shutil.copy2(self.selected_file_path, destination_path)
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kopyalanamadı: {str(e)}")
            return
        
        # Form verilerini al
        subtitle = self.submission_fields.get('subtitle', tk.Entry()).get().strip()
        keywords = self.submission_fields.get('keywords', tk.Entry()).get().strip()
        article_type = self.submission_fields.get('type', ttk.Combobox()).get()
        field = self.submission_fields.get('field', ttk.Combobox()).get()
        abstract_tr = self.submission_fields.get('abstract_tr', scrolledtext.ScrolledText()).get("1.0", tk.END).strip()
        abstract_en = self.submission_fields.get('abstract_en', scrolledtext.ScrolledText()).get("1.0", tk.END).strip()
        
        # Editör ataması - mevcut editörlerden birini seç (admin hariç)
        assigned_editor = None
        all_editors = self.get_users_by_role("Editör")
        # Admin'i listeden çıkar
        editors = [e for e in all_editors if e != "admin"]
        if editors:
            # İlk editörü ata (basit yük dağılımı - gerçek sistemde daha gelişmiş algoritma kullanılabilir)
            assigned_editor = editors[0]
        
        # Yapay zeka ile alan editörü ataması
        assigned_field_editor = None
        ai_message = ""
        
        try:
            # AI ile makale sınıflandırması yap
            detected_field = self.ai_classifier.classify_article(
                title=title,
                abstract_tr=abstract_tr,
                abstract_en=abstract_en,
                keywords=keywords,
                field=field
            )
            
            if detected_field:
                # Alan editörlerini getir (admin hariç)
                all_field_editors = self.get_users_by_role("Alan Editörü")
                # Admin'i listeden çıkar
                field_editors = [fe for fe in all_field_editors if fe != "admin"]
                
                if field_editors:
                    # Alan editörlerinin uzmanlık alanlarını getir
                    editor_expertise = {}
                    for fe_username in field_editors:
                        fe_user = self.db.get_user(fe_username)
                        if fe_user and fe_user.get("expertise_field"):
                            editor_expertise[fe_username] = fe_user["expertise_field"]
                    
                    # AI ile uygun alan editörünü seç
                    assigned_field_editor = self.ai_classifier.assign_field_editor(
                        detected_field, field_editors, editor_expertise
                    )
                    
                    if assigned_field_editor:
                        ai_message = f"\n🤖 Yapay Zeka: Makale '{detected_field}' alanına sınıflandırıldı.\n📝 Alan Editörü '{assigned_field_editor}' otomatik atandı."
                    else:
                        ai_message = f"\n🤖 Yapay Zeka: Makale '{detected_field}' alanına sınıflandırıldı ancak uygun alan editörü bulunamadı."
                else:
                    ai_message = f"\n🤖 Yapay Zeka: Makale '{detected_field}' alanına sınıflandırıldı ancak sistemde alan editörü bulunmamaktadır."
            else:
                ai_message = "\n🤖 Yapay Zeka: Makale sınıflandırılamadı. Editör manuel atama yapacaktır."
        except Exception as e:
            ai_message = f"\n⚠️ Yapay Zeka analizi sırasında hata oluştu: {str(e)}"
        
        # Durum belirleme: Hem editör hem alan editörü varsa "Alan Editörü İncelemede", sadece editör varsa "Editör İncelemede"
        if assigned_field_editor:
            article_status = "Alan Editörü İncelemede"
        elif assigned_editor:
            article_status = "Editör İncelemede"
        else:
            article_status = "Beklemede"
        
        # Makale verisi oluştur
        article = {
            "id": article_id,
            "title": title,
            "author": self.current_user,
            "authors": user.get("name", self.current_user) if user else self.current_user,
            "status": article_status,
            "editor": assigned_editor,
            "field_editor": assigned_field_editor,
            "reviewers": [],
            "decisions": {},
            "file_path": destination_path,
            "scheduled": False
        }
        
        if self.db.add_article(article):
            editor_info = ""
            if assigned_editor:
                editor_info = f"\n📋 Editör '{assigned_editor}' atandı."
            
            messagebox.showinfo("Başarılı", 
                              f"{article_id} gönderildi.{editor_info}{ai_message}\n"
                              f"Dosya: {os.path.basename(destination_path)}")
            # Formu temizle
            self.selected_file_path = None
            if file_info_label:
                file_info_label.config(text="Dosya seçilmedi", fg=self.colors['secondary'])
            self.show_submissions()
        else:
            messagebox.showerror("Hata", "Makale gönderilemedi.")

    def assign_field_editor(self, tree):
        if self.user_role not in ["Admin", "Editör"]:
            messagebox.showerror("Hata", "Sadece editör alan editörü atayabilir.")
            return
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        item = tree.item(selected[0])["values"]
        art_id = item[0]
        art = self.db.get_article(art_id)
        if not art:
            return
        all_fes = self.get_users_by_role("Alan Editörü")
        # Admin'i listeden çıkar
        fes = [fe for fe in all_fes if fe != "admin"]
        if not fes:
            messagebox.showerror("Hata", "Alan editörü tanımlı değil (admin hariç).")
            return
        chosen = fes[0]  # basit seçim
        # Alan editörü seçim penceresi
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Alan Editörü Seç")
        selection_window.geometry("400x300")
        selection_window.configure(bg='white')
        
        tk.Label(selection_window, text="Alan Editörü Seçin:", 
                font=('Arial', 12, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=20)
        
        fe_var = tk.StringVar()
        fe_combo = ttk.Combobox(selection_window, textvariable=fe_var, 
                               values=[f"{fe} - {self.db.get_user(fe).get('name', '')}" for fe in fes],
                               state='readonly', width=40)
        fe_combo.pack(pady=10, padx=20, fill=tk.X)
        
        def confirm_assignment():
            selected_fe = fe_var.get().split(" - ")[0]
            if selected_fe:
                self.db.update_article(art_id, {
                    "field_editor": selected_fe,
                    "editor": self.current_user,
                    "status": "Alan Editöründe"
                })
                messagebox.showinfo("Bilgi", f"{art_id} {selected_fe} alan editörüne atandı.")
                selection_window.destroy()
                self.show_submissions()
        
        tk.Button(selection_window, text="Ata", bg=self.colors['success'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=confirm_assignment,
                 padx=20, pady=10).pack(pady=20)
    
    def open_article_file(self, tree):
        """Makale dosyasını aç"""
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        item = tree.item(selected[0])["values"]
        art_id = item[0]
        art = self.db.get_article(art_id)
        if not art:
            return
        
        file_path = art.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Hata", "Makale dosyası bulunamadı.")
            return
        
        try:
            # Windows'ta dosyayı varsayılan uygulamayla aç
            os.startfile(file_path)
        except Exception as e:
            # Alternatif yöntem
            try:
                import subprocess
                subprocess.Popen([file_path], shell=True)
            except Exception as e2:
                messagebox.showerror("Hata", f"Dosya açılamadı: {str(e2)}")
    
    def reject_article_early(self, tree):
        """Ön incelemede makaleyi reddet"""
        if self.user_role not in ["Admin", "Editör"]:
            messagebox.showerror("Hata", "Sadece editör bu işlemi yapabilir.")
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        item = tree.item(selected[0])["values"]
        art_id = item[0]
        art = self.db.get_article(art_id)
        if not art:
            return
        
        # Reddetme nedeni penceresi
        reject_window = tk.Toplevel(self.root)
        reject_window.title("Makaleyi Reddet")
        reject_window.geometry("500x400")
        reject_window.configure(bg='white')
        
        tk.Label(reject_window, text="Reddetme Nedeni:", 
                font=('Arial', 12, 'bold'), bg='white', fg=self.colors['danger']).pack(pady=10)
        
        reason_text = scrolledtext.ScrolledText(reject_window, height=10, width=50,
                                                font=('Arial', 10), relief=tk.FLAT,
                                                bg=self.colors['light'], bd=2)
        reason_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        def confirm_rejection():
            reason = reason_text.get("1.0", tk.END).strip()
            if not reason:
                messagebox.showerror("Hata", "Lütfen reddetme nedenini belirtin.")
                return
            
            # Makaleyi reddet
            self.db.update_article(art_id, {
                "status": "Reddedildi",
                "editor": self.current_user
            })
            
            # Yazara mesaj gönder
            author = art.get("author", "")
            if author:
                self.db.add_message(
                    art_id,
                    self.current_user,
                    author,
                    f"Makale Reddedildi: {art.get('title', art_id)}",
                    f"Sayın Yazar,\n\nMakaleniz ön inceleme aşamasında reddedilmiştir.\n\nReddetme Nedeni:\n{reason}\n\nSaygılarımızla,\nEditör"
                )
            
            messagebox.showinfo("Bilgi", f"{art_id} reddedildi ve yazara bildirildi.")
            reject_window.destroy()
            self.show_submissions()
        
        tk.Button(reject_window, text="Reddet", bg=self.colors['danger'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=confirm_rejection,
                 padx=20, pady=10).pack(pady=10)
    
    def communicate_with_author(self, tree):
        """Yazarla iletişim kur"""
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        item = tree.item(selected[0])["values"]
        art_id = item[0]
        art = self.db.get_article(art_id)
        if not art:
            return
        
        author = art.get("author", "")
        if not author:
            messagebox.showerror("Hata", "Yazar bilgisi bulunamadı.")
            return
        
        # İletişim penceresi
        comm_window = tk.Toplevel(self.root)
        comm_window.title(f"Yazarla İletişim - {art_id}")
        comm_window.geometry("600x500")
        comm_window.configure(bg='white')
        
        # Mesaj geçmişi
        tk.Label(comm_window, text="Mesaj Geçmişi:", 
                font=('Arial', 11, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=10, anchor='w', padx=20)
        
        messages_frame = tk.Frame(comm_window, bg='white')
        messages_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        messages_canvas = tk.Canvas(messages_frame, bg='white', height=200)
        messages_scrollbar = ttk.Scrollbar(messages_frame, orient="vertical", command=messages_canvas.yview)
        messages_scrollable = tk.Frame(messages_canvas, bg='white')
        
        messages_scrollable.bind(
            "<Configure>",
            lambda e: messages_canvas.configure(scrollregion=messages_canvas.bbox("all"))
        )
        
        messages_canvas.create_window((0, 0), window=messages_scrollable, anchor="nw")
        messages_canvas.configure(yscrollcommand=messages_scrollbar.set)
        
        # Mesajları göster
        messages = self.db.get_messages_by_article(art_id)
        for msg in messages:
            msg_frame = tk.Frame(messages_scrollable, bg=self.colors['light'], relief=tk.RAISED, borderwidth=1)
            msg_frame.pack(fill=tk.X, pady=5, padx=5)
            
            from_user = self.db.get_user(msg["from_user"])
            from_name = from_user.get("name", msg["from_user"]) if from_user else msg["from_user"]
            
            tk.Label(msg_frame, text=f"{from_name} ({msg['from_user']}) - {msg['subject']}",
                    font=('Arial', 9, 'bold'), bg=self.colors['light'], fg=self.colors['primary']).pack(anchor='w', padx=10, pady=(5, 0))
            tk.Label(msg_frame, text=msg["message"], font=('Arial', 9),
                    bg=self.colors['light'], fg=self.colors['dark_text'], wraplength=500,
                    justify='left').pack(anchor='w', padx=10, pady=5)
            tk.Label(msg_frame, text=msg["created_at"], font=('Arial', 8),
                    bg=self.colors['light'], fg=self.colors['secondary']).pack(anchor='w', padx=10, pady=(0, 5))
        
        messages_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        messages_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Yeni mesaj gönderme
        tk.Label(comm_window, text="Yeni Mesaj:", 
                font=('Arial', 11, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(10, 5), anchor='w', padx=20)
        
        subject_frame = tk.Frame(comm_window, bg='white')
        subject_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(subject_frame, text="Konu:", font=('Arial', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        subject_entry = tk.Entry(subject_frame, font=('Arial', 10), width=50)
        subject_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        message_text = scrolledtext.ScrolledText(comm_window, height=6, width=60,
                                                 font=('Arial', 10), relief=tk.FLAT,
                                                 bg=self.colors['light'], bd=2)
        message_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        def send_message():
            subject = subject_entry.get().strip()
            message = message_text.get("1.0", tk.END).strip()
            
            if not subject or not message:
                messagebox.showerror("Hata", "Lütfen konu ve mesajı doldurun.")
                return
            
            self.db.add_message(art_id, self.current_user, author, subject, message)
            messagebox.showinfo("Başarılı", "Mesaj gönderildi.")
            comm_window.destroy()
            self.communicate_with_author(tree)  # Pencereyi yenile
        
        tk.Button(comm_window, text="📧 Mesaj Gönder", bg=self.colors['success'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=send_message,
                 padx=20, pady=10).pack(pady=10)

    def assign_reviewers(self, tree):
        if self.user_role != "Alan Editörü":
            messagebox.showerror("Hata", "Sadece alan editörü hakem atayabilir.")
            return
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        item = tree.item(selected[0])["values"]
        art_id = item[0]
        art = self.db.get_article(art_id)
        if not art:
            return
        
        reviewers = self.get_users_by_role("Hakem")
        if len(reviewers) < 2:
            messagebox.showerror("Hata", "En az 2 hakem tanımlayın.")
            return
        
        # Hakem seçim penceresi
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Hakem Havuzundan Seç")
        selection_window.geometry("550x550")
        selection_window.configure(bg='white')
        
        # Ana frame
        main_frame = tk.Frame(selection_window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="Hakem Havuzu - 2 Hakem Seçin:", 
                font=('Arial', 12, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(0, 10))
        
        # Hakem listesi (scrollable checkbox'lar ile)
        list_container = tk.Frame(main_frame, bg='white')
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(list_container, bg='white')
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        reviewers_frame = tk.Frame(canvas, bg='white')
        
        reviewers_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=reviewers_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        selected_reviewers = []
        reviewer_vars = {}
        
        # Seçilen hakem sayısını gösteren label
        count_frame = tk.Frame(main_frame, bg='white')
        count_frame.pack(fill=tk.X, padx=10, pady=(5, 5))
        
        count_label = tk.Label(count_frame, 
                              text="Seçilen hakem sayısı: 0/2",
                              font=('Arial', 11, 'bold'),
                              bg='white',
                              fg=self.colors['primary'])
        count_label.pack()
        
        def update_count_label():
            """Seçilen hakem sayısını güncelle"""
            count = len(selected_reviewers)
            count_label.config(text=f"Seçilen hakem sayısı: {count}/2")
            if count == 2:
                count_label.config(fg=self.colors['success'])
            else:
                count_label.config(fg=self.colors['primary'])
        
        # toggle_reviewer_selection fonksiyonunu güncelle - count_label'ı da güncelle
        def toggle_with_count(reviewer_username, var):
            """Hakem seçimini toggle et ve sayacı güncelle"""
            self.toggle_reviewer_selection(reviewer_username, var, selected_reviewers)
            update_count_label()
        
        for reviewer_username in reviewers:
            reviewer = self.db.get_user(reviewer_username)
            reviewer_name = reviewer.get("name", reviewer_username) if reviewer else reviewer_username
            expertise = reviewer.get("expertise_field", "") if reviewer else ""
            
            var = tk.BooleanVar()
            reviewer_vars[reviewer_username] = var
            
            # Hakem kartı
            reviewer_item = tk.Frame(reviewers_frame, bg='white', relief=tk.FLAT)
            reviewer_item.pack(fill=tk.X, pady=3, padx=5)
            
            # Checkbox
            checkbox = tk.Checkbutton(reviewer_item, 
                                     variable=var,
                                     font=('Arial', 10),
                                     bg='white',
                                     fg=self.colors['dark_text'],
                                     command=lambda r=reviewer_username, v=var: toggle_with_count(r, v))
            checkbox.pack(side=tk.LEFT, padx=(0, 10))
            
            # Bilgi etiketi
            info_text = f"{reviewer_name} ({reviewer_username})"
            if expertise:
                info_text += f"\n   📚 Uzmanlık: {expertise}"
            
            info_label = tk.Label(reviewer_item, 
                                 text=info_text,
                                 font=('Arial', 10),
                                 bg='white',
                                 fg=self.colors['dark_text'],
                                 anchor='w',
                                 justify='left')
            info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def confirm_assignment():
            print(f"DEBUG: confirm_assignment çağrıldı. Seçilen hakemler: {selected_reviewers}")
            
            if len(selected_reviewers) != 2:
                messagebox.showerror("Hata", f"Lütfen tam olarak 2 hakem seçin.\n\nŞu anda {len(selected_reviewers)} hakem seçili.")
                return
            
            try:
                # Hakemleri ata
                print(f"DEBUG: Makale {art_id} için hakemler atanıyor: {selected_reviewers}")
                self.db.update_article(art_id, {
                    "reviewers": selected_reviewers,
                    "status": "Hakemde"
                })
                
                # Güncellemenin başarılı olduğunu kontrol et
                updated_art = self.db.get_article(art_id)
                if not updated_art:
                    raise Exception("Makale güncellenemedi - makale bulunamadı")
                
                print(f"DEBUG: Makale güncellendi. Yeni durum: {updated_art.get('status')}, Hakemler: {updated_art.get('reviewers')}")
                
                # Hakemlere bildirim mesajı gönder
                messages_sent = 0
                for reviewer_username in selected_reviewers:
                    try:
                        reviewer = self.db.get_user(reviewer_username)
                        reviewer_name = reviewer.get("name", reviewer_username) if reviewer else reviewer_username
                        success = self.db.add_message(
                            art_id,
                            self.current_user,
                            reviewer_username,
                            f"Hakemlik Görevi: {art.get('title', art_id)}",
                            f"Sayın {reviewer_name},\n\nMakale değerlendirmesi için size görev atanmıştır.\n\nMakale: {art.get('title', art_id)}\nMakale ID: {art_id}\n\nLütfen makaleyi inceleyip değerlendirmenizi yapınız.\n\nSaygılarımızla,\nAlan Editörü"
                        )
                        if success:
                            messages_sent += 1
                            print(f"DEBUG: Mesaj {reviewer_username} hakemine gönderildi")
                        else:
                            print(f"UYARI: Mesaj {reviewer_username} hakemine gönderilemedi")
                    except Exception as e:
                        print(f"HATA: {reviewer_username} hakemine mesaj gönderilirken hata: {str(e)}")
                
                # Başarı mesajı
                reviewer_names = []
                for reviewer_username in selected_reviewers:
                    reviewer = self.db.get_user(reviewer_username)
                    reviewer_name = reviewer.get("name", reviewer_username) if reviewer else reviewer_username
                    reviewer_names.append(f"{reviewer_name} ({reviewer_username})")
                
                success_msg = f"✅ Hakemler başarıyla atandı!\n\n"
                success_msg += f"Makale: {art_id}\n"
                success_msg += f"Hakemler:\n"
                success_msg += f"1. {reviewer_names[0]}\n"
                success_msg += f"2. {reviewer_names[1]}\n\n"
                if messages_sent == 2:
                    success_msg += "✓ Her iki hakeme de bildirim gönderildi."
                elif messages_sent == 1:
                    success_msg += "⚠ Uyarı: Sadece 1 hakeme bildirim gönderildi."
                else:
                    success_msg += "⚠ Uyarı: Hakemlere bildirim gönderilemedi."
                
                messagebox.showinfo("Başarılı", success_msg)
                selection_window.destroy()
                
                # Sayfayı güncelle
                try:
                    self.show_submissions()
                except Exception as e:
                    print(f"HATA: Sayfa güncellenirken hata: {str(e)}")
                    traceback.print_exc()
                    
            except Exception as e:
                error_msg = f"Hakem atama işlemi başarısız oldu.\n\nHata: {str(e)}"
                print(f"HATA: {error_msg}")
                traceback.print_exc()
                messagebox.showerror("Hata", error_msg)
        
        # Buton frame'i - list_container'dan sonra görünür olması için
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=10, pady=(10, 10))
        
        tk.Button(button_frame, text="✅ Hakemleri Ata", bg=self.colors['success'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=confirm_assignment,
                 padx=30, pady=12, font=('Arial', 11, 'bold')).pack()
    
    def toggle_reviewer_selection(self, reviewer_username, var, selected_list):
        """Hakem seçimini toggle et"""
        if var.get():
            if reviewer_username not in selected_list:
                if len(selected_list) < 2:
                    selected_list.append(reviewer_username)
                else:
                    var.set(False)
                    messagebox.showwarning("Uyarı", "En fazla 2 hakem seçebilirsiniz.")
        else:
            if reviewer_username in selected_list:
                selected_list.remove(reviewer_username)

    def reviewer_decision(self, tree, decision):
        if self.user_role != "Hakem":
            return
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        art_id = tree.item(selected[0])["values"][0]
        art = self.db.get_article(art_id)
        if not art:
            return
        
        # Karar verme penceresi
        decision_window = tk.Toplevel(self.root)
        decision_window.title(f"Karar Ver - {decision}")
        decision_window.geometry("600x500")
        decision_window.configure(bg='white')
        
        tk.Label(decision_window, text=f"Karar: {decision}", 
                font=('Arial', 14, 'bold'), bg='white', 
                fg=self.colors['success'] if decision == "Kabul" else 
                   self.colors['danger'] if decision == "Ret" else 
                   self.colors['warning']).pack(pady=15)
        
        tk.Label(decision_window, text="Açıklama/Gerekçe:", 
                font=('Arial', 11, 'bold'), bg='white', fg=self.colors['dark']).pack(pady=(10, 5), anchor='w', padx=20)
        
        comment_text = scrolledtext.ScrolledText(decision_window, height=10, width=60,
                                                 font=('Arial', 10), relief=tk.FLAT,
                                                 bg=self.colors['light'], bd=2)
        comment_text.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        # Dosya yükleme
        file_frame = tk.Frame(decision_window, bg='white')
        file_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(file_frame, text="Ek Dosya (İsteğe Bağlı):", 
                font=('Arial', 10, 'bold'), bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(0, 5))
        
        file_info_label = tk.Label(file_frame, text="Dosya seçilmedi",
                                   font=('Arial', 9), bg='white', fg=self.colors['secondary'])
        file_info_label.pack(anchor='w', pady=(0, 5))
        
        selected_file_path = [None]  # List olarak kullanıyoruz çünkü lambda closure için
        
        def select_file():
            file_path = filedialog.askopenfilename(
                title="Ek Dosya Seç",
                filetypes=[
                    ("Tüm Dosyalar", "*.*"),
                    ("PDF Dosyası", "*.pdf"),
                    ("Word Belgesi", "*.docx *.doc"),
                    ("Metin Dosyası", "*.txt")
                ]
            )
            if file_path:
                selected_file_path[0] = file_path
                file_name = os.path.basename(file_path)
                file_info_label.config(text=f"✓ Seçilen: {file_name}", fg=self.colors['success'])
        
        tk.Button(file_frame, text="📎 Dosya Seç", font=('Arial', 9),
                 bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                 cursor='hand2', padx=15, pady=5, command=select_file).pack(anchor='w')
        
        def submit_decision():
            comment = comment_text.get("1.0", tk.END).strip()
            if not comment:
                messagebox.showerror("Hata", "Lütfen kararınızın gerekçesini açıklayın.")
                return
            
            # Dosyayı kopyala (varsa)
            review_file_path = ""
            file_uploaded = False
            if selected_file_path[0] and os.path.exists(selected_file_path[0]):
                try:
                    # Dosya yolunu düzelt - __file__ yerine doğru yol
                    current_file = os.path.abspath(__file__)
                    base_dir = os.path.dirname(os.path.dirname(current_file))
                    uploads_dir = os.path.join(base_dir, "uploads", "reviews")
                    
                    # Klasör yoksa oluştur
                    if not os.path.exists(uploads_dir):
                        os.makedirs(uploads_dir, exist_ok=True)
                    
                    # Dosya adını oluştur
                    file_ext = os.path.splitext(selected_file_path[0])[1] or ".pdf"
                    # Dosya adında özel karakterleri temizle
                    safe_art_id = art_id.replace("/", "_").replace("\\", "_")
                    safe_username = self.current_user.replace("/", "_").replace("\\", "_")
                    safe_decision = decision.replace("/", "_").replace("\\", "_")
                    new_file_name = f"{safe_art_id}_{safe_username}_{safe_decision}{file_ext}"
                    destination_path = os.path.join(uploads_dir, new_file_name)
                    
                    # Dosyayı kopyala
                    shutil.copy2(selected_file_path[0], destination_path)
                    
                    # Dosyanın başarıyla kopyalandığını kontrol et
                    if os.path.exists(destination_path):
                        review_file_path = destination_path
                        file_uploaded = True
                    else:
                        messagebox.showerror("Hata", "Dosya kopyalanamadı. Lütfen tekrar deneyin.")
                        return
                except Exception as e:
                    error_msg = f"Dosya kopyalanamadı: {str(e)}\n\nDosya: {selected_file_path[0]}\nHedef: {destination_path if 'destination_path' in locals() else 'Bilinmiyor'}"
                    messagebox.showerror("Hata", error_msg)
                    return
            elif selected_file_path[0]:
                messagebox.showerror("Hata", f"Seçilen dosya bulunamadı: {selected_file_path[0]}")
                return
            
            # Önce makaleyi veritabanından güncel halini al
            fresh_art = self.db.get_article(art_id)
            if not fresh_art:
                messagebox.showerror("Hata", "Makale bulunamadı. Lütfen tekrar deneyin.")
                return
            
            # Hakem kararını veritabanına kaydet
            review_success = self.db.add_review(art_id, self.current_user, decision, comment, review_file_path)
            if not review_success:
                messagebox.showerror("Hata", "Karar kaydedilemedi. Lütfen tekrar deneyin.")
                return
            
            # Makale kararlarını güncelle (güncel veriyi kullan)
            decisions = fresh_art.get("decisions", {}).copy()
            decisions[self.current_user] = decision
            
            # Karar kontrolü: 1 ret 1 onay varsa 3. hakem için hazır
            decision_values = list(decisions.values())
            has_reject = "Ret" in decision_values
            has_accept = "Kabul" in decision_values
            
            if len(decisions) >= len(fresh_art.get("reviewers", [])):
                new_status = "Hakem Kararı"
            elif has_reject and has_accept and len(fresh_art.get("reviewers", [])) == 2:
                # 1 ret 1 onay durumu - 3. hakem için hazır
                new_status = "3. Hakem Gerekli"
            else:
                new_status = "Hakemde"
            
            # Makaleyi güncelle
            update_success = self.db.update_article(art_id, {"decisions": decisions, "status": new_status})
            if not update_success:
                print(f"UYARI: Makale güncellenemedi: {art_id}")
            
            # Güncellemenin başarılı olduğunu doğrula
            updated_art = self.db.get_article(art_id)
            if updated_art:
                print(f"DEBUG: Makale güncellendi. Yeni durum: {updated_art.get('status')}, Kararlar: {updated_art.get('decisions')}")
            else:
                print(f"UYARI: Güncellenmiş makale alınamadı: {art_id}")
            
            # Alan editörüne bildirim - ZORUNLU
            field_editor = art.get("field_editor")
            print(f"DEBUG: field_editor = {field_editor}, art_id = {art_id}")
            
            message_sent = False
            if not field_editor:
                warning_msg = f"Makale {art_id} için alan editörü atanmamış!"
                print(f"UYARI: {warning_msg}")
            else:
                # Alan editörüne mesaj gönder - ZORUNLU
                try:
                    reviewer = self.db.get_user(self.current_user)
                    reviewer_name = reviewer.get("name", self.current_user) if reviewer else self.current_user
                    
                    # Mesaj içeriğini oluştur
                    message_content = f"Sayın Alan Editörü,\n\n{reviewer_name} ({self.current_user}) hakemi makale için '{decision}' kararı vermiştir.\n\n"
                    message_content += f"Makale Başlığı: {art.get('title', 'Belirtilmemiş')}\n"
                    message_content += f"Makale ID: {art_id}\n\n"
                    message_content += f"Gerekçe:\n{comment}\n"
                    
                    # Dosya bilgisi ekle
                    if file_uploaded and review_file_path:
                        file_name = os.path.basename(review_file_path)
                        message_content += f"\n\n📎 Ek Dosya: {file_name}\n(Hakem kararı dosyası sisteme yüklenmiştir. Dosya yolu: {review_file_path})"
                    
                    subject = f"Hakem Kararı: {art.get('title', art_id)[:50]}"
                    
                    print(f"DEBUG: Mesaj gönderiliyor - from: {self.current_user}, to: {field_editor}")
                    print(f"DEBUG: subject: {subject}")
                    print(f"DEBUG: message_content uzunluğu: {len(message_content)}")
                    
                    # Mesajı gönder - tekrar dene mekanizması
                    max_retries = 3
                    success = False
                    last_error = None
                    
                    for attempt in range(max_retries):
                        try:
                            success = self.db.add_message(
                                art_id,
                                self.current_user,
                                field_editor,
                                subject,
                                message_content
                            )
                            if success:
                                break
                            else:
                                last_error = "add_message False döndü"
                                print(f"DEBUG: Deneme {attempt + 1}/{max_retries} başarısız: {last_error}")
                                if attempt < max_retries - 1:
                                    time.sleep(0.5)  # Kısa bekleme
                        except Exception as e:
                            last_error = str(e)
                            print(f"DEBUG: Deneme {attempt + 1}/{max_retries} exception: {last_error}")
                            if attempt < max_retries - 1:
                                time.sleep(0.5)
                    
                    print(f"DEBUG: Mesaj gönderme sonucu: {success}")
                    
                    if not success:
                        error_detail = f"Mesaj gönderilemedi - {art_id} -> {field_editor}"
                        if last_error:
                            error_detail += f"\nHata: {last_error}"
                        print(f"UYARI: {error_detail}")
                        
                        # Mesajı dosyaya kaydet (yedek)
                        try:
                            backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "message_backups")
                            if not os.path.exists(backup_dir):
                                os.makedirs(backup_dir, exist_ok=True)
                            backup_file = os.path.join(backup_dir, f"msg_{art_id}_{self.current_user}_{int(time.time())}.txt")
                            with open(backup_file, 'w', encoding='utf-8') as f:
                                f.write(f"TO: {field_editor}\n")
                                f.write(f"FROM: {self.current_user}\n")
                                f.write(f"SUBJECT: {subject}\n")
                                f.write(f"ARTICLE_ID: {art_id}\n")
                                f.write(f"\n{message_content}")
                            print(f"DEBUG: Mesaj yedek dosyaya kaydedildi: {backup_file}")
                        except Exception as backup_error:
                            print(f"DEBUG: Yedek kayıt hatası: {backup_error}")
                        
                        message_sent = False
                    else:
                        print(f"BAŞARILI: Mesaj {field_editor} alan editörüne gönderildi.")
                        message_sent = True
                        # Mesajın gerçekten gönderildiğini doğrula
                        verify_messages = self.db.get_messages_by_user(field_editor)
                        found = False
                        for msg in verify_messages:
                            if (msg.get("article_id") == art_id and 
                                msg.get("from_user") == self.current_user and
                                msg.get("subject") == subject):
                                found = True
                                break
                        if found:
                            print(f"DOĞRULAMA: Mesaj alan editörünün mesaj kutusunda bulundu.")
                        else:
                            print(f"UYARI: Mesaj gönderildi ancak doğrulama başarısız!")
                            
                except Exception as e:
                    error_msg = f"Alan editörüne mesaj gönderilirken hata: {str(e)}"
                    print(f"HATA: {error_msg}")
                    traceback.print_exc()
                    message_sent = False
            
            # Başarı mesajını oluştur
            success_msg = f"✅ Değerlendirmeniz başarıyla gönderildi!\n\n"
            success_msg += f"Makale: {art_id}\n"
            success_msg += f"Karar: {decision}\n"
            if file_uploaded:
                success_msg += "✓ Ek dosya başarıyla yüklendi.\n"
            
            if message_sent:
                success_msg += f"\n✓ Alan editörüne ({field_editor}) bildirim başarıyla gönderildi."
            elif field_editor:
                success_msg += f"\n⚠ Uyarı: Alan editörüne ({field_editor}) bildirim gönderilemedi."
            else:
                success_msg += "\n⚠ Uyarı: Makale için alan editörü atanmamış, bildirim gönderilemedi."
            
            # Ek bilgiler
            if has_reject and has_accept:
                success_msg += "\n\nℹ️ Not: 3. hakem gerekli olabilir."
            
            # Pencereyi kapat (mesajdan ÖNCE)
            decision_window.destroy()
            
            # Başarı mesajını göster (pencere kapandıktan SONRA)
            messagebox.showinfo("✅ Değerlendirme Gönderildi", success_msg)
            
            # Sayfayı güncelle - her durumda güncelle
            try:
                # Önce mevcut görünümü kontrol et
                if hasattr(self, 'current_view'):
                    if self.current_view == 'evaluated':
                        # Değerlendirilenler sayfasındaysa, yeni kararı göster
                        self.show_evaluated()
                    elif self.current_view in ['assigned', 'pending_tasks']:
                        # Atanan makaleler veya bekleyen görevler sayfasındaysa, 
                        # karar verilen makale listeden çıkacak
                        self.show_assigned()
                    elif self.current_view == 'sent_decisions':
                        # Gönderilen kararlar sayfasındaysa, yeni kararı göster
                        self.show_sent_decisions()
                    else:
                        # Varsayılan olarak atanan makaleleri göster
                        self.show_assigned()
                else:
                    # current_view yoksa, atanan makaleleri göster
                    self.show_assigned()
                    
            except Exception as e:
                print(f"HATA: Sayfa güncellenirken hata: {str(e)}")
                traceback.print_exc()
                # Hata olsa bile tekrar dene
                try:
                    self.show_assigned()
                except:
                    pass
        
        tk.Button(decision_window, text="✅ Kararı Gönder", bg=self.colors['success'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=submit_decision,
                 padx=20, pady=10).pack(pady=15)
    
    def show_article_details_for_reviewer(self, tree):
        """Hakem için makale detaylarını göster"""
        if self.user_role != "Hakem":
            return
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        art_id = tree.item(selected[0])["values"][0]
        art = self.db.get_article(art_id)
        if not art:
            messagebox.showerror("Hata", "Makale bulunamadı.")
            return
        
        # Detay penceresi
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Makale Detayları - {art_id}")
        detail_window.geometry("800x700")
        detail_window.configure(bg='white')
        
        # Scrollable frame
        main_container = tk.Frame(detail_window, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_container, bg='white')
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scrollable_frame.bind("<Configure>", on_frame_configure)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Canvas scroll ayarı
        def on_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas.find_all()[0], width=canvas_width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        # İçerik
        content_frame = tk.Frame(scrollable_frame, bg='white', padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        tk.Label(content_frame, text="Makale Detayları", 
                font=('Arial', 18, 'bold'), bg='white', fg=self.colors['primary']).pack(anchor='w', pady=(0, 20))
        
        # Makale bilgileri
        info_items = [
            ("Makale ID:", art_id),
            ("Başlık:", art.get("title", "Belirtilmemiş")),
            ("Yazar:", art.get("authors", art.get("author", "Belirtilmemiş"))),
            ("Durum:", art.get("status", "Belirtilmemiş")),
            ("Editör:", art.get("editor", "Atanmamış")),
            ("Alan Editörü:", art.get("field_editor", "Atanmamış")),
        ]
        
        for label, value in info_items:
            row_frame = tk.Frame(content_frame, bg='white')
            row_frame.pack(fill=tk.X, pady=5)
            tk.Label(row_frame, text=label, font=('Arial', 11, 'bold'), 
                    bg='white', fg=self.colors['dark'], width=15, anchor='w').pack(side=tk.LEFT)
            tk.Label(row_frame, text=str(value), font=('Arial', 11), 
                    bg='white', fg=self.colors['dark'], anchor='w').pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Hakemler
        reviewers = art.get("reviewers", [])
        if reviewers:
            tk.Label(content_frame, text="Hakemler:", font=('Arial', 11, 'bold'), 
                    bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(10, 5))
            for reviewer in reviewers:
                reviewer_user = self.db.get_user(reviewer)
                reviewer_name = reviewer_user.get("name", reviewer) if reviewer_user else reviewer
                tk.Label(content_frame, text=f"  • {reviewer_name} ({reviewer})", 
                        font=('Arial', 10), bg='white', fg=self.colors['dark']).pack(anchor='w', padx=20)
        
        # Kararlar
        decisions = art.get("decisions", {})
        if decisions:
            tk.Label(content_frame, text="Hakem Kararları:", font=('Arial', 11, 'bold'), 
                    bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(10, 5))
            for reviewer, decision in decisions.items():
                reviewer_user = self.db.get_user(reviewer)
                reviewer_name = reviewer_user.get("name", reviewer) if reviewer_user else reviewer
                decision_color = self.colors['success'] if decision == "Kabul" else \
                               self.colors['danger'] if decision == "Ret" else \
                               self.colors['warning']
                tk.Label(content_frame, text=f"  • {reviewer_name}: {decision}", 
                        font=('Arial', 10), bg='white', fg=decision_color).pack(anchor='w', padx=20)
        
        # Dosya bilgisi
        file_path = art.get("file_path", "")
        if file_path:
            file_frame = tk.Frame(content_frame, bg='white')
            file_frame.pack(fill=tk.X, pady=(10, 0))
            tk.Label(file_frame, text="Makale Dosyası:", font=('Arial', 11, 'bold'), 
                    bg='white', fg=self.colors['dark']).pack(anchor='w')
            tk.Label(file_frame, text=f"  {os.path.basename(file_path)}", 
                    font=('Arial', 10), bg='white', fg=self.colors['secondary']).pack(anchor='w', padx=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel desteği
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # Kapat butonu
        button_frame = tk.Frame(detail_window, bg='white')
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Kapat", bg=self.colors['secondary'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=detail_window.destroy,
                 padx=20, pady=10).pack()
    
    def download_article_file_for_reviewer(self, tree):
        """Hakem için makale dosyasını indir"""
        if self.user_role != "Hakem":
            return
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        art_id = tree.item(selected[0])["values"][0]
        art = self.db.get_article(art_id)
        if not art:
            messagebox.showerror("Hata", "Makale bulunamadı.")
            return
        
        file_path = art.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Hata", "Makale dosyası bulunamadı.")
            return
        
        # Dosya kaydetme konumu seç
        file_name = os.path.basename(file_path)
        save_path = filedialog.asksaveasfilename(
            title="Dosyayı Kaydet",
            defaultextension=os.path.splitext(file_name)[1],
            initialfile=file_name,
            filetypes=[
                ("Tüm Dosyalar", "*.*"),
                ("PDF Dosyası", "*.pdf"),
                ("Word Belgesi", "*.docx *.doc"),
                ("Metin Dosyası", "*.txt")
            ]
        )
        
        if save_path:
            try:
                shutil.copy2(file_path, save_path)
                messagebox.showinfo("Başarılı", f"Dosya başarıyla indirildi:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya indirilemedi: {str(e)}")

    def communicate_with_reviewers(self, tree):
        """Hakemlerle iletişim kur"""
        if self.user_role != "Alan Editörü":
            messagebox.showerror("Hata", "Sadece alan editörü bu işlemi yapabilir.")
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        item = tree.item(selected[0])["values"]
        art_id = item[0]
        art = self.db.get_article(art_id)
        if not art:
            return
        
        reviewers = art.get("reviewers", [])
        if not reviewers:
            messagebox.showwarning("Uyarı", "Bu makale için henüz hakem atanmamış.")
            return
        
        # İletişim penceresi
        comm_window = tk.Toplevel(self.root)
        comm_window.title(f"Hakemlerle İletişim - {art_id}")
        comm_window.geometry("700x600")
        comm_window.configure(bg='white')
        
        # Hakem seçimi
        tk.Label(comm_window, text="Hakem Seçin:", 
                font=('Arial', 11, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=10, anchor='w', padx=20)
        
        reviewer_var = tk.StringVar()
        reviewer_options = []
        for reviewer_username in reviewers:
            reviewer = self.db.get_user(reviewer_username)
            reviewer_name = reviewer.get("name", reviewer_username) if reviewer else reviewer_username
            expertise = reviewer.get("expertise_field", "") if reviewer else ""
            
            display_text = f"{reviewer_name} ({reviewer_username})"
            if expertise:
                display_text += f" - 📚 {expertise}"
            
            reviewer_options.append(display_text)
        
        reviewer_combo = ttk.Combobox(comm_window, textvariable=reviewer_var,
                                     values=reviewer_options, state='readonly', width=50)
        reviewer_combo.pack(pady=5, padx=20, fill=tk.X)
        reviewer_combo.current(0)  # İlk hakemi varsayılan seç
        
        # Mesaj geçmişi
        tk.Label(comm_window, text="Mesaj Geçmişi:", 
                font=('Arial', 11, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(20, 10), anchor='w', padx=20)
        
        messages_frame = tk.Frame(comm_window, bg='white')
        messages_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        messages_canvas = tk.Canvas(messages_frame, bg='white', height=200)
        messages_scrollbar = ttk.Scrollbar(messages_frame, orient="vertical", command=messages_canvas.yview)
        messages_scrollable = tk.Frame(messages_canvas, bg='white')
        
        messages_scrollable.bind(
            "<Configure>",
            lambda e: messages_canvas.configure(scrollregion=messages_canvas.bbox("all"))
        )
        
        messages_canvas.create_window((0, 0), window=messages_scrollable, anchor="nw")
        messages_canvas.configure(yscrollcommand=messages_scrollbar.set)
        
        def refresh_messages():
            # Mesajları temizle
            for widget in messages_scrollable.winfo_children():
                widget.destroy()
            
            # Seçili hakemle mesajları göster
            selected_option = reviewer_var.get()
            if not selected_option:
                return
            
            # Format: "İsim (username)" veya sadece username
            if " (" in selected_option and ")" in selected_option:
                selected_reviewer = selected_option.split(" (")[1].split(")")[0]
            else:
                # Eğer format farklıysa, reviewers listesinden bul
                selected_reviewer = None
                for rev in reviewers:
                    if rev in selected_option or selected_option in rev:
                        selected_reviewer = rev
                        break
                if not selected_reviewer:
                    selected_reviewer = reviewers[0] if reviewers else None
            
            # Bu hakemle olan mesajları filtrele
            all_messages = self.db.get_messages_by_article(art_id)
            reviewer_messages = [m for m in all_messages 
                                if m["from_user"] == selected_reviewer or m["to_user"] == selected_reviewer]
            
            if not reviewer_messages:
                tk.Label(messages_scrollable, text="Henüz mesaj yok.",
                        font=('Arial', 10), bg='white', fg=self.colors['secondary']).pack(pady=20)
            else:
                for msg in reviewer_messages:
                    msg_frame = tk.Frame(messages_scrollable, bg=self.colors['light'], relief=tk.RAISED, borderwidth=1)
                    msg_frame.pack(fill=tk.X, pady=5, padx=5)
                    
                    from_user = self.db.get_user(msg["from_user"])
                    from_name = from_user.get("name", msg["from_user"]) if from_user else msg["from_user"]
                    
                    tk.Label(msg_frame, text=f"{from_name} ({msg['from_user']}) - {msg['subject']}",
                            font=('Arial', 9, 'bold'), bg=self.colors['light'], fg=self.colors['primary']).pack(anchor='w', padx=10, pady=(5, 0))
                    tk.Label(msg_frame, text=msg["message"], font=('Arial', 9),
                            bg=self.colors['light'], fg=self.colors['dark_text'], wraplength=600,
                            justify='left').pack(anchor='w', padx=10, pady=5)
                    tk.Label(msg_frame, text=msg["created_at"], font=('Arial', 8),
                            bg=self.colors['light'], fg=self.colors['secondary']).pack(anchor='w', padx=10, pady=(0, 5))
        
        reviewer_combo.bind("<<ComboboxSelected>>", lambda e: refresh_messages())
        refresh_messages()  # İlk yükleme
        
        messages_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        messages_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Yeni mesaj gönderme
        tk.Label(comm_window, text="Yeni Mesaj:", 
                font=('Arial', 11, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=(10, 5), anchor='w', padx=20)
        
        subject_frame = tk.Frame(comm_window, bg='white')
        subject_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(subject_frame, text="Konu:", font=('Arial', 10), bg='white').pack(side=tk.LEFT, padx=(0, 10))
        subject_entry = tk.Entry(subject_frame, font=('Arial', 10), width=50)
        subject_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        message_text = scrolledtext.ScrolledText(comm_window, height=6, width=70,
                                                 font=('Arial', 10), relief=tk.FLAT,
                                                 bg=self.colors['light'], bd=2)
        message_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        def send_message():
            # Hakem seçimini düzelt
            selected_option = reviewer_var.get()
            if not selected_option:
                messagebox.showerror("Hata", "Lütfen bir hakem seçin.")
                return
            
            # Format: "İsim (username)" veya sadece username
            if " (" in selected_option and ")" in selected_option:
                selected_reviewer = selected_option.split(" (")[1].split(")")[0]
            else:
                # Eğer format farklıysa, reviewers listesinden bul
                selected_reviewer = None
                for rev in reviewers:
                    if rev in selected_option or selected_option in rev:
                        selected_reviewer = rev
                        break
                if not selected_reviewer:
                    selected_reviewer = reviewers[0] if reviewers else None
            
            if not selected_reviewer:
                messagebox.showerror("Hata", "Hakem seçilemedi.")
                return
            
            subject = subject_entry.get().strip()
            message = message_text.get("1.0", tk.END).strip()
            
            if not subject or not message:
                messagebox.showerror("Hata", "Lütfen konu ve mesajı doldurun.")
                return
            
            # Mesajı gönder
            self.db.add_message(art_id, self.current_user, selected_reviewer, subject, message)
            messagebox.showinfo("Başarılı", f"Mesaj {selected_reviewer} hakemine gönderildi.")
            subject_entry.delete(0, tk.END)
            message_text.delete("1.0", tk.END)
            refresh_messages()  # Mesaj geçmişini yenile
        
        tk.Button(comm_window, text="📧 Mesaj Gönder", bg=self.colors['success'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=send_message,
                 padx=20, pady=10).pack(pady=10)

    def assign_third_reviewer(self, tree):
        """3. hakem atama (1 ret 1 onay durumunda)"""
        if self.user_role != "Alan Editörü":
            messagebox.showerror("Hata", "Sadece alan editörü bu işlemi yapabilir.")
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        item = tree.item(selected[0])["values"]
        art_id = item[0]
        art = self.db.get_article(art_id)
        if not art:
            return
        
        # Durum kontrolü
        if art.get("status") != "3. Hakem Gerekli":
            messagebox.showwarning("Uyarı", 
                                  "Bu makale için 3. hakem ataması gerekli değil.\n"
                                  "3. hakem sadece 1 ret 1 onay durumunda atanabilir.")
            return
        
        # Mevcut hakemleri kontrol et
        current_reviewers = art.get("reviewers", [])
        if len(current_reviewers) >= 3:
            messagebox.showinfo("Bilgi", "Bu makale için zaten 3 hakem atanmış.")
            return
        
        # Hakem seçim penceresi
        selection_window = tk.Toplevel(self.root)
        selection_window.title("3. Hakem Seç")
        selection_window.geometry("500x350")
        selection_window.configure(bg='white')
        
        tk.Label(selection_window, text="3. Hakem Seçin:", 
                font=('Arial', 12, 'bold'), bg='white', fg=self.colors['warning']).pack(pady=20)
        
        # Mevcut hakemleri hariç tut
        all_reviewers = self.get_users_by_role("Hakem")
        available_reviewers = [r for r in all_reviewers if r not in current_reviewers]
        
        if not available_reviewers:
            messagebox.showerror("Hata", "Atanabilecek hakem bulunamadı.")
            selection_window.destroy()
            return
        
        reviewer_var = tk.StringVar()
        reviewer_options = []
        for reviewer_username in available_reviewers:
            reviewer = self.db.get_user(reviewer_username)
            reviewer_name = reviewer.get("name", reviewer_username) if reviewer else reviewer_username
            expertise = reviewer.get("expertise_field", "") if reviewer else ""
            
            display_text = f"{reviewer_name} ({reviewer_username})"
            if expertise:
                display_text += f" - 📚 {expertise}"
            
            reviewer_options.append(display_text)
        
        reviewer_combo = ttk.Combobox(selection_window, textvariable=reviewer_var,
                                     values=reviewer_options, state='readonly', width=50)
        reviewer_combo.pack(pady=10, padx=20, fill=tk.X)
        
        def confirm_assignment():
            selected_text = reviewer_var.get()
            if not selected_text:
                messagebox.showerror("Hata", "Lütfen bir hakem seçin.")
                return
            # Format: "Ad (username) - 📚 Uzmanlık" veya "Ad (username)"
            # Username'i parantez içinden al
            if " (" in selected_text:
                selected_reviewer = selected_text.split(" (")[1].split(")")[0]
            else:
                selected_reviewer = None
            if not selected_reviewer:
                messagebox.showerror("Hata", "Hakem seçilemedi.")
                return
            
            # 3. hakemi ekle
            new_reviewers = current_reviewers + [selected_reviewer]
            self.db.update_article(art_id, {
                "reviewers": new_reviewers,
                "status": "Hakemde"
            })
            
            # 3. hakeme bildirim gönder
            reviewer = self.db.get_user(selected_reviewer)
            reviewer_name = reviewer.get("name", selected_reviewer) if reviewer else selected_reviewer
            self.db.add_message(
                art_id,
                self.current_user,
                selected_reviewer,
                f"3. Hakem Görevi: {art.get('title', art_id)}",
                f"Sayın {reviewer_name},\n\nMakale değerlendirmesi için size 3. hakem olarak görev atanmıştır.\n\n"
                f"Makale: {art.get('title', art_id)}\nMakale ID: {art_id}\n\n"
                f"Not: Bu makale için 1 hakem 'Ret', 1 hakem 'Kabul' vermiştir. "
                f"Lütfen makaleyi inceleyip değerlendirmenizi yapınız.\n\nSaygılarımızla,\nAlan Editörü"
            )
            
            messagebox.showinfo("Başarılı", 
                              f"3. hakem atandı: {selected_reviewer}\nHakeme bildirim gönderildi.")
            selection_window.destroy()
            self.show_submissions()
        
        tk.Button(selection_window, text="✅ 3. Hakemi Ata", bg=self.colors['warning'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=confirm_assignment,
                 padx=20, pady=10).pack(pady=20)

    def show_reviewer_decisions_for_fe(self, tree):
        """Alan editörü için hakem kararlarını göster"""
        if self.user_role != "Alan Editörü":
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        
        art_id = tree.item(selected[0])["values"][0]
        art = self.db.get_article(art_id)
        if not art:
            messagebox.showerror("Hata", "Makale bulunamadı.")
            return
        
        # Hakem kararlarını getir
        reviews = self.db.get_reviews_by_article(art_id)
        
        if not reviews:
            messagebox.showinfo("Bilgi", "Bu makale için henüz hakem kararı bulunmamaktadır.")
            return
        
        # Kararları gösteren pencere
        decision_window = tk.Toplevel(self.root)
        decision_window.title(f"Hakem Kararları - {art_id}")
        decision_window.geometry("900x600")
        decision_window.configure(bg='white')
        
        # Başlık
        header_frame = tk.Frame(decision_window, bg='white')
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(header_frame, text=f"📋 Hakem Kararları", 
                font=('Arial', 16, 'bold'), bg='white', 
                fg=self.colors['primary']).pack(anchor='w')
        
        tk.Label(header_frame, text=f"Makale: {art.get('title', art_id)}", 
                font=('Arial', 11), bg='white', 
                fg=self.colors['dark_text']).pack(anchor='w', pady=(5, 0))
        
        tk.Label(header_frame, text=f"Makale ID: {art_id}", 
                font=('Arial', 10), bg='white', 
                fg=self.colors['secondary']).pack(anchor='w', pady=(2, 10))
        
        # Scrollable frame
        canvas = tk.Canvas(decision_window, bg='white')
        scrollbar = ttk.Scrollbar(decision_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Her hakem kararını göster
        for idx, review in enumerate(reviews):
            reviewer_username = review.get("reviewer_username", "")
            reviewer = self.db.get_user(reviewer_username)
            reviewer_name = reviewer.get("name", reviewer_username) if reviewer else reviewer_username
            
            decision = review.get("decision", "")
            comment = review.get("comment", "")
            review_date = review.get("created_at", "")[:19] if review.get("created_at") else ""
            file_path = review.get("file_path", "")
            
            # Karar kartı
            card = tk.Frame(scrollable_frame, bg='white', relief=tk.RAISED, borderwidth=2)
            card.pack(fill=tk.X, padx=20, pady=10)
            
            # İç frame
            inner_frame = tk.Frame(card, bg='white')
            inner_frame.pack(fill=tk.X, padx=15, pady=15)
            
            # Hakem bilgisi ve karar
            info_frame = tk.Frame(inner_frame, bg='white')
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            decision_color = self.colors['success'] if decision == "Kabul" else \
                           self.colors['danger'] if decision == "Ret" else \
                           self.colors['warning']
            
            tk.Label(info_frame, text=f"👤 Hakem: {reviewer_name} ({reviewer_username})", 
                    font=('Arial', 12, 'bold'), bg='white', 
                    fg=self.colors['dark']).pack(anchor='w', side=tk.LEFT)
            
            tk.Label(info_frame, text=f"Karar: {decision}", 
                    font=('Arial', 12, 'bold'), bg='white', 
                    fg=decision_color).pack(anchor='w', side=tk.LEFT, padx=(20, 0))
            
            if review_date:
                tk.Label(info_frame, text=f"📅 {review_date}", 
                        font=('Arial', 9), bg='white', 
                        fg=self.colors['secondary']).pack(anchor='e', side=tk.RIGHT)
            
            # Gerekçe
            tk.Label(inner_frame, text="Gerekçe:", 
                    font=('Arial', 10, 'bold'), bg='white', 
                    fg=self.colors['dark']).pack(anchor='w', pady=(5, 2))
            
            comment_text = scrolledtext.ScrolledText(inner_frame, height=6, width=80,
                                                     font=('Arial', 10), relief=tk.FLAT,
                                                     bg=self.colors['light'], bd=1, wrap=tk.WORD)
            comment_text.insert("1.0", comment)
            comment_text.config(state=tk.DISABLED)
            comment_text.pack(fill=tk.X, pady=(0, 10))
            
            # Dosya indirme butonu (varsa)
            if file_path and os.path.exists(file_path):
                file_frame = tk.Frame(inner_frame, bg='white')
                file_frame.pack(fill=tk.X, pady=(0, 5))
                
                file_name = os.path.basename(file_path)
                tk.Label(file_frame, text=f"📎 Ek Dosya: {file_name}", 
                        font=('Arial', 9), bg='white', 
                        fg=self.colors['secondary']).pack(side=tk.LEFT)
                
                def download_review_file(path=file_path):
                    try:
                        dest_path = filedialog.asksaveasfilename(
                            title="Dosyayı Kaydet",
                            defaultextension=os.path.splitext(path)[1],
                            initialfile=os.path.basename(path)
                        )
                        if dest_path:
                            shutil.copy2(path, dest_path)
                            messagebox.showinfo("Başarılı", "Dosya başarıyla indirildi.")
                    except Exception as e:
                        messagebox.showerror("Hata", f"Dosya indirilemedi: {str(e)}")
                
                tk.Button(file_frame, text="📥 İndir", 
                         font=('Arial', 9), bg=self.colors['info'], fg='white',
                         relief=tk.FLAT, cursor='hand2', padx=10, pady=3,
                         command=download_review_file).pack(side=tk.LEFT, padx=(10, 0))
            
            # Ayırıcı (son değilse)
            if idx < len(reviews) - 1:
                separator = tk.Frame(scrollable_frame, bg='#ddd', height=1)
                separator.pack(fill=tk.X, padx=20, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Kapat butonu
        close_btn = tk.Button(decision_window, text="Kapat", bg=self.colors['secondary'], 
                             fg='white', relief=tk.FLAT, cursor='hand2',
                             command=decision_window.destroy, padx=20, pady=10)
        close_btn.pack(pady=15)

    def send_recommendation_to_editor(self, tree):
        """Editöre makale önerisi gönder"""
        if self.user_role != "Alan Editörü":
            messagebox.showerror("Hata", "Sadece alan editörü bu işlemi yapabilir.")
            return
        
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        item = tree.item(selected[0])["values"]
        art_id = item[0]
        art = self.db.get_article(art_id)
        if not art:
            return
        
        editor = art.get("editor")
        if not editor:
            messagebox.showerror("Hata", "Bu makale için editör bilgisi bulunamadı.")
            return
        
        # Öneri penceresi
        recommendation_window = tk.Toplevel(self.root)
        recommendation_window.title(f"Editöre Öneri Gönder - {art_id}")
        recommendation_window.geometry("600x500")
        recommendation_window.configure(bg='white')
        
        tk.Label(recommendation_window, text="Editöre Öneri:", 
                font=('Arial', 14, 'bold'), bg='white', fg=self.colors['primary']).pack(pady=15)
        
        # Hakem kararlarını göster
        reviews = self.db.get_reviews_by_article(art_id)
        if reviews:
            tk.Label(recommendation_window, text="Hakem Kararları:", 
                    font=('Arial', 11, 'bold'), bg='white', fg=self.colors['dark']).pack(pady=(10, 5), anchor='w', padx=20)
            
            reviews_frame = tk.Frame(recommendation_window, bg='white')
            reviews_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
            
            reviews_canvas = tk.Canvas(reviews_frame, bg='white', height=100)
            reviews_scrollbar = ttk.Scrollbar(reviews_frame, orient="vertical", command=reviews_canvas.yview)
            reviews_scrollable = tk.Frame(reviews_canvas, bg='white')
            
            reviews_scrollable.bind(
                "<Configure>",
                lambda e: reviews_canvas.configure(scrollregion=reviews_canvas.bbox("all"))
            )
            
            reviews_canvas.create_window((0, 0), window=reviews_scrollable, anchor="nw")
            reviews_canvas.configure(yscrollcommand=reviews_scrollbar.set)
            
            for review in reviews:
                reviewer = self.db.get_user(review["reviewer_username"])
                reviewer_name = reviewer.get("name", review["reviewer_username"]) if reviewer else review["reviewer_username"]
                
                review_frame = tk.Frame(reviews_scrollable, bg=self.colors['light'], relief=tk.RAISED, borderwidth=1)
                review_frame.pack(fill=tk.X, pady=3, padx=3)
                
                decision_color = self.colors['success'] if review["decision"] == "Kabul" else \
                               self.colors['danger'] if review["decision"] == "Ret" else \
                               self.colors['warning']
                
                # Üst satır: Hakem adı ve karar
                top_frame = tk.Frame(review_frame, bg=self.colors['light'])
                top_frame.pack(fill=tk.X, padx=5, pady=2)
                tk.Label(top_frame, text=f"{reviewer_name}: {review['decision']}", 
                        font=('Arial', 9, 'bold'), bg=self.colors['light'], fg=decision_color).pack(side=tk.LEFT)
                
                # Dosya indirme butonu (varsa)
                review_file_path = review.get("file_path", "")
                if review_file_path and os.path.exists(review_file_path):
                    def download_review_file(file_path=review_file_path, reviewer=reviewer_name):
                        file_name = os.path.basename(file_path)
                        save_path = filedialog.asksaveasfilename(
                            title="Hakem Dosyasını Kaydet",
                            defaultextension=os.path.splitext(file_name)[1],
                            initialfile=file_name
                        )
                        if save_path:
                            try:
                                shutil.copy2(file_path, save_path)
                                messagebox.showinfo("Başarılı", f"Dosya başarıyla indirildi:\n{save_path}")
                            except Exception as e:
                                messagebox.showerror("Hata", f"Dosya indirilemedi: {str(e)}")
                    
                    tk.Button(top_frame, text="📥 Dosyayı İndir", 
                             font=('Arial', 8), bg=self.colors['secondary'], fg='white',
                             relief=tk.FLAT, cursor='hand2', padx=8, pady=2,
                             command=lambda f=review_file_path, r=reviewer_name: download_review_file(f, r)).pack(side=tk.RIGHT)
                
                # Açıklama
                if review.get("comment"):
                    tk.Label(review_frame, text=review["comment"][:100] + ("..." if len(review["comment"]) > 100 else ""), 
                            font=('Arial', 8), bg=self.colors['light'], fg=self.colors['dark_text'],
                            wraplength=500).pack(anchor='w', padx=5, pady=2)
            
            reviews_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            reviews_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Öneri seçimi
        tk.Label(recommendation_window, text="Yayına Uygunluk Önerisi:", 
                font=('Arial', 11, 'bold'), bg='white', fg=self.colors['dark']).pack(pady=(20, 10), anchor='w', padx=20)
        
        recommendation_var = tk.StringVar(value="Yayına Uygun")
        recommendation_options = ["Yayına Uygun", "Düzeltme Sonrası Yayınlanabilir", "Yayına Uygun Değil"]
        
        for option in recommendation_options:
            tk.Radiobutton(recommendation_window, text=option, variable=recommendation_var,
                          value=option, font=('Arial', 10), bg='white',
                          fg=self.colors['dark_text']).pack(anchor='w', padx=40, pady=3)
        
        # Açıklama
        tk.Label(recommendation_window, text="Açıklama:", 
                font=('Arial', 11, 'bold'), bg='white', fg=self.colors['dark']).pack(pady=(15, 5), anchor='w', padx=20)
        
        comment_text = scrolledtext.ScrolledText(recommendation_window, height=8, width=60,
                                                 font=('Arial', 10), relief=tk.FLAT,
                                                 bg=self.colors['light'], bd=2)
        comment_text.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        
        # Dosya yükleme
        file_frame = tk.Frame(recommendation_window, bg='white')
        file_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(file_frame, text="Ek Dosya (İsteğe Bağlı):", 
                font=('Arial', 10, 'bold'), bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(0, 5))
        
        file_info_label = tk.Label(file_frame, text="Dosya seçilmedi",
                                   font=('Arial', 9), bg='white', fg=self.colors['secondary'])
        file_info_label.pack(anchor='w', pady=(0, 5))
        
        selected_file_path = [None]
        
        def select_file():
            file_path = filedialog.askopenfilename(
                title="Ek Dosya Seç",
                filetypes=[
                    ("Tüm Dosyalar", "*.*"),
                    ("PDF Dosyası", "*.pdf"),
                    ("Word Belgesi", "*.docx *.doc"),
                    ("Metin Dosyası", "*.txt")
                ]
            )
            if file_path:
                selected_file_path[0] = file_path
                file_name = os.path.basename(file_path)
                file_info_label.config(text=f"✓ Seçilen: {file_name}", fg=self.colors['success'])
        
        tk.Button(file_frame, text="📎 Dosya Seç", font=('Arial', 9),
                 bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                 cursor='hand2', padx=15, pady=5, command=select_file).pack(anchor='w')
        
        def send_recommendation():
            recommendation = recommendation_var.get()
            comment = comment_text.get("1.0", tk.END).strip()
            
            if not comment:
                messagebox.showerror("Hata", "Lütfen önerinizin açıklamasını yazın.")
                return
            
            # Dosyayı kopyala (varsa)
            recommendation_file_path = ""
            file_uploaded = False
            if selected_file_path[0] and os.path.exists(selected_file_path[0]):
                try:
                    current_file = os.path.abspath(__file__)
                    base_dir = os.path.dirname(os.path.dirname(current_file))
                    uploads_dir = os.path.join(base_dir, "uploads", "recommendations")
                    
                    if not os.path.exists(uploads_dir):
                        os.makedirs(uploads_dir, exist_ok=True)
                    
                    file_ext = os.path.splitext(selected_file_path[0])[1] or ".pdf"
                    safe_art_id = art_id.replace("/", "_").replace("\\", "_")
                    safe_username = self.current_user.replace("/", "_").replace("\\", "_")
                    new_file_name = f"{safe_art_id}_{safe_username}_recommendation{file_ext}"
                    destination_path = os.path.join(uploads_dir, new_file_name)
                    
                    shutil.copy2(selected_file_path[0], destination_path)
                    
                    if os.path.exists(destination_path):
                        recommendation_file_path = destination_path
                        file_uploaded = True
                    else:
                        messagebox.showerror("Hata", "Dosya kopyalanamadı. Lütfen tekrar deneyin.")
                        return
                except Exception as e:
                    messagebox.showerror("Hata", f"Dosya kopyalanamadı: {str(e)}")
                    return
            
            # Öneriyi kaydet
            recommendation_text = f"{recommendation}: {comment}"
            if file_uploaded:
                recommendation_text += f" [DOSYA: {os.path.basename(recommendation_file_path)}]"
            
            self.db.update_article(art_id, {
                "field_editor_recommendation": recommendation_text
            })
            
            # Editöre mesaj gönder
            field_editor = self.db.get_user(self.current_user)
            field_editor_name = field_editor.get("name", self.current_user) if field_editor else self.current_user
            
            message_content = f"Sayın Editör,\n\n{field_editor_name} (Alan Editörü) olarak makale değerlendirmesini tamamladım.\n\n"
            message_content += f"Önerim: {recommendation}\n\nAçıklama:\n{comment}\n\n"
            message_content += f"Makale ID: {art_id}\nMakale: {art.get('title', art_id)}\n\n"
            
            if file_uploaded and recommendation_file_path:
                file_name = os.path.basename(recommendation_file_path)
                message_content += f"📎 Ek Dosya: {file_name}\n(Öneri dosyası sisteme yüklenmiştir. Dosya yolu: {recommendation_file_path})\n\n"
            
            message_content += f"Saygılarımızla,\nAlan Editörü"
            
            success = self.db.add_message(
                art_id,
                self.current_user,
                editor,
                f"Alan Editörü Önerisi: {art.get('title', art_id)[:50]}",
                message_content
            )
            
            if success:
                success_msg = "Öneriniz editöre gönderildi."
                if file_uploaded:
                    success_msg += "\n✓ Dosya başarıyla yüklendi."
                messagebox.showinfo("Başarılı", success_msg)
            else:
                messagebox.showerror("Hata", "Öneri kaydedildi ancak editöre mesaj gönderilemedi. Lütfen sistem yöneticisine bildirin.")
            
            recommendation_window.destroy()
            self.show_submissions()
        
        tk.Button(recommendation_window, text="📤 Öneriyi Gönder", bg=self.colors['success'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=send_recommendation,
                 padx=20, pady=10).pack(pady=15)

    def finalize_articles_view(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        header = tk.Label(self.content_area, text="✅ Editör Kararı",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')

        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("Kod", "Başlık", "Yazar", "Durum", "Hakem Kararları")
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        all_articles = self.db.get_all_articles()
        for art in all_articles:
            if art.get("status") in ["Hakem Kararı", "Hakemde", "Alan Editöründe", "Editör İncelemede"]:
                decisions = ", ".join([f"{r}:{d}" for r, d in art.get("decisions", {}).items()])
                author = art.get("authors", art.get("author", ""))
                tree.insert('', tk.END, values=(art["id"], art["title"], author, art["status"], decisions))

        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(self.content_area, text="Karar Ver ve Yayına Hazırla", bg=self.colors['success'], fg='white',
                  relief=tk.FLAT, cursor='hand2', command=lambda: self.finalize_articles(tree)).pack(pady=10)

    def finalize_articles(self, tree):
        if self.user_role not in ["Admin", "Editör"]:
            messagebox.showerror("Hata", "Sadece editör karar verebilir.")
            return
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Hata", "Bir makale seçin.")
            return
        art_id = tree.item(selected[0])["values"][0]
        art = self.db.get_article(art_id)
        if not art:
            return

        decisions = list(art.get("decisions", {}).values())
        if any(d == "Ret" for d in decisions):
            final_status = "Reddedildi"
        elif any(d == "Düzeltme" for d in decisions):
            final_status = "Düzeltme İstendi"
        elif decisions:
            final_status = "Kabul"
        else:
            final_status = "Editör Kararı Bekleniyor"

        new_status = "Yayına Hazır" if final_status == "Kabul" else final_status
        scheduled = final_status == "Kabul"
        self.db.update_article(art_id, {"status": new_status, "scheduled": 1 if scheduled else 0})
        messagebox.showinfo("Bilgi", f"{art_id} için sonuç: {new_status}")
        self.show_submissions()

    def show_publish_issue(self):
        """Editör için sayı oluşturma ve yayınlama ekranı"""
        if self.user_role not in ["Admin", "Editör"]:
            messagebox.showerror("Hata", "Sadece editör bu işlemi yapabilir.")
            return
        
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = tk.Label(self.content_area, text="📚 Sayı Oluştur ve Yayınla",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        
        # Yayına hazır makaleler
        ready_articles = self.db.get_ready_to_publish_articles()
        
        if not ready_articles:
            tk.Label(self.content_area, text="Yayına hazır makale bulunamadı.",
                    font=('Arial', 12), bg='white', fg=self.colors['secondary']).pack(pady=50)
            return
        
        # Sayı bilgileri
        info_frame = tk.Frame(self.content_area, bg='white')
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(info_frame, text="Yayına Hazır Makaleler:", 
                font=('Arial', 12, 'bold'), bg='white', fg=self.colors['dark']).pack(anchor='w', pady=5)
        tk.Label(info_frame, text=f"Toplam {len(ready_articles)} makale yayına hazır.",
                font=('Arial', 10), bg='white', fg=self.colors['secondary']).pack(anchor='w')
        
        # Makale listesi
        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        columns = ("Seç", "Kod", "Başlık", "Yazar", "Durum")
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Checkbox'lar için
        selected_articles = []
        
        for art in ready_articles:
            var = tk.BooleanVar()
            selected_articles.append({"article": art, "var": var})
            
            author = art.get("authors", art.get("author", ""))
            tree.insert('', tk.END, values=(
                "☐", art["id"], art["title"][:50] + "...", author, art["status"]
            ), tags=(art["id"],))
        
        def toggle_selection(event):
            item = tree.selection()[0] if tree.selection() else None
            if item:
                art_id = tree.item(item)["values"][1]
                for sel in selected_articles:
                    if sel["article"]["id"] == art_id:
                        sel["var"].set(not sel["var"].get())
                        tree.item(item, values=(
                            "☑" if sel["var"].get() else "☐",
                            tree.item(item)["values"][1],
                            tree.item(item)["values"][2],
                            tree.item(item)["values"][3],
                            tree.item(item)["values"][4]
                        ))
                        break
        
        tree.bind("<Double-1>", toggle_selection)
        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Sayı bilgileri girişi
        issue_frame = tk.Frame(self.content_area, bg='white')
        issue_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(issue_frame, text="Sayı Bilgileri:", 
                font=('Arial', 12, 'bold'), bg='white', fg=self.colors['dark']).pack(anchor='w', pady=10)
        
        input_frame = tk.Frame(issue_frame, bg='white')
        input_frame.pack(fill=tk.X)
        
        tk.Label(input_frame, text="Cilt:", font=('Arial', 10), bg='white').grid(row=0, column=0, padx=10, pady=5, sticky='w')
        volume_var = tk.StringVar(value=str(datetime.now().year - 2010))
        volume_entry = tk.Entry(input_frame, textvariable=volume_var, width=10, font=('Arial', 10))
        volume_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(input_frame, text="Sayı:", font=('Arial', 10), bg='white').grid(row=0, column=2, padx=10, pady=5, sticky='w')
        issue_var = tk.StringVar(value="1")
        issue_entry = tk.Entry(input_frame, textvariable=issue_var, width=10, font=('Arial', 10))
        issue_entry.grid(row=0, column=3, padx=10, pady=5)
        
        tk.Label(input_frame, text="Yıl:", font=('Arial', 10), bg='white').grid(row=0, column=4, padx=10, pady=5, sticky='w')
        year_var = tk.StringVar(value=str(datetime.now().year))
        year_entry = tk.Entry(input_frame, textvariable=year_var, width=10, font=('Arial', 10))
        year_entry.grid(row=0, column=5, padx=10, pady=5)
        
        def publish_issue():
            volume = volume_var.get().strip()
            issue = issue_var.get().strip()
            year = year_var.get().strip()
            
            if not all([volume, issue, year]):
                messagebox.showerror("Hata", "Lütfen tüm sayı bilgilerini girin.")
                return
            
            # Seçili makaleleri al
            selected = [sel["article"] for sel in selected_articles if sel["var"].get()]
            if not selected:
                messagebox.showerror("Hata", "Lütfen en az bir makale seçin.")
                return
            
            # Onay al
            confirm = messagebox.askyesno("Onay", 
                                         f"Cilt {volume}, Sayı {issue}, {year} sayısını yayınlamak istediğinizden emin misiniz?\n\n"
                                         f"Seçili {len(selected)} makale yayınlanacak.")
            if not confirm:
                return
            
            # Makaleleri yayınla
            page_num = 1
            for idx, art in enumerate(selected, 1):
                pages = f"{page_num}-{page_num + 9}"  # Her makale 10 sayfa varsayımı
                page_num += 10
                
                self.db.update_article(art["id"], {
                    "status": "Yayınlandı",
                    "volume": volume,
                    "issue": issue,
                    "year": year,
                    "pages": pages
                })
            
            messagebox.showinfo("Başarılı", 
                              f"Cilt {volume}, Sayı {issue}, {year} sayısı yayınlandı!\n"
                              f"{len(selected)} makale yayınlandı.")
            self.show_publish_issue()  # Ekranı yenile
        
        tk.Button(issue_frame, text="📚 Sayıyı Yayınla", bg=self.colors['success'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=publish_issue,
                 font=('Arial', 12, 'bold'), padx=30, pady=12).pack(pady=20)
    
    def show_archive(self):
        """Arşiv görünümü"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = tk.Label(self.content_area, text="📖 Dergi Arşivi",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        
        # Yayınlanmış sayıları getir
        published_issues = self.db.get_published_issues()
        
        if not published_issues:
            tk.Label(self.content_area, text="Henüz yayınlanmış sayı bulunmamaktadır.",
                    font=('Arial', 12), bg='white', fg=self.colors['secondary']).pack(pady=50)
            return
        
        # Sayılar listesi
        issues_frame = tk.Frame(self.content_area, bg='white')
        issues_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(issues_frame, bg='white')
        scrollbar = ttk.Scrollbar(issues_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for issue in published_issues:
            # Sayı kartı
            issue_card = tk.Frame(scrollable_frame, bg='white', relief=tk.RAISED, borderwidth=2)
            issue_card.pack(fill=tk.X, pady=10, padx=10)
            
            # Sayı başlığı
            issue_header = tk.Frame(issue_card, bg=self.colors['primary'], height=50)
            issue_header.pack(fill=tk.X)
            issue_header.pack_propagate(False)
            
            issue_title = tk.Label(issue_header, 
                                  text=f"Cilt {issue['volume']}, Sayı {issue['issue']}, {issue['year']}",
                                  font=('Arial', 14, 'bold'), bg=self.colors['primary'], fg='white')
            issue_title.pack(pady=15)
            
            # Makaleler
            articles = self.db.get_articles_by_volume_issue(issue['volume'], issue['issue'], issue['year'])
            
            articles_frame = tk.Frame(issue_card, bg='white')
            articles_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
            
            if articles:
                tk.Label(articles_frame, text=f"{len(articles)} Makale", 
                        font=('Arial', 10, 'bold'), bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(0, 10))
                
                for idx, art in enumerate(articles, 1):
                    article_item = tk.Frame(articles_frame, bg=self.colors['light'], relief=tk.FLAT)
                    article_item.pack(fill=tk.X, pady=3)
                    
                    # Makale numarası ve başlık
                    title_frame = tk.Frame(article_item, bg=self.colors['light'])
                    title_frame.pack(fill=tk.X, padx=10, pady=5)
                    
                    num_label = tk.Label(title_frame, text=f"{idx}.", font=('Arial', 10, 'bold'),
                                        bg=self.colors['light'], fg=self.colors['primary'], width=3, anchor='w')
                    num_label.pack(side=tk.LEFT)
                    
                    title_label = tk.Label(title_frame, text=art["title"], font=('Arial', 10),
                                          bg=self.colors['light'], fg=self.colors['primary'], cursor='hand2',
                                          anchor='w', wraplength=600, justify='left')
                    title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
                    title_label.bind('<Enter>', lambda e, l=title_label: l.config(fg=self.colors['secondary'], font=('Arial', 10, 'underline')))
                    title_label.bind('<Leave>', lambda e, l=title_label: l.config(fg=self.colors['primary'], font=('Arial', 10)))
                    
                    # Yazar ve sayfa bilgisi
                    info_label = tk.Label(title_frame, 
                                         text=f"{art.get('authors', art.get('author', ''))} - Sayfa {art.get('pages', 'N/A')}",
                                         font=('Arial', 9), bg=self.colors['light'], fg=self.colors['secondary'])
                    info_label.pack(side=tk.RIGHT, padx=10)
            else:
                tk.Label(articles_frame, text="Bu sayıda makale bulunamadı.",
                        font=('Arial', 10), bg='white', fg=self.colors['secondary']).pack(pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_public_archive(self):
        """Genel kullanıcılar için arşiv görünümü"""
        self.clear_screen()
        self.main_container.configure(bg='white')
        
        # Üst navigasyon barı
        nav_bar = tk.Frame(self.main_container, bg='white', height=40)
        nav_bar.pack(fill=tk.X)
        nav_bar.pack_propagate(False)
        
        nav_left = tk.Frame(nav_bar, bg='white')
        nav_left.pack(side=tk.LEFT, padx=20, pady=8)
        
        nav_items = ["Ana Sayfa", "Arşiv", "Hakkında", "İletişim"]
        for item in nav_items:
            nav_link = tk.Label(nav_left, text=item, font=('Arial', 10),
                               bg='white', fg=self.colors['primary'], cursor='hand2', padx=8)
            nav_link.pack(side=tk.LEFT)
            nav_link.bind('<Enter>', lambda e, l=nav_link: l.config(fg=self.colors['secondary']))
            nav_link.bind('<Leave>', lambda e, l=nav_link: l.config(fg=self.colors['primary']))
            
            if item == "Ana Sayfa":
                nav_link.bind('<Button-1>', lambda e: self.show_home_page())
            elif item == "Arşiv":
                nav_link.bind('<Button-1>', lambda e: self.show_public_archive())
        
        nav_right = tk.Frame(nav_bar, bg='white')
        nav_right.pack(side=tk.RIGHT, padx=20, pady=8)
        
        if self.current_user:
            login_link = tk.Label(nav_right, text="Yönetim Paneli", font=('Arial', 10),
                                  bg='white', fg=self.colors['primary'], cursor='hand2')
            login_link.pack(side=tk.RIGHT)
            login_link.bind('<Button-1>', lambda e: self.show_main_dashboard())
        else:
            login_link = tk.Label(nav_right, text="Giriş Yap", font=('Arial', 10),
                                  bg='white', fg=self.colors['primary'], cursor='hand2')
            login_link.pack(side=tk.RIGHT)
            login_link.bind('<Button-1>', lambda e: self.show_login_screen())
        
        login_link.bind('<Enter>', lambda e, l=login_link: l.config(fg=self.colors['secondary']))
        login_link.bind('<Leave>', lambda e, l=login_link: l.config(fg=self.colors['primary']))
        
        # Başlık
        header_frame = tk.Frame(self.main_container, bg='white')
        header_frame.pack(fill=tk.X, pady=30)
        
        tk.Label(header_frame, text="📖 Dergi Arşivi",
                font=('Arial', 24, 'bold'), bg='white', fg=self.colors['primary']).pack()
        
        # Yayınlanmış sayıları getir
        published_issues = self.db.get_published_issues()
        
        if not published_issues:
            tk.Label(self.main_container, text="Henüz yayınlanmış sayı bulunmamaktadır.",
                    font=('Arial', 12), bg='white', fg=self.colors['secondary']).pack(pady=50)
            return
        
        # İçerik alanı
        content_frame = tk.Frame(self.main_container, bg='#f5f5f5')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(content_frame, bg='#f5f5f5')
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f5f5f5')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for issue in published_issues:
            # Sayı kartı
            issue_card = tk.Frame(scrollable_frame, bg='white', relief=tk.RAISED, borderwidth=2)
            issue_card.pack(fill=tk.X, pady=15, padx=10)
            
            # Sayı başlığı
            issue_header = tk.Frame(issue_card, bg=self.colors['primary'], height=60)
            issue_header.pack(fill=tk.X)
            issue_header.pack_propagate(False)
            
            issue_title = tk.Label(issue_header, 
                                  text=f"Cilt {issue['volume']}, Sayı {issue['issue']}, {issue['year']}",
                                  font=('Arial', 16, 'bold'), bg=self.colors['primary'], fg='white')
            issue_title.pack(pady=18)
            
            # Makaleler
            articles = self.db.get_articles_by_volume_issue(issue['volume'], issue['issue'], issue['year'])
            
            articles_frame = tk.Frame(issue_card, bg='white')
            articles_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
            
            if articles:
                tk.Label(articles_frame, text=f"{len(articles)} Makale", 
                        font=('Arial', 11, 'bold'), bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(0, 15))
                
                for idx, art in enumerate(articles, 1):
                    article_item = tk.Frame(articles_frame, bg=self.colors['light'], relief=tk.FLAT)
                    article_item.pack(fill=tk.X, pady=5)
                    
                    # Makale numarası ve başlık
                    title_frame = tk.Frame(article_item, bg=self.colors['light'])
                    title_frame.pack(fill=tk.X, padx=15, pady=8)
                    
                    num_label = tk.Label(title_frame, text=f"{idx}.", font=('Arial', 11, 'bold'),
                                        bg=self.colors['light'], fg=self.colors['primary'], width=3, anchor='w')
                    num_label.pack(side=tk.LEFT)
                    
                    title_label = tk.Label(title_frame, text=art["title"], font=('Arial', 11),
                                          bg=self.colors['light'], fg=self.colors['primary'], cursor='hand2',
                                          anchor='w', wraplength=700, justify='left')
                    title_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
                    title_label.bind('<Enter>', lambda e, l=title_label: l.config(fg=self.colors['secondary'], font=('Arial', 11, 'underline')))
                    title_label.bind('<Leave>', lambda e, l=title_label: l.config(fg=self.colors['primary'], font=('Arial', 11)))
                    
                    # Yazar ve sayfa bilgisi
                    info_frame = tk.Frame(title_frame, bg=self.colors['light'])
                    info_frame.pack(side=tk.RIGHT, padx=10)
                    
                    author_label = tk.Label(info_frame, 
                                           text=art.get('authors', art.get('author', '')),
                                           font=('Arial', 9), bg=self.colors['light'], fg=self.colors['dark_text'])
                    author_label.pack(side=tk.LEFT, padx=(0, 10))
                    
                    pages_label = tk.Label(info_frame, 
                                          text=f"Sayfa: {art.get('pages', 'N/A')}",
                                          font=('Arial', 9), bg=self.colors['light'], fg=self.colors['secondary'])
                    pages_label.pack(side=tk.LEFT)
                    
                    # PDF butonu
                    pdf_btn = tk.Label(info_frame, text="📄 PDF", font=('Arial', 9, 'bold'),
                                      bg=self.colors['light'], fg=self.colors['danger'], cursor='hand2')
                    pdf_btn.pack(side=tk.LEFT, padx=(10, 0))
                    pdf_btn.bind('<Enter>', lambda e, l=pdf_btn: l.config(fg=self.colors['danger_light']))
                    pdf_btn.bind('<Leave>', lambda e, l=pdf_btn: l.config(fg=self.colors['danger']))
            else:
                tk.Label(articles_frame, text="Bu sayıda makale bulunamadı.",
                        font=('Arial', 10), bg='white', fg=self.colors['secondary']).pack(pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_messages(self):
        """Kullanıcıya gelen mesajları göster (Admin, Alan Editörü, Hakem)"""
        if self.user_role not in ["Admin", "Alan Editörü", "Hakem"]:
            messagebox.showerror("Hata", "Bu alana erişim yetkiniz yok.")
            return
        
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = tk.Label(self.content_area, text="📧 Gelen Mesajlar",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        
        # Mesajları getir - mevcut kullanıcıya gelen mesajlar
        messages = self.db.get_messages_by_user(self.current_user)
        
        if not messages:
            tk.Label(self.content_area, text="Henüz mesaj bulunmamaktadır.",
                    font=('Arial', 12), bg='white', fg=self.colors['secondary']).pack(pady=50)
            return
        
        # Okunmamış mesaj sayısı
        unread_count = sum(1 for m in messages if not m["is_read"])
        if unread_count > 0:
            info_label = tk.Label(self.content_area, 
                                 text=f"📬 {unread_count} okunmamış mesaj",
                                 font=('Arial', 11, 'bold'), bg='white', fg=self.colors['warning'])
            info_label.pack(pady=10, padx=20, anchor='w')
        
        # Mesaj listesi
        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(list_frame, bg='white')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for msg in messages:
            # Mesaj kartı
            msg_card = tk.Frame(scrollable_frame, bg='white', relief=tk.RAISED, borderwidth=1)
            msg_card.pack(fill=tk.X, pady=8, padx=5)
            
            # Okunmamış mesajlar için farklı renk
            bg_color = self.colors['light'] if not msg["is_read"] else 'white'
            msg_card.configure(bg=bg_color)
            
            # Mesaj başlığı
            header_frame = tk.Frame(msg_card, bg=bg_color)
            header_frame.pack(fill=tk.X, padx=15, pady=10)
            
            # Gönderen bilgisi
            from_user = self.db.get_user(msg["from_user"])
            from_name = from_user.get("name", msg["from_user"]) if from_user else msg["from_user"]
            
            subject_label = tk.Label(header_frame, 
                                    text=f"{'📬 ' if not msg['is_read'] else '📭 '}{msg['subject']}",
                                    font=('Arial', 12, 'bold'), bg=bg_color, fg=self.colors['primary'])
            subject_label.pack(side=tk.LEFT)
            
            # Tarih
            date_label = tk.Label(header_frame, text=msg["created_at"],
                                 font=('Arial', 9), bg=bg_color, fg=self.colors['secondary'])
            date_label.pack(side=tk.RIGHT)
            
            # Gönderen bilgisi
            from_label = tk.Label(header_frame, text=f"Gönderen: {from_name} ({msg['from_user']})",
                                 font=('Arial', 9), bg=bg_color, fg=self.colors['dark_text'])
            from_label.pack(side=tk.LEFT, padx=(10, 0))
            
            # Mesaj içeriği
            content_frame = tk.Frame(msg_card, bg=bg_color)
            content_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
            
            message_label = tk.Label(content_frame, text=msg["message"],
                                    font=('Arial', 10), bg=bg_color, fg=self.colors['dark_text'],
                                    wraplength=900, justify='left', anchor='w')
            message_label.pack(anchor='w', fill=tk.X)
            
            # Okundu işaretle butonu
            if not msg["is_read"]:
                def mark_read(msg_id=msg["id"]):
                    self.db.mark_message_read(msg_id)
                    self.show_messages()  # Yenile
                
                read_btn = tk.Button(content_frame, text="✓ Okundu İşaretle",
                                    font=('Arial', 9), bg=self.colors['success'], fg='white',
                                    relief=tk.FLAT, cursor='hand2', command=mark_read,
                                    padx=10, pady=5)
                read_btn.pack(anchor='w', pady=(5, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_sent_messages(self):
        """Kullanıcının gönderdiği mesajları göster"""
        if self.user_role not in ["Alan Editörü", "Hakem", "Admin"]:
            messagebox.showerror("Hata", "Bu alana erişim yetkiniz yok.")
            return
        
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = tk.Label(self.content_area, text="📤 Gönderilen Mesajlar",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        
        # Gönderilen mesajları getir
        messages = self.db.get_messages_by_from_user(self.current_user)
        
        if not messages:
            tk.Label(self.content_area, text="Henüz mesaj göndermediniz.",
                    font=('Arial', 12), bg='white', fg=self.colors['secondary']).pack(pady=50)
            return
        
        # Mesaj listesi
        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(list_frame, bg='white')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for msg in messages:
            # Mesaj kartı
            msg_card = tk.Frame(scrollable_frame, bg='white', relief=tk.RAISED, borderwidth=1)
            msg_card.pack(fill=tk.X, pady=8, padx=5)
            
            # Mesaj başlığı
            header_frame = tk.Frame(msg_card, bg='white')
            header_frame.pack(fill=tk.X, padx=15, pady=10)
            
            # Alıcı bilgisi
            to_user = self.db.get_user(msg["to_user"])
            to_name = to_user.get("name", msg["to_user"]) if to_user else msg["to_user"]
            
            subject_label = tk.Label(header_frame, 
                                    text=f"📤 {msg['subject']}",
                                    font=('Arial', 12, 'bold'), bg='white', fg=self.colors['primary'])
            subject_label.pack(side=tk.LEFT)
            
            # Tarih
            date_label = tk.Label(header_frame, text=msg["created_at"],
                                 font=('Arial', 9), bg='white', fg=self.colors['secondary'])
            date_label.pack(side=tk.RIGHT)
            
            # Alıcı bilgisi
            to_label = tk.Label(header_frame, text=f"Alıcı: {to_name} ({msg['to_user']})",
                                 font=('Arial', 9), bg='white', fg=self.colors['dark_text'])
            to_label.pack(side=tk.LEFT, padx=(10, 0))
            
            # Mesaj içeriği
            content_frame = tk.Frame(msg_card, bg='white')
            content_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
            
            message_label = tk.Label(content_frame, text=msg["message"],
                                    font=('Arial', 10), bg='white', fg=self.colors['dark_text'],
                                    wraplength=900, justify='left', anchor='w')
            message_label.pack(anchor='w', fill=tk.X)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_sent_decisions(self):
        """Hakemlerin gönderdiği kararları göster"""
        if self.user_role != "Hakem":
            messagebox.showerror("Hata", "Bu alana sadece hakem erişebilir.")
            return
        
        # Mevcut görünümü kaydet
        self.current_view = 'sent_decisions'
        
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = tk.Label(self.content_area, text="📤 Gönderilen Kararlar",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        
        # Hakem kararlarını getir - reviews tablosundan direkt al (daha güvenilir)
        # Tüm makaleleri al
        all_articles = self.db.get_all_articles()
        my_decisions = []
        
        # Reviews tablosundan bu hakemin tüm kararlarını al
        for art in all_articles:
            reviews = self.db.get_reviews_by_article(art["id"])
            for review in reviews:
                if review["reviewer_username"] == self.current_user:
                    my_decisions.append({
                        "article": art,
                        "review": review,
                        "decision": review.get("decision", "")
                    })
        
        # Tarihe göre sırala (en yeni önce)
        my_decisions.sort(key=lambda x: x["review"].get("created_at", ""), reverse=True)
        
        if not my_decisions:
            tk.Label(self.content_area, text="Henüz karar göndermediniz.",
                    font=('Arial', 12), bg='white', fg=self.colors['secondary']).pack(pady=50)
            return
        
        # Karar listesi
        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(list_frame, bg='white')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for item in my_decisions:
            art = item["article"]
            review = item["review"]
            decision = item["decision"]
            
            # Karar kartı
            decision_card = tk.Frame(scrollable_frame, bg='white', relief=tk.RAISED, borderwidth=1)
            decision_card.pack(fill=tk.X, pady=8, padx=5)
            
            # Karar başlığı
            header_frame = tk.Frame(decision_card, bg='white')
            header_frame.pack(fill=tk.X, padx=15, pady=10)
            
            decision_color = self.colors['success'] if decision == "Kabul" else \
                           self.colors['danger'] if decision == "Ret" else \
                           self.colors['warning']
            
            subject_label = tk.Label(header_frame, 
                                    text=f"📋 {art['id']} - {art['title'][:50]}",
                                    font=('Arial', 12, 'bold'), bg='white', fg=self.colors['primary'])
            subject_label.pack(side=tk.LEFT)
            
            # Tarih
            date_str = review.get("created_at", "")[:19] if review.get("created_at") else "Bilinmiyor"
            date_label = tk.Label(header_frame, text=date_str,
                                 font=('Arial', 9), bg='white', fg=self.colors['secondary'])
            date_label.pack(side=tk.RIGHT)
            
            # Karar bilgisi
            decision_label = tk.Label(header_frame, text=f"Karar: {decision}",
                                 font=('Arial', 10, 'bold'), bg='white', fg=decision_color)
            decision_label.pack(side=tk.LEFT, padx=(10, 0))
            
            # Açıklama
            content_frame = tk.Frame(decision_card, bg='white')
            content_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
            
            if review.get("comment"):
                comment_label = tk.Label(content_frame, text=f"Açıklama: {review['comment']}",
                                        font=('Arial', 10), bg='white', fg=self.colors['dark_text'],
                                        wraplength=900, justify='left', anchor='w')
                comment_label.pack(anchor='w', fill=tk.X)
            
            # Dosya bilgisi
            if review.get("file_path"):
                file_label = tk.Label(content_frame, text=f"📎 Ek Dosya: {os.path.basename(review['file_path'])}",
                                     font=('Arial', 9), bg='white', fg=self.colors['secondary'])
                file_label.pack(anchor='w', pady=(5, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_contact_messages(self):
        """Admin için iletişim mesajlarını göster"""
        if self.user_role != "Admin":
            messagebox.showerror("Hata", "Sadece admin bu alana erişebilir.")
            return
        
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = tk.Label(self.content_area, text="📨 İletişim Mesajları",
                          font=('Arial', 20, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20, padx=20, anchor='w')
        
        # Mesajları getir
        messages = self.db.get_contact_messages()
        
        if not messages:
            tk.Label(self.content_area, text="Henüz iletişim mesajı bulunmamaktadır.",
                    font=('Arial', 12), bg='white', fg=self.colors['secondary']).pack(pady=50)
            return
        
        # Okunmamış mesaj sayısı
        unread_count = sum(1 for m in messages if not m["is_read"])
        if unread_count > 0:
            info_label = tk.Label(self.content_area, 
                                 text=f"📬 {unread_count} okunmamış mesaj",
                                 font=('Arial', 11, 'bold'), bg='white', fg=self.colors['warning'])
            info_label.pack(pady=10, padx=20, anchor='w')
        
        # Filtreleme butonları
        filter_frame = tk.Frame(self.content_area, bg='white')
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Mesaj listesi
        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(list_frame, bg='white')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def show_all():
            display_messages(self.db.get_contact_messages())
        
        def show_unread():
            display_messages(self.db.get_contact_messages(unread_only=True))
        
        def display_messages(msgs):
            """Mesajları göster"""
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            for msg in msgs:
                # Mesaj kartı
                msg_card = tk.Frame(scrollable_frame, bg='white', relief=tk.RAISED, borderwidth=1)
                msg_card.pack(fill=tk.X, pady=8, padx=5)
                
                # Okunmamış mesajlar için farklı renk
                bg_color = self.colors['light'] if not msg["is_read"] else 'white'
                msg_card.configure(bg=bg_color)
                
                # Mesaj başlığı
                header_frame = tk.Frame(msg_card, bg=bg_color)
                header_frame.pack(fill=tk.X, padx=15, pady=10)
                
                subject_label = tk.Label(header_frame, 
                                        text=f"{'📬 ' if not msg['is_read'] else '📭 '}{msg['subject']}",
                                        font=('Arial', 12, 'bold'), bg=bg_color, fg=self.colors['primary'])
                subject_label.pack(side=tk.LEFT)
                
                # Tarih
                date_label = tk.Label(header_frame, text=msg["created_at"],
                                     font=('Arial', 9), bg=bg_color, fg=self.colors['secondary'])
                date_label.pack(side=tk.RIGHT)
                
                # Gönderen bilgisi
                info_frame = tk.Frame(msg_card, bg=bg_color)
                info_frame.pack(fill=tk.X, padx=15, pady=(0, 5))
                
                name_label = tk.Label(info_frame, text=f"👤 {msg['name']}",
                                     font=('Arial', 10, 'bold'), bg=bg_color, fg=self.colors['dark_text'])
                name_label.pack(side=tk.LEFT, padx=(0, 15))
                
                email_label = tk.Label(info_frame, text=f"📧 {msg['email']}",
                                      font=('Arial', 10), bg=bg_color, fg=self.colors['secondary'])
                email_label.pack(side=tk.LEFT)
                
                # Mesaj içeriği
                content_frame = tk.Frame(msg_card, bg=bg_color)
                content_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
                
                message_label = tk.Label(content_frame, text=msg["message"],
                                        font=('Arial', 10), bg=bg_color, fg=self.colors['dark_text'],
                                        wraplength=900, justify='left', anchor='w')
                message_label.pack(anchor='w', fill=tk.X)
                
                # Butonlar
                button_frame = tk.Frame(content_frame, bg=bg_color)
                button_frame.pack(fill=tk.X, pady=(5, 0))
                
                # Okundu işaretle butonu
                if not msg["is_read"]:
                    def mark_read(msg_id=msg["id"]):
                        self.db.mark_contact_message_read(msg_id)
                        show_all()  # Yenile
                    
                    read_btn = tk.Button(button_frame, text="✓ Okundu İşaretle",
                                        font=('Arial', 9), bg=self.colors['success'], fg='white',
                                        relief=tk.FLAT, cursor='hand2', command=mark_read,
                                        padx=10, pady=5)
                    read_btn.pack(side=tk.LEFT, padx=(0, 5))
                
                # E-posta yanıtla butonu
                def reply_email(email=msg['email'], subject=msg['subject']):
                    import webbrowser
                    subject_encoded = subject.replace(" ", "%20").replace("Re:", "Re%3A")
                    mailto_link = f"mailto:{email}?subject=Re:%20{subject_encoded}"
                    webbrowser.open(mailto_link)
                
                reply_btn = tk.Button(button_frame, text="📧 E-posta ile Yanıtla",
                                     font=('Arial', 9), bg=self.colors['primary'], fg='white',
                                     relief=tk.FLAT, cursor='hand2', 
                                     command=lambda e=msg['email'], s=msg['subject']: reply_email(e, s),
                                     padx=10, pady=5)
                reply_btn.pack(side=tk.LEFT, padx=5)
            
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Filtreleme butonları
        tk.Button(filter_frame, text="Tümü", font=('Arial', 10),
                 bg=self.colors['primary'], fg='white', relief=tk.FLAT,
                 cursor='hand2', padx=15, pady=5, command=show_all).pack(side=tk.LEFT, padx=5)
        
        tk.Button(filter_frame, text="Okunmamışlar", font=('Arial', 10),
                 bg=self.colors['secondary'], fg='white', relief=tk.FLAT,
                 cursor='hand2', padx=15, pady=5, command=show_unread).pack(side=tk.LEFT, padx=5)
        
        # İlk yüklemede tüm mesajları göster
        display_messages(messages)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_reviewer_request_form(self):
        """Hakemlik isteği gönderme formu"""
        # Form penceresi
        request_window = tk.Toplevel(self.root)
        request_window.title("Hakemlik İsteği Gönder")
        request_window.geometry("600x700")
        request_window.configure(bg='white')
        request_window.transient(self.root)
        request_window.grab_set()
        
        # Başlık
        header = tk.Label(request_window, text="👨‍⚖️ Hakemlik İsteği",
                          font=('Arial', 18, 'bold'), bg='white', fg=self.colors['primary'])
        header.pack(pady=20)
        
        # Bilgi mesajı
        info_label = tk.Label(request_window, 
                             text="Hakemlik yapmak istiyorsanız lütfen aşağıdaki formu doldurun.\nİsteğiniz admin'e iletilecektir.",
                             font=('Arial', 10), bg='white', fg=self.colors['dark_text'],
                             justify='center', wraplength=500)
        info_label.pack(pady=10, padx=20)
        
        # Canvas ve scrollbar için container
        canvas_container = tk.Frame(request_window, bg='white')
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas ve scrollbar
        canvas = tk.Canvas(canvas_container, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form alanları
        form_frame = tk.Frame(scrollable_frame, bg='white')
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Ad Soyad
        tk.Label(form_frame, text="Ad Soyad *", font=('Arial', 10, 'bold'),
                bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(10, 5))
        name_entry = tk.Entry(form_frame, font=('Arial', 11), relief=tk.FLAT,
                             bg=self.colors['light'], bd=2, width=50)
        name_entry.pack(fill=tk.X, ipady=8)
        
        # E-posta
        tk.Label(form_frame, text="E-posta *", font=('Arial', 10, 'bold'),
                bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(15, 5))
        email_entry = tk.Entry(form_frame, font=('Arial', 11), relief=tk.FLAT,
                              bg=self.colors['light'], bd=2, width=50)
        email_entry.pack(fill=tk.X, ipady=8)
        
        # Kurum/Üniversite
        tk.Label(form_frame, text="Kurum/Üniversite *", font=('Arial', 10, 'bold'),
                bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(15, 5))
        institution_entry = tk.Entry(form_frame, font=('Arial', 11), relief=tk.FLAT,
                                    bg=self.colors['light'], bd=2, width=50)
        institution_entry.pack(fill=tk.X, ipady=8)
        
        # Uzmanlık Alanları
        tk.Label(form_frame, text="Uzmanlık Alanları *", font=('Arial', 10, 'bold'),
                bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(15, 5))
        tk.Label(form_frame, text="(Virgülle ayırarak birden fazla alan yazabilirsiniz)",
                font=('Arial', 8), bg='white', fg=self.colors['secondary']).pack(anchor='w', pady=(0, 5))
        expertise_entry = tk.Entry(form_frame, font=('Arial', 11), relief=tk.FLAT,
                                   bg=self.colors['light'], bd=2, width=50)
        expertise_entry.pack(fill=tk.X, ipady=8)
        
        # Özgeçmiş/Deneyim
        tk.Label(form_frame, text="Özgeçmiş ve Deneyim *", font=('Arial', 10, 'bold'),
                bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(15, 5))
        cv_text = scrolledtext.ScrolledText(form_frame, height=6, width=50,
                                           font=('Arial', 10), relief=tk.FLAT,
                                           bg=self.colors['light'], bd=2)
        cv_text.pack(fill=tk.BOTH, expand=True)
        
        # Ek Notlar
        tk.Label(form_frame, text="Ek Notlar (İsteğe Bağlı)", font=('Arial', 10, 'bold'),
                bg='white', fg=self.colors['dark']).pack(anchor='w', pady=(15, 5))
        notes_text = scrolledtext.ScrolledText(form_frame, height=4, width=50,
                                              font=('Arial', 10), relief=tk.FLAT,
                                              bg=self.colors['light'], bd=2)
        notes_text.pack(fill=tk.BOTH, expand=True)
        
        def submit_request():
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            institution = institution_entry.get().strip()
            expertise = expertise_entry.get().strip()
            cv = cv_text.get("1.0", tk.END).strip()
            notes = notes_text.get("1.0", tk.END).strip()
            
            # Validasyon
            if not all([name, email, institution, expertise, cv]):
                messagebox.showerror("Hata", "Lütfen zorunlu alanları doldurun (* işaretli alanlar).")
                return
            
            # E-posta format kontrolü
            if "@" not in email:
                messagebox.showerror("Hata", "Lütfen geçerli bir e-posta adresi girin.")
                return
            
            # Admin kullanıcısını bul
            admin_user = self.db.get_user("admin")
            if not admin_user:
                messagebox.showerror("Hata", "Admin kullanıcısı bulunamadı.")
                return
            
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
            
            # Admin'e mesaj gönder (article_id olmadan - genel mesaj için özel ID kullan)
            # Genel mesajlar için özel bir article_id kullanabiliriz
            general_id = "GENEL-HAKEMLIK-ISTEKLERI"
            
            self.db.add_message(
                general_id,
                email,  # Gönderen olarak e-posta kullan
                "admin",  # Admin'e gönder
                f"Hakemlik İsteği - {name}",
                message_content
            )
            
            messagebox.showinfo("Başarılı", 
                              "Hakemlik isteğiniz admin'e gönderildi.\n"
                              "İsteğiniz değerlendirildikten sonra size dönüş yapılacaktır.")
            request_window.destroy()
        
        # Gönder butonu (scrollable_frame içinde)
        button_frame = tk.Frame(form_frame, bg='white')
        button_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(button_frame, text="❌ İptal", bg=self.colors['danger'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=request_window.destroy,
                 padx=20, pady=10, font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="✅ İsteği Gönder", bg=self.colors['success'], fg='white',
                 relief=tk.FLAT, cursor='hand2', command=submit_request,
                 padx=20, pady=10, font=('Arial', 11, 'bold')).pack(side=tk.RIGHT, padx=5)
        
        # Canvas ve scrollbar'ı pack et
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel desteği (Windows ve Linux için)
        def on_mousewheel(event):
            if event.delta:
                # Windows
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            else:
                # Linux
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
        
        # Windows için
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        # Linux için
        canvas.bind_all("<Button-4>", on_mousewheel)
        canvas.bind_all("<Button-5>", on_mousewheel)
        
        # Canvas'a focus ver
        canvas.focus_set()

    def show_list_view_table(self, data, header_text):
        list_frame = tk.Frame(self.content_area, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        columns = ('Kod', 'Başlık', 'Yazar', 'Tarih', 'Durum')
        tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=180)
        for item in data:
            tree.insert('', tk.END, values=item)
        tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


if __name__ == "__main__":
    root = tk.Tk()
    app = AkademikDergiSistemi(root)
    root.mainloop()
