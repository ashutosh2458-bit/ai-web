"""Layout Chat Studio: runs in the browser via Pyodide (Python compiled to WebAssembly).
A rule-based chatbot plus basic tools edit one `STATE` dict; page(), css() and js() turn it into code."""
import colorsys, copy, html as _html, json, re

SEC = {
    "hero": ("Hero", ["hero", "banner"]),
    "features": ("Features", ["feature", "benefit", "service"]),
    "stats": ("Stats", ["stat", "number", "metric"]),
    "pricing": ("Pricing", ["pricing", "price", "plan"]),
    "testimonial": ("Testimonial", ["testimonial", "review", "quote"]),
    "faq": ("FAQ", ["faq", "question"]),
    "contact": ("Contact form", ["contact", "form"]),
    "cta": ("Call to action", ["cta", "call to action", "signup", "sign up"]),
    "footer": ("Footer", ["footer"]),
}
FONTS = {"sans": "system-ui,-apple-system,'Segoe UI',sans-serif", "serif": "Georgia,'Times New Roman',serif",
         "rounded": "'Trebuchet MS','Segoe UI',sans-serif", "mono": "ui-monospace,'SFMono-Regular',Menlo,monospace"}
COLORS = {"red": "#e5383b", "orange": "#f77f00", "yellow": "#e9b800", "gold": "#c9951a", "green": "#2b9348",
          "lime": "#6aa84f", "teal": "#0f9d94", "cyan": "#0aa5c0", "blue": "#2a6fdb", "navy": "#1f3a8a",
          "indigo": "#4a3fd1", "purple": "#8a3ffc", "violet": "#8a3ffc", "pink": "#e0408f", "rose": "#e11d48",
          "brown": "#8a5a3c", "gray": "#5b6b7a", "grey": "#5b6b7a", "black": "#1b1f24"}
DEFAULT = dict(brand="Brandname", accent="#2a44e8", dark=False, font="sans", radius=12, space=80, width=1120,
               nav="top", hero="split", cols=3, cards="cards", js=False,
               sections=["hero", "features", "stats", "cta", "footer"])
CH = {"font": tuple(FONTS), "nav": ("top", "center", "pill"), "hero": ("split", "reverse", "center", "big"),
      "cards": ("cards", "lines")}
RNG = {"radius": (0, 32), "space": (32, 128), "width": (880, 1320), "cols": (2, 4)}


def clean(s):
    o = copy.deepcopy(DEFAULT)
    for k, v in (s or {}).items():
        try:
            if k == "brand":
                o[k] = str(v).strip()[:30] or o[k]
            elif k == "accent":
                if re.fullmatch(r"#[0-9a-fA-F]{6}", str(v)):
                    o[k] = str(v).lower()
            elif k in ("dark", "js"):
                o[k] = bool(v)
            elif k in CH:
                if v in CH[k]:
                    o[k] = v
            elif k in RNG:
                o[k] = max(RNG[k][0], min(RNG[k][1], int(v)))
            elif k == "sections":
                o[k] = [x for x in dict.fromkeys(v) if x in SEC]
        except (TypeError, ValueError):
            pass
    return o


# ---------------------------------------------------------------- colors
def rgb(c): return [int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)]
def hls(c): return colorsys.rgb_to_hls(*rgb(c))
def lum(c): r, g, b = rgb(c); return .2126 * r + .7152 * g + .0722 * b
def hsl(h, s, l): return f"hsl({h * 360:.0f},{s * 100:.0f}%,{l * 100:.0f}%)"


def tokens(s, dark):
    h, l, sat = hls(s["accent"])
    t = .25 if sat > .1 else 0
    if dark:
        return f"--bg:{hsl(h, t, .09)};--fg:#eef1f6;--sf:{hsl(h, t * .9, .14)};--ln:{hsl(h, t * .7, .24)}"
    return f"--bg:{hsl(h, t * 1.5, .97)};--fg:#18202b;--sf:#fff;--ln:{hsl(h, t, .86)}"


