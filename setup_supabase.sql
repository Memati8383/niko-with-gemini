-- ============================================================================
-- Niko AI - Supabase Veritabanı Şeması
-- Bu SQL dosyasını Supabase Dashboard > SQL Editor'de çalıştırın
-- ============================================================================

-- 1. Kullanıcılar Tablosu
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    plain_password TEXT,
    email TEXT UNIQUE,
    full_name TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    profile_image TEXT,
    deleted_at TIMESTAMPTZ
);

-- 2. Sohbet Oturumları Tablosu
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    username TEXT NOT NULL,
    title TEXT DEFAULT 'Yeni Sohbet',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_session_user FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 3. Sohbet Mesajları Tablosu
CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'bot')),
    content TEXT NOT NULL,
    thought TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_message_session FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
);

-- 4. E-posta Doğrulama Kodları Tablosu (Opsiyonel - bellekte de tutulabilir)
CREATE TABLE IF NOT EXISTS email_verifications (
    email TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    username TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    attempts INTEGER DEFAULT 0,
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ
);

-- ============================================================================
-- İndeksler (Performans İyileştirmeleri)
-- ============================================================================

-- Kullanıcı e-posta araması için
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- Kullanıcı adına göre oturum araması için
CREATE INDEX IF NOT EXISTS idx_sessions_username ON chat_sessions (username);

-- Oturum tarihine göre sıralama için
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON chat_sessions (created_at DESC);

-- Oturum ID'sine göre mesaj araması için
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON chat_messages (session_id);

-- Mesaj sıralama için
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON chat_messages (created_at);

-- Süresi dolmuş doğrulama kodlarını temizlemek için
CREATE INDEX IF NOT EXISTS idx_email_verifications_expires ON email_verifications (expires_at);

-- ============================================================================
-- Row Level Security (RLS) Politikaları
-- Supabase'de service_role key kullandığımız için RLS'i devre dışı bırakıyoruz
-- Veriler sadece backend üzerinden erişilebilir
-- ============================================================================

ALTER TABLE users DISABLE ROW LEVEL SECURITY;

ALTER TABLE chat_sessions DISABLE ROW LEVEL SECURITY;

ALTER TABLE chat_messages DISABLE ROW LEVEL SECURITY;

ALTER TABLE email_verifications DISABLE ROW LEVEL SECURITY;

-- ============================================================================
-- Mevcut Kullanıcı Verilerini Aktarma (Opsiyonel)
-- users.json dosyasındaki mevcut kullanıcıları eklemek için bu INSERT'leri
-- kullanabilirsiniz. Şifreleri ve tarihleri mevcut verilerinizden alın.
-- ============================================================================

-- Örnek: Admin kullanıcısını ekle
-- INSERT INTO users (username, password, plain_password, email, full_name, is_admin, created_at)
-- VALUES ('admin', '$2b$12$VB9d...', NULL, 'admin@niko.ai', 'Emre Göksu', true, '2026-01-11T06:13:26.725959')
-- ON CONFLICT (username) DO NOTHING;