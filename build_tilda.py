# Собирает tilda-block.html (код для блока T123 в Тильде) из index.html.
# Наш дизайн и наш поп-ап остаются, а заявка уходит через скрытую форму Тильды
# (блок BF502N с #popup:register): так работают Google Таблица и переход в WhatsApp.
import re

BASE = 'https://sultanabdibaevv-droid.github.io/vop-intensiv/'
s = open('index.html', encoding='utf-8').read()

fonts = re.search(r'(<link rel="preconnect"[\s\S]*?display=swap" rel="stylesheet">)', s).group(1)
css = s[s.index('<style>') + 7:s.index('</style>')]
body = s[s.index('<body>') + 6:s.index('</body>')]

# --- scope global rules so they don't touch Tilda's own blocks
for a, b in [
    ('*{box-sizing:border-box;margin:0;padding:0}', '.vop,.vop *{box-sizing:border-box;margin:0;padding:0}'),
    ('html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}', 'html{scroll-behavior:smooth}'),
    ('body{background:var(--bg);', '.vop{background:var(--bg);'),
    ('img{max-width:100%;display:block}', '.vop img{max-width:100%;display:block}'),
    ('\nsection{padding:44px 0}', '\n.vop section{padding:44px 0}'),
    ('  section{padding:84px 0}', '  .vop section{padding:84px 0}'),
    ('footer{padding:30px 0 130px;', '.vop footer{padding:30px 0 130px;'),
    (':root{\n', '.vop{\n'),
    # hide Tilda's own popup trigger visuals; our modal is used instead
]:
    assert a in css, a[:50]
    css = css.replace(a, b, 1)

# --- images -> absolute URLs on GitHub Pages
body = body.replace('src="assets/', 'src="' + BASE + 'assets/').replace('data-src="assets/', 'data-src="' + BASE + 'assets/')

html = body[:body.index('<script>')]
js = body[body.index('<script>') + 8:body.index('</script>')]

# --- submit: instead of our endpoint, fill and submit the hidden Tilda form
old_try = js[js.index('  try {\n    if (FORM_ENDPOINT)'):js.index('  } catch (err) {')]
new_try = '''  try {
    await sendToTilda(name, digits);
    form.style.display = 'none';
    document.getElementById('regOk').style.display = 'block';
    // Тильда сама перекинет в WhatsApp после записи в таблицу; запасной переход через 7 секунд
    setTimeout(() => { location.href = WHATSAPP_GROUP; }, 7000);
'''
js = js.replace(old_try, new_try)
js = js.replace('const FORM_ENDPOINT = "";\n', '')
js = js.replace('''/* ---- submit ---- */''', '''/* ---- bridge to the hidden Tilda form (BF502N, #popup:register) ---- */
function sendToTilda(name, digits) {
  const tf = document.querySelector('form.t-form.js-form-proccess');
  if (!tf) return Promise.reject(new Error('Tilda form not found'));
  const setVal = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  const fire = el => ['input', 'keyup', 'change', 'blur'].forEach(t => el.dispatchEvent(new Event(t, { bubbles: true })));
  const n = tf.querySelector('input[name="Name"]');
  const tel = tf.querySelector('.t-input-phonemask');
  // Тильда принимает в имени только буквы, пробел, дефис и апостроф
  const cleanName = name.replace(/[^\\p{L}\\s'-]/gu, ' ').replace(/\\s+/g, ' ').trim() || 'Аты жоқ';
  setVal.call(n, cleanName); fire(n);
  setVal.call(tel, digits.slice(1)); fire(tel);
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

/* ---- submit ---- */''')
js = js.replace("    alert('Қате шықты, қайта көріңіз.');",
                "    document.querySelector('.agree').textContent = 'Тіркелу өтпеді. Атыңызды тек әріптермен жазып, қайта басыңыз.';")
assert 'sendToTilda(name, digits);' in js and 'alert(' not in js

out = ('<!-- ВОП интенсив · блок T123 для Tilda. Собран из index.html скриптом build_tilda.py.\n'
       '     Заявки уходят через скрытую форму Tilda (#popup:register) → Google Таблица → WhatsApp. -->\n'
       + fonts + '\n<style>\n' + css + '</style>\n<div class="vop">\n' + html.strip() + '\n</div>\n<script>' + js + '</script>\n')
open('tilda-block.html', 'w', encoding='utf-8').write(out)
print(len(out), 'data-open' in out, 'sendToTilda' in out)
