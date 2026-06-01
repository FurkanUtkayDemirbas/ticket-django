import os

filepath = 'panel/templates/index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace header section
old_header = '''<div class="mb-10 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
    <div>
        <h1 class="text-3xl font-black text-slate-900 tracking-tight">Merhaba, Utkay 👋</h1>
        <p class="text-sm text-slate-500 font-medium">Sistemin genel durumu ve güncel veriler aşağıdadır.</p>
    </div>'''

new_header = '''<div class="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
    <div>
        <h1 class="text-2xl font-bold text-slate-800 tracking-wide mb-2">Sistem Özeti</h1>
        <p class="text-sm text-slate-500 font-medium">İşletmenizin anlık durumunu buradan takip edebilirsiniz.</p>
    </div>'''
content = content.replace(old_header, new_header)

# Card 1: Toplam Muhatap (Mavi)
old_card1 = '''    <!-- Müşteri (Blue Card) -->
    <div class="bg-[#eff6ff] p-6 rounded-3xl border border-[#dbeafe] shadow-sm hover:shadow-md transition group relative overflow-hidden">
        <div class="absolute -right-4 -top-4 w-16 h-16 bg-blue-100 rounded-full group-hover:scale-150 transition-transform duration-500 opacity-30"></div>
        <div class="relative">
            <div class="flex items-center justify-between mb-4">
                <div class="w-10 h-10 bg-blue-600 text-white rounded-xl flex items-center justify-center shadow-md shadow-blue-500/20">
                    <i class="fa-solid fa-user-group text-sm"></i>
                </div>
                <span class="text-[10px] font-bold text-blue-600 bg-blue-100/50 px-2 py-1 rounded-lg uppercase tracking-wider">Müşteri</span>
            </div>
            <h4 class="text-3xl font-black text-blue-900">{{ toplam_muhatap }}</h4>
            <p class="text-xs text-blue-700 mt-1 font-medium">Kayıtlı Muhataplar</p>
        </div>
    </div>'''

new_card1 = '''    <!-- Müşteri (Blue Card - Vollcar Style) -->
    <div class="bg-[#f0f7ff] p-6 rounded-xl border border-blue-100/50 shadow-sm flex items-center justify-between relative overflow-hidden">
        <div>
            <h4 class="text-xs font-bold text-blue-800 uppercase tracking-wider mb-3">TOPLAM MUHATAP</h4>
            <span class="text-3xl font-extrabold text-[#1e3a8a]">{{ toplam_muhatap }}</span>
        </div>
        <div class="w-12 h-12 bg-[#dbeafe] rounded-full flex items-center justify-center shadow-inner">
            <i class="fa-solid fa-user-group text-blue-600 text-lg"></i>
        </div>
    </div>'''
content = content.replace(old_card1, new_card1)

# Card 2: Bekleyen İşler (Sarı)
old_card2 = '''    <!-- Bekleyen (Yellow Card) -->
    <div class="bg-[#fffbeb] p-6 rounded-3xl border border-[#fef3c7] shadow-sm hover:shadow-md transition group relative overflow-hidden">
        <div class="absolute -right-4 -top-4 w-16 h-16 bg-amber-100 rounded-full group-hover:scale-150 transition-transform duration-500 opacity-30"></div>
        <div class="relative">
            <div class="flex items-center justify-between mb-4">
                <div class="w-10 h-10 bg-amber-500 text-white rounded-xl flex items-center justify-center shadow-md shadow-amber-500/20">
                    <i class="fa-solid fa-clock text-sm"></i>
                </div>
                <span class="text-[10px] font-bold text-amber-700 bg-amber-100/50 px-2 py-1 rounded-lg uppercase tracking-wider">Bekleyen</span>
            </div>
            <h4 class="text-3xl font-black text-amber-900">{{ acik_ticketlar }}</h4>
            <p class="text-xs text-amber-700 mt-1 font-medium">İşlem Bekleyenler</p>
        </div>
    </div>'''

