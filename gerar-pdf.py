# Gera um PDF com a identidade do Meu Plantão a partir de um arquivo .md deste projeto.
# Uso: python3 gerar-pdf.py ARQUIVO.md SAIDA.pdf "Subtítulo da capa" "Linhas da capa (use <br>)"
# Precisa do Google Chrome instalado. Imagens: ![legenda](caminho.png) e, para celular, ![legenda](caminho.png){mobile}
import html, os, re, subprocess, sys, tempfile

src, saida, sub, meta = sys.argv[1:5]
base = os.path.dirname(os.path.abspath(src))
L = open(src, encoding="utf-8").read().split("\n")
LI = r'^(\s*)([-*]|\d+\.)\s+(.*)$'

def inl(t):
    codes = []
    def k(m):
        codes.append("<code>" + html.escape(m.group(1)) + "</code>")
        return "\x00%d\x00" % (len(codes) - 1)
    t = re.sub(r'`([^`]+)`', k, t)
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(https?://[^\s)<]+)', r'<a href="\1">\1</a>', t)
    return re.sub(r'\x00(\d+)\x00', lambda m: codes[int(m.group(1))], t)

def table(rows):
    cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
    h = "<table><thead><tr>" + "".join(f"<th>{inl(c)}</th>" for c in cells(rows[0])) + "</tr></thead><tbody>"
    for r in rows[2:]:
        h += "<tr>" + "".join(f"<td>{inl(c)}</td>" for c in cells(r)) + "</tr>"
    return h + "</tbody></table>"

def lists(i):
    items = []
    while i < len(L):
        l = L[i]; m = re.match(LI, l)
        if m:
            items.append([len(m.group(1)), m.group(2)[:-1] if m.group(2)[-1] == '.' else '', m.group(3), []]); i += 1; continue
        if l.strip() == "" and i + 1 < len(L) and re.match(r'^\s+\S', L[i + 1]):
            i += 1; continue
        if l.startswith("   ") and items and l.strip():
            if l.strip().startswith("|"):
                rows = []
                while i < len(L) and L[i].strip().startswith("|"):
                    rows.append(L[i].strip()); i += 1
                items[-1][3].append(table(rows)); continue
            items[-1][3].append("<p>" + inl(l.strip()) + "</p>"); i += 1; continue
        break
    o = ""; stack = []
    for ind, num, txt, extra in items:
        while stack and ind < stack[-1][0]:
            o += "</li></%s>" % stack.pop()[1]
        if not stack or ind > stack[-1][0]:
            tag = "ol" if num else "ul"; stack.append((ind, tag))
            o += ('<ol start="%s"><li>' % num) if num else "<ul><li>"
        else:
            o += "</li><li>"
        o += inl(txt) + "".join(extra)
    while stack:
        o += "</li></%s>" % stack.pop()[1]
    return o, i

body = []; i = 0
while i < len(L):
    l = L[i]
    if not l.strip():
        i += 1; continue
    m = re.match(r'^(#{1,4})\s+(.*)', l)
    if m:
        n = len(m.group(1)); t = m.group(2)
        if n == 1:
            i += 1; continue
        cls = ' class="prompt-start"' if t.startswith("PROMPT") else (' class="quebra"' if t.startswith("Prévia") else "")
        body.append(f"<h{n}{cls}>{inl(t)}</h{n}>"); i += 1; continue
    mi = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)(\{mobile\})?', l.strip())
    if mi:
        caminho = os.path.abspath(os.path.join(base, mi.group(2)))
        cls = "shot mob" if mi.group(3) else "shot"
        cap = body.pop() if body and body[-1].startswith("<p><strong>") else ""
        body.append(f'<figure class="{cls}">{cap}<img src="file://{caminho}" alt="{html.escape(mi.group(1))}"></figure>'); i += 1; continue
    if l.strip() == "---":
        body.append("<hr>"); i += 1; continue
    if l.startswith(">"):
        body.append("<blockquote>" + inl(l.lstrip("> ")) + "</blockquote>"); i += 1; continue
    if l.startswith("|"):
        rows = []
        while i < len(L) and L[i].startswith("|"):
            rows.append(L[i]); i += 1
        body.append(table(rows)); continue
    if re.match(LI, l):
        h, i = lists(i); body.append(h); continue
    p = [l.strip()]; i += 1
    while i < len(L) and L[i].strip() and not re.match(r'^(#|\||>|!\[|\s*([-*]|\d+\.)\s|---)', L[i]):
        p.append(L[i].strip()); i += 1
    body.append("<p>" + inl(" ".join(p)) + "</p>")

