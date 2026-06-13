#!/usr/bin/env python3
"""
最简密码门：给 200KB 单页 test2.html 加一个密码门
原则：不碰原 test2.html 的任何内容，只在 <head> 后注入独立 overlay + 校验 JS
"""
import re
from pathlib import Path

PASSWORD = "baisi2026"

# 完整的密码门：自包含样式 + 校验脚本 + overlay HTML
# 用最小 CSS 作用域（#baisiGate *），绝对不会污染原 test2.html 的样式
PWD_GATE = """
<!-- Baisi password gate (injected) -->
<style>
#baisiGate {
  position: fixed; inset: 0; z-index: 2147483647;
  background: linear-gradient(135deg, #0d0905 0%, #170d02 50%, #0d0905 100%);
  display: flex; align-items: center; justify-content: center;
  padding: 24px; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
}
#baisiGate.hidden { display: none; }
#baisiGate .box {
  background: #1d1107; border: 1px solid #3a2614; border-radius: 12px;
  padding: 48px 40px; max-width: 420px; width: 100%;
  box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  text-align: center;
}
#baisiGate .logo { color: #ffac02; font-weight: 800; font-size: 13px; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 16px; }
#baisiGate h1 { color: #f5e9d5; font-size: 24px; font-weight: 800; margin-bottom: 8px; }
#baisiGate h1 span { color: #ffac02; }
#baisiGate .sub { color: #a89080; font-size: 13px; margin-bottom: 28px; }
#baisiGate input {
  width: 100%; background: #0d0905; border: 1px solid #3a2614;
  border-radius: 6px; padding: 14px 16px; color: #f5e9d5;
  font-size: 16px; outline: none; box-sizing: border-box; margin-bottom: 12px;
  font-family: inherit;
}
#baisiGate input:focus { border-color: #ffac02; }
#baisiGate input::placeholder { color: #6e5a48; }
#baisiGate button {
  width: 100%; background: linear-gradient(135deg, #ffac02 0%, #edff45 100%);
  border: none; border-radius: 6px; padding: 14px;
  color: #170d02; font-size: 16px; font-weight: 700; cursor: pointer;
  font-family: inherit;
}
#baisiGate .err { color: #ff5e5e; font-size: 13px; min-height: 20px; margin-top: 12px; }
#baisiGate .hint { margin-top: 24px; padding-top: 24px; border-top: 1px solid #3a2614; color: #6e5a48; font-size: 12px; line-height: 1.6; }
#baisiGate .lock-btn {
  position: fixed; top: 16px; right: 16px; z-index: 1000;
  background: #1d1107; border: 1px solid #3a2614; color: #a89080;
  padding: 6px 12px; border-radius: 4px; font-size: 12px; cursor: pointer;
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif;
}
#baisiGate .lock-btn:hover { border-color: #ff5e5e; color: #ff5e5e; }
</style>
<div id="baisiGate">
  <div class="box">
    <div class="logo">百思传媒 · 内部资料</div>
    <h1>影视娱乐号 <span>诊断报告</span></h1>
    <p class="sub">5 个账号 · 9 份报告 · 仅限内部访问</p>
    <input type="password" id="baisiPwd" placeholder="请输入密码" autocomplete="off">
    <button id="baisiBtn">🔓 解锁</button>
    <div class="err" id="baisiErr"></div>
    <div class="hint">内部资料 · 请勿外传<br>密码错误请向项目负责人索取</div>
  </div>
</div>
<button class="lock-btn" id="baisiLock" style="display:none;">🔒 锁屏</button>
<script>
(function(){
  var PWD = "baisi2026";
  var KEY = "baisi_unlocked";
  var gate = document.getElementById('baisiGate');
  var inp = document.getElementById('baisiPwd');
  var btn = document.getElementById('baisiBtn');
  var err = document.getElementById('baisiErr');
  var lock = document.getElementById('baisiLock');
  function unlock() {
    localStorage.setItem(KEY, '1');
    gate.classList.add('hidden');
    lock.style.display = 'block';
  }
  function relock() {
    localStorage.removeItem(KEY);
    location.reload();
  }
  function check() {
    if (inp.value === PWD) {
      unlock();
    } else {
      err.textContent = '密码错误，请重试';
      inp.value = '';
      inp.focus();
    }
  }
  btn.addEventListener('click', check);
  inp.addEventListener('keydown', function(e){ if (e.key === 'Enter') check(); });
  lock.addEventListener('click', relock);
  // 已解锁过直接进入
  if (localStorage.getItem(KEY) === '1') {
    unlock();
  } else {
    setTimeout(function(){ inp.focus(); }, 100);
  }
})();
</script>
<!-- /Baisi password gate -->
"""


def main():
    targets = [Path("test2.html"), Path("test.html")]
    for target in targets:
        if not target.exists():
            print(f"{target} 不存在，跳过")
            continue
        html = target.read_text(encoding="utf-8")

        # 检查是否已经注入过（避免重复）
        if 'id="baisiGate"' in html:
            print(f"{target} 已经注入过密码门，跳过")
            continue

        # 注入到 <body> 之后（不是 </head> 之前）
        # 这样密码门在所有内容之上，但不影响原 HTML 的 CSS 加载
        out_html = re.sub(r'(<body[^>]*>)', r'\1' + PWD_GATE, html, count=1)

        target.write_text(out_html, encoding="utf-8")
        size_kb = target.stat().st_size / 1024
        print(f"✓ {target} ({size_kb:.1f} KB) — 已注入最简密码门")


if __name__ == "__main__":
    main()
