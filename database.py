"""
Niko AI - Supabase Veritabanı Katmanı
Tüm veri erişim işlemlerini yöneten merkezi modül.

Vercel'in read-only dosya sistemi sorunu nedeniyle JSON dosyaları yerine
Supabase (PostgreSQL) kullanılmaktadır.
"""

import os
import logging
from typing import Optional, List, Dict
from datetime import datetime, timezone
from supabase import create_client, Client

logger = logging.getLogger("NikoAI")

# ============================================================================
# Supabase İstemcisi (Singleton)
# ============================================================================

_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """
    Supabase istemcisini singleton olarak döndürür.
    .env dosyasından SUPABASE_URL ve SUPABASE_SERVICE_KEY değerlerini okur.
    
    Returns:
        Client: Supabase istemci örneği
        
    Raises:
        ValueError: Supabase yapılandırması eksikse
    """
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not url or not key:
            raise ValueError(
                "SUPABASE_URL ve SUPABASE_SERVICE_KEY çevresel değişkenleri gereklidir. "
                "Lütfen .env dosyanızı kontrol edin."
            )
        
        _supabase_client = create_client(url, key)
        logger.info("✅ Supabase bağlantısı kuruldu")
    
    return _supabase_client


# ============================================================================
# Kullanıcı Veritabanı İşlemleri
# ============================================================================

