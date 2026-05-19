import os
import json
import webbrowser
import uvicorn
import secrets
from typing import Optional, Dict
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import bcrypt
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

from database import UserDB
HOST = "127.0.0.1"
PORT = 8085  # Ana uygulamayla çakışmayı önlemek için farklı port kullanılıyor

app = FastAPI(title="Niko Kullanıcı Yöneticisi")

# CORS'u etkinleştir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modeller ---
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    is_admin: Optional[bool] = False

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

# --- Yardımcı Fonksiyonlar ---
def load_users():
    """Supabase'den tüm kullanıcıları yükle"""
    return UserDB.load_all()

def save_users(users):
    """Geriye dönük uyumluluk için korunuyor - bireysel güncellemeler kullanılır"""
    # Artık JSON dosyasına yazmak yerine doğrudan UserDB metodları kullanılır
    pass

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

# --- HTML İçeriği ---
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Niko Kullanıcı Yönetim Paneli</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body {
            font-family: 'Outfit', sans-serif;
            background-color: #0f172a;
            color: #e2e8f0;
            overflow-x: hidden;
        }
        .glass-panel {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .glass-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .glass-card:hover {
            transform: translateY(-2px);
            background: rgba(30, 41, 59, 0.6);
            border-color: rgba(99, 102, 241, 0.3);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        }
        .neon-text {
            text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
        }
        .custom-scrollbar::-webkit-scrollbar {
            width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: #0f172a;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: #475569;
        }
        .status-badge {
            position: relative;
            overflow: hidden;
        }
        .status-badge::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: 0.5s;
        }
        .status-badge:hover::before {
            left: 100%;
        }
        
        /* Modal Animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        .modal-animate {
            animation: fadeIn 0.2s ease-out forwards;
        }
        
        /* Toast Animation */
        .toast-animate {
            animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        .toast-fade-out {
            animation: fadeOut 0.3s ease-out forwards;
        }
        @keyframes fadeOut {
            from { opacity: 1; transform: scale(1); }
            to { opacity: 0; transform: scale(0.9); }
        }
    </style>
</head>
<body class="min-h-screen relative custom-scrollbar">
    <!-- Background Gradients -->
    <div class="fixed inset-0 z-[-1] overflow-hidden pointer-events-none">
        <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-500/10 rounded-full blur-[100px]"></div>
        <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 rounded-full blur-[100px]"></div>
    </div>

    <!-- Toast Notification Container -->
    <div id="toastContainer" class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 pointer-events-none"></div>

    <div class="container mx-auto px-4 py-8 max-w-7xl">
        <!-- Header -->
        <header class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-10">
            <div class="flex items-center gap-4">
                <div class="p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
                    <i data-lucide="users" class="w-8 h-8 text-indigo-400"></i>
                </div>
                <div>
                    <h1 class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400 neon-text">
                        Kullanıcı Yönetimi
                    </h1>
                    <p class="text-slate-400 text-sm mt-1 font-medium">Supabase Bulut Veritabanı ve Kullanıcı Yönetim Paneli</p>
                </div>
            </div>
            
            <div class="flex flex-wrap items-center gap-3">
                <button onclick="openAddModal()" class="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:from-indigo-600 hover:to-purple-600 transition-all font-semibold shadow-md shadow-indigo-500/15 border border-indigo-500/20">
                    <i data-lucide="user-plus" class="w-4 h-4"></i> Yeni Kullanıcı
                </button>
                <button onclick="fetchUsers()" class="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors border border-slate-700 font-medium">
                    <i data-lucide="refresh-cw" class="w-4 h-4"></i> Yenile
                </button>
                <div class="px-4 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
                    Sistem Aktif
                </div>
            </div>
        </header>

        <!-- Stats & Actions -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="glass-panel p-6 rounded-2xl">
                <div class="text-slate-400 text-sm font-medium mb-2">Toplam Kullanıcı</div>
                <div class="text-4xl font-bold text-white" id="totalUsers">0</div>
            </div>
            <div class="glass-panel p-6 rounded-2xl relative overflow-hidden group">
                <div class="absolute right-0 top-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                    <i data-lucide="alert-triangle" class="w-16 h-16 text-amber-500"></i>
                </div>
                <div class="text-slate-400 text-sm font-medium mb-2">Hatalı Hesaplar</div>
                <div class="text-4xl font-bold text-amber-500" id="faultyUsers">0</div>
                <p class="text-xs text-amber-500/60 mt-2">Eksik bilgi içeren hesaplar</p>
            </div>
            <div class="glass-panel p-6 rounded-2xl flex items-center justify-between">
                <div>
                    <div class="text-slate-400 text-sm font-medium mb-1">Veritabanı Sağlayıcısı</div>
                    <div class="text-xs text-slate-300 font-bold flex items-center gap-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                        Supabase Cloud (PostgreSQL)
                    </div>
                </div>
                <div class="p-3 bg-emerald-500/10 rounded-lg">
                    <i data-lucide="cloud-lightning" class="w-6 h-6 text-emerald-400"></i>
                </div>
            </div>
        </div>

        <!-- Users Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fadeIn" id="usersGrid">
            <!-- Loading State -->
            <div class="col-span-2 flex justify-center py-20">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
            </div>
        </div>
    </div>

    <!-- Add User Modal -->
    <div id="addModal" class="fixed inset-0 z-50 hidden">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" onclick="closeAddModal()"></div>
        <div class="absolute inset-0 flex items-center justify-center p-4">
            <div class="glass-panel w-full max-w-md rounded-2xl p-6 modal-animate" id="addModalContent">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-xl font-bold text-white flex items-center gap-2">
                        <i data-lucide="user-plus" class="w-5 h-5 text-indigo-400"></i>
                        Yeni Kullanıcı Ekle
                    </h3>
                    <button onclick="closeAddModal()" class="text-slate-400 hover:text-white transition-colors">
                        <i data-lucide="x" class="w-5 h-5"></i>
                    </button>
                </div>

                <form id="addForm" onsubmit="handleAddUser(event)" class="space-y-4">
                    <div class="space-y-1">
                        <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Kullanıcı Adı</label>
                        <input type="text" id="addUsername" required placeholder="Örn: ahmet123" class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all placeholder:text-slate-600">
                    </div>

                    <div class="space-y-1">
                        <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">E-posta</label>
                        <input type="email" id="addEmail" required placeholder="Örn: ahmet@example.com" class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all placeholder:text-slate-600">
                    </div>

                    <div class="space-y-1">
                        <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Ad Soyad</label>
                        <input type="text" id="addFullName" required placeholder="Örn: Ahmet Yılmaz" class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all placeholder:text-slate-600">
                    </div>

                    <div class="space-y-1">
                         <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Şifre</label>
                         <input type="text" id="addPassword" required placeholder="En az 6 karakter" class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all placeholder:text-slate-600">
                    </div>

                    <div class="flex items-center gap-3 pt-2">
                        <label class="flex items-center gap-2 cursor-pointer group">
                            <input type="checkbox" id="addIsAdmin" class="w-4 h-4 rounded border-slate-700 bg-slate-900 text-indigo-500 focus:ring-offset-0 focus:ring-indigo-500/20">
                            <span class="text-sm text-slate-300 group-hover:text-white transition-colors">Yönetici Yetkisi</span>
                        </label>
                    </div>

                    <div class="pt-6 grid grid-cols-2 gap-3">
                        <button type="button" onclick="closeAddModal()" class="w-full px-4 py-2.5 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white transition-colors text-sm font-medium">İptal</button>
                        <button type="submit" class="w-full px-4 py-2.5 rounded-lg bg-indigo-500 hover:bg-indigo-600 text-white transition-colors text-sm font-medium shadow-lg shadow-indigo-500/20">Oluştur</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- Edit User Modal -->
    <div id="editModal" class="fixed inset-0 z-50 hidden">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" onclick="closeModal()"></div>
        <div class="absolute inset-0 flex items-center justify-center p-4">
            <div class="glass-panel w-full max-w-md rounded-2xl p-6 modal-animate" id="modalContent">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-xl font-bold text-white flex items-center gap-2">
                        <i data-lucide="user-cog" class="w-5 h-5 text-indigo-400"></i>
                        Kullanıcı Düzenle
                    </h3>
                    <button onclick="closeModal()" class="text-slate-400 hover:text-white transition-colors">
                        <i data-lucide="x" class="w-5 h-5"></i>
                    </button>
                </div>

                <form id="editForm" onsubmit="handleInitialSave(event)" class="space-y-4">
                    <input type="hidden" id="editUsername">
                    
                    <div class="space-y-1">
                        <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Kullanıcı Adı</label>
                        <input type="text" id="displayUsername" disabled class="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-300 cursor-not-allowed">
                    </div>

                    <div class="space-y-1">
                        <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">E-posta</label>
                        <input type="email" id="editEmail" class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all placeholder:text-slate-600">
                    </div>

                    <div class="space-y-1">
                        <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Ad Soyad</label>
                        <input type="text" id="editFullName" class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all placeholder:text-slate-600">
                    </div>

                    <div class="space-y-1">
                         <label class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Şifre Değiştir (Opsiyonel)</label>
                         <input type="text" id="editPassword" placeholder="Değiştirmek için yeni şifre yazın" class="w-full bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all placeholder:text-slate-600">
                    </div>

                    <div class="flex items-center gap-3 pt-2">
                        <label class="flex items-center gap-2 cursor-pointer group">
                            <input type="checkbox" id="editIsAdmin" class="w-4 h-4 rounded border-slate-700 bg-slate-900 text-indigo-500 focus:ring-offset-0 focus:ring-indigo-500/20">
                            <span class="text-sm text-slate-300 group-hover:text-white transition-colors">Yönetici Yetkisi</span>
                        </label>
                    </div>

                    <div class="pt-6 grid grid-cols-2 gap-3">
                        <button type="button" onclick="closeModal()" class="w-full px-4 py-2.5 rounded-lg border border-slate-700 text-slate-300 hover:bg-slate-800 hover:text-white transition-colors text-sm font-medium">İptal</button>
                        <button type="submit" class="w-full px-4 py-2.5 rounded-lg bg-indigo-500 hover:bg-indigo-600 text-white transition-colors text-sm font-medium shadow-lg shadow-indigo-500/20">Kaydet</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script>
        lucide.createIcons();
        let usersData = {};

        // Dynamic gradient picker for avatars based on username hash
        function getAvatarStyles(username) {
            const gradients = [
                { from: 'from-indigo-500/20', to: 'to-purple-500/20', border: 'border-indigo-500/30', text: 'text-indigo-400' },
                { from: 'from-pink-500/20', to: 'to-rose-500/20', border: 'border-pink-500/30', text: 'text-pink-400' },
                { from: 'from-blue-500/20', to: 'to-cyan-500/20', border: 'border-blue-500/30', text: 'text-blue-400' },
                { from: 'from-emerald-500/20', to: 'to-teal-500/20', border: 'border-emerald-500/30', text: 'text-emerald-400' },
                { from: 'from-violet-500/20', to: 'to-fuchsia-500/20', border: 'border-violet-500/30', text: 'text-violet-400' },
                { from: 'from-amber-500/20', to: 'to-orange-500/20', border: 'border-amber-500/30', text: 'text-amber-400' }
            ];
            
            let hash = 0;
            for (let i = 0; i < username.length; i++) {
                hash = username.charCodeAt(i) + ((hash << 5) - hash);
            }
            const index = Math.abs(hash) % gradients.length;
            return gradients[index];
        }

        // Custom Toast Notification System
        function showToast(message, type = 'success') {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = `glass-panel px-4 py-3 rounded-xl flex items-center gap-3 shadow-lg border toast-animate max-w-sm pointer-events-auto`;
            
            let iconColor = 'text-emerald-400';
            let iconName = 'check-circle';
            let borderColor = 'border-emerald-500/20';
            let bgGradient = 'bg-emerald-500/10';
            
            if (type === 'error') {
                iconColor = 'text-rose-400';
                iconName = 'alert-triangle';
                borderColor = 'border-rose-500/20';
                bgGradient = 'bg-rose-500/10';
            } else if (type === 'info') {
                iconColor = 'text-sky-400';
                iconName = 'info';
                borderColor = 'border-sky-500/20';
                bgGradient = 'bg-sky-500/10';
            }
            
            toast.classList.add(borderColor, bgGradient);
            
            toast.innerHTML = `
                <div class="p-1.5 rounded-lg bg-white/5 ${iconColor}">
                    <i data-lucide="${iconName}" class="w-5 h-5"></i>
                </div>
                <div class="text-sm font-medium text-slate-200 pr-2">${message}</div>
                <button onclick="this.parentElement.remove()" class="ml-auto text-slate-400 hover:text-white transition-colors">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            `;
            
            container.appendChild(toast);
            lucide.createIcons();
            
            setTimeout(() => {
                toast.classList.add('toast-fade-out');
                toast.addEventListener('animationend', () => {
                    toast.remove();
                });
            }, 4000);
        }

        async function fetchUsers() {
            try {
                const response = await fetch('/api/users');
                usersData = await response.json();
                renderUsers();
            } catch (err) {
                console.error('Kullanıcılar getirilerken hata:', err);
                showToast('Kullanıcılar yüklenirken bir hata oluştu', 'error');
            }
        }

        function isFaulty(user) {
            return !user.email || !user.full_name || !user.password;
        }

        function renderUsers() {
            const grid = document.getElementById('usersGrid');
            grid.innerHTML = '';
            
            let faultyCount = 0;
            const userList = Object.entries(usersData);
            document.getElementById('totalUsers').innerText = userList.length;

            userList.forEach(([username, user]) => {
                const faulty = isFaulty(user);
                if (faulty) faultyCount++;

                const card = document.createElement('div');
                card.className = `glass-card rounded-xl p-5 relative overflow-hidden group ${faulty ? 'border-amber-500/30 bg-amber-500/5' : ''}`;
                
                const colors = getAvatarStyles(username);
                const hasPassword = !!user.password;

                card.innerHTML = `
                    <div class="flex justify-between items-start mb-4">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-full bg-gradient-to-tr ${colors.from} ${colors.to} border ${colors.border} ${colors.text} flex items-center justify-center font-bold text-lg select-none">
                                ${username.charAt(0).toUpperCase()}
                            </div>
                            <div>
                                <h3 class="font-bold text-white tracking-wide flex items-center gap-1.5">
                                    ${username}
                                    ${user.is_admin ? '<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center gap-0.5">🛡️ Admin</span>' : ''}
                                </h3>
                                <div class="text-xs ${faulty ? 'text-amber-400' : 'text-slate-400'}">
                                    ${user.is_admin ? 'Yönetici Hesabı' : 'Standart Kullanıcı'}
                                </div>
                            </div>
                        </div>
                        <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button onclick="openEditModal('${username}')" class="p-2 rounded-lg hover:bg-white/10 text-slate-300 hover:text-white transition-colors" title="Düzenle">
                                <i data-lucide="edit-2" class="w-4 h-4"></i>
                            </button>
                            <button onclick="deleteUser('${username}')" class="p-2 rounded-lg hover:bg-red-500/20 text-slate-300 hover:text-red-400 transition-colors" title="Sil">
                                <i data-lucide="trash-2" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </div>
                    
                    <div class="space-y-3 text-sm">
                        <div class="flex justify-between items-center py-1 border-b border-white/5">
                            <span class="text-slate-500">E-posta</span>
                            <span class="text-slate-300 font-mono ${!user.email ? 'text-amber-500 italic' : ''}">${user.email || 'Eksik'}</span>
                        </div>
                        <div class="flex justify-between items-center py-1 border-b border-white/5">
                            <span class="text-slate-500">Ad Soyad</span>
                            <span class="text-slate-300 ${!user.full_name ? 'text-amber-500 italic' : ''}">${user.full_name || 'Eksik'}</span>
                        </div>
                        
                        <div class="flex justify-between items-center py-1 border-b border-white/5">
                            <span class="text-slate-500">Şifre</span>
                            <div class="font-mono text-sm text-indigo-300 bg-indigo-500/10 px-2.5 py-1 rounded selectable-text">
                                ${user._plain_password ? user._plain_password : '<span class="text-slate-500 text-xs italic flex items-center gap-1 cursor-help" title="Bu kullanıcı eski sistemden aktarıldığı için düz şifresi yoktur. Şifreyi düzenleyip yenisini yazarak düz metin olarak görünmesini sağlayabilirsiniz."><i data-lucide="lock" class="w-3 h-3"></i> Hash (Gizli)</span>'}
                            </div>
                        </div>

                        <div class="flex justify-between items-center py-1 pt-2">
                             <span class="text-slate-500 text-xs">Oluşturuldu</span>
                             <span class="text-slate-400 text-xs">${user.created_at ? new Date(user.created_at).toLocaleDateString("tr-TR") : '-'}</span>
                        </div>
                    </div>
                    
                    ${faulty ? `
                        <div class="absolute bottom-0 left-0 w-full h-1 bg-amber-500/50"></div>
                        <div class="absolute top-2 right-2">
                           <span class="flex h-2 w-2">
                              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                              <span class="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
                            </span>
                        </div>
                    ` : ''}
                `;
                grid.appendChild(card);
            });
            
            document.getElementById('faultyUsers').innerText = faultyCount;
            lucide.createIcons();
        }

        // Add User Modal controllers
        function openAddModal() {
            document.getElementById('addForm').reset();
            const modal = document.getElementById('addModal');
            modal.classList.remove('hidden');
        }

        function closeAddModal() {
            document.getElementById('addModal').classList.add('hidden');
        }

        async function handleAddUser(e) {
            e.preventDefault();
            const username = document.getElementById('addUsername').value.trim();
            const email = document.getElementById('addEmail').value.trim();
            const fullName = document.getElementById('addFullName').value.trim();
            const password = document.getElementById('addPassword').value;
            const isAdmin = document.getElementById('addIsAdmin').checked;
            
            if (!username || !email || !fullName || !password) {
                showToast('Lütfen tüm zorunlu alanları doldurun.', 'error');
                return;
            }
            
            if (password.length < 6) {
                showToast('Şifre en az 6 karakter olmalıdır.', 'error');
                return;
            }
            
            try {
                const res = await fetch('/api/users', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username,
                        email,
                        full_name: fullName,
                        password,
                        is_admin: isAdmin
                    })
                });
                
                if (res.ok) {
                    showToast('Kullanıcı başarıyla oluşturuldu.', 'success');
                    closeAddModal();
                    fetchUsers();
                } else {
                    const errText = await res.text();
                    let detail = 'Bir hata oluştu';
                    try {
                        const errJson = JSON.parse(errText);
                        detail = errJson.detail || detail;
                    } catch(e) {}
                    showToast('Hata: ' + detail, 'error');
                }
            } catch (err) {
                console.error(err);
                showToast('Bir ağ hatası oluştu.', 'error');
            }
        }

        // Edit User Modal controllers
        function openEditModal(username) {
            const user = usersData[username];
            document.getElementById('editUsername').value = username;
            document.getElementById('displayUsername').value = username;
            document.getElementById('editEmail').value = user.email || '';
            document.getElementById('editFullName').value = user.full_name || '';
            document.getElementById('editIsAdmin').checked = user.is_admin || false;
            document.getElementById('editPassword').value = ''; 
            
            const modal = document.getElementById('editModal');
            modal.classList.remove('hidden');
        }

        function closeModal() {
            document.getElementById('editModal').classList.add('hidden');
        }

        async function handleInitialSave(e) {
            e.preventDefault();
            const username = document.getElementById('editUsername').value;
            const data = {
                email: document.getElementById('editEmail').value.trim(),
                full_name: document.getElementById('editFullName').value.trim(),
                is_admin: document.getElementById('editIsAdmin').checked
            };
            
            const pass = document.getElementById('editPassword').value;
            if (pass && pass.trim() !== '') {
                if (pass.length < 6) {
                    showToast('Şifre en az 6 karakter olmalıdır.', 'error');
                    return;
                }
                data.password = pass;
            }

            try {
                const res = await fetch(`/api/users/${username}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (res.ok) {
                    showToast('Kullanıcı başarıyla güncellendi.', 'success');
                    closeModal();
                    fetchUsers();
                } else {
                    const errText = await res.text();
                    let detail = 'Güncelleme başarısız';
                    try {
                        const errJson = JSON.parse(errText);
                        detail = errJson.detail || detail;
                    } catch(e) {}
                    showToast('Hata: ' + detail, 'error');
                }
            } catch (err) {
                console.error(err);
                showToast('Bir hata oluştu', 'error');
            }
        }

        // toggleHash kaldırıldı - şifreler doğrudan düz metin olarak listeleniyor, hash olanlar gizli kalıyor.

        async function deleteUser(username) {
            if (!confirm(`"${username}" kullanıcısını silmek istediğinize emin misiniz?`)) return;
            
            try {
                const res = await fetch(`/api/users/${username}`, {
                    method: 'DELETE'
                });
                
                if (res.ok) {
                    showToast('Kullanıcı başarıyla silindi.', 'success');
                    fetchUsers();
                } else {
                    showToast('Kullanıcı silinemedi.', 'error');
                }
            } catch (err) {
                console.error(err);
                showToast('Bir hata oluştu', 'error');
            }
        }

        // Başlangıç
        fetchUsers();
    </script>
</body>
</html>
"""

# --- API Uç Noktaları ---

@app.get("/")
async def get_ui():
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/api/users")
async def get_users():
    return load_users()

@app.post("/api/users")
async def create_user(new_user: UserCreate):
    username = new_user.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Kullanıcı adı boş olamaz")
        
    if UserDB.get(username) is not None:
        raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten kullanılmaktadır")
        
    email = new_user.email.strip()
    if not email:
        raise HTTPException(status_code=400, detail="E-posta adresi boş olamaz")
        
    full_name = new_user.full_name.strip()
    password = new_user.password
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Şifre en az 6 karakter olmalıdır")
        
    user_data = {
        "password": hash_password(password),
        "_plain_password": password,
        "email": email,
        "full_name": full_name,
        "is_admin": new_user.is_admin or False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    success = UserDB.create(username, user_data)
    if not success:
        raise HTTPException(status_code=500, detail="Kullanıcı oluşturulurken veritabanı hatası meydana geldi")
        
    return {"message": "Kullanıcı başarıyla oluşturuldu"}

@app.put("/api/users/{username}")
async def update_user(username: str, update: UserUpdate):
    user = UserDB.get(username)
    if user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    db_updates = {}
    if update.email is not None:
        db_updates["email"] = update.email
    if update.full_name is not None:
        db_updates["full_name"] = update.full_name
    if update.is_admin is not None:
        db_updates["is_admin"] = update.is_admin
    if update.password is not None and len(update.password) > 0:
        if len(update.password) < 6:
            raise HTTPException(status_code=400, detail="Şifre en az 6 karakter olmalıdır")
        db_updates["password"] = hash_password(update.password)
        db_updates["plain_password"] = update.password
    
    if db_updates:
        UserDB.update(username, db_updates)
    return {"message": "Kullanıcı güncellendi"}

@app.delete("/api/users/{username}")
async def delete_user(username: str):
    if UserDB.get(username) is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    
    UserDB.delete(username)
    return {"message": "Kullanıcı silindi"}

if __name__ == "__main__":
    print("Kullanıcı Yönetim Sistemi başlatılıyor...")
    # Kısa bir gecikmeden sonra tarayıcıyı aç
    webbrowser.open(f"http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
