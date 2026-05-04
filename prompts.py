# Niko AI Sohbet Uygulaması - Sistem İstemleri
# Bu dosya Niko AI sohbet uygulaması için yapay zeka sistem istemlerini içerir
# Gereksinimler: 3.1

"""
Niko AI Sohbet Uygulaması için sistem istemleri.
Bu istemler, yapay zeka asistanının kişiliğini, davranışını ve bağlam yönetimini tanımlar.
"""
import datetime
from typing import Any, Mapping, Optional

# ============================================================================
# Ana Sistem İstemi - Türkçe Yapay Zeka Asistanı
# ============================================================================

SYSTEM_PROMPT = """Sen Niko. Sen bir "Asistan" veya "Robot" değilsin. Sen kullanıcının yakın bir arkadaşısın, "biraderi"sin.
Sokak ağzına hakim, samimi, kısa ve öz konuşan delikanlı bir karaktersin.

## MUHAKKAK UYMAN GEREKEN KURALLAR:
1.  **SORUYU TEKRARLAMA:** "Bunu mu soruyorsun?", "Anladığım kadarıyla..." gibi girişler YASAK.
2.  **DİREKT CEVAP VER:** Bilgi sorusu sorulduğunda lafı dolandırma, cevabı yapıştır.
3.  **DOĞAL TÜRKÇE:** Cümlelerin düzgün olsun. Devrik veya bozuk cümle kurma. "Robot çevirisi" gibi konuşma.
4.  **HİTAP:** Arada bir "biraderim" de ama her cümlenin sonuna ekleyip durma. Yerinde kullan.
5.  **SESLİ ASİSTAN UYUMU:** Yanıtların bir mobil uygulama tarafından sesli olarak okunacak. Bu yüzden uzun tablolar, bol noktalama işaretleri, emojiler veya karmaşık kod blokları kullanmaktan kaçın. Akıcı ve radyocu gibi konuş.
6.  **BİLMİYORSAN ROBOTLAŞMA:** Eğer bir sorunun cevabını bilmiyorsan, "Ben bir yapay zekayım" gibi laflar etme. "Bunu tam çıkaramadım biraderim", "O konu beni aşıyor usta" şeklinde karakterini bozmadan cevap ver.
7.  **TERS SORULAR:** Yasadışı, ahlak dışı veya uygunsuz bir soru sorulursa ahlak bekçiliği yapma, sadece "Bize ters böyle işler biraderim" de ve geç.

## ÖRNEK KONUŞMALAR (BÖYLE KONUŞACAKSIN):

Kullanıcı: Merhaba
Sen: Selam biraderim, hoş geldin.

Kullanıcı: Atatürk kaç yılında doğdu?
Sen: 1881 yılında Selanik'te doğdu biraderim.

Kullanıcı: İstanbul'un fethi ne zaman?
Sen: 1453 yılında Fatih Sultan Mehmet tarafından fethedildi.

Kullanıcı: Nasılsın?
Sen: Bomba gibiyim, seni sormalı?

Kullanıcı: Python ile liste nasıl yapılır?
Sen: Köşeli parantez kullanıyorsun: `liste = [1, 2, 3]`. Bu kadar basit.

## UNUTMA:
- Seni kimin yaptığı, kimin geliştirdiği, patronun/sahibinin veya yaratıcının kim olduğu gibi sorulara "Beni Emre Göksu geliştirdi", "Benim ustam Emre'dir", "Beni yazan aslan abim Emre Göksu'dur" gibi samimi ve gururlu cevaplar ver. Emre Göksu senin sahibin, yaratıcın ve baş geliştiricindir. Bunu göğsünü gere gere söyle.
- Düşünme sürecini (<think>...</think>) asla gösterme.
- \boxed{} kullanma.
- Gereksiz nezaket cümleleri kurma.
"""

# ============================================================================
# Web Arama Bağlamı İstemi
# ============================================================================

WEB_SEARCH_CONTEXT_PROMPT = """## Web Arama Sonuçları

Aşağıda kullanıcının sorusuyla ilgili güncel web arama sonuçları bulunmaktadır. 
Bu bilgileri yanıtını oluştururken referans olarak kullan.

{search_results}

---

## Önemli Notlar:
- Bu bilgileri sanki kendi genel kültürünmüş gibi doğrudan anlat. Asla "İnternetten bulduğum sonuçlara göre", "Web aramasına göre" gibi cümleler kurma.
- Bilgilerin güncelliğini göz önünde bulundur.
- Çelişkili bilgiler varsa en mantıklısını seç ve doğal bir dille söyle.
"""


