# 📚 Akademik Dergi Yönetim Sistemi (DYS)

Modern, kullanıcı dostu ve AI destekli akademik dergi yönetim web uygulaması. Flask tabanlı bu sistem, akademik dergilerin tüm süreçlerini dijitalleştirerek yönetmenize olanak sağlar.

## 📋 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Özellikler](#-özellikler)
- [Sistem Gereksinimleri](#-sistem-gereksinimleri)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Kullanıcı Rolleri ve Yetkileri](#-kullanıcı-rolleri-ve-yetkileri)
- [Proje Yapısı](#-proje-yapısı)
- [Teknik Detaylar](#-teknik-detaylar)
- [Yaygın Sorunlar ve Çözümleri](#-yaygın-sorunlar-ve-çözümleri)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)

---

## 🎯 Proje Hakkında

Bu proje, akademik dergilerin makale gönderim, değerlendirme, yayınlama ve yönetim süreçlerini dijitalleştiren kapsamlı bir web uygulamasıdır. Sistem, yapay zeka destekli otomatik sınıflandırma ve editör atama özellikleriyle akademik dergi yönetimini modernize eder.

### Ana Amaçlar

- ✅ Makale gönderim ve takip sürecini dijitalleştirmek
- ✅ Hakem değerlendirme sürecini kolaylaştırmak
- ✅ AI destekli otomatik editör ataması yapmak
- ✅ Kullanıcı dostu modern arayüz sunmak
- ✅ Tüm süreçleri merkezi bir platformda toplamak

---

## ✨ Özellikler

### 🔐 Kullanıcı Yönetimi
- **Çoklu Rol Sistemi**: Admin, Editör, Alan Editörü, Hakem ve Yazar rolleri
- **Rol Değiştirme**: Kullanıcılar (özellikle Admin) farklı rollere geçiş yapabilir
- **Kullanıcı Yönetimi**: Admin kullanıcı ekleme, silme, rol atama ve şifre sıfırlama yapabilir
- **Güvenli Kimlik Doğrulama**: Şifre hashleme ile güvenli giriş sistemi

### 📝 Makale Yönetimi
- **Makale Gönderimi**: Yazar makalelerini sisteme yükleyebilir
- **Otomatik Sınıflandırma**: AI destekli makale sınıflandırma ve alan editörü ataması
- **Durum Takibi**: Makalelerin durumları gerçek zamanlı takip edilir
- **Dosya Yönetimi**: PDF, DOC, DOCX, TXT formatlarında dosya yükleme desteği

### 👨‍⚖️ Hakem Değerlendirme Sistemi
- **Hakem Ataması**: Editörler makalelere hakem atayabilir
- **Değerlendirme Formu**: Hakemler detaylı değerlendirme yapabilir
- **Karar Verme**: Kabul, Red, Düzeltme gibi kararlar verilebilir
- **Dosya Yükleme**: Hakemler değerlendirme dosyalarını yükleyebilir

### 📊 İstatistikler ve Raporlama
- **Dashboard**: Her rol için özelleştirilmiş dashboard
- **İstatistikler**: Makale, kullanıcı ve süreç istatistikleri
- **Arşiv**: Yayınlanmış sayılar ve makaleler arşivlenir

### 💬 İletişim Sistemi
- **Mesajlaşma**: Kullanıcılar arası mesajlaşma
- **İletişim Formu**: Ziyaretçiler iletişim formu gönderebilir
- **Bildirimler**: Flash mesajları ile kullanıcı bilgilendirmesi

### 🌐 Kamuya Açık Sayfalar
- **Ana Sayfa**: Son sayı ve dergi bilgileri
- **Hakkında**: Dergi hakkında bilgiler
- **KEŞFET Menüsü**: 
  - Amaç ve Kapsam
  - Yazım Kuralları
  - Etik Politikası
  - Ücret Politikası
  - Editör Kurulu
  - Dizinler
- **Arşiv**: Yayınlanmış tüm sayılar
- **Hakemlik İsteği**: Hakem olmak isteyenler başvuru yapabilir

---

## 💻 Sistem Gereksinimleri

### Minimum Gereksinimler
- **Python**: 3.8 veya üzeri
- **İşletim Sistemi**: Windows, macOS, Linux
- **RAM**: En az 2GB
- **Disk Alanı**: En az 100MB boş alan

### Önerilen Gereksinimler
- **Python**: 3.10 veya üzeri
- **RAM**: 4GB veya üzeri
- **Tarayıcı**: Chrome, Firefox, Edge (son sürümler)

---

## 🚀 Kurulum

### Adım 1: Projeyi İndirin

GitHub'dan projeyi klonlayın veya ZIP olarak indirin:

```bash
git clone https://github.com/kullaniciadi/DYS_web.git
cd DYS_web
```

### Adım 2: Python Kurulumunu Kontrol Edin

Terminal/Command Prompt'ta Python sürümünüzü kontrol edin:

```bash
python --version
```

Eğer Python yüklü değilse, [python.org](https://www.python.org/downloads/) adresinden indirip kurun.

### Adım 3: Sanal Ortam Oluşturun (Önerilen)

Sanal ortam oluşturmak projeyi izole eder ve bağımlılık çakışmalarını önler:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Adım 4: Bağımlılıkları Yükleyin

Proje klasöründe `requirements.txt` dosyasındaki paketleri yükleyin:

```bash
pip install -r requirements.txt
```

Bu komut şunları yükler:
- Flask 3.0.0 (Web framework)
- Werkzeug 3.0.1 (Güvenlik ve dosya yönetimi)

### Adım 5: Uygulamayı Başlatın

```bash
python app.py
```

Başarılı bir şekilde başlatıldığında terminalde şu mesajı göreceksiniz:

```
 * Running on http://0.0.0.0:5000
```

### Adım 6: Tarayıcıda Açın

Tarayıcınızda şu adresi açın:

```
http://localhost:5000
```

veya

```
http://127.0.0.1:5000
```

---

## 📖 Kullanım

### İlk Giriş

Sistem ilk başlatıldığında otomatik olarak aşağıdaki test kullanıcıları oluşturulur:

| Rol | Kullanıcı Adı | Şifre |
|-----|---------------|-------|
| **Admin** | `admin` | `DYS.2025` |
| **Editör** | `editor1` | `pass` |
| **Alan Editörü** | `fe1` | `pass` |
| **Hakem** | `rev1` | `pass` |
| **Yazar** | `author1` | `pass` |

⚠️ **Güvenlik Uyarısı**: Production ortamında mutlaka bu şifreleri değiştirin!

### Temel İşlemler

#### 1. Giriş Yapma

1. Ana sayfada sağ üst köşedeki "Giriş Yap" butonuna tıklayın
2. Kullanıcı adı ve şifrenizi girin
3. "Giriş" butonuna tıklayın

#### 2. Makale Gönderme (Yazar)

1. Giriş yaptıktan sonra "Makale Gönder" menüsüne gidin
2. Makale bilgilerini doldurun:
   - Başlık
   - Alt başlık
   - Anahtar kelimeler
   - Tür
   - Alan
   - Türkçe ve İngilizce özet
3. Makale dosyasını seçin (PDF, DOC, DOCX, TXT)
4. "Gönder" butonuna tıklayın

#### 3. Makale Değerlendirme (Hakem)

1. "Atanan Değerlendirmeler" menüsüne gidin
2. Değerlendireceğiniz makaleyi seçin
3. Değerlendirme formunu doldurun
4. Kararınızı verin (Kabul, Red, Düzeltme)
5. İsteğe bağlı olarak değerlendirme dosyası yükleyin
6. "Değerlendirmeyi Gönder" butonuna tıklayın

#### 4. Sayı Oluşturma (Editör)

1. "Sayı Oluştur ve Yayınla" menüsüne gidin
2. Yıl, Cilt ve Sayı numaralarını girin (Cilt numarası yıl değiştiğinde otomatik hesaplanır)
3. Yayınlanacak makaleleri seçin
4. "Sayıyı Oluştur ve Yayınla" butonuna tıklayın

---

## 👥 Kullanıcı Rolleri ve Yetkileri

### 🔴 Admin

**Yetkiler:**
- ✅ Tüm kullanıcıları yönetebilir (ekleme, silme, rol atama)
- ✅ Tüm makalelere erişebilir
- ✅ Tüm rollere geçiş yapabilir
- ✅ Sistem ayarlarını yönetebilir
- ✅ İstatistikleri görüntüleyebilir
- ✅ Mesajları yönetebilir

**Menüler:**
- Ana Sayfa
- Kullanıcı Yönetimi
- Gelen Mesajlar
- İletişim Mesajları
- Gönderilenler
- Değerlendirmede
- İstatistikler
- Ayarlar

### 🟡 Editör

**Yetkiler:**
- ✅ Makaleleri gözden geçirebilir
- ✅ Hakem atayabilir
- ✅ Makale kararları verebilir
- ✅ Sayı oluşturup yayınlayabilir
- ✅ Arşivi yönetebilir
- ✅ Hakemleri yönetebilir

**Menüler:**
- Ana Sayfa
- Gönderilenler
- Onay Bekleyenler
- Değerlendirmede
- Kabul Edilenler
- Reddedilenler
- Sayı Oluştur ve Yayınla
- Arşiv
- Hakemler
- İstatistikler
- Ayarlar

### 🟢 Alan Editörü

**Yetkiler:**
- ✅ Kendi alanındaki makaleleri gözden geçirebilir
- ✅ Alan editörü önerisi yapabilir
- ✅ Makale kararları verebilir
- ✅ Hakem atayabilir

**Menüler:**
- Ana Sayfa
- Atanan Makaleler
- Değerlendirmeler
- Hakem Kararları
- Ayarlar

### 🔵 Hakem

**Yetkiler:**
- ✅ Atanan makaleleri değerlendirebilir
- ✅ Değerlendirme kararı verebilir
- ✅ Değerlendirme dosyası yükleyebilir
- ✅ Gönderilen kararları görüntüleyebilir

**Menüler:**
- Ana Sayfa
- Atanan Değerlendirmeler
- Gönderilen Kararlar
- Ayarlar

### 🟣 Yazar

**Yetkiler:**
- ✅ Makale gönderebilir
- ✅ Kendi makalelerini görüntüleyebilir
- ✅ Makale durumunu takip edebilir
- ✅ Yayınlarını görüntüleyebilir

**Menüler:**
- Ana Sayfa
- Yeni Makale Gönder
- Makalelerim
- Durum Takibi
- Yayınlarım
- Ayarlar

---

## 📁 Proje Yapısı

```
DYS_web/
│
├── app.py                          # Ana Flask uygulaması
├── requirements.txt                 # Python bağımlılıkları
├── README.md                       # Bu dosya
├── dergi_sistemi.db                # SQLite veritabanı (otomatik oluşur)
│
├── templates/                      # HTML şablonları
│   ├── base.html                   # Temel şablon
│   ├── dashboard_base.html         # Dashboard temel şablonu
│   ├── home.html                   # Ana sayfa
│   ├── login.html                  # Giriş sayfası
│   ├── register.html               # Kayıt sayfası
│   ├── dashboard.html              # Dashboard
│   ├── new_submission.html         # Makale gönderme
│   ├── my_articles.html            # Makalelerim
│   ├── submissions.html             # Gönderilenler (Editör)
│   ├── review_articles.html        # Değerlendirme
│   ├── publish_issue.html          # Sayı oluşturma
│   ├── archive.html                # Arşiv
│   ├── user_management.html        # Kullanıcı yönetimi
│   ├── messages.html               # Mesajlar
│   ├── statistics.html             # İstatistikler
│   ├── about.html                  # Hakkında
│   ├── contact.html                # İletişim
│   └── discover_*.html             # KEŞFET menü sayfaları
│
├── static/                         # Statik dosyalar
│   ├── css/
│   │   └── style.css               # Özel CSS stilleri
│   └── js/                         # JavaScript dosyaları
│
├── uploads/                        # Yüklenen dosyalar
│   ├── reviews/                    # Hakem değerlendirmeleri
│   └── recommendations/             # Alan editörü önerileri
│
└── Dergi_Yonetim_Sistemi/          # Orijinal modüller
    ├── database.py                 # Veritabanı işlemleri
    ├── ai_classifier.py            # AI sınıflandırıcı
    └── dergiYonetimSistemi.py      # Orijinal masaüstü uygulaması
```

---

## 🔧 Teknik Detaylar

### Kullanılan Teknolojiler

- **Backend Framework**: Flask 3.0.0
- **Veritabanı**: SQLite3
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI/ML**: Özel sınıflandırma algoritması
- **Güvenlik**: Werkzeug (şifre hashleme, dosya güvenliği)

### Veritabanı Yapısı

Sistem aşağıdaki tabloları kullanır:

1. **users**: Kullanıcı bilgileri ve rolleri
2. **articles**: Makale bilgileri ve durumları
3. **reviews**: Hakem değerlendirmeleri
4. **messages**: Kullanıcı mesajları
5. **issues**: İletişim formu mesajları

### API Endpoints

- `/api/max-volume/<year>`: Yıl için önerilen cilt numarasını döndürür

### Güvenlik Özellikleri

- ✅ Şifre hashleme (Werkzeug)
- ✅ Session yönetimi
- ✅ Dosya yükleme güvenliği (secure_filename)
- ✅ Role-based access control (RBAC)
- ✅ SQL injection koruması (parametreli sorgular)

---

## ❓ Yaygın Sorunlar ve Çözümleri

### Sorun 1: "ModuleNotFoundError: No module named 'flask'"

**Çözüm:**
```bash
pip install -r requirements.txt
```

### Sorun 2: "Port 5000 already in use"

**Çözüm:**
- Çalışan uygulamayı durdurun (Ctrl+C)
- Veya farklı bir port kullanın:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Sorun 3: "Veritabanı bulunamadı"

**Çözüm:**
- Uygulama ilk çalıştırıldığında otomatik oluşturulur
- `dergi_sistemi.db` dosyasının proje klasöründe olduğundan emin olun

### Sorun 4: "Dosya yüklenemedi"

**Çözüm:**
- Dosya boyutunun 16MB'dan küçük olduğundan emin olun
- Dosya formatının desteklenen formatlardan biri olduğunu kontrol edin (PDF, DOC, DOCX, TXT)
- `uploads` klasörünün yazma iznine sahip olduğundan emin olun

### Sorun 5: "Sayfa bulunamadı (404)"

**Çözüm:**
- Giriş yapmış olduğunuzdan emin olun
- Rolünüzün o sayfaya erişim yetkisi olduğunu kontrol edin
- URL'nin doğru olduğundan emin olun

### Sorun 6: "Cilt numarası yanlış görünüyor"

**Çözüm:**
- Flask uygulamasını yeniden başlatın
- Tarayıcı cache'ini temizleyin (Ctrl+F5)
- Veritabanında kayıtların doğru olduğunu kontrol edin

---

## 🤝 Katkıda Bulunma

Bu projeye katkıda bulunmak istiyorsanız:

1. Projeyi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

### Katkıda Bulunurken Dikkat Edilmesi Gerekenler

- ✅ Kod standartlarına uyun (PEP 8)
- ✅ Yorum satırları ekleyin
- ✅ Test edin
- ✅ README'yi güncelleyin
- ✅ Commit mesajlarını açıklayıcı yazın

---

## 📝 Geliştirme Notları

### Yeni Özellik Ekleme

1. `app.py` dosyasına yeni route ekleyin
2. Gerekli template dosyasını `templates/` klasörüne ekleyin
3. Veritabanı değişikliği gerekiyorsa `database.py` dosyasını güncelleyin
4. CSS stilleri için `static/css/style.css` dosyasını güncelleyin

### Veritabanı Migration

Veritabanı şeması değiştiğinde:
1. `database.py` dosyasındaki `init_database()` metodunu güncelleyin
2. Migration kodları ekleyin (ALTER TABLE vb.)

### Production Deployment

Production ortamında:
1. `app.py` dosyasındaki `secret_key` değerini değiştirin
2. `debug=False` yapın
3. Güvenli bir web sunucusu kullanın (Gunicorn, uWSGI)
4. HTTPS kullanın
5. Veritabanı yedekleme stratejisi oluşturun

---

## 📄 Lisans

Bu proje açık kaynaklıdır ve eğitim amaçlı kullanılabilir.

---


## 📚 Ek Kaynaklar

- [Flask Dokümantasyonu](https://flask.palletsprojects.com/)
- [Bootstrap 5 Dokümantasyonu](https://getbootstrap.com/docs/5.0/)
- [SQLite Dokümantasyonu](https://www.sqlite.org/docs.html)

---

**Not**: Bu README dosyası projenin genel kullanımını açıklamak için hazırlanmıştır. Daha detaylı bilgi için kod içindeki yorum satırlarına bakabilirsiniz.