# ---------------------------------------------------------------- CSS
BLOCK = {
    "base": """*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font-family:@FONT@;line-height:1.55}
.c{max-width:var(--w);margin:0 auto;padding:0 24px}
section{padding:var(--sp) 0}
h1{font-size:clamp(34px,5vw,60px);line-height:1.05;margin:0 0 16px}
h2{font-size:clamp(26px,3.5vw,38px);margin:0 0 28px}
.btn{display:inline-block;background:var(--ac);color:var(--on);padding:12px 22px;border-radius:var(--r);text-decoration:none;border:0;cursor:pointer;font:inherit;font-weight:600}
""",
    "nav": """nav .c{display:flex;align-items:center;justify-content:space-between;padding-top:20px;padding-bottom:20px}
nav a{margin-left:20px;color:inherit;text-decoration:none}
""",
    "hero": """.hero .c{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center}
.art{aspect-ratio:4/3;width:100%;border-radius:var(--r);background:linear-gradient(135deg,var(--ac),var(--ac2))}
@media(max-width:760px){.hero .c{grid-template-columns:1fr}}
""",
    "card": """.card{padding:24px;border-radius:var(--r);background:var(--sf);border:1px solid var(--ln)}
.card h3{margin:0 0 6px}.card p{margin:0;opacity:.75}
""",
    "features": """.grid{display:grid;grid-template-columns:repeat(@COLS@,1fr);gap:24px}
.lines .card{background:none;border:0;border-top:2px solid var(--fg);border-radius:0;padding-left:0}
.icon{width:40px;height:40px;border-radius:var(--r);background:var(--ac2);margin-bottom:14px}
@media(max-width:760px){.grid{grid-template-columns:1fr}}
""",
    "stats": """.stats .c{display:flex;justify-content:space-around;text-align:center;flex-wrap:wrap;gap:24px}
.stats b{display:block;font-size:44px;color:var(--ac2)}
""",
    "pricing": """.plans{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.plans .hot{border:2px solid var(--ac)}.plans ul{padding-left:18px;margin:12px 0 20px}
.price{font-size:36px;font-weight:800;margin:6px 0}
@media(max-width:760px){.plans{grid-template-columns:1fr}}
""",
    "testimonial": """.quote{font-size:clamp(22px,3vw,34px);max-width:760px;margin:0 auto 12px;text-align:center}
""",
    "faq": """.faq .c{max-width:760px}
details{border-top:1px solid var(--ln);padding:16px 0}details:last-child{border-bottom:1px solid var(--ln)}
summary{cursor:pointer;font-weight:600}details p{margin:10px 0 0;opacity:.8}
""",
    "contact": """.contact .c{max-width:560px}
form{display:grid;gap:14px}label{display:grid;gap:6px;font-weight:600;font-size:14px}
input,textarea{font:inherit;padding:12px;border:1px solid var(--ln);border-radius:var(--r);background:var(--sf);color:inherit;width:100%}
""",
    "cta": """.cta .c{background:var(--ac);color:var(--on);border-radius:var(--r);padding:56px 24px;text-align:center}
.cta h2{margin-bottom:20px}.cta .btn{background:var(--on);color:var(--ac)}
""",
    "footer": "footer{border-top:1px solid var(--ln);padding:32px 0;font-size:14px;opacity:.85}\n",
}
NAVV = {"top": "",
        "center": "nav.center .c{flex-direction:column;gap:12px}nav.center a{margin:0 10px}\n",
        "pill": "nav.pill .c{margin-top:16px;max-width:calc(var(--w) - 80px);background:var(--sf);border:1px solid var(--ln);border-radius:999px;padding:12px 28px}\n"}
HEROV = {"split": "", "reverse": ".hero.reverse .art{order:-1}\n",
         "center": ".hero.center .c{grid-template-columns:1fr;text-align:center;justify-items:center}\n",
         "big": ".hero.big .c{grid-template-columns:1fr}.hero.big h1{font-size:clamp(48px,9vw,112px);line-height:.95}\n"}
