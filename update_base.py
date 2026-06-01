import os
import re

filepath = 'panel/templates/base.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace body background
content = content.replace('bg-[#f8fafc]', 'bg-[#f8f9fa]')
content = content.replace("font-family: 'Inter', sans-serif;", "font-family: 'Nunito', sans-serif;")
content = content.replace('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap', 'https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700;800;900&display=swap')
content = content.replace("'Inter', sans-serif", "'Nunito', sans-serif")

# Replace aside classes
content = content.replace('w-64 bg-[#0c1524] border-r-[3px] border-[#3b82f6] flex flex-col shadow-xl', 'w-[260px] bg-[#0b1221] flex flex-col shadow-2xl z-20')
content = content.replace('text-xl font-black tracking-wider text-[#3b82f6] uppercase', 'text-2xl font-extrabold tracking-wide text-blue-500 uppercase')
# Remove padding from nav, Vollcar items touch the edges
content = content.replace('<nav class="flex-1 px-4 space-y-1 overflow-y-auto">', '<nav class="flex-1 space-y-1 overflow-y-auto mt-4">')

# Update active/inactive links
new_base = 'flex items-center space-x-3 py-3 px-8 transition-all duration-200'
content = content.replace('flex items-center space-x-3 p-3 rounded-lg transition', new_base)

content = content.replace('bg-[#1e293b] text-white font-semibold', 'bg-[#151f32] text-white font-bold border-l-[5px] border-blue-500')
content = content.replace('text-slate-400 hover:text-white hover:bg-[#1e293b]/50', 'text-slate-400 hover:text-white hover:bg-[#151f32]/50 border-l-[5px] border-transparent')
content = content.replace('flex items-center space-x-3 p-2 rounded-lg transition', 'flex items-center space-x-3 py-2 px-8 transition-all duration-200 border-l-[5px] border-transparent')

# Add top header inside main
main_start = '<main class="flex-1 flex flex-col overflow-y-auto">'
top_header = """
            <header class="bg-white px-8 py-4 flex items-center justify-between sticky top-0 z-10 border-b border-gray-100 shadow-sm">
                <div class="text-slate-800 font-bold text-lg tracking-wide">Hoş Geldin</div>
                <div class="flex items-center space-x-4">
                    <span class="text-sm font-semibold text-slate-500">{{ request.user.username|default:"admin" }}</span>
                </div>
            </header>
"""
if 'Hoş Geldin' not in content:
    content = content.replace(main_start, main_start + top_header)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('Updated base.html successfully')