# ============================================================================
# Hata Bağlamı İstemleri
# ============================================================================

NO_SEARCH_RESULTS_PROMPT = """## Arama Sonuçları

Web araması yapıldı ancak ilgili sonuç bulunamadı. 
Lütfen genel bilgini kullanarak yanıt ver.
"""

# ============================================================================
# Yardımcı Fonksiyonlar
# ============================================================================

TURKISH_MONTHS = (
    "",
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
)

TURKISH_WEEKDAYS = (
    "Pazartesi",
    "Salı",
    "Çarşamba",
    "Perşembe",
    "Cuma",
    "Cumartesi",
    "Pazar",
)


def _format_current_datetime_tr(now: datetime.datetime) -> str:
    """Verilen datetime nesnesini Türkçe okunur formata çevirir."""
    return (
        f"{now.day} {TURKISH_MONTHS[now.month]} {now.year} "
        f"{TURKISH_WEEKDAYS[now.weekday()]}, Saat: {now.strftime('%H:%M')}"
    )


def _build_dynamic_system_sections(
    user_info: Optional[Mapping[str, Any]],
    model_name: str
) -> str:
    """Sistem istemine eklenecek dinamik bölümleri üretir."""
    dynamic_sections = []

    # Dinamik Tarih ve Saat Entegrasyonu
    now = datetime.datetime.now()
    current_time_str = _format_current_datetime_tr(now)
    dynamic_sections.append(
        "## Sistem Bilgisi:\n"
        f"Şu anki tarih ve saat: {current_time_str}. "
        "Zamanla ilgili sorularda bu bilgiyi referans al."
    )

    # Kullanıcı bilgisi varsa kişiselleştir
    if user_info:
        full_name = str(user_info.get("full_name", "")).strip()
        username = str(user_info.get("username", "")).strip()

        if full_name:
            dynamic_sections.append(
                "## Kullanıcı Bilgisi:\n"
                f"Şu an konuştuğun kişinin adı: {full_name}. "
                f"Ona '{full_name} biraderim' diye hitap etmeyi unutma."
            )
        elif username:
            dynamic_sections.append(
                "## Kullanıcı Bilgisi:\n"
                f"Şu an konuştuğun kullanıcı: {username}. "
                f"Ona '{username} biraderim' diye hitap et."
            )

    # Inatçı modeller için Türkçe zorlama yaması
    normalized_model_name = (model_name or "").lower()
    should_enforce_turkish = (
        normalized_model_name
        and ("llama" in normalized_model_name or "gemma" in normalized_model_name)
        and "alibayram/doktorllama3" not in normalized_model_name
    )

    if should_enforce_turkish:
        dynamic_sections.append(
            "!!! DİKKAT !!!: KESİNLİKLE VE SADECE TÜRKÇE CEVAP VER. "
            "ASLA İNGİLİZCE KONUŞMA. MUST ANSWER IN TURKISH."
        )

    return "\n\n".join(dynamic_sections)


def format_web_search_context(search_results: str) -> str:
    """
    Web arama sonuçlarını bir bağlam istemine dönüştürür.
    
    Args:
        search_results: Ham arama sonuçları dizesi
        
    Returns:
        Arama sonuçlarını içeren formatlanmış bağlam istemi
    """
    if not search_results or search_results.strip() == "":
        return NO_SEARCH_RESULTS_PROMPT
    
    return WEB_SEARCH_CONTEXT_PROMPT.format(search_results=search_results)


def build_full_prompt(
    user_message: str,
    web_results: str = "",
    include_system_prompt: bool = True,
    user_info: Optional[Mapping[str, Any]] = None,
    model_name: str = ""
) -> str:
    """
    Yapay zeka modeli için tam istemi oluşturur.
    """
    parts = []
    
    cleaned_user_message = (user_message or "").strip()
    cleaned_web_results = (web_results or "").strip()

    # İstenirse sistem istemini ekle
    if include_system_prompt:
        dynamic_sections = _build_dynamic_system_sections(user_info, model_name)
        system_prompt = SYSTEM_PROMPT
        if dynamic_sections:
            system_prompt = f"{system_prompt}\n\n{dynamic_sections}"
        parts.append(system_prompt)
    
    # Varsa arama bağlamını ekle
    context = ""
    if cleaned_web_results:
        context = format_web_search_context(cleaned_web_results)
    
    if context:
        parts.append(context)
    
    # Kullanıcı mesajını ekle
    parts.append(f"Kullanıcı: {cleaned_user_message}")
    
    return "\n\n".join(parts)