new_card2 = '''    <!-- Bekleyen (Yellow Card - Vollcar Style) -->
    <div class="bg-[#fffbf0] p-6 rounded-xl border border-amber-100/50 shadow-sm flex items-center justify-between relative overflow-hidden">
        <div>
            <h4 class="text-xs font-bold text-amber-700 uppercase tracking-wider mb-3">BEKLEYEN İŞLER</h4>
            <span class="text-3xl font-extrabold text-amber-600">{{ acik_ticketlar }}</span>
        </div>
        <div class="w-12 h-12 bg-[#fef3c7] rounded-full flex items-center justify-center shadow-inner">
            <i class="fa-solid fa-clock text-amber-600 text-lg"></i>
        </div>
    </div>'''
content = content.replace(old_card2, new_card2)

# Card 3: Tamamlanan (Yeşil)
old_card3 = '''    <!-- Çözüldü (Green Card) -->
    <div class="bg-[#f0fdf4] p-6 rounded-3xl border border-[#dcfce7] shadow-sm hover:shadow-md transition group relative overflow-hidden">
        <div class="absolute -right-4 -top-4 w-16 h-16 bg-emerald-100 rounded-full group-hover:scale-150 transition-transform duration-500 opacity-30"></div>
        <div class="relative">
            <div class="flex items-center justify-between mb-4">
                <div class="w-10 h-10 bg-emerald-500 text-white rounded-xl flex items-center justify-center shadow-md shadow-emerald-500/20">
                    <i class="fa-solid fa-check-double text-sm"></i>
                </div>
                <span class="text-[10px] font-bold text-emerald-700 bg-emerald-100/50 px-2 py-1 rounded-lg uppercase tracking-wider">Çözüldü</span>
            </div>
            <h4 class="text-3xl font-black text-emerald-900">{{ tamamlanan_count }}</h4>
            <p class="text-xs text-emerald-700 mt-1 font-medium">Toplam Başarı</p>
        </div>
    </div>'''

new_card3 = '''    <!-- Çözüldü (Green Card - Vollcar Style) -->
    <div class="bg-[#f0fdf4] p-6 rounded-xl border border-emerald-100/50 shadow-sm flex items-center justify-between relative overflow-hidden">
        <div>
            <h4 class="text-xs font-bold text-emerald-700 uppercase tracking-wider mb-3">ÇÖZÜLENLER</h4>
            <span class="text-3xl font-extrabold text-emerald-600">{{ tamamlanan_count }}</span>
        </div>
        <div class="w-12 h-12 bg-[#dcfce7] rounded-full flex items-center justify-center shadow-inner">
            <i class="fa-solid fa-check-circle text-emerald-600 text-lg"></i>
        </div>
    </div>'''
content = content.replace(old_card3, new_card3)

# Card 4: Sözleşme (Beyaz)
old_card4 = '''    <!-- Sözleşme (White Card) -->
    <div class="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm hover:shadow-md transition group relative overflow-hidden">
        <div class="absolute -right-4 -top-4 w-16 h-16 bg-slate-50 rounded-full group-hover:scale-150 transition-transform duration-500 opacity-50"></div>
        <div class="relative">
            <div class="flex items-center justify-between mb-4">
                <div class="w-10 h-10 bg-slate-800 text-white rounded-xl flex items-center justify-center shadow-md shadow-slate-800/20">
                    <i class="fa-solid fa-file-signature text-sm"></i>
                </div>
                <span class="text-[10px] font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded-lg uppercase tracking-wider">Sözleşme</span>
            </div>
            <h4 class="text-3xl font-black text-slate-800">{{ toplam_sozlesme }}</h4>
            <p class="text-xs text-slate-400 mt-1 font-medium">Aktif Anlaşmalar</p>
        </div>
    </div>'''

new_card4 = '''    <!-- Sözleşme (White Card - Vollcar Style) -->
    <div class="bg-white p-6 rounded-xl border border-slate-100 shadow-sm flex items-center justify-between relative overflow-hidden">
        <div>
            <h4 class="text-xs font-bold text-slate-600 uppercase tracking-wider mb-3">TOPLAM SÖZLEŞME</h4>
            <span class="text-3xl font-extrabold text-slate-800">{{ toplam_sozlesme }}</span>
        </div>
        <div class="w-12 h-12 bg-slate-100 rounded-full flex items-center justify-center shadow-inner">
            <i class="fa-solid fa-file-contract text-slate-600 text-lg"></i>
        </div>
    </div>'''
content = content.replace(old_card4, new_card4)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated index.html successfully')
