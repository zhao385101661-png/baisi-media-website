#!/usr/bin/env python3
"""
拆分 test2.html 成多页结构 + 加密码门
- test2.html: 密码门 + 目录页（9 张卡片 + 链接）
- test2/index.html: 报告 1 (原 index 总览)
- test2/B-sop.html: 报告 2
- test2/B.html: 报告 3
- test2/compare.html: 报告 4
- test2/action.html: 报告 5
- test2/A.html: 报告 6
- test2/C.html: 报告 7
- test2/D.html: 报告 8
- test2/E.html: 报告 9
"""
import re
from pathlib import Path

REPORTS_DIR = Path("../xiaohongshu-analysis/reports")
TEST2_DIR = Path("test2")  # 9 个子报告放这里
OUT_DIR = Path(".")  # 顶层是 test2.html 入口 + test.html

PASSWORD = "baisi2026"  # 密码

# 报告顺序（目录页按此排序）
REPORT_ORDER = [
    ("index", "总览", "首页/9 报告导航"),
    ("B-sop", "B 账号 90 天 SOP", "急救+重定位执行手册"),
    ("B", "B 西湖边的夏雨荷", "单号报告 - 最弱号诊断"),
    ("compare", "5 号横向对比", "数据矩阵 + 健康度排名"),
    ("action", "整改建议", "P0/P1/P2 行动清单 + 资源分配"),
    ("A", "A 满级观众", "单号报告 - 主号候选"),
    ("C", "C 一个奈斯的观众", "单号报告 - 标杆号"),
    ("D", "D 没错我是高贵路人", "单号报告 - 差异化人设"),
    ("E", "E 追娱少女", "单号报告 - 男粉稀缺位"),
]


def extract_body(html):
    m = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    return m.group(1) if m else html


def extract_css(html):
    css = []
    for m in re.finditer(r'<style[^>]*>(.*?)</style>', html, re.DOTALL):
        css.append(m.group(1))
    return "\n".join(css)


def clean_body_for_subpage(body):
    """子页面：去掉 nav（重复），去掉 hero 内的 nav"""
    body = re.sub(r'<nav.*?</nav>', '', body, flags=re.DOTALL)
    return body