JS_CSS = """.tools{display:flex;gap:8px;align-items:center}
.tools button{font:inherit;background:none;border:1px solid var(--ln);color:inherit;border-radius:var(--r);padding:6px 12px;cursor:pointer}
a:focus-visible,button:focus-visible{outline:3px solid var(--ac2);outline-offset:2px}
nav .c{flex-wrap:wrap}.menu{display:none}
.hide{opacity:0;transform:translateY(16px);transition:opacity .5s,transform .5s}.hide.in{opacity:1;transform:none}
@media(max-width:760px){.menu{display:inline-block}.links{display:none;width:100%;order:3}.links.open{display:flex;flex-direction:column;gap:12px;padding-bottom:12px}.links a{margin:0}}
@media(prefers-reduced-motion:reduce){.hide{opacity:1;transform:none;transition:none}}
"""


def css(s):
    h, l, sat = hls(s["accent"])
    ac2 = hsl((h + .12) % 1, .7 if sat > .1 else 0, .58)
    on = "#111" if lum(s["accent"]) > .5 else "#fff"
    o = ":root{%s;--ac:%s;--ac2:%s;--on:%s;--r:%dpx;--sp:%dpx;--w:%dpx}\n" % (
        tokens(s, s["dark"]), s["accent"], ac2, on, s["radius"], s["space"], s["width"])
    names = ["base", "nav"]
    for k in s["sections"]:
        names += {"features": ["card", "features"], "pricing": ["card", "pricing"]}.get(k, [k])
    for n in dict.fromkeys(names):
        o += BLOCK[n].replace("@FONT@", FONTS[s["font"]]).replace("@COLS@", str(s["cols"]))
        o += NAVV[s["nav"]] if n == "nav" else HEROV[s["hero"]] if n == "hero" else ""
    if s["js"]:
        o += ":root[data-theme=dark]{%s}\n:root[data-theme=light]{%s}\n" % (tokens(s, True), tokens(s, False)) + JS_CSS
    return o


# ---------------------------------------------------------------- HTML
def nav_html(s, B):
    secs = s["sections"]
    links = "".join(f'<a href="#{k}">{n}</a>' for k, n in
                    (("features", "Features"), ("pricing", "Pricing"), ("faq", "FAQ"), ("contact", "Contact"))
                    if k in secs) or '<a href="#hero">Home</a>'
    cta = "#contact" if "contact" in secs else "#cta" if "cta" in secs else "#"
    tools = ('<div class="tools"><button class="theme" aria-label="Toggle light or dark theme">Theme</button>'
             '<button class="menu" aria-label="Open menu" aria-expanded="false">Menu</button></div>') if s["js"] else ""
    cls = "" if s["nav"] == "top" else s["nav"]
    return (f'<nav class="{cls}"><div class="c"><strong>{B}</strong><div class="links">{links}'
            f'<a href="{cta}" class="btn">Sign up</a></div>{tools}</div></nav>\n')


