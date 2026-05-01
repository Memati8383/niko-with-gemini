# 🔌 API Dokümantasyonu

Niko AI Backend API referansı.

## 🌐 Base URL

```
Yerel: http://localhost:8000
Tunnel: https://your-tunnel-url.trycloudflare.com
```

## 🔐 Kimlik Doğrulama

API, JWT (JSON Web Token) tabanlı kimlik doğrulama kullanır.

### Token Alma

**Endpoint:** `POST /token`

**Request Body:**

```json
{
  "username": "kullanici_adi",
  "password": "sifre"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Token Kullanımı

Tüm korumalı endpoint'lerde header'a ekleyin:

```
Authorization: Bearer <token>
```

## 📡 Endpoints

### 1. Kullanıcı İşlemleri

#### Kayıt Ol

```http
POST /signup
Content-Type: application/json

{
  "username": "yeni_kullanici",
  "password": "guvenli_sifre",
  "email": "email@example.com"
}
```

**Response:**

```json
{
  "message": "Kullanıcı başarıyla oluşturuldu",
  "user_id": "uuid-here"
}
```

#### Giriş Yap

```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=kullanici&password=sifre
```

#### Profil Bilgisi

```http
GET /profile
Authorization: Bearer <token>
```

**Response:**

```json
{
  "user_id": "uuid",
  "username": "kullanici",
  "email": "email@example.com",
  "created_at": "2026-02-07T10:00:00",
  "profile_picture": "base64_image_data"
}
```

#### Profil Güncelle

```http
PUT /profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "yeni@example.com",
  "profile_picture": "base64_image_data"
}
```

### 2. Chat İşlemleri

#### Mesaj Gönder

```http
POST /chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Merhaba Niko",
  "model": "RefinedNeuro/RN_TR_R2:latest",
  "personality": "normal",
  "web_search": false
}
```

**Response (Stream):**

```json
data: {"type": "thought", "content": "Kullanıcı selamlaşıyor..."}
data: {"type": "response", "content": "Merhaba! Nasıl yardımcı olabilirim?"}
data: {"type": "done"}
```

#### Sohbet Geçmişi

```http
GET /history?limit=50&offset=0
Authorization: Bearer <token>
```

**Response:**

```json
{
  "total": 100,
  "messages": [
    {
      "id": "msg-uuid",
      "user_message": "Merhaba",
      "ai_response": "Merhaba! Nasıl yardımcı olabilirim?",
      "timestamp": "2026-02-07T10:00:00",
      "model": "RefinedNeuro/RN_TR_R2:latest"
    }
  ]
}
```

#### Geçmişi Temizle

```http
DELETE /history
Authorization: Bearer <token>
```

#### Geçmişi Dışa Aktar

```http
GET /history/export?format=json
Authorization: Bearer <token>
```

### 3. Model İşlemleri

#### Mevcut Modelleri Listele

```http
GET /models
Authorization: Bearer <token>
```

**Response:**

```json
{
  "models": [
    {
      "name": "RefinedNeuro/RN_TR_R2:latest",
      "size": "7B",
      "modified_at": "2026-02-07T10:00:00"
    }
  ]
}
```

#### Model Bilgisi

```http
GET /models/{model_name}
Authorization: Bearer <token>
```

### 4. Sistem İşlemleri

#### Sağlık Kontrolü

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "ollama": "connected",
  "version": "1.0.0"
}
```

#### Versiyon Bilgisi

```http
GET /version
```

**Response:**

```json
{
  "version": "1.0.0",
  "build_date": "2026-02-07",
  "latest_version": "1.0.0",
  "update_available": false
}
```

### 5. Admin İşlemleri

#### Tüm Kullanıcıları Listele

```http
GET /admin/users
Authorization: Bearer <admin_token>
```

**Response:**

```json
{
  "users": [
    {
      "user_id": "uuid",
      "username": "kullanici",
      "role": "user",
      "created_at": "2026-02-07T10:00:00"
    }
  ]
}
```

#### Kullanıcı Sil

```http
DELETE /admin/users/{user_id}
Authorization: Bearer <admin_token>
```

#### Sistem İstatistikleri

```http
GET /admin/stats
Authorization: Bearer <admin_token>
```

**Response:**

```json
{
  "total_users": 100,
  "total_messages": 5000,
  "active_users_today": 25,
  "disk_usage": "2.5 GB"
}
```

## 🔊 Text-to-Speech

#### Metni Sese Çevir

```http
POST /tts
Authorization: Bearer <token>
Content-Type: application/json

{
  "text": "Merhaba dünya",
  "voice": "tr-TR-AhmetNeural",
  "rate": "+0%",
  "pitch": "+0Hz"
}
```

**Response:** Audio file (audio/mpeg)

## 🔍 Web Arama

#### Arama Yap

```http
POST /search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "Python nedir",
  "max_results": 5
}
```

**Response:**

```json
{
  "results": [
    {
      "title": "Python Programlama Dili",
      "url": "https://example.com",
      "snippet": "Python, yüksek seviyeli..."
    }
  ]
}
```

## ⚠️ Hata Kodları

| Kod | Açıklama              |
| --- | --------------------- |
| 200 | Başarılı              |
| 201 | Oluşturuldu           |
| 400 | Geçersiz istek        |
| 401 | Yetkisiz              |
| 403 | Yasak                 |
| 404 | Bulunamadı            |
| 429 | Çok fazla istek       |
| 500 | Sunucu hatası         |
| 503 | Servis kullanılamıyor |

## 🔒 Rate Limiting

- Genel: 100 istek/dakika
- Chat: 20 istek/dakika
- TTS: 10 istek/dakika

## 📝 Örnek Kullanım

### Python

```python
import requests

# Giriş yap
response = requests.post(
    "http://localhost:8000/token",
    data={"username": "user", "password": "pass"}
)
token = response.json()["access_token"]

# Mesaj gönder
response = requests.post(
    "http://localhost:8000/chat",
    headers={"Authorization": f"Bearer {token}"},
    json={"message": "Merhaba", "model": "RefinedNeuro/RN_TR_R2:latest"}
)
```

### JavaScript

```javascript
// Giriş yap
const loginResponse = await fetch("http://localhost:8000/token", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: "username=user&password=pass",
});
const { access_token } = await loginResponse.json();

// Mesaj gönder
const chatResponse = await fetch("http://localhost:8000/chat", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${access_token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    message: "Merhaba",
    model: "RefinedNeuro/RN_TR_R2:latest",
  }),
});
```

### cURL

```bash
# Giriş yap
TOKEN=$(curl -X POST "http://localhost:8000/token" \
  -d "username=user&password=pass" | jq -r '.access_token')

# Mesaj gönder
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Merhaba","model":"RefinedNeuro/RN_TR_R2:latest"}'
```

## 🔄 WebSocket (Gelecek Sürüm)

Gerçek zamanlı chat için WebSocket desteği planlanıyor.

---

Daha fazla bilgi için [GitHub Wiki](https://github.com/Memati8383/niko-with-gemini/wiki) sayfasını ziyaret edin.```
