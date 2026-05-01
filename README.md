# 🤖 Niko AI Ecosystem (Cloud Edition)

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.0-orange.svg)
![Deployment](https://img.shields.io/badge/deployment-Vercel-black.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Google Gemini API ile güçlendirilmiş, Vercel uyumlu, Türkçe optimize edilmiş yapay zeka asistanı**

[🚀 Vercel'e Dağıt](#-vercel-dağıtımı) • [📖 Dokümantasyon](docs/) • [🐛 Hata Bildir](https://github.com/Memati8383/Niko-AI/issues)

</div>

---

## 🌐 Güncel API Adresi: (https://niko-with-gemini.vercel.app)

---

## 📝 Hakkında

Niko AI, tamamen bulut tabanlı ve serverless (sunucusuz) mimariye geçiş yapmış, gelişmiş Türkçe sesli komut desteği sunan bir kişisel yapay zeka asistanıdır. Google Gemini API (`google-genai`) altyapısı sayesinde yerel donanım bağımlılığı olmadan, Vercel gibi platformlarda saniyeler içinde yayına alınabilir.

Proje tamamen **Türkçe** olarak yerelleştirilmiştir ve modern bir "birader" kişiliğine sahiptir.

## 🚀 Temel Özellikler

### 🤖 Yapay Zeka & Dil Yetenekleri

- **Google Gemini Entegrasyonu:** `google-genai` (v2) SDK'sı ile Gemini 1.5 Flash, Pro ve 2.0 modellerine erişim.
- **Düşünce Akışı (Thought Process):** AI'nın yanıt üretme sürecini gerçek zamanlı izleme.
- **Kişilik Modları:** Samimi, kısa ve öz konuşan "delikanlı" karakteri (Niko).
- **Gerçek Zamanlı Web Arama:** DuckDuckGo entegrasyonu ile güncel dünya bilgilerine erişim.
- **Multimodal Destek:** Resim analizi ve görsel anlama yeteneği.

### 🔐 Güvenlik & Bulut Uyumluluğu

- **Serverless Ready:** Vercel ve Netlify üzerinde sorunsuz çalışma.
- **Stateless Mimari:** `/tmp` dizini ve çevresel değişkenler üzerinden akıllı veri yönetimi.
- **Unified Auth System:** JWT tabanlı güvenli kimlik doğrulama.

### 💻 Web Arayüzü

- **Avant-Garde UI:** Glassmorphism ve premium mikro-etkileşimlerle donatılmış modern sohbet ekranı.
- **Responsive Tasarım:** Mobil ve masaüstü tarayıcılarla tam uyum.

## 📁 Proje Yapısı

```text
Niko-AI/
├── api/
│   └── index.py            # 🚀 Vercel Giriş Noktası (Serverless Function)
├── main.py                 # Ana FastAPI Backend uygulaması (Yerel ve Bulut uyumlu)
├── vercel.json             # Vercel dağıtım konfigürasyonu
├── requirements.txt        # Python bağımlılıkları (google-genai dahil)
├── prompts.py              # AI Sistem Promptları ve Niko Kişiliği
├── static/                 # Web Frontend (HTML, CSS, JS)
└── Niko Mobile App/        # Android Native (Java) kaynak kodları
```

## 🛠️ Kurulum ve Çalıştırma

### 1. Vercel Dağıtımı (Önerilen)

Projeyi buluta taşımak için:

1. Bu depoyu fork edin.
2. Vercel üzerinde yeni bir proje oluşturun ve deponuzu bağlayın.
3. Aşağıdaki **Environment Variables** (Çevresel Değişkenler) bilgilerini ekleyin:
   - `GEMINI_API_KEY`: Google AI Studio'dan aldığınız API anahtarı. Birden fazla anahtar kullanmak isterseniz virgülle ayırarak yazabilirsiniz (Örn: `key1,key2,key3`). Kota dolduğunda otomatik olarak bir sonraki anahtara geçilecektir.
   - `JWT_SECRET`: Rastgele bir güvenli metin (token imzalama için).
   - `RESEND_API_KEY`: (Opsiyonel) E-posta doğrulaması için.
   - `DEFAULT_MODEL`: `gemini-1.5-flash`

### 2. Yerel Kurulum

```bash
# Projeyi indirin
git clone https://github.com/Memati8383/niko-with-gemini.git
cd Niko-AI

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# .env dosyasını oluşturun ve API anahtarınızı ekleyin
echo GEMINI_API_KEY=your_api_key_here > .env

# Uygulamayı başlatın
python main.py
```

---

## 🧑‍💻 Geliştirici Notları

- **Veri Kalıcılığı:** Vercel'in serverless yapısı gereği `/tmp` dizinine yazılan veriler (sohbet geçmişi vb.) geçicidir. Üretim ortamında kalıcı veri için bir veritabanı (MongoDB, PostgreSQL) kullanılması önerilir.
- **Hızlı Commit:** Kod değişikliklerini hızlıca GitHub'a göndermek için `hizli_commit.bat` aracını kullanabilirsiniz.

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

---

<div align="center">

**Niko AI - Geleceğin Asistanı, Şimdi Bulutta** 🚀

Made with ❤️ in Turkey 🇹🇷

[⬆ Başa Dön](#-niko-ai-ecosystem-cloud-edition)

</div>