def section_html(k, s, B):
    cta = "#contact" if "contact" in s["sections"] else "#cta" if "cta" in s["sections"] else "#"
    if k == "hero":
        art = "" if s["hero"] == "big" else '<div class="art" role="img" aria-label="Image placeholder"></div>'
        return (f'<section class="hero {s["hero"]}" id="hero"><div class="c"><div><h1>Build something people remember</h1>'
                f'<p>A short line that explains what you do and who it is for.</p><a href="{cta}" class="btn">Get started</a></div>{art}</div></section>\n')
    if k == "features":
        n = 4 if s["cols"] == 4 else s["cols"] * 2
        cards = "".join(f'<div class="card"><div class="icon"></div><h3>Feature {i}</h3><p>One sentence on the benefit.</p></div>\n'
                        for i in range(1, n + 1))
        lines = " lines" if s["cards"] == "lines" else ""
        return f'<section id="features"><div class="c"><h2>What you get</h2><div class="grid{lines}">\n{cards}</div></div></section>\n'
    if k == "stats":
        return ('<section class="stats" id="stats"><div class="c"><div><b data-to="12" data-suffix="k">12k</b>customers</div>'
                '<div><b data-to="99.9" data-suffix="%">99.9%</b>uptime</div><div><b data-to="4.8">4.8</b>average rating</div></div></section>\n')
    if k == "pricing":
        tiers = [("Starter", "$9", ""), ("Pro", "$29", " hot"), ("Team", "$79", "")]
        cards = "".join(f'<div class="card{h}"><h3>{n}</h3><div class="price">{p}</div><ul><li>Feature one</li><li>Feature two</li><li>Feature three</li></ul>'
                        f'<a href="#" class="btn">Choose {n}</a></div>\n' for n, p, h in tiers)
        return f'<section id="pricing"><div class="c"><h2>Pricing</h2><div class="plans">\n{cards}</div></div></section>\n'
    if k == "testimonial":
        return ('<section id="testimonial"><div class="c"><p class="quote">“This changed how our whole team ships.”</p>'
                '<p style="text-align:center;opacity:.7">Name, Company</p></div></section>\n')
    if k == "faq":
        qa = "".join(f"<details><summary>Question {i}?</summary><p>A short, helpful answer.</p></details>\n" for i in (1, 2, 3))
        return f'<section class="faq" id="faq"><div class="c"><h2>Questions</h2>\n{qa}</div></section>\n'
    if k == "contact":
        return ('<section class="contact" id="contact"><div class="c"><h2>Get in touch</h2><form action="#">'
                '<label>Name<input name="name" required></label><label>Email<input type="email" name="email" required></label>'
                '<label>Message<textarea name="message" rows="4" required></textarea></label>'
                '<button class="btn" type="submit">Send message</button></form></div></section>\n')
    if k == "cta":
        return '<section class="cta" id="cta"><div class="c"><h2>Ready to start?</h2><a href="#" class="btn">Create your account</a></div></section>\n'
    return f'<footer><div class="c">© {B}. All rights reserved.</div></footer>\n'


def body(s):
    B = _html.escape(s["brand"])
    return nav_html(s, B) + "".join(section_html(k, s, B) for k in s["sections"])


# ---------------------------------------------------------------- JS
JS_CORE = r"""
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

// 1. Mobile menu
const menu = $('.menu'), links = $('.links');
menu.addEventListener('click', () => {
  const open = links.classList.toggle('open');
  menu.setAttribute('aria-expanded', open);
});
$$('.links a').forEach(a => a.addEventListener('click', () => {
  links.classList.remove('open');
  menu.setAttribute('aria-expanded', false);
}));

// 2. Light/dark theme toggle (remembers the choice)
const root = document.documentElement;
try { const t = localStorage.getItem('theme'); if (t) root.dataset.theme = t; } catch (e) {}
$('.theme').addEventListener('click', () => {
  const next = (root.dataset.theme || (DEFAULT_DARK ? 'dark' : 'light')) === 'dark' ? 'light' : 'dark';
  root.dataset.theme = next;
  try { localStorage.setItem('theme', next); } catch (e) {}
});

// 3. Fade cards in as they scroll into view
const reveal = new IntersectionObserver(entries => entries.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add('in'); reveal.unobserve(e.target); }
}), { threshold: 0.15 });
$$('.card').forEach(c => { c.classList.add('hide'); reveal.observe(c); });
"""
JS_STATS = r"""
// Count the numbers up when they appear
$$('[data-to]').forEach(el => {
  const to = +el.dataset.to, dec = (el.dataset.to.split('.')[1] || '').length, suf = el.dataset.suffix || '';
  new IntersectionObserver(([e], o) => {
    if (!e.isIntersecting) return;
    o.disconnect();
    const t0 = performance.now();
    const step = t => {
      const p = Math.min((t - t0) / 1200, 1);
      el.textContent = (to * p).toFixed(dec) + suf;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }).observe(el);
});
"""
JS_FORM = r"""
// Contact form: shows a thank-you message. To really send it, replace this with a
// fetch() call to a form service (Formspree, Netlify Forms, your own API...).
const form = $('form');
form.addEventListener('submit', e => {
  e.preventDefault();
  form.innerHTML = '<p><strong>Thanks!</strong> We will get back to you soon.</p>';
});
"""


