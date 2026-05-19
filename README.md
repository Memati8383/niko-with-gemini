# 🤖 Niko AI Ecosystem (Supabase Cloud Edition)

<div align="center">

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.0-orange.svg)
![Database](https://img.shields.io/badge/database-Supabase%20PostgreSQL-3ECF8E.svg)
![Deployment](https://img.shields.io/badge/deployment-Vercel-black.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Google Gemini API ile güçlendirilmiş, Vercel uyumlu, Supabase PostgreSQL veri tabanlı ve Türkçe optimize edilmiş yapay zeka asistanı**

[🚀 Vercel'e Dağıt](#-vercel-dağıtımı) • [📖 Dokümantasyon](docs/) • [🐛 Hata Bildir](https://github.com/Memati8383/Niko-AI/issues)

</div>

---

## 🌐 Güncel API Adresi: (https://niko-with-gemini.vercel.app)

---

## 📝 Hakkında

Niko AI, tamamen bulut tabanlı ve serverless (sunucusuz) mimariye geçiş yapmış, gelişmiş Türkçe sesli komut desteği sunan bir kişisel yapay zeka asistanıdır. Google Gemini API (`google-genai`) altyapısı sayesinde yerel donanım bağımlılığı olmadan, Vercel gibi serverless platformlarda saniyeler içinde yayına alınabilir.

Sistem, **Supabase PostgreSQL** veritabanı entegrasyonu sayesinde Vercel serverless konteynerlarının yaşam döngülerinden bağımsız olarak tüm kullanıcı verilerini, e-posta doğrulamalarını ve sohbet geçmişlerini kalıcı ve güvenli bir şekilde saklar.

Proje tamamen **Türkçe** olarak yerelleştirilmiştir ve modern bir "birader" kişiliğine sahiptir.

---

## 🚀 Temel Özellikler

### 🤖 Yapay Zeka & Dil Yetenekleri

- **Google Gemini Entegrasyonu:** `google-genai` (v2) SDK'sı ile Gemini 1.5 Flash, Pro ve 2.0 modellerine erişim.
- **Düşünce Akışı (Thought Process):** Yapay zekanın yanıt üretme aşamasındaki akıl yürütme sürecini gerçek zamanlı izleme.
- **Kişilik Modları:** Samimi, kısa ve öz konuşan "delikanlı" karakteri (Niko).
- **Gerçek Zamanlı Web Arama:** DuckDuckGo entegrasyonu ile anlık dünya bilgilerine erişim.
- **Multimodal Destek:** Resim analizi ve görsel anlama yeteneği.

### 🔐 Güvenlik & Kalıcı Bulut Uyumluluğu

- **Supabase PostgreSQL Kalıcılığı:** `/tmp` ve bellek içi (in-memory) değişken bağımlılıkları tamamen kaldırılarak, tüm veri tabakası canlı bir SQL veritabanına taşınmıştır.
- **Güvenli Kimlik Doğrulama:** JWT (JSON Web Token) tabanlı güvenli kimlik doğrulama sistemi.
- **Doğrulama Güvenliği:** Vercel serverless ortamlarında sıfırlanmayan, tamamen veritabanı destekli, brute force korumalı e-posta doğrulama sistemi (`EmailVerificationDB`).

### 💻 Web Arayüzü

- **Avant-Garde UI:** Glassmorphism tasarımı ve premium mikro-etkileşimlerle donatılmış modern sohbet ekranı.
- **Responsive Tasarım:** Mobil ve masaüstü tüm cihazlarla %100 uyumlu arayüz.

---

## 📁 Proje Yapısı

```text
Niko-AI/
├── api/
│   └── index.py            # 🚀 Vercel Giriş Noktası (Serverless Function Köprüsü)
├── database.py             # 🗄️ Supabase PostgreSQL Veritabanı Katmanı (UserDB, ChatDB, EmailVerificationDB)
├── email_verification.py   # 🔐 Doğrulama E-postaları ve Kod Yönetim Servisi
├── setup_supabase.sql      # 📜 SQL Şema Oluşturma Betiği (Tablolar, İndeksler ve Cascade Kuralları)
├── main.py                 # Ana FastAPI Backend Uygulaması
├── vercel.json             # Vercel dağıtım konfigürasyonu
├── requirements.txt        # Python bağımlılıkları (Supabase & Google GenAI dahil)
├── prompts.py              # AI Sistem Promptları ve Niko Kişiliği
├── static/                 # Web Frontend (HTML, CSS, JS)
└── Niko Mobile App/        # Android Native (Java) kaynak kodları
```

---

## 🛠️ Kurulum ve Dağıtım

### 1. Vercel Dağıtımı (Önerilen)

Projeyi serverless bulut mimarisinde kalıcı olarak çalıştırmak için:

1. Bu depoyu fork edin.
2. [Supabase](https://supabase.com) üzerinde yeni bir PostgreSQL projesi oluşturun.
3. Supabase Dashboard → **SQL Editor** bölümüne gidip `setup_supabase.sql` dosyasının içeriğini yapıştırarak **Run** butonuna basın.
4. Vercel üzerinde yeni bir proje oluşturun ve deponuzu bağlayın.
5. Vercel Dashboard → **Environment Variables** bölümüne aşağıdaki değişkenleri ekleyin:

| Değişken Adı           | Açıklama                                                                                                     |
| ---------------------- | ------------------------------------------------------------------------------------------------------------ |
| `GEMINI_API_KEY`       | Google AI Studio API anahtarı. Birden fazla anahtarı virgülle ayırarak yazabilirsiniz (Kota aşımı koruması). |
| `SUPABASE_URL`         | Supabase projenizin API URL adresi.                                                                          |
| `SUPABASE_SERVICE_KEY` | Supabase projenizin güvenli `service_role` API anahtarı.                                                     |
| `JWT_SECRET`           | Token imzalamak için rastgele üretilmiş güvenli bir metin.                                                   |
| `RESEND_API_KEY`       | (Opsiyonel) Resend API kullanarak e-posta doğrulaması göndermek için gerekli anahtar.                        |
| `DEFAULT_MODEL`        | Asistanın varsayılan kullanacağı model (Örn: `gemini-2.0-flash-exp`).                                        |

---

### 2. Yerel Kurulum ve Çalıştırma

Yerel makinenizde test etmek ve geliştirmek için:

```bash
# 1. Projeyi indirin
git clone https://github.com/Memati8383/niko-with-gemini.git
cd niko-with-gemini

# 2. Python sanal ortamını oluşturun ve etkinleştirin
python -m venv venv
venv\Scripts\activate  # Windows için

# 3. Bağımlılıkları yükleyin
python -m pip install -r requirements.txt

# 4. .env dosyanızı oluşturun ve Supabase ile Gemini anahtarlarınızı ekleyin
# Örnek içerik:
# GEMINI_API_KEY=AIzaSy...
# SUPABASE_URL=https://xxxxxxxxxxx.supabase.co
# SUPABASE_SERVICE_KEY=eyJhbGci...
# JWT_SECRET=random_secret_string

# 5. Mevcut JSON verilerinizi Supabase'e taşımak isterseniz (Opsiyonel):
python -c "from database import migrate_json_to_supabase; migrate_json_to_supabase()"

# 6. Uygulamayı yerelde başlatın (Klasik yöntem)
python main.py

# VEYA daha kolay bir yönetim ve tünel kontrolü için:
sistemi_baslat.bat
```

Yerel sunucu başladıktan sonra `http://localhost:8001` adresi üzerinden API ve Web arayüzüne erişebilirsiniz.

---

## 🧑‍💻 Veri Kalıcılığı ve Güvenlik Notları

- **Stateless Vercel Uyumlu:** Artık diskte hiçbir yerel `.json` dosyası yazılmaz veya okunmaz. Tüm kullanıcı oluşturma, sohbet oturumları, mesaj geçmişleri ve e-posta doğrulama durumları anında Supabase'e yansıtılır.
- **SQL Cascade ve İndeksler:** Tüm ilişkili tablolar `CASCADE` kuralları ile silme ve güncellemeyi destekler. Örneğin bir kullanıcı silindiğinde, ona ait tüm sohbet oturumları ve mesajlar Supabase tarafından otomatik olarak temizlenir.

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---

<div align="center">

**Niko AI - Geleceğin Kalıcı Bulut Asistanı** 🚀

Made with ❤️ in Turkey 🇹🇷

[⬆ Başa Dön](#-niko-ai-ecosystem-supabase-cloud-edition)

</div>