class UserDB:
    """
    Kullanıcı CRUD işlemleri için veritabanı katmanı.
    Eski JSON dosya tabanlı sistemin yerine geçer.
    """
    
    @staticmethod
    def load_all() -> dict:
        """
        Tüm kullanıcıları yükle (eski load_users() karşılığı).
        
        Returns:
            dict: {username: user_data} formatında kullanıcı sözlüğü
        """
        try:
            db = get_supabase()
            result = db.table("users").select("*").execute()
            
            users = {}
            for row in result.data:
                username = row["username"]
                users[username] = {
                    "password": row["password"],
                    "_plain_password": row.get("plain_password"),
                    "email": row.get("email"),
                    "full_name": row.get("full_name"),
                    "is_admin": row.get("is_admin", False),
                    "created_at": row.get("created_at", ""),
                    "profile_image": row.get("profile_image"),
                }
                if row.get("deleted_at"):
                    users[username]["deleted_at"] = row["deleted_at"]
            
            return users
        except Exception as e:
            logger.error(f"❌ Kullanıcılar yüklenemedi: {e}")
            return {}
    
    @staticmethod
    def get(username: str) -> Optional[dict]:
        """
        Tek bir kullanıcıyı getir.
        
        Args:
            username: Kullanıcı adı
            
        Returns:
            dict veya None: Kullanıcı verisi
        """
        try:
            db = get_supabase()
            result = db.table("users").select("*").eq("username", username).execute()
            
            if not result.data:
                return None
            
            row = result.data[0]
            user = {
                "password": row["password"],
                "_plain_password": row.get("plain_password"),
                "email": row.get("email"),
                "full_name": row.get("full_name"),
                "is_admin": row.get("is_admin", False),
                "created_at": row.get("created_at", ""),
                "profile_image": row.get("profile_image"),
            }
            if row.get("deleted_at"):
                user["deleted_at"] = row["deleted_at"]
            
            return user
        except Exception as e:
            logger.error(f"❌ Kullanıcı getirilemedi ({username}): {e}")
            return None
    
    @staticmethod
    def create(username: str, user_data: dict) -> bool:
        """
        Yeni kullanıcı oluştur.
        
        Args:
            username: Kullanıcı adı
            user_data: Kullanıcı verileri (password, email, full_name, vb.)
            
        Returns:
            bool: Başarılıysa True
        """
        try:
            db = get_supabase()
            db.table("users").insert({
                "username": username,
                "password": user_data["password"],
                "plain_password": user_data.get("_plain_password"),
                "email": user_data.get("email"),
                "full_name": user_data.get("full_name"),
                "is_admin": user_data.get("is_admin", False),
                "created_at": user_data.get("created_at", datetime.now(timezone.utc).isoformat()),
                "profile_image": user_data.get("profile_image"),
            }).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Kullanıcı oluşturulamadı ({username}): {e}")
            return False
    
    @staticmethod
    def update(username: str, updates: dict) -> bool:
        """
        Kullanıcı bilgilerini güncelle.
        
        Args:
            username: Kullanıcı adı
            updates: Güncellenecek alanlar (Supabase sütun adlarıyla)
            
        Returns:
            bool: Başarılıysa True
        """
        try:
            db = get_supabase()
            # _plain_password -> plain_password dönüşümü
            if "_plain_password" in updates:
                updates["plain_password"] = updates.pop("_plain_password")
            db.table("users").update(updates).eq("username", username).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Kullanıcı güncellenemedi ({username}): {e}")
            return False
    
    @staticmethod
    def delete(username: str) -> bool:
        """
        Kullanıcıyı kalıcı olarak sil.
        
        Args:
            username: Silinecek kullanıcı adı
            
        Returns:
            bool: Başarılıysa True
        """
        try:
            db = get_supabase()
            db.table("users").delete().eq("username", username).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Kullanıcı silinemedi ({username}): {e}")
            return False
    
    @staticmethod
    def rename(old_username: str, new_username: str) -> bool:
        """
        Kullanıcı adını değiştir.
        ON UPDATE CASCADE sayesinde ilişkili tablolar da güncellenir.
        
        Args:
            old_username: Eski kullanıcı adı
            new_username: Yeni kullanıcı adı
            
        Returns:
            bool: Başarılıysa True
        """
        try:
            db = get_supabase()
            db.table("users").update({"username": new_username}).eq("username", old_username).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Kullanıcı adı değiştirilemedi ({old_username} -> {new_username}): {e}")
            return False
    
    @staticmethod
    def email_exists(email: str, exclude_username: str = None) -> bool:
        """
        E-posta adresinin başka bir kullanıcı tarafından kullanılıp kullanılmadığını kontrol et.
        
        Args:
            email: E-posta adresi
            exclude_username: Bu kullanıcı adı hariç tutulur (güncelleme sırasında)
            
        Returns:
            bool: E-posta zaten kullanılıyorsa True
        """
        try:
            db = get_supabase()
            query = db.table("users").select("username").eq("email", email)
            if exclude_username:
                query = query.neq("username", exclude_username)
            result = query.execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ E-posta kontrol hatası ({email}): {e}")
            return False
    
    @staticmethod
    def get_expired_deleted_users(days: int = 30) -> List[str]:
        """
        Belirtilen gün sayısından daha önce silinmek üzere işaretlenmiş kullanıcıları getir.
        
        Args:
            days: Gün eşiği (varsayılan 30)
            
        Returns:
            List[str]: Silinecek kullanıcı adları listesi
        """
        try:
            db = get_supabase()
            cutoff = datetime.now(timezone.utc)
            # deleted_at NOT NULL olan ve 30 günden eski olanları bul
            result = db.table("users").select("username, deleted_at").not_.is_("deleted_at", "null").execute()
            
            expired_users = []
            for row in result.data:
                deleted_at = datetime.fromisoformat(row["deleted_at"].replace("Z", "+00:00"))
                if (cutoff - deleted_at).days >= days:
                    expired_users.append(row["username"])
            
            return expired_users
        except Exception as e:
            logger.error(f"❌ Süresi dolmuş hesaplar kontrol edilemedi: {e}")
            return []


# ============================================================================
# Sohbet Geçmişi Veritabanı İşlemleri
# ============================================================================