svg = re.sub(r'<\?xml.*?\?>', '', open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-almeida-carneiro.svg"), encoding="utf-8").read())
doc = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{html.escape(sub)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@500;600&family=DM+Serif+Display:ital@1&family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@400&display=swap">
<style>
@page{{size:A4;margin:18mm 17mm 18mm}}
@page capa{{margin:0}}
:root{{--navy:#0B1B36;--fg:#18263D;--muted:#667085;--line:#E3E7ED;--ok:#2E8B68;--okbg:#E5F2EC}}
*{{box-sizing:border-box}}
body{{font-family:"Source Sans 3",system-ui,sans-serif;color:var(--fg);font-size:10.5pt;line-height:1.5;margin:0}}
.capa{{page:capa;width:210mm;height:297mm;background:var(--navy);color:#fff;margin:0;padding:0 24mm;display:flex;flex-direction:column;justify-content:center;page-break-after:always;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.capa .logo svg{{width:200px;height:auto}} .capa .logo svg *{{fill:#fff!important}}
.capa h1{{font-family:"DM Serif Display",serif;font-style:italic;font-weight:400;font-size:46pt;margin:34px 0 6px}}
.capa .sub{{font-family:Outfit,sans-serif;font-size:15pt;color:#C9D6E8;margin:0}}
.capa .div{{width:56px;height:2px;background:#7AA8D4;margin:26px 0}}
.capa .meta{{font-size:10.5pt;color:#AFC0D8;line-height:1.7}}
h2{{font-family:Outfit,sans-serif;font-weight:600;color:var(--navy);font-size:16pt;margin:22px 0 8px;page-break-after:avoid}}
h2.quebra{{page-break-before:always}}
h2.prompt-start{{page-break-before:always;background:var(--navy);color:#fff;padding:12px 16px;border-radius:8px;font-size:15pt;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
h3{{font-family:Outfit,sans-serif;font-weight:600;color:var(--navy);font-size:13pt;margin:20px 0 6px;padding-bottom:4px;border-bottom:1px solid var(--line);page-break-after:avoid}}
h4{{font-family:Outfit,sans-serif;font-weight:500;color:var(--navy);font-size:11pt;margin:14px 0 4px;page-break-after:avoid}}
p{{margin:6px 0}} ul,ol{{margin:4px 0 8px;padding-left:20px}} li{{margin:3px 0}} li>ul,li>ol{{margin:2px 0}} li>p{{margin:4px 0}}
code{{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:8.6pt;background:#F1F3F6;border-radius:4px;padding:1px 4px;color:#243552;word-break:break-word}}
table{{width:100%;border-collapse:collapse;margin:8px 0 12px;font-size:9.6pt}}
tr{{page-break-inside:avoid}}
th{{text-align:left;font-family:Outfit,sans-serif;font-weight:500;font-size:8.6pt;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);border-bottom:1.5px solid var(--line);padding:6px 8px}}
td{{border-bottom:1px solid var(--line);padding:6px 8px;vertical-align:top}}
blockquote{{margin:12px 0;background:var(--okbg);border-left:3px solid var(--ok);padding:10px 14px;border-radius:6px}}
hr{{border:0;border-top:1px solid var(--line);margin:18px 0}}
a{{color:var(--navy)}}
figure.shot{{margin:8px 0 18px;page-break-inside:avoid}} figure.shot img{{width:100%;border:1px solid var(--line);border-radius:8px;display:block}} figure.mob img{{width:62mm}}
</style></head><body>
<section class="capa"><div class="logo">{svg}</div><h1>Meu Plantão</h1><p class="sub">{html.escape(sub)}</p><div class="div"></div>
<div class="meta">{meta}</div></section>
{"".join(body)}</body></html>"""

tmp = os.path.join(tempfile.mkdtemp(), "doc.html")
open(tmp, "w", encoding="utf-8").write(doc)
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                "--virtual-time-budget=8000", "--print-to-pdf=" + os.path.abspath(saida), "file://" + tmp],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
print("PDF gerado:", saida)
