# Собирает kitap/tilda-block.html (код для блока T123 в Тильде) из kitap/index.html.
# Формы нет: кнопки «Сатып алу» сразу открывают WhatsApp.
import re
BASE = 'https://sultanabdibaevv-droid.github.io/vop-intensiv/'
s = open('kitap/index.html', encoding='utf-8').read()
fonts = re.search(r'(<link rel="preconnect"[\s\S]*?display=swap" rel="stylesheet">)', s).group(1)
css = s[s.index('<style>') + 7:s.index('</style>')]
body = s[s.index('<body>') + 6:s.index('</body>')]
for a, b in [
    ('*{box-sizing:border-box;margin:0;padding:0}', '.vop,.vop *{box-sizing:border-box;margin:0;padding:0}'),
    ('html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}', 'html{scroll-behavior:smooth}'),
    ('body{background:var(--bg);', '.vop{background:var(--bg);'),
    ('img{max-width:100%;display:block}', '.vop img{max-width:100%;display:block}'),
    ('\nsection{padding:52px 0}', '\n.vop section{padding:52px 0}'),
    ('  section{padding:80px 0}', '  .vop section{padding:80px 0}'),
    ('\nfooter{padding:26px 0 130px;', '\n.vop footer{padding:26px 0 130px;'),
    (':root{\n', '.vop{\n'),
]:
    assert a in css, a[:50]
    css = css.replace(a, b, 1)
body = re.sub(r'((?:data-)?src|href)="\.\./assets/', lambda m: m.group(1) + '="' + BASE + 'assets/', body)
assert '../assets' not in body
html = body[:body.index('<script>')]
js = body[body.index('<script>') + 8:body.index('</script>')]
out = ('<!-- ВОП ем схема · блок T123 для Tilda. Собран из kitap/index.html скриптом build_tilda_kitap.py. -->\n'
       + fonts + '\n<style>\n' + css + '</style>\n<div class="vop">\n' + html.strip() + '\n</div>\n<script>' + js + '</script>\n')
open('kitap/tilda-block.html', 'w', encoding='utf-8').write(out)
print(len(out))