def js(s):
    o = "// Behavior for the exported page. Use together with the HTML and CSS.\nconst DEFAULT_DARK = %s;\n" % (
        "true" if s["dark"] else "false") + JS_CORE
    if "stats" in s["sections"]:
        o += JS_STATS
    if "contact" in s["sections"]:
        o += JS_FORM
    return o


def page(s, linked=False):
    style = '<link rel="stylesheet" href="style.css">\n' if linked else "<style>\n" + css(s) + "</style>\n"
    script = "" if not s["js"] else ('<script src="script.js"></script>\n' if linked else "<script>\n" + js(s) + "</script>\n")
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>' + _html.escape(s["brand"]) +
            "</title>\n" + style + "</head>\n<body>\n" + body(s) + script + "</body>\n</html>\n")


# ---------------------------------------------------------------- chatbot
STATE = clean(None)
HIST = []
ADD = r"\b(add|include|insert|put|show|need|want|create|with|plus|also)\b"
DEL = r"\b(remove|delete|drop|hide|without|no|get rid of|take out|skip)\b"
BRAND = re.compile(r"(?:called|named|call it|name it|brand name is|brand is|company is|business is|for)\s+[\"“']?"
                   r"([A-Z0-9][\w&'.\- ]{0,28}?)[\"”']?(?=\s*(?:,|;|\.|!|\?|$|\band\b|\bwith\b|\bin\b|\bthat\b|\bbut\b))")
PRESETS = {
    "SaaS": (r"\b(saas|startup|software)\b", dict(sections=["hero", "features", "stats", "pricing", "faq", "cta", "footer"], hero="split", cards="cards")),
    "portfolio": (r"\bportfolio\b", dict(sections=["hero", "features", "testimonial", "contact", "footer"], hero="big", font="serif", cards="lines")),
    "restaurant": (r"\b(restaurant|cafe|café|bakery)\b", dict(sections=["hero", "features", "testimonial", "contact", "footer"], hero="center", font="serif", radius=8)),
    "blog": (r"\bblog\b", dict(sections=["hero", "features", "cta", "footer"], hero="center", cards="lines")),
    "agency": (r"\b(agency|studio)\b", dict(sections=["hero", "stats", "features", "testimonial", "contact", "footer"], hero="big", nav="pill")),
    "shop": (r"\b(shop|store|ecommerce|e-commerce)\b", dict(sections=["hero", "features", "pricing", "testimonial", "faq", "footer"], hero="reverse", cols=4)),
}
HELP = ("I can edit your layout from plain English. Try:\n• Build a SaaS landing page (or portfolio, restaurant, blog, agency, shop)\n"
        "• Add pricing and a FAQ / remove the stats\n• Move pricing above the FAQ\n• Make it dark with a teal accent\n"
        "• Use a centered hero, a floating nav, 4 columns\n• Sharper corners, serif font, more spacing\n"
        "• Add JavaScript\n• Call it Luna Coffee\n• Undo / Reset")


def find_sections(t):
    pos = {}
    for k, (_, kws) in SEC.items():
        for w in kws:
            m = re.search(r"\b" + re.escape(w) + r"s?\b", t)
            if m:
                pos[k] = min(pos.get(k, 999), m.start())
    return sorted(pos, key=pos.get)


def add_section(k):
    S = STATE["sections"]
    if k in S:
        return None
    i = {"hero": 0, "footer": len(S)}.get(k)
    if i is None:
        i = next((S.index(x) for x in ("cta", "footer") if x in S and x != k), len(S))
    S.insert(i, k)
    return f"Added a {SEC[k][0].lower()} section."


def remove_section(k):
    if k not in STATE["sections"]:
        return None
    STATE["sections"].remove(k)
    return f"Removed the {SEC[k][0].lower()} section."


