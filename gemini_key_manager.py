import os
import json
import logging
import asyncio
import random
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import google.genai as genai

logger = logging.getLogger("niko.gemini_key_manager")

class GeminiKeyManager:
    """
    Sıfırdan tasarlanmış modern Gemini API Anahtarı ve Kota Yönetim Sistemi.
    
    Özellikler:
    - Thread-safe & Async-friendly (asyncio.Lock ile)
    - Esnek Rotasyon Stratejileri (sequential, health_priority, random, least_used)
    - Otomatik İyileştirme (quota_exceeded durumundaki anahtarları cooldown sonrası veya gün dönümünde sıfırlar)
    - Detaylı Olay Günlüğü (Rolling Event Log)
    - Dinamik Anahtar Ekleme, Silme ve Limit Düzenleme
    - Tarih bazlı istatistik kaydı (Per-key ve Global)
    """

    def __init__(self, metadata_file: str = "api_keys_metadata.json", cooldown_minutes: int = 60):
        self.metadata_file = metadata_file
        self.cooldown_minutes = cooldown_minutes
        self.lock = asyncio.Lock()
        
        # Temel durum değişkenleri
        self.api_keys: List[str] = []
        self.keys_metadata: List[Dict[str, Any]] = []
        self.current_key_index: int = 0
        self.rotation_strategy: str = "sequential"
        self.history_stats: Dict[str, Dict[str, int]] = {}
        self.key_rotation_logs: List[Dict[str, Any]] = []
        
        # Yükleme işlemi
        self._load_from_file_or_env()

    def _add_log(self, level: str, message: str):
        """Olay günlüğüne thread-safe olmayan şekilde yeni bir olay ekler."""
        self.key_rotation_logs.insert(0, {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message
        })
        # Son 100 log ile sınırla
        if len(self.key_rotation_logs) > 100:
            self.key_rotation_logs.pop()

    def _save_metadata(self):
        """Meta verileri dosyaya kaydeder."""
        try:
            data = {
                "api_keys": self.api_keys,
                "rotation_strategy": self.rotation_strategy,
                "current_key_index": self.current_key_index,
                "keys_metadata": self.keys_metadata,
                "history_stats": self.history_stats,
                "key_rotation_logs": self.key_rotation_logs
            }
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Meta veri dosyaya kaydedilemedi: {e}")

    def _load_from_file_or_env(self):
        """Dosyadan veya çevre değişkenlerinden verileri yükler."""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self.api_keys = data.get("api_keys", [])
                self.rotation_strategy = data.get("rotation_strategy", "sequential")
                self.current_key_index = data.get("current_key_index", 0)
                self.keys_metadata = data.get("keys_metadata", [])
                self.history_stats = data.get("history_stats", {})
                self.key_rotation_logs = data.get("key_rotation_logs", [])
                
                # Eğer meta verilerdeki anahtar sayısı kodla uyuşmuyorsa senkronize et
                if not self.api_keys or len(self.keys_metadata) != len(self.api_keys):
                    self._sync_with_env()
                else:
                    self._add_log("info", "API anahtarı durum bilgileri dosyadan başarıyla yüklendi.")
            else:
                self._sync_with_env()
        except Exception as e:
            logger.error(f"Meta veri yüklenirken hata oluştu: {e}")
            self._sync_with_env()

    def _sync_with_env(self):
        """Çevre değişkenlerindeki API anahtarlarını yükler ve meta verileri sıfırlar."""
        env_keys = os.getenv("GEMINI_API_KEY", "")
        self.api_keys = [k.strip() for k in env_keys.split(",") if k.strip()]
        
        self.keys_metadata = []
        self.current_key_index = 0
        self.history_stats = {}
        self.key_rotation_logs = []
        
        self._seed_history_stats()
        
        for i, key in enumerate(self.api_keys):
            masked_key = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else f"Key_{i+1}"
            key_stats = {}
            self._seed_history_stats(key_stats)
            self.keys_metadata.append(self._create_empty_metadata(i, masked_key, key_stats))
            
        self._add_log("info", f"Sistem çevre değişkenlerindeki {len(self.api_keys)} anahtar ile sıfırdan başlatıldı.")
        self._save_metadata()

    def _create_empty_metadata(self, index: int, masked_key: str, history_stats: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "index": index,
            "masked_key": masked_key,
            "status": "active",  # "active", "quota_exceeded", "invalid", "error"
            "request_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "request_limit": 1500,
            "quota_exceeded_at": None,
            "last_used_at": None,
            "last_error": None,
            "history_stats": history_stats or {}
        }

    def _seed_history_stats(self, target_dict=None):
        """Sistem ilk açıldığında gösterim amaçlı son 7 güne boş veriler tohumlar."""
        try:
            today = datetime.now(timezone.utc)
            for i in range(6, -1, -1):
                d_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                stats = {"requests": 0, "success": 0, "failure": 0}
                if target_dict is None:
                    self.history_stats[d_str] = stats
                else:
                    target_dict[d_str] = stats
        except Exception as e:
            logger.warning(f"Tarih tohumlama hatası: {e}")

    def _record_stat(self, index: int, is_success: bool, error_msg: Optional[str] = None):
        """İstatistikleri ve tarih bazlı verileri günceller."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Global tarih istatistikleri
        if today_str not in self.history_stats:
            self.history_stats[today_str] = {"requests": 0, "success": 0, "failure": 0}
        self.history_stats[today_str]["requests"] += 1
        if is_success:
            self.history_stats[today_str]["success"] += 1
        else:
            self.history_stats[today_str]["failure"] += 1

        # Anahtar bazlı istatistikler
        if 0 <= index < len(self.keys_metadata):
            meta = self.keys_metadata[index]
            meta["request_count"] += 1
            meta["last_used_at"] = datetime.now(timezone.utc).isoformat()
            
            if "history_stats" not in meta:
                meta["history_stats"] = {}
            if today_str not in meta["history_stats"]:
                meta["history_stats"][today_str] = {"requests": 0, "success": 0, "failure": 0}
                
            meta["history_stats"][today_str]["requests"] += 1
            
            if is_success:
                meta["success_count"] += 1
                meta["status"] = "active"
                meta["last_error"] = None
                meta["history_stats"][today_str]["success"] += 1
            else:
                meta["failure_count"] += 1
                meta["last_error"] = error_msg
                meta["history_stats"][today_str]["failure"] += 1

    def _check_auto_heal(self):
        """
        Quota_exceeded durumundaki anahtarları inceler.
        Cooldown süresi dolmuşsa veya yeni bir güne geçilmişse durumu sıfırlar.
        """
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")
        healed_any = False
        
        for meta in self.keys_metadata:
            if meta["status"] == "quota_exceeded" and meta["quota_exceeded_at"]:
                try:
                    q_time = datetime.fromisoformat(meta["quota_exceeded_at"])
                    # 1. Koşul: Cooldown süresi dolmuş mu?
                    is_cooldown_over = (now - q_time) >= timedelta(minutes=self.cooldown_minutes)
                    # 2. Koşul: Gün değişti mi?
                    is_new_day = q_time.strftime("%Y-%m-%d") != today_str
                    
                    if is_cooldown_over or is_new_day:
                        meta["status"] = "active"
                        meta["quota_exceeded_at"] = None
                        meta["last_error"] = None
                        self._add_log("success", f"Anahtar {meta['index'] + 1} kotası otomatik iyileştirme ile sıfırlandı.")
                        healed_any = True
                except Exception as e:
                    logger.error(f"Otomatik iyileştirme tarihi ayrıştırılırken hata: {meta['index']}: {e}")
                    
        if healed_any:
            self._save_metadata()

    # ============================================================================
    # API & Dış Erişim Metotları (Thread-Safe)
    # ============================================================================

    async def get_active_client(self) -> tuple[Optional[genai.Client], int]:
        """
        Şu an aktif olan ve kullanılabilir durumda olan API istemcisini ve indeksini döndürür.
        """
        async with self.lock:
            self._check_auto_heal()
            
            if not self.api_keys:
                return None, -1
                
            # Eğer aktif anahtar kullanılamaz durumdaysa, otomatik olarak başka bir anahtara geçiş yap
            active_meta = self.keys_metadata[self.current_key_index]
            if active_meta["status"] in ["quota_exceeded", "invalid"]:
                logger.warning(f"Aktif API anahtarı (İndeks: {self.current_key_index}) {active_meta['status']} durumunda. Yeni anahtar seçiliyor...")
                self._select_next_key_under_lock()
                
            key = self.api_keys[self.current_key_index]
            client = genai.Client(api_key=key)
            return client, self.current_key_index

    async def mark_success(self, index: int):
        """Bir isteğin başarılı olduğunu bildirir."""
        async with self.lock:
            self._record_stat(index, is_success=True)
            self._save_metadata()

    async def mark_failure(self, index: int, error: Exception) -> bool:
        """
        Bir istek hatasını bildirir. Hata türünü analiz ederek anahtar durumunu günceller.
        Eğer rotasyon yapılması gerekiyorsa True döndürür.
        """
        async with self.lock:
            error_msg = str(error)
            err_lower = error_msg.lower()
            
            is_quota = "429" in err_lower or "quota" in err_lower or "limit" in err_lower
            is_invalid = "400" in err_lower or "invalid" in err_lower or "not valid" in err_lower
            
            status = "error"
            if is_quota:
                status = "quota_exceeded"
            elif is_invalid:
                status = "invalid"
                
            if 0 <= index < len(self.keys_metadata):
                meta = self.keys_metadata[index]
                meta["status"] = status
                if is_quota:
                    meta["quota_exceeded_at"] = datetime.now(timezone.utc).isoformat()
                    
                self._record_stat(index, is_success=False, error_msg=error_msg)
                
                reason = "Kota Doldu" if is_quota else ("Geçersiz Anahtar" if is_invalid else "Hata Aldı")
                self._add_log("error", f"Anahtar {index + 1} başarısız oldu: {reason} ({error_msg[:60]})")
                
            # Eğer hata veren anahtar şu anki aktif anahtar ise rotasyon yap
            should_rotate = (is_quota or is_invalid or status == "error") and len(self.api_keys) > 1
            if should_rotate and self.current_key_index == index:
                self._select_next_key_under_lock()
                
            self._save_metadata()
            return should_rotate

    def _select_next_key_under_lock(self):
        """
        Rotasyon stratejisine göre sıradaki en uygun anahtarı seçer ve aktif yapar.
        (Kilit altında çağrılmalıdır)
        """
        if len(self.api_keys) <= 1:
            return

        strategy = self.rotation_strategy
        active_candidates = [m for m in self.keys_metadata if m["status"] == "active"]
        
        if not active_candidates:
            # Tüm anahtarlar sorunluysa, en son quota_exceeded olanı veya ilkini fallback yapalım
            logger.error("Tüm API anahtarları devre dışı! İlk anahtara fallback yapılıyor.")
            self.current_key_index = 0
            self._add_log("warning", "Tüm anahtarlar kullanım dışı. İlk anahtar aktif edildi.")
            return

        if strategy == "health_priority":
            # Başarı oranı en yüksek ve hata sayısı en az olanı seç
            def get_score(meta):
                success_ratio = meta["success_count"] / meta["request_count"] if meta["request_count"] > 0 else 1.0
                # Skor formülü: başarı oranı öncelikli, hatalar azaltıcı etkiye sahip
                return success_ratio * 1000 - meta["failure_count"] * 10
            
            active_candidates.sort(key=get_score, reverse=True)
            self.current_key_index = active_candidates[0]["index"]
            self._add_log("info", f"Sağlık öncelikli rotasyon yapıldı. Anahtar {self.current_key_index + 1} seçildi.")
            
        elif strategy == "random":
            # Rastgele bir sağlıklı anahtar seç
            chosen = random.choice(active_candidates)
            self.current_key_index = chosen["index"]
            self._add_log("info", f"Rastgele rotasyon yapıldı. Anahtar {self.current_key_index + 1} seçildi.")
            
        elif strategy == "least_used":
            # İstek sayısı en az olan sağlıklı anahtarı seç
            active_candidates.sort(key=lambda m: m["request_count"])
            self.current_key_index = active_candidates[0]["index"]
            self._add_log("info", f"En az kullanılan rotasyon yapıldı. Anahtar {self.current_key_index + 1} seçildi.")
            
        else: # sequential (Round-Robin)
            # Sıradaki sağlıklı anahtarı seç
            next_idx = (self.current_key_index + 1) % len(self.api_keys)
            found = False
            for _ in range(len(self.api_keys)):
                meta = self.keys_metadata[next_idx]
                if meta["status"] == "active":
                    self.current_key_index = next_idx
                    found = True
                    break
                next_idx = (next_idx + 1) % len(self.api_keys)
                
            if not found:
                self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
                
            self._add_log("info", f"Sıralı rotasyon yapıldı. Anahtar {self.current_key_index + 1} seçildi.")

    # ============================================================================
    # Yönetici Panel Metotları (Thread-Safe)
    # ============================================================================

    async def get_keys_status_payload(self) -> dict:
        """Dashboard'un get_api_keys_status istekleri için veri paketi döner."""
        async with self.lock:
            self._check_auto_heal()
            return {
                "keys": self.keys_metadata,
                "current_key_index": self.current_key_index,
                "total_keys": len(self.api_keys),
                "rotation_strategy": self.rotation_strategy,
                "history_stats": self.history_stats
            }

    async def get_logs_payload(self) -> dict:
        """Dashboard olay günlüğü istekleri için veri döner."""
        async with self.lock:
            return {"logs": self.key_rotation_logs}

    async def update_rotation_strategy(self, strategy: str) -> str:
        """Stratejiyi günceller."""
        if strategy not in ["sequential", "health_priority", "random", "least_used"]:
            raise ValueError("Geçersiz rotasyon stratejisi")
            
        async with self.lock:
            self.rotation_strategy = strategy
            self._add_log("info", f"Rotasyon stratejisi '{strategy}' olarak değiştirildi.")
            self._save_metadata()
            return strategy

    async def reset_key(self, index: int) -> dict:
        """Belirli anahtarı sıfırlar ve tekrar 'active' yapar."""
        async with self.lock:
            if index < 0 or index >= len(self.api_keys):
                raise IndexError("Geçersiz anahtar indeksi")
                
            meta = self.keys_metadata[index]
            meta["status"] = "active"
            meta["quota_exceeded_at"] = None
            meta["last_error"] = None
            
            self._add_log("success", f"Anahtar {index + 1} durumu yönetici tarafından aktif edildi.")
            self._save_metadata()
            return meta

    async def set_active_key(self, index: int) -> int:
        """Aktif anahtar indeksini manuel ayarlar."""
        async with self.lock:
            if index < 0 or index >= len(self.api_keys):
                raise IndexError("Geçersiz anahtar indeksi")
                
            self.current_key_index = index
            self._add_log("info", f"Aktif anahtar manuel olarak İndeks {index + 1} yapıldı.")
            self._save_metadata()
            return self.current_key_index

    async def update_key_limit(self, index: int, limit: int) -> int:
        """İstek limitini günceller."""
        if limit <= 0:
            raise ValueError("Limit 0'dan büyük olmalıdır")
            
        async with self.lock:
            if index < 0 or index >= len(self.api_keys):
                raise IndexError("Geçersiz anahtar indeksi")
                
            self.keys_metadata[index]["request_limit"] = limit
            self._add_log("info", f"Anahtar {index + 1} günlük limiti {limit} olarak güncellendi.")
            self._save_metadata()
            return limit

    async def add_key(self, api_key: str) -> dict:
        """Sisteme dinamik yeni anahtar ekler."""
        key = api_key.strip()
        if not key:
            raise ValueError("API anahtarı boş olamaz")
            
        async with self.lock:
            if key in self.api_keys:
                raise ValueError("Bu API anahtarı zaten sisteme kayıtlı")
                
            self.api_keys.append(key)
            new_index = len(self.api_keys) - 1
            masked = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else f"Key_{new_index + 1}"
            
            key_stats = {}
            self._seed_history_stats(key_stats)
            new_meta = self._create_empty_metadata(new_index, masked, key_stats)
            self.keys_metadata.append(new_meta)
            
            self._add_log("success", f"Yeni API anahtarı sisteme eklendi: {masked}")
            self._save_metadata()
            return new_meta

    async def delete_key(self, index: int):
        """Dinamik olarak anahtarı kaldırır."""
        async with self.lock:
            if index < 0 or index >= len(self.api_keys):
                raise IndexError("Geçersiz anahtar indeksi")
                
            if len(self.api_keys) <= 1:
                raise ValueError("Sistemde en az bir adet API anahtarı bulunmalıdır")
                
            removed_key = self.api_keys.pop(index)
            removed_meta = self.keys_metadata.pop(index)
            
            # İndeksleri yeniden ata
            for i, meta in enumerate(self.keys_metadata):
                meta["index"] = i
                
            # Eğer silinen aktif anahtar ise indeksi ayarla
            if self.current_key_index == index:
                self.current_key_index = 0
            elif self.current_key_index > index:
                self.current_key_index -= 1
                
            self._add_log("warning", f"Anahtar {index + 1} sistemden kaldırıldı: {removed_meta['masked_key']}")
            self._save_metadata()

    async def test_key(self, index: int) -> dict:
        """Belirli anahtarı doğrudan test eder."""
        # Kilidi almadan önce anahtarın kopyasını alıyoruz, aio call kilit dışı çalışmalı
        async with self.lock:
            if index < 0 or index >= len(self.api_keys):
                raise IndexError("Geçersiz anahtar indeksi")
            test_key = self.api_keys[index]
            meta = self.keys_metadata[index]

        temp_client = genai.Client(api_key=test_key)
        try:
            # Hızlı bir test isteği gönder
            await temp_client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents="test"
            )
            
            # Başarılı ise durumu güncelle
            async with self.lock:
                meta["status"] = "active"
                meta["quota_exceeded_at"] = None
                meta["last_error"] = None
                self._add_log("success", f"Anahtar {index + 1} manuel test edildi: Başarılı")
                self._save_metadata()
                
            return {"status": "success", "message": "Anahtar başarıyla doğrulandı. Sağlıklı çalışıyor."}
            
        except Exception as e:
            error_msg = str(e)
            err_lower = error_msg.lower()
            is_quota = "429" in err_lower or "quota" in err_lower or "limit" in err_lower
            is_invalid = "400" in err_lower or "invalid" in err_lower or "not valid" in err_lower
            
            status = "error"
            if is_quota:
                status = "quota_exceeded"
            elif is_invalid:
                status = "invalid"
                
            async with self.lock:
                meta["status"] = status
                if is_quota:
                    meta["quota_exceeded_at"] = datetime.now(timezone.utc).isoformat()
                meta["last_error"] = error_msg
                meta["failure_count"] += 1
                
                self._add_log("error", f"Anahtar {index + 1} manuel test edildi: Başarısız ({status})")
                self._save_metadata()
                
            return {
                "status": "failed",
                "message": "Doğrulama başarısız oldu.",
                "error": error_msg,
                "detected_status": status
            }
