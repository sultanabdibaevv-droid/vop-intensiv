# Собирает kurs/tilda-block.html (код для блока T123 в Тильде) из kurs/index.html.
# Дизайн и наш поп-ап остаются, заявка уходит через скрытую форму Тильды
# (блок BF502N): поля Name, Phone, Tariff → Google Таблица курса.
import re

BASE = 'https://sultanabdibaevv-droid.github.io/vop-intensiv/'
s = open('kurs/index.html', encoding='utf-8').read()

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
    ('\nfooter{padding:28px 0 130px;', '\n.vop footer{padding:28px 0 130px;'),
    (':root{\n', '.vop{\n'),
]:
    assert a in css, a[:50]
    css = css.replace(a, b, 1)

body = body.replace('src="../assets/', 'src="' + BASE + 'assets/').replace('data-src="../assets/', 'data-src="' + BASE + 'assets/')
html = body[:body.index('<script>')]
js = body[body.index('<script>') + 8:body.index('</script>')]

old = "  if (FORM_ENDPOINT) { try { await fetch(FORM_ENDPOINT, { method: 'POST', mode: 'no-cors', body: JSON.stringify({ name, phone: '+' + digits, tariff }) }); } catch (_) {} }\n  form.style.display = 'none'; document.getElementById('regOk').style.display = 'block';"
assert old in js
js = js.replace(old, """  const btn = document.getElementById('submitBtn');
  btn.disabled = true; btn.textContent = 'Жіберілуде...';
  try {
    await sendToTilda(name, digits, tariff);
    form.style.display = 'none'; document.getElementById('regOk').style.display = 'block';
  } catch (err) {
    btn.disabled = false; btn.textContent = 'Тіркелу';
    document.querySelector('.agree').textContent = 'Тіркелу өтпеді. Атыңызды тек әріптермен жазып, қайта басыңыз.';
  }""")
js = js.replace('const FORM_ENDPOINT = "";\n', '')
js = js.replace("form.addEventListener('submit'", """/* bridge to the hidden Tilda form (BF502N): Name, Phone, Tariff */
function sendToTilda(name, digits, tariff) {
  const tf = document.querySelector('form.t-form.js-form-proccess');
  if (!tf) return Promise.reject(new Error('Tilda form not found'));
  const setVal = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  const fire = el => ['input', 'keyup', 'change', 'blur'].forEach(t => el.dispatchEvent(new Event(t, { bubbles: true })));
  const cleanName = name.replace(/[^\\p{L}\\s'-]/gu, ' ').replace(/\\s+/g, ' ').trim() || 'Аты жоқ';
  const n = tf.querySelector('input[name="Name"]'); setVal.call(n, cleanName); fire(n);
  const tel = tf.querySelector('.t-input-phonemask'); setVal.call(tel, digits.slice(1)); fire(tel);
  const tr = tf.querySelector('input[name="Tariff"]'); if (tr) { setVal.call(tr, tariff); fire(tr); }
  return new Promise((res, rej) => setTimeout(() => {
    tf.querySelector('.t-submit').click();
    setTimeout(() => {
      const box = tf.querySelector('.js-errorbox-all');
      const msg = box && box.offsetParent !== null ? box.innerText.trim() : '';
      const shown = [...tf.querySelectorAll('.t-input-error')].map(e => e.innerText.trim()).filter(Boolean);
      (msg || shown.length) ? rej(new Error(msg || shown[0])) : res();
    }, 1200);
  }, 150));
}

form.addEventListener('submit'""", 1)
assert 'sendToTilda(name, digits, tariff)' in js and 'FORM_ENDPOINT' not in js

out = ('<!-- ВОП жұмысы курсы · блок T123 для Tilda. Собран из kurs/index.html скриптом build_tilda_kurs.py.\n'
       '     Заявки уходят через скрытую форму Tilda → Google Таблица курса. -->\n'
       + fonts + '\n<style>\n' + css + '</style>\n<div class="vop">\n' + html.strip() + '\n</div>\n<script>' + js + '</script>\n')
open('kurs/tilda-block.html', 'w', encoding='utf-8').write(out)
print(len(out))