def chat(text):
    global STATE
    low, done, lv = text.lower(), [], None

    def chg(key, val, msg):
        if STATE[key] != val:
            STATE[key] = val
            done.append(msg)

    if re.fullmatch(r"\s*(hi|hello|hey)\W*", low):
        return "Hi! Tell me what kind of website you want, or say help to see examples."
    if re.search(r"\bhelp\b|what can you do", low):
        return HELP
    if re.search(r"\b(reset|start over)\b", low):
        STATE = clean(None)
        return "Reset to the starting layout."
    m = BRAND.search(text)
    if m:
        chg("brand", m.group(1).strip(), f"Named the site {m.group(1).strip()}.")
        low = low.replace(m.group(0).lower(), " ")
    for name, (pat, patch) in PRESETS.items():
        if re.search(pat, low):
            STATE.update(copy.deepcopy(patch))
            done.append(f"Started from a {name} layout.")
            break
    for c in re.split(r"\s*(?:,|;|\.|!|\band\b|\bthen\b|\bbut\b|\balso\b|\bplus\b)\s*", low):
        if not c:
            continue
        secs = find_sections(c)
        lv = "del" if re.search(DEL, c) else "add" if re.search(ADD, c) else lv
        if secs and re.search(r"\b(move|put|place|shift)\b", c) and re.search(r"\b(top|first|start|bottom|last|end|above|before|below|after|under)\b", c):
            k, S = secs[0], STATE["sections"]
            if k in S:
                S.remove(k)
                rel = re.search(r"\b(above|before|below|after|under)\b", c)
                if rel and len(secs) > 1 and secs[1] in S:
                    j = S.index(secs[1]) + (0 if rel.group(1) in ("above", "before") else 1)
                elif re.search(r"\b(bottom|last|end)\b", c):
                    j = S.index("footer") if "footer" in S else len(S)
                else:
                    j = 0
                S.insert(j, k)
                done.append(f"Moved the {SEC[k][0].lower()} section.")
        elif secs:
            for k in secs:
                r = add_section(k) if lv == "add" else remove_section(k) if lv == "del" else None
                if r:
                    done.append(r)
        nav_w = re.search(r"\b(nav|navbar|navigation|menu|logo)\b", c)
        if nav_w:
            if re.search(r"\bcent(er|ered)\b", c): chg("nav", "center", "Centered the navigation.")
            elif re.search(r"\b(pill|floating|float)\b", c): chg("nav", "pill", "Switched to a floating pill navigation.")
            elif re.search(r"\b(top|simple|normal|standard)\b", c): chg("nav", "top", "Switched to a standard top navigation.")
        elif re.search(r"\b(hero|banner|headline|oversized|huge|giant|flip|reverse|split|side by side)\b|image (on the )?(left|right)|big (text|type|title)", c):
            if re.search(r"\b(reverse|flip)\b|image (on the )?left", c): chg("hero", "reverse", "Put the hero image on the left.")
            elif re.search(r"\b(big|huge|oversized|giant)\b", c): chg("hero", "big", "Switched to an oversized-type hero.")
            elif re.search(r"\bcent(er|ered)\b", c): chg("hero", "center", "Centered the hero.")
            elif re.search(r"\bsplit\b|side by side|image (on the )?right", c): chg("hero", "split", "Switched to a split hero.")
        js_off = re.search(r"\b(no|without|remove|disable|turn off)\b[^.]*\b(javascript|js|script|animations?|interactiv\w*)\b", c)
        js_on = re.search(r"\b(javascript|js|interactive|interactivity|animations?|toggle|switcher)\b", c)
        if js_off: chg("js", False, "Turned JavaScript off.")
        elif js_on: chg("js", True, "Turned JavaScript on (mobile menu, theme toggle, scroll animations).")
        if not js_on:
            if re.search(r"\b(dark|night)\b", c) and not re.search(r"\b(not|no) dark\b", c): chg("dark", True, "Switched to a dark theme.")
            elif re.search(r"\blight (mode|theme|background|version)\b|white background|\bday mode\b|\b(not|no) dark\b", c): chg("dark", False, "Switched to a light theme.")
        for w, hx in COLORS.items():
            if re.search(r"\b" + w + r"\b", c):
                chg("accent", hx, f"Set the accent color to {w}.")
        hx = re.search(r"#[0-9a-f]{6}\b", c)
        if hx: chg("accent", hx.group(0), f"Set the accent color to {hx.group(0)}.")
        if not nav_w:
            for pat, f in ((r"\b(sans|sans-serif|modern font|clean font)\b", "sans"), (r"\b(serif|elegant|classic|editorial|traditional)\b", "serif"),
                           (r"\b(mono|monospace|techy|terminal)\b", "mono"), (r"\b(playful|friendly|fun)\b", "rounded")):
                if re.search(pat, c):
                    chg("font", f, f"Changed the font style to {f}.")
                    break
            if re.search(r"\b(sharp|sharper|square|boxy|angular)\b|straight corners|no (rounded|radius|round)", c): chg("radius", 0, "Made the corners sharp.")
            elif re.search(r"\b(very rounded|pill|fully rounded|circular)\b", c): chg("radius", 28, "Made the corners very round.")
            elif re.search(r"\b(rounded|rounder|round|soft|curvy)\b", c): chg("radius", min(32, STATE["radius"] + 8) if "more" in c else 16, "Rounded the corners.")
        m2 = re.search(r"\b(\d|two|three|four)\s*[- ]?\s*col", c)
        if m2:
            n = {"two": 2, "three": 3, "four": 4}.get(m2.group(1)) or int(m2.group(1))
            if 2 <= n <= 4: chg("cols", n, f"Set the feature grid to {n} columns.")
        if re.search(r"\b(spacious|airy|roomy)\b|more (space|spacing|whitespace|breathing)", c): chg("space", min(128, STATE["space"] + 24), "Added more spacing.")
        elif re.search(r"\b(compact|tight|dense)\b|less (space|spacing)", c): chg("space", max(32, STATE["space"] - 24), "Tightened the spacing.")
        if re.search(r"\b(wide|full.?width)\b", c): chg("width", 1280, "Made the page wider.")
        elif re.search(r"\b(narrow|slim)\b", c): chg("width", 960, "Made the page narrower.")
        if re.search(r"\b(flat|lines|line style|minimal cards|no cards|borderless)\b", c): chg("cards", "lines", "Switched to flat, ruled cards.")
        elif re.search(r"\b(boxed|card style|cards)\b", c): chg("cards", "cards", "Switched to boxed cards.")
    if done:
        return "Done:\n" + "\n".join("• " + d for d in done)
    return "I couldn't find a change in that. " + HELP


