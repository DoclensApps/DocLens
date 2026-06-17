from flask import Flask, request, render_template_string
import re

app = Flask(__name__)

PATTERNS = [
    (r'\bhereinafter\b', 'from this point on'),
    (r'\bheretofore\b', 'before now'),
    (r'\bpursuant to\b', 'under'),
    (r'\bshall\b', 'must'),
    (r'\bnotwithstanding\b', 'despite'),
    (r'\bin the event that\b', 'if'),
    (r'\bterminate\b', 'end'),
    (r'\bcommence\b', 'start'),
    (r'\bprior to\b', 'before'),
    (r'\bsubsequent to\b', 'after'),
    (r'\bwhereas\b', 'because'),
    (r'\butilize\b', 'use'),
    (r'\baforementioned\b', 'earlier mentioned'),
    (r'\bnull and void\b', 'not valid'),
    (r'\bcease and desist\b', 'stop'),
    (r'\bfull force and effect\b', 'still valid'),
]

def simplify_sentence(sentence):
    s = sentence.strip()
    for pat, repl in PATTERNS:
        s = re.sub(pat, repl, s, flags=re.I)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def split_sentences(text):
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]

def summarize(text):
    sentences = split_sentences(text)
    simple = [simplify_sentence(s) for s in sentences]
    simple = [s for s in simple if s]
    if not simple:
        return "Paste legal text to see a simpler version."
    return " ".join(simple[:8])

def extract_points(text):
    points = []
    for sent in split_sentences(text):
        s = simplify_sentence(sent)
        if re.search(r'\b(pay|payment|rent|fee|deadline|due|terminate|end|cancel|refund|renew|liability|owe|must|agree|notice|penalty|late)\b', s, flags=re.I):
            points.append(s)
        elif len(s.split()) <= 16:
            points.append(s)

    seen = set()
    clean = []
    for p in points:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            clean.append(p)
    return clean[:7]

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>DocLens</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 960px;
      margin: 0 auto;
      padding: 24px 16px 40px;
      background: #f7f8fc;
      color: #111827;
    }
    .hero {
      background: linear-gradient(135deg, #0f172a, #2563eb);
      color: white;
      padding: 26px 22px;
      border-radius: 24px;
      text-align: center;
      box-shadow: 0 14px 40px rgba(15,23,42,0.22);
      margin-bottom: 18px;
    }
    .hero h1 {
      margin: 0;
      font-size: 42px;
    }
    .hero p {
      margin: 8px 0 0 0;
      opacity: 0.92;
      font-size: 16px;
    }
    .center {
      text-align: center;
      color: #475569;
      margin-bottom: 14px;
    }
    .card {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 20px;
      padding: 18px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.04);
      margin-top: 14px;
    }
    textarea {
      width: 100%;
      height: 240px;
      box-sizing: border-box;
      border-radius: 14px;
      border: 1px solid #cbd5e1;
      padding: 14px;
      font-size: 15px;
      line-height: 1.6;
      resize: vertical;
    }
    button {
      background: #2563eb;
      color: white;
      border: none;
      border-radius: 12px;
      padding: 12px 18px;
      font-size: 15px;
      font-weight: 700;
      cursor: pointer;
      display: block;
      margin: 14px auto 0;
    }
    button:hover {
      background: #1d4ed8;
    }
    ul {
      line-height: 1.7;
    }
    .plans {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-top: 18px;
    }
    .plan {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 18px;
      padding: 16px;
      text-align: center;
    }
    .plan strong {
      font-size: 18px;
    }
    .free { border-color: #e5e7eb; }
    .pro { border-color: #c7d2fe; }
    .business { border-color: #bae6fd; }
    .notice {
      background: #fff7ed;
      border: 1px solid #fed7aa;
      color: #9a3412;
      padding: 12px 14px;
      border-radius: 14px;
      margin-top: 14px;
      text-align: center;
      font-size: 14px;
    }
  </style>
</head>
<body>
  <div class="hero">
    <h1>DocLens</h1>
    <p>Turn legal text into clearer English.</p>
  </div>

  <div class="center">Simple, centered, and built for easier reading.</div>

  <div class="card">
    <form method="post">
      <textarea name="document" placeholder="Paste a contract, lease, terms of service, or other legal text here...">{{ document or '' }}</textarea>
      <button type="submit">Simplify with DocLens</button>
    </form>
    <div class="notice">Not legal advice. This is for easier understanding only.</div>
  </div>

  {% if simplified %}
  <div class="card">
    <h2>What it means</h2>
    <p style="line-height:1.9;font-size:16px;">{{ simplified }}</p>
  </div>

  <div class="card">
    <h2>Important points</h2>
    {% if bullets %}
      <ul>
        {% for item in bullets %}
          <li>{{ item }}</li>
        {% endfor %}
      </ul>
    {% else %}
      <p>No clear key points found yet.</p>
    {% endif %}
  </div>
  {% endif %}

  <div class="plans">
    <div class="plan free">
      <strong>Free</strong>
      <div style="color:#64748b;margin-top:8px;">1 document per day</div>
    </div>
    <div class="plan pro">
      <strong>Pro</strong>
      <div style="color:#64748b;margin-top:8px;">Unlimited docs + saved history</div>
    </div>
    <div class="plan business">
      <strong>Business</strong>
      <div style="color:#64748b;margin-top:8px;">Team tools + contract review</div>
    </div>
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    document = ""
    simplified = ""
    bullets = []
    if request.method == "POST":
        document = request.form.get("document", "")
        simplified = summarize(document)
        bullets = extract_points(document)
    return render_template_string(HTML, document=document, simplified=simplified, bullets=bullets)

if __name__ == "__main__":
    app.run(debug=True)
