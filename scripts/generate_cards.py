import requests
import os

GITHUB_USER = "phoenixhsien"          # 请换成你的用户名
TOKEN = os.environ["GH_TOKEN"]        # 从 Actions 环境获取
HEADERS = {"Authorization": f"token {TOKEN}"}

def fetch_data():
    """抓取公开统计信息"""
    user_resp = requests.get(f"https://api.github.com/users/{GITHUB_USER}", headers=HEADERS).json()
    repos_resp = requests.get(f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100", headers=HEADERS).json()

    total_stars = sum(r["stargazers_count"] for r in repos_resp)
    total_forks = sum(r["forks_count"] for r in repos_resp)
    public_repos = user_resp["public_repos"]
    followers = user_resp["followers"]

    lang_bytes = {}
    for r in repos_resp:
        if r["fork"] or r["language"] is None:
            continue
        lang_bytes[r["language"]] = lang_bytes.get(r["language"], 0) + r.get("size", 0) * 1024

    return {
        "stars": total_stars,
        "forks": total_forks,
        "repos": public_repos,
        "followers": followers,
        "langs": lang_bytes
    }

# ---------- 公用样式 ----------
COMMON_STYLE = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&amp;display=swap');
        .bg { fill: #0D1117; }
        .border-glow { stroke: #FF8C00; stroke-width: 2.5; filter: drop-shadow(0 0 6px #FF8C00); }
        .label { font-family: 'Fira Code', monospace; font-size: 12px; fill: #FF8C00; opacity: 0.9; }
        .value { font-family: 'Fira Code', monospace; font-size: 16px; fill: #FFFFFF; font-weight: bold; }
        .poem { font-family: 'Fira Code', monospace; font-size: 9px; fill: #FF8C00; opacity: 0.6; }
        .cursor { animation: blink 1s step-end infinite; }
        @keyframes blink { 50% { opacity: 0; } }
    </style>
"""

# ---------- 卡片1：总览卡片（终端式） ----------
def draw_stats_card(data):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="200" viewBox="0 0 420 200">
  {COMMON_STYLE}
  <rect class="bg" width="420" height="200" rx="12" />
  <rect class="border-glow" width="420" height="200" rx="12" fill="none" />

  <text x="20" y="35" class="label">[phoenix@jarvis]$ cat /home/stats</text>
  <text x="20" y="35" class="value" fill="#FF8C00" font-size="12">
    <tspan class="cursor">█</tspan>
  </text>

  <text x="30" y="70" class="label">├─ ⭐ Stars      :</text>
  <text x="200" y="70" class="value">{data["stars"]}</text>

  <text x="30" y="100" class="label">├─ 📦 Repos      :</text>
  <text x="200" y="100" class="value">{data["repos"]}</text>

  <text x="30" y="130" class="label">├─ 👥 Followers  :</text>
  <text x="200" y="130" class="value">{data["followers"]}</text>

  <text x="30" y="160" class="label">└─ 🍴 Forks      :</text>
  <text x="200" y="160" class="value">{data["forks"]}</text>

  <text x="250" y="190" class="poem">~ weaving dreams into code</text>
</svg>'''
    return svg

# ---------- 卡片2：语言比例条（反应堆风格） ----------
def draw_languages_card(lang_bytes):
    if not lang_bytes:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="50"><text x="10" y="30" fill="#FF8C00">No languages</text></svg>'

    total = sum(lang_bytes.values())
    sorted_langs = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)[:5]

    colors = {
        "Python": "#3776AB",
        "Java": "#ED8B00",
        "C": "#00599C",
        "JavaScript": "#F7DF1E",
        "TypeScript": "#3178C6",
        "Rust": "#DEA584",
        "Go": "#00ADD8",
        "Kotlin": "#A97BFF",
        "Swift": "#F05138",
        "Blockchain": "#FF8C00"
    }

    bar_y = 70
    bar_height = 24
    x_start = 30
    bar_width = 360
    rects = ""
    x = x_start
    for lang, bytes_count in sorted_langs:
        ratio = bytes_count / total
        w = max(bar_width * ratio, 4)
        color = colors.get(lang, "#FF8C00")
        rects += f'<rect x="{x:.0f}" y="{bar_y}" width="{w:.0f}" height="{bar_height}" fill="{color}" rx="4" />'
        x += w

    legend = ""
    y = bar_y + bar_height + 18
    x = x_start
    for lang, bytes_count in sorted_langs:
        color = colors.get(lang, "#FF8C00")
        pct = bytes_count / total * 100
        legend += f'<rect x="{x}" y="{y}" width="10" height="10" fill="{color}" rx="2" />'
        legend += f'<text x="{x+16}" y="{y+10}" class="label" font-size="11" fill="#FFFFFF">{lang} ({pct:.1f}%)</text>'
        x += 130
        if x > x_start + 260:
            x = x_start
            y += 22

    svg_height = max(y + 40, 130)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="420" height="{svg_height}" viewBox="0 0 420 {svg_height}">
  {COMMON_STYLE}
  <rect class="bg" width="420" height="{svg_height}" rx="12" />
  <rect class="border-glow" width="420" height="{svg_height}" rx="12" fill="none" />

  <text x="20" y="35" class="label">[phoenix@jarvis]$ cat /home/lang_distribution</text>
  <text x="20" y="35" class="value" fill="#FF8C00" font-size="12">
    <tspan class="cursor">█</tspan>
  </text>

  {rects}
  {legend}
  <text x="250" y="{svg_height-10}" class="poem">~ my pigments of creation</text>
</svg>'''
    return svg

if __name__ == "__main__":
    data = fetch_data()
    with open("stats.svg", "w") as f:
        f.write(draw_stats_card(data))
    with open("languages.svg", "w") as f:
        f.write(draw_languages_card(data["langs"]))
    print("✨ Cards generated with soul.")