class ChatDB:
    """
    Sohbet oturumları ve mesajlar için veritabanı katmanı.
    Eski JSON dosya tabanlı HistoryService'in yerine geçer.
    """
    
    @staticmethod
    def create_session(username: str, session_id: str = None) -> str:
        """
        Yeni bir sohbet oturumu oluştur.
        
        Args:
            username: Kullanıcı adı
            session_id: Opsiyonel UUID (verilmezse otomatik oluşturulur)
            
        Returns:
            str: Oluşturulan oturum ID'si
        """
        try:
            import uuid
            db = get_supabase()
            sid = session_id or str(uuid.uuid4())
            
            db.table("chat_sessions").insert({
                "id": sid,
                "username": username,
                "title": "Yeni Sohbet",
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            
            return sid
        except Exception as e:
            logger.error(f"❌ Oturum oluşturulamadı ({username}): {e}")
            raise
    
    @staticmethod
    def session_exists(username: str, session_id: str) -> bool:
        """
        Bir oturumun var olup olmadığını kontrol et.
        
        Args:
            username: Kullanıcı adı
            session_id: Oturum ID'si
            
        Returns:
            bool: Oturum varsa True
        """
        try:
            db = get_supabase()
            result = db.table("chat_sessions").select("id").eq("id", session_id).eq("username", username).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ Oturum kontrol hatası: {e}")
            return False
    
    @staticmethod
    def add_message(username: str, session_id: str, role: str, content: str, thought: str = None) -> None:
        """
        Oturuma bir mesaj ekle ve ilk mesajdan başlık güncelle.
        
        Args:
            username: Kullanıcı adı
            session_id: Oturum ID'si
            role: Mesaj rolü ('user' veya 'bot')
            content: Mesaj içeriği
            thought: Düşünce metni (opsiyonel)
        """
        try:
            db = get_supabase()
            
            # Mesajı ekle
            msg_data = {
                "session_id": session_id,
                "role": role,
                "content": content,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            if thought:
                msg_data["thought"] = thought
            
            db.table("chat_messages").insert(msg_data).execute()
            
            # İlk kullanıcı mesajından başlığı güncelle
            if role == "user":
                # Oturumdaki mesaj sayısını kontrol et
                count_result = db.table("chat_messages").select("id", count="exact").eq("session_id", session_id).execute()
                if count_result.count == 1:
                    title = content[:50] + ("..." if len(content) > 50 else "")
                    db.table("chat_sessions").update({"title": title}).eq("id", session_id).execute()
                    
        except Exception as e:
            logger.error(f"❌ Mesaj eklenemedi (oturum: {session_id}): {e}")
            raise
    
    @staticmethod
    def get_session(username: str, session_id: str) -> dict:
        """
        Tüm mesajlarıyla belirli bir oturumu getir.
        
        Args:
            username: Kullanıcı adı
            session_id: Oturum ID'si
            
        Returns:
            dict: Oturum verileri (id, title, timestamp, messages)
            
        Raises:
            ValueError: Oturum bulunamazsa
        """
        try:
            db = get_supabase()
            
            # Oturumu getir
            session_result = db.table("chat_sessions").select("*").eq("id", session_id).eq("username", username).execute()
            
            if not session_result.data:
                raise ValueError("Oturum bulunamadı")
            
            session = session_result.data[0]
            
            # Mesajları getir (sıralı)
            messages_result = db.table("chat_messages").select("role, content, thought").eq("session_id", session_id).order("created_at").execute()
            
            messages = []
            for msg in messages_result.data:
                m = {"role": msg["role"], "content": msg["content"]}
                if msg.get("thought"):
                    m["thought"] = msg["thought"]
                messages.append(m)
            
            return {
                "id": session["id"],
                "title": session["title"],
                "timestamp": session["created_at"],
                "messages": messages
            }
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"❌ Oturum getirilemedi ({session_id}): {e}")
            raise ValueError("Oturum bulunamadı")
    
    @staticmethod
    def get_history(username: str) -> List[dict]:
        """
        Bir kullanıcı için tüm sohbet oturumlarını getir (mesajsız).
        
        Args:
            username: Kullanıcı adı
            
        Returns:
            List[dict]: Oturum listesi (id, title, timestamp)
        """
        try:
            db = get_supabase()
            result = db.table("chat_sessions").select("id, title, created_at").eq("username", username).order("created_at", desc=True).execute()
            
            sessions = []
            for row in result.data:
                sessions.append({
                    "id": row["id"],
                    "title": row["title"],
                    "timestamp": row["created_at"]
                })
            
            return sessions
        except Exception as e:
            logger.error(f"❌ Geçmiş getirilemedi ({username}): {e}")
            return []
    
    @staticmethod
    def delete_session(username: str, session_id: str) -> bool:
        """
        Belirli bir oturumu sil (CASCADE ile mesajlar da silinir).
        
        Args:
            username: Kullanıcı adı
            session_id: Silinecek oturum ID'si
            
        Returns:
            bool: Silme başarılıysa True
        """
        try:
            db = get_supabase()
            result = db.table("chat_sessions").delete().eq("id", session_id).eq("username", username).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ Oturum silinemedi ({session_id}): {e}")
            return False
    
    @staticmethod
    def delete_all_sessions(username: str) -> int:
        """
        Bir kullanıcı için tüm oturumları sil.
        
        Args:
            username: Kullanıcı adı
            
        Returns:
            int: Silinen oturum sayısı
        """
        try:
            db = get_supabase()
            result = db.table("chat_sessions").delete().eq("username", username).execute()
            return len(result.data)
        except Exception as e:
            logger.error(f"❌ Oturumlar silinemedi ({username}): {e}")
            return 0
    
    @staticmethod
    def export_markdown(username: str, session_id: str) -> str:
        """
        Bir oturumu Markdown formatında dışa aktar.
        
        Args:
            username: Kullanıcı adı
            session_id: Oturum ID'si
            
        Returns:
            str: Markdown formatında oturum içeriği
        """
        session = ChatDB.get_session(username, session_id)
        
        md = f"# {session['title']}\n\n"
        md += f"*Tarih: {session['timestamp']}*\n\n---\n\n"
        
        for msg in session["messages"]:
            role = "👤 Kullanıcı" if msg["role"] == "user" else "🤖 Niko"
            md += f"### {role}\n\n{msg['content']}\n\n"
        
        return md


# ============================================================================
# E-posta Doğrulama Veritabanı İşlemleri
# ============================================================================

class EmailVerificationDB:
    """
    E-posta doğrulama kodları için veritabanı katmanı.
    Bellekte saklanan e-posta doğrulama sisteminin yerine geçer (serverless uyumluluğu için).
    """
    
    @staticmethod
    def set_code(email: str, code: str, username: str, expires_at: datetime) -> bool:
        """
        E-posta doğrulama kodunu kaydet veya güncelle.
        """
        try:
            db = get_supabase()
            db.table("email_verifications").upsert({
                "email": email,
                "code": code,
                "username": username,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "attempts": 0,
                "verified": False,
                "verified_at": None
            }).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Doğrulama kodu kaydedilemedi ({email}): {e}")
            return False
            
    @staticmethod
    def get_code(email: str) -> Optional[dict]:
        """
        Bir e-posta adresi için aktif doğrulama kaydını getir.
        """
        try:
            db = get_supabase()
            result = db.table("email_verifications").select("*").eq("email", email).execute()
            if not result.data:
                return None
            
            row = result.data[0]
            # Datetime dönüşümleri (timezone aware yap)
            expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
            created_at = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
            
            verified_at = None
            if row.get("verified_at"):
                verified_at = datetime.fromisoformat(row["verified_at"].replace("Z", "+00:00"))
                
            return {
                "email": row["email"],
                "code": row["code"],
                "username": row["username"],
                "expires_at": expires_at,
                "created_at": created_at,
                "attempts": row.get("attempts", 0),
                "verified": row.get("verified", False),
                "verified_at": verified_at
            }
        except Exception as e:
            logger.error(f"❌ Doğrulama kodu getirilemedi ({email}): {e}")
            return None
            
    @staticmethod
    def increment_attempts(email: str) -> bool:
        """
        Deneme sayısını 1 artır.
        """
        try:
            db = get_supabase()
            # Önce mevcut deneme sayısını al
            record = EmailVerificationDB.get_code(email)
            if not record:
                return False
                
            db.table("email_verifications").update({
                "attempts": record["attempts"] + 1
            }).eq("email", email).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Deneme sayısı artırılamadı ({email}): {e}")
            return False
            
    @staticmethod
    def set_verified(email: str, verified: bool = True, expires_at: datetime = None) -> bool:
        """
        Kaydı doğrulanmış olarak işaretle ve isteğe bağlı olarak yeni bir expires_at belirle.
        """
        try:
            db = get_supabase()
            updates = {
                "verified": verified,
                "verified_at": datetime.now(timezone.utc).isoformat() if verified else None
            }
            if expires_at:
                updates["expires_at"] = expires_at.isoformat()
                
            db.table("email_verifications").update(updates).eq("email", email).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Doğrulama durumu güncellenemedi ({email}): {e}")
            return False
            
    @staticmethod
    def delete_code(email: str) -> bool:
        """
        Bir e-posta adresine ait doğrulama kaydını tamamen sil.
        """
        try:
            db = get_supabase()
            db.table("email_verifications").delete().eq("email", email).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Doğrulama kaydı silinemedi ({email}): {e}")
            return False
            
    @staticmethod
    def cleanup_expired_codes() -> int:
        """
        Süresi dolmuş tüm doğrulama kodlarını veritabanından sil.
        """
        try:
            db = get_supabase()
            now = datetime.now(timezone.utc).isoformat()
            result = db.table("email_verifications").delete().lt("expires_at", now).execute()
            return len(result.data) if result.data else 0
        except Exception as e:
            logger.error(f"❌ Süresi dolmuş doğrulama kodları temizlenemedi: {e}")
            return 0


# ============================================================================
# Veri Göçü Yardımcısı
# ============================================================================

def migrate_json_to_supabase():
    """
    Mevcut JSON verilerini Supabase'e göç eder.
    Bu fonksiyon bir kerelik çalıştırılmalıdır.
    
    Kullanım:
        python -c "from database import migrate_json_to_supabase; migrate_json_to_supabase()"
    """
    import json
    
    print("🔄 JSON -> Supabase veri göçü başlıyor...")
    
    db = get_supabase()
    
    # 1. Kullanıcıları göç ettir
    users_file = "users.json"
    if os.path.exists(users_file):
        with open(users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        for username, data in users.items():
            try:
                db.table("users").upsert({
                    "username": username,
                    "password": data.get("password", ""),
                    "plain_password": data.get("_plain_password"),
                    "email": data.get("email"),
                    "full_name": data.get("full_name"),
                    "is_admin": data.get("is_admin", False),
                    "created_at": data.get("created_at", datetime.now(timezone.utc).isoformat()),
                    "profile_image": data.get("profile_image"),
                }).execute()
                print(f"  ✅ Kullanıcı aktarıldı: {username}")
            except Exception as e:
                print(f"  ❌ Kullanıcı aktarılamadı ({username}): {e}")
    else:
        print("  ⚠️ users.json bulunamadı, atlanıyor...")
    
    # 2. Sohbet geçmişini göç ettir
    history_dir = "history"
    if os.path.exists(history_dir):
        for filename in os.listdir(history_dir):
            if not filename.endswith(".json"):
                continue
            
            filepath = os.path.join(history_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                
                # Dosya adından kullanıcı adını çıkar (username_sessionid.json)
                parts = filename.rsplit("_", 1)
                if len(parts) != 2:
                    continue
                username = parts[0]
                
                # Oturumu ekle
                db.table("chat_sessions").upsert({
                    "id": session["id"],
                    "username": username,
                    "title": session.get("title", "Yeni Sohbet"),
                    "created_at": session.get("timestamp", datetime.now(timezone.utc).isoformat())
                }).execute()
                
                # Mesajları ekle
                for msg in session.get("messages", []):
                    msg_data = {
                        "session_id": session["id"],
                        "role": msg["role"],
                        "content": msg["content"],
                    }
                    if msg.get("thought"):
                        msg_data["thought"] = msg["thought"]
                    
                    db.table("chat_messages").insert(msg_data).execute()
                
                print(f"  ✅ Oturum aktarıldı: {filename}")
            except Exception as e:
                print(f"  ❌ Oturum aktarılamadı ({filename}): {e}")
    else:
        print("  ⚠️ history/ dizini bulunamadı, atlanıyor...")
    
    print("\n🎉 Veri göçü tamamlandı!")