def make_password_gate(title, content_url, success_redirect):
    """密码门 HTML - 输入正确密码后跳转到目标页"""
    # 用 JS 验证，密码哈希存储在前端（轻量防护，不是真安全）
    # 真正安全需要后端，这里是给团队内部用的
    pwd_hash = hashlib_sha256(PASSWORD)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - 内部资料</title>
  <meta name="robots" content="noindex, nofollow">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      background: linear-gradient(135deg, #0d0905 0%, #170d02 50%, #0d0905 100%);
      color: #f5e9d5;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }}
    .gate {{
      background: #1d1107;
      border: 1px solid #3a2614;
      border-radius: 12px;
      padding: 48px 40px;
      max-width: 440px;
      width: 100%;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }}
    .gate-logo {{
      color: #ffac02;
      font-weight: 800;
      font-size: 14px;
      letter-spacing: 3px;
      text-transform: uppercase;
      margin-bottom: 16px;
      text-align: center;
    }}
    .gate-title {{
      font-size: 28px;
      font-weight: 800;
      text-align: center;
      margin-bottom: 8px;
    }}
    .gate-title span {{ color: #ffac02; }}
    .gate-sub {{
      color: #a89080;
      font-size: 14px;
      text-align: center;
      margin-bottom: 32px;
    }}
    .gate-form {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .gate-input {{
      background: #0d0905;
      border: 1px solid #3a2614;
      border-radius: 6px;
      padding: 14px 16px;
      color: #f5e9d5;
      font-size: 16px;
      width: 100%;
      outline: none;
      transition: border-color .2s;
    }}
    .gate-input:focus {{ border-color: #ffac02; }}
    .gate-input::placeholder {{ color: #6e5a48; }}
    .gate-btn {{
      background: linear-gradient(135deg, #ffac02 0%, #edff45 100%);
      border: none;
      border-radius: 6px;
      padding: 14px 16px;
      color: #170d02;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
      transition: transform .1s, box-shadow .2s;
    }}
    .gate-btn:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(255,172,2,0.3); }}
    .gate-btn:active {{ transform: translateY(0); }}
    .gate-error {{
      color: #ff5e5e;
      font-size: 13px;
      text-align: center;
      min-height: 20px;
    }}
    .gate-hint {{
      margin-top: 24px;
      padding-top: 24px;
      border-top: 1px solid #3a2614;
      color: #6e5a48;
      font-size: 12px;
      text-align: center;
      line-height: 1.6;
    }}
  </style>
</head>
<body>
  <div class="gate">
    <div class="gate-logo">百思传媒 · 内部资料</div>
    <h1 class="gate-title">{title}</h1>
    <p class="gate-sub">此页面需要密码访问</p>
    <form class="gate-form" onsubmit="return checkPwd(event)">
      <input type="password" id="pwd" class="gate-input" placeholder="请输入密码" autocomplete="off" autofocus>
      <button type="submit" class="gate-btn">🔓 解锁</button>
      <div class="gate-error" id="err"></div>
    </form>
    <div class="gate-hint">
      内部资料 · 请勿外传<br>
      密码错误请向项目负责人索取
    </div>
  </div>
  <script>
    // 简单哈希
    async function sha256(text) {{
      const buf = new TextEncoder().encode(text);
      const hash = await crypto.subtle.digest('SHA-256', buf);
      return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2,'0')).join('');
    }}
    const CORRECT_HASH = "{pwd_hash}";
    const TARGET_URL = "{success_redirect}";
    const SESSION_KEY = "baisi_pwd_ok";
    async function checkPwd(e) {{
      e.preventDefault();
      const pwd = document.getElementById('pwd').value;
      const err = document.getElementById('err');
      err.textContent = '';
      const h = await sha256(pwd);
      if (h === CORRECT_HASH) {{
        // 存 session - 同一会话内免输
        sessionStorage.setItem(SESSION_KEY, '1');
        sessionStorage.setItem(SESSION_KEY + '_hash', h);
        window.location.href = TARGET_URL;
      }} else {{
        err.textContent = '密码错误，请重试';
        document.getElementById('pwd').value = '';
        document.getElementById('pwd').focus();
      }}
      return false;
    }}
    // 已解锁过直接跳
    if (sessionStorage.getItem(SESSION_KEY) === '1' && sessionStorage.getItem(SESSION_KEY + '_hash') === CORRECT_HASH) {{
      window.location.href = TARGET_URL;
    }}
  </script>
</body>
</html>"""


def hashlib_sha256(s):
    """前置计算的 SHA-256 (Python hashlib 替代浏览器 crypto.subtle)"""
    import hashlib
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


# ============= 入口页：test2.html =============
def make_entry_page():
    """test2.html - 密码门 + 目录页 (用 JS 在客户端做密码校验+渲染)"""
    # 思路：单文件包含密码门 + 目录 + 跳转逻辑
    # 用户输入密码 → JS 校验 → 通过后渲染目录卡片
    pwd_hash = hashlib_sha256(PASSWORD)

    cards = []
    colors = ["ffac02", "54a87e", "edff45", "ff5e5e", "ffac02", "54a87e", "edff45", "ff5e5e", "ffac02"]
    icons = ["🎬", "🚑", "⚠️", "📊", "🚨", "📘", "📗", "📙", "📕"]
    for i, (rid, title, desc) in enumerate(REPORT_ORDER):
        cards.append(f"""
      <div class="card" style="--accent: #{colors[i]};" data-target="{rid}.html">
          <div class="card-icon">{icons[i]}</div>
          <div class="card-body">
            <div class="card-title">{title}</div>
            <div class="card-desc">{desc}</div>
          </div>
          <div class="card-arrow">→</div>
        </a>
        """)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>百思传媒 · 影视娱乐号诊断报告 - 内部资料</title>
  <meta name="robots" content="noindex, nofollow">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      background: #0d0905;
      color: #f5e9d5;
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}

    /* 密码门 */
    .gate {{
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      background: linear-gradient(135deg, #0d0905 0%, #170d02 50%, #0d0905 100%);
    }}
    .gate-box {{
      background: #1d1107;
      border: 1px solid #3a2614;
      border-radius: 12px;
      padding: 48px 40px;
      max-width: 440px;
      width: 100%;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }}
    .gate-logo {{ color: #ffac02; font-weight: 800; font-size: 14px; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 16px; text-align: center; }}
    .gate-title {{ font-size: 28px; font-weight: 800; text-align: center; margin-bottom: 8px; }}
    .gate-title span {{ color: #ffac02; }}
    .gate-sub {{ color: #a89080; font-size: 14px; text-align: center; margin-bottom: 32px; }}
    .gate-form {{ display: flex; flex-direction: column; gap: 16px; }}
    .gate-input {{ background: #0d0905; border: 1px solid #3a2614; border-radius: 6px; padding: 14px 16px; color: #f5e9d5; font-size: 16px; outline: none; transition: border-color .2s; }}
    .gate-input:focus {{ border-color: #ffac02; }}
    .gate-input::placeholder {{ color: #6e5a48; }}
    .gate-btn {{ background: linear-gradient(135deg, #ffac02 0%, #edff45 100%); border: none; border-radius: 6px; padding: 14px 16px; color: #170d02; font-size: 16px; font-weight: 700; cursor: pointer; transition: transform .1s, box-shadow .2s; }}
    .gate-btn:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(255,172,2,0.3); }}
    .gate-error {{ color: #ff5e5e; font-size: 13px; text-align: center; min-height: 20px; }}
    .gate-hint {{ margin-top: 24px; padding-top: 24px; border-top: 1px solid #3a2614; color: #6e5a48; font-size: 12px; text-align: center; line-height: 1.6; }}

    /* 目录页 */
    .portal {{ display: none; min-height: 100vh; }}
    .portal.unlocked {{ display: block; }}

    .hero {{
      background: linear-gradient(135deg, #170d02 0%, #261609 50%, #170d02 100%);
      border-bottom: 2px solid #ffac02;
      padding: 80px 0 60px;
      position: relative;
      overflow: hidden;
    }}
    .hero::before {{
      content: ''; position: absolute; top: 0; right: 0; width: 600px; height: 600px;
      background: radial-gradient(circle, rgba(255,172,2,0.12) 0%, transparent 70%);
      pointer-events: none;
    }}
    .container {{ max-width: 1280px; margin: 0 auto; padding: 0 24px; position: relative; }}
    .hero-meta {{ color: #54a87e; font-size: 14px; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px; }}
    .hero h1 {{ font-size: 52px; font-weight: 800; line-height: 1.1; margin-bottom: 16px; }}
    .hero h1 span {{ color: #ffac02; }}
    .hero .sub {{ color: #a89080; font-size: 18px; max-width: 800px; margin-bottom: 24px; }}
    .hero .meta-row {{ display: flex; gap: 12px; flex-wrap: wrap; }}
    .hero .meta-pill {{ background: #1d1107; border: 1px solid #3a2614; padding: 6px 12px; border-radius: 4px; font-size: 13px; color: #a89080; }}
    .hero .meta-pill b {{ color: #ffac02; }}

    section {{ padding: 64px 0; }}
    .section-label {{ color: #ffac02; font-size: 13px; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 8px; }}
    .section-title {{ font-size: 36px; font-weight: 800; margin-bottom: 12px; }}
    .section-sub {{ color: #a89080; font-size: 16px; margin-bottom: 32px; }}

    .grid {{ display: grid; gap: 20px; grid-template-columns: repeat(3, 1fr); }}
    @media (max-width: 1024px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    @media (max-width: 640px) {{ .grid {{ grid-template-columns: 1fr; }} }}

    .card {{
      display: flex; align-items: center; gap: 16px;
      background: #1d1107;
      border: 1px solid #3a2614;
      border-left: 4px solid var(--accent, #ffac02);
      border-radius: 8px;
      padding: 24px;
      text-decoration: none; color: inherit;
      transition: transform .15s, border-color .2s, background .2s;
    }}
    .card:hover {{
      transform: translateY(-2px);
      background: #261609;
      border-color: var(--accent, #ffac02);
    }}
    .card-icon {{ font-size: 32px; flex-shrink: 0; }}
    .card-body {{ flex: 1; }}
    .card-title {{ font-size: 18px; font-weight: 700; margin-bottom: 4px; }}
    .card-desc {{ color: #a89080; font-size: 13px; }}
    .card-arrow {{ color: #ffac02; font-size: 24px; font-weight: 700; }}

    .alert {{
      padding: 16px 20px;
      border-radius: 6px;
      margin-bottom: 16px;
      border-left: 4px solid;
      display: flex; align-items: flex-start; gap: 12px;
    }}
    .alert-info {{ background: rgba(84,168,126,0.08); border-color: #54a87e; }}
    .alert-warn {{ background: rgba(255,172,2,0.08); border-color: #ffac02; }}
    .alert-danger {{ background: rgba(255,94,94,0.08); border-color: #ff5e5e; }}
    .alert-body {{ flex: 1; color: #f5e9d5; font-size: 14px; }}
    .alert-title {{ font-weight: 700; margin-bottom: 4px; }}

    footer {{ background: #170d02; padding: 32px 0; text-align: center; color: #6e5a48; font-size: 13px; border-top: 1px solid #3a2614; }}
    .logout-btn {{
      position: fixed; top: 16px; right: 16px;
      background: #1d1107; border: 1px solid #3a2614;
      color: #a89080; padding: 6px 12px; border-radius: 4px;
      font-size: 12px; cursor: pointer; z-index: 100;
    }}
    .logout-btn:hover {{ border-color: #ff5e5e; color: #ff5e5e; }}
  </style>
</head>
<body>
  <!-- 密码门 -->
  <div class="gate" id="gate">
    <div class="gate-box">
      <div class="gate-logo">百思传媒 · 内部资料</div>
      <h1 class="gate-title">影视娱乐号 <span>诊断报告</span></h1>
      <p class="gate-sub">5 个账号 · 9 份报告 · 仅限内部访问</p>
      <form class="gate-form" onsubmit="return checkPwd(event)">
        <input type="password" id="pwd" class="gate-input" placeholder="请输入密码" autocomplete="off" autofocus>
        <button type="submit" class="gate-btn">🔓 解锁</button>
        <div class="gate-error" id="err"></div>
      </form>
      <div class="gate-hint">内部资料 · 请勿外传<br>密码错误请向项目负责人索取</div>
    </div>
  </div>

  <!-- 目录页 -->
  <div class="portal" id="portal">
    <button class="logout-btn" onclick="logout()">🔒 锁屏</button>
    <header class="hero">
      <div class="container">
        <div class="hero-meta">百思传媒 · 内部诊断资料</div>
        <h1>影视娱乐号 <span>诊断报告合集</span></h1>
        <p class="sub">5 个影视娱乐小红书号 · 9 份报告 · 数据基于公开页 30-32 篇样本 · 生成于 2026-06-13</p>
        <div class="meta-row">
          <div class="meta-pill">5 个 <b>账号</b></div>
          <div class="meta-pill">9 份 <b>报告</b></div>
          <div class="meta-pill">~155 篇 <b>笔记样本</b></div>
          <div class="meta-pill">同质化 <b>矩阵</b></div>
        </div>
      </div>
    </header>

    <section>
      <div class="container">
        <div class="section-label">REPORTS</div>
        <h2 class="section-title">9 份报告</h2>
        <p class="section-sub">点击进入单份报告 · 同一会话内免输密码</p>

        <div class="alert alert-danger">
          <div class="alert-body">
            <div class="alert-title">⚠️ 矩阵预警</div>
            5 个号全由同一公司运营（IP 山西 / @Yanan 小助理 / 影视娱乐），同质化 100%；B 号（西湖边的夏雨荷）已近算法降权边缘，<b>必须立即介入</b>。
          </div>
        </div>

        <div class="grid">
          {''.join(cards)}
        </div>
      </div>
    </section>

    <section style="padding-top: 0;">
      <div class="container">
        <div class="section-label">QUICK READ</div>
        <h2 class="section-title">核心结论 (3 分钟读完)</h2>

        <div class="alert alert-warn">
          <div class="alert-body">
            <div class="alert-title">最弱号 B - 急救</div>
            30 篇笔记 12 篇低赞 (40%)，6 篇死 (0-5 赞)。<b>本周：停发 7 天 + 隐藏死笔记 + 改简介去 @Yanan</b>。详见 B 报告 + B-sop。
          </div>
        </div>
        <div class="alert alert-info">
          <div class="alert-body">
            <div class="alert-title">最强号 C - 标杆</div>
            均赞 6183 / 爆款率 12%，是矩阵里的健康标杆。把 C 的爆款逻辑写成 SOP 复制到 A/D/E。详见 C 报告。
          </div>
        </div>
        <div class="alert alert-warn">
          <div class="alert-body">
            <div class="alert-title">差异化机会</div>
            5 个号全部"剧情切片"赛道，差异化严重不足。考虑孵化 1-2 个新赛道号（古装女主/男粉向/行业视角）。
          </div>
        </div>
      </div>
    </section>
  </div>

  <footer>
    <div class="container">
      <p>百思传媒旗下影视娱乐号诊断报告 · 内部资料 · 生成于 2026-06-13</p>
      <p style="color: #3a2614; margin-top: 8px; font-size: 12px;">数据来源: 小红书公开页 · 建议登录后台复查真实互动数据</p>
    </div>
  </footer>

  <script>
    async function sha256(text) {{
      const buf = new TextEncoder().encode(text);
      const hash = await crypto.subtle.digest('SHA-256', buf);
      return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2,'0')).join('');
    }}
    const CORRECT_PWD = "baisi2026";
    const LS_KEY = "baisi_unlocked";

    function checkPwd(e) {{
      e.preventDefault();
      const pwd = document.getElementById('pwd').value;
      const err = document.getElementById('err');
      if (pwd === CORRECT_PWD) {{
        localStorage.setItem(LS_KEY, '1');
        unlock();
      }} else {{
        err.textContent = '密码错误，请重试';
        document.getElementById('pwd').value = '';
        document.getElementById('pwd').focus();
      }}
      return false;
    }}

    function unlock() {{
      document.getElementById('gate').style.display = 'none';
      document.getElementById('portal').classList.add('unlocked');
      document.title = '百思传媒 · 影视娱乐号诊断报告 (已解锁)';
    }}

    function logout() {{
      localStorage.removeItem(LS_KEY);
      location.reload();
    }}

    // 已解锁过直接进
    if (localStorage.getItem(LS_KEY) === '1') {{
      unlock();
    }}
  </script>
</body>
</html>"""


# ============= 9 个子报告页 =============
def make_subpage(src_file, out_file, title):
    """输出子页：顶部导航条 + 检查 localStorage 决定是否跳转回入口"""
    src = REPORTS_DIR / src_file
    if not src.exists():
        print(f"跳过 {src_file}: 不存在")
        return False
    html = src.read_text(encoding="utf-8")

    # 只注入样式 + 导航条 + 跳转检查
    injection = f"""
    <style>
      .subpage-nav {{
        position: sticky; top: 0; z-index: 100;
        background: #170d02; border-bottom: 2px solid #ffac02;
        padding: 12px 24px;
        display: flex; align-items: center; gap: 16px;
        font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
        font-size: 14px;
      }}
      .subpage-nav a {{ color: #ffac02; text-decoration: none; font-weight: 600; }}
      .subpage-nav a:hover {{ color: #edff45; }}
      .subpage-nav .title {{ color: #f5e9d5; font-weight: 700; flex: 1; }}
      .subpage-nav .lock-btn {{
        background: #1d1107; border: 1px solid #3a2614; color: #a89080;
        padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer;
        font-family: inherit;
      }}
      .subpage-nav .lock-btn:hover {{ border-color: #ff5e5e; color: #ff5e5e; }}
    </style>
    <script>
      // 共享 localStorage 标志 - 入口页解锁后所有子页免输密码
      if (localStorage.getItem('baisi_unlocked') !== '1') {{
        window.location.href = '../test2.html';
      }}
      function subLogout() {{
        localStorage.removeItem('baisi_unlocked');
        window.location.href = '../test2.html';
      }}
    </script>
    """

    sub_nav = f"""
    <div class="subpage-nav">
      <a href="../test2.html">← 返回目录</a>
      <span class="title">{title}</span>
      <button class="lock-btn" onclick="subLogout()">🔒 锁屏</button>
    </div>
    """

    # 在 </head> 前注入样式+脚本
    out_html = html.replace('</head>', injection + '</head>', 1)
    # 在 <body ...> 后插入 nav
    out_html = re.sub(r'(<body[^>]*>)', r'\1' + sub_nav, out_html, count=1)

    target = TEST2_DIR / out_file
    target.write_text(out_html, encoding="utf-8")
    print(f"✓ {target}")
    return True


# ============= 给 test.html 加跳转检查 =============
def patch_test_html():
    """test.html 改为检查 localStorage 决定是否跳转回 test2.html 解锁"""
    target = Path("test.html")
    if not target.exists():
        print(f"test.html 不存在")
        return False
    html = target.read_text(encoding="utf-8")

    # 注入脚本：未解锁跳到 test2.html
    # 同时在 body 开头插入顶部导航条（返回 test2.html + 锁屏）
    injection = """
    <style>
      .subpage-nav {
        position: sticky; top: 0; z-index: 100;
        background: #170d02; border-bottom: 2px solid #ffac02;
        padding: 12px 24px;
        display: flex; align-items: center; gap: 16px;
        font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
        font-size: 14px;
      }
      .subpage-nav a { color: #ffac02; text-decoration: none; font-weight: 600; }
      .subpage-nav a:hover { color: #edff45; }
      .subpage-nav .title { color: #f5e9d5; font-weight: 700; flex: 1; }
      .subpage-nav .lock-btn {
        background: #1d1107; border: 1px solid #3a2614; color: #a89080;
        padding: 4px 10px; border-radius: 4px; font-size: 12px; cursor: pointer;
        font-family: inherit;
      }
      .subpage-nav .lock-btn:hover { border-color: #ff5e5e; color: #ff5e5e; }
    </style>
    <script>
      if (localStorage.getItem('baisi_unlocked') !== '1') {
        window.location.href = 'test2.html';
      }
      function subLogout() {
        localStorage.removeItem('baisi_unlocked');
        window.location.href = 'test2.html';
      }
    </script>
    """
    sub_nav = """
    <div class="subpage-nav">
      <a href="test2.html">← 返回目录</a>
      <span class="title">test.html · 旧报告</span>
      <button class="lock-btn" onclick="subLogout()">🔒 锁屏</button>
    </div>
    """

    # 在 </head> 前注入样式+脚本
    if '</head>' in html:
        out_html = html.replace('</head>', '</head>' + injection, 1)
    else:
        out_html = injection + html
    # 在 <body ...> 后插入 nav
    out_html = re.sub(r'(<body[^>]*>)', r'\1' + sub_nav, out_html, count=1)

    target.write_text(out_html, encoding="utf-8")
    print(f"✓ {target} (加 localStorage 跳转检查)")
    return True


# ============= 主程序 =============
def main():
    # 创建 test2 目录
    TEST2_DIR.mkdir(exist_ok=True)

    # 1. test2.html 入口页 (密码门 + 目录)
    entry = make_entry_page()
    Path("test2.html").write_text(entry, encoding="utf-8")
    print(f"✓ test2.html (入口)")

    # 2. 9 个子报告
    title_map = {
        "index": "总览 - 5 号诊断概览",
        "B-sop": "B 账号 90 天重生 SOP",
        "B": "B 西湖边的夏雨荷 - 单号报告",
        "compare": "5 号横向对比",
        "action": "整改建议 - P0/P1/P2",
        "A": "A 满级观众 - 单号报告",
        "C": "C 一个奈斯的观众 - 单号报告",
        "D": "D 没错我是高贵路人 - 单号报告",
        "E": "E 追娱少女 - 单号报告",
    }
    file_map = {
        "index": "index.html",
        "B-sop": "B-sop.html",
        "B": "B.html",
        "compare": "compare.html",
        "action": "action.html",
        "A": "A.html",
        "C": "C.html",
        "D": "D.html",
        "E": "E.html",
    }
    for rid, _, _ in REPORT_ORDER:
        make_subpage(file_map[rid], f"{rid}.html", title_map[rid])

    # 3. test.html 加密码门
    patch_test_html()

    # 4. 列出最终结构
    print("\n=== 最终部署结构 ===")
    print("./test.html  (密码门 + 旧内容)")
    print("./test2.html (密码门 + 9 张卡片目录)")
    print("./test2/")
    for rid, title, desc in REPORT_ORDER:
        print(f"  ├── {rid}.html  ({title})")


if __name__ == "__main__":
    main()