# ---------------------------------------------------------------- API used by the web page
def out(reply=None, linked=False):
    r = {"state": STATE, "meta": {"sections": {k: v[0] for k, v in SEC.items()}},
         "code": {"html": page(STATE, linked), "css": css(STATE), "js": js(STATE)}}
    if reply:
        r["reply"] = reply
    return json.dumps(r)


def commit(before):
    if STATE != before:
        HIST.append(before)
        del HIST[:-30]


def api(raw):
    global STATE
    m = json.loads(raw)
    c, before = m.get("cmd"), copy.deepcopy(STATE)
    if c == "load":
        STATE = clean(m.get("state"))
        HIST.clear()
    elif c == "chat":
        if re.search(r"\bundo\b", m["text"].lower()):
            if HIST:
                STATE = HIST.pop()
                return out("Undone.")
            return out("Nothing to undo.")
        reply = chat(m["text"])
        commit(before)
        return out(reply)
    elif c == "set":
        STATE = clean({**STATE, m["key"]: m["value"]})
        commit(before)
    elif c == "add":
        add_section(m["type"])
        commit(before)
    elif c == "remove":
        remove_section(m["type"])
        commit(before)
    elif c == "move":
        S = STATE["sections"]
        i, j = S.index(m["type"]), S.index(m["type"]) + int(m["dir"])
        if 0 <= j < len(S):
            S[i], S[j] = S[j], S[i]
        commit(before)
    elif c == "undo" and HIST:
        STATE = HIST.pop()
    elif c == "reset":
        STATE = clean(None)
        commit(before)
    elif c == "linked":
        return out(linked=True)
    return out()
