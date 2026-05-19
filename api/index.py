"""
Niko AI - Vercel Giriş Noktası
Bu dosya Vercel serverless fonksiyon giriş noktasıdır.
Tüm uygulama mantığı main.py dosyasındadır.
"""

import sys
import os

# Ana dizini Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# .env dosyasını yükle
from dotenv import load_dotenv
load_dotenv()

# Ana uygulamayı import et - Vercel bu 'app' nesnesini kullanır
from main import app
