{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 35,
   "metadata": {},
   "outputs": [],
   "source": [
    "import re\n",
    "import ipywidgets as widgets\n",
    "from IPython.display import display, clear_output, HTML as IPHTML\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 36,
   "metadata": {},
   "outputs": [],
   "source": [
    "APP_NAME = \"DocLens\"\n",
    "\n",
    "LEGAL_MAP = [\n",
    "    (r'\\bshall\\b', 'must'),\n",
    "    (r'\\bhereinafter\\b', 'from this point on'),\n",
    "    (r'\\bpursuant to\\b', 'under'),\n",
    "    (r'\\bnotwithstanding\\b', 'despite'),\n",
    "    (r'\\bin the event that\\b', 'if'),\n",
    "    (r'\\bprior to\\b', 'before'),\n",
    "    (r'\\bsubsequent to\\b', 'after'),\n",
    "    (r'\\bcommence\\b', 'start'),\n",
    "    (r'\\bterminate\\b', 'end'),\n",
    "    (r'\\butilize\\b', 'use'),\n",
    "    (r'\\baforementioned\\b', 'earlier mentioned'),\n",
    "    (r'\\bnull and void\\b', 'not valid'),\n",
    "    (r'\\bcease and desist\\b', 'stop'),\n",
    "    (r'\\bfull force and effect\\b', 'still valid'),\n",
    "]\n",
    "\n",
    "def clean_spaces(text):\n",
    "    return re.sub(r'\\s+', ' ', text).strip()\n",
    "\n",
    "def simplify_sentence(sentence):\n",
    "    s = sentence.strip()\n",
    "    if not s:\n",
    "        return \"\"\n",
    "    for pat, repl in LEGAL_MAP:\n",
    "        s = re.sub(pat, repl, s, flags=re.I)\n",
    "    s = re.sub(r'\\bthe party of the first part\\b', 'the first person or group', s, flags=re.I)\n",
    "    s = re.sub(r'\\bthe party of the second part\\b', 'the second person or group', s, flags=re.I)\n",
    "    s = clean_spaces(s)\n",
    "    if len(s) > 140:\n",
    "        parts = s.split(',')\n",
    "        if len(parts) > 1:\n",
    "            s = parts[0].strip() + \". \" + \", \".join(p.strip() for p in parts[1:]).strip()\n",
    "    return s\n",
    "\n",
    "def split_sentences(text):\n",
    "    return [x.strip() for x in re.split(r'(?<=[.!?])\\s+', text) if x.strip()]\n",
    "\n",
    "def summarize(text):\n",
    "    sentences = split_sentences(text)\n",
    "    simple = [simplify_sentence(s) for s in sentences]\n",
    "    simple = [s for s in simple if s]\n",
    "    if not simple:\n",
    "        return \"Paste legal text to see a simpler version.\"\n",
    "    return \" \".join(simple[:8])\n",
    "\n",
    "def extract_points(text):\n",
    "    points = []\n",
    "    for sent in split_sentences(text):\n",
    "        s = simplify_sentence(sent)\n",
    "        if re.search(r'\\b(pay|payment|rent|fee|deadline|due|terminate|end|cancel|refund|renew|liability|owe|must|agree|notice|penalty|late)\\b', s, flags=re.I):\n",
    "            points.append(s)\n",
    "        elif len(s.split()) <= 16:\n",
    "            points.append(s)\n",
    "    seen = set()\n",
    "    out = []\n",
    "    for p in points:\n",
    "        k = p.lower()\n",
    "        if k not in seen:\n",
    "            seen.add(k)\n",
    "            out.append(p)\n",
    "    return out[:7]\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "metadata": {},
   "outputs": [],
   "source": [
    "title = widgets.HTML(f\"\"\"\n",
    "<div style=\"\n",
    "    max-width: 900px;\n",
    "    margin: 0 auto 18px auto;\n",
    "    padding: 26px 22px;\n",
    "    border-radius: 24px;\n",
    "    background: linear-gradient(135deg, #0f172a, #2563eb);\n",
    "    color: white;\n",
    "    text-align: center;\n",
    "    box-shadow: 0 14px 40px rgba(15,23,42,0.22);\n",
    "\">\n",
    "  <div style=\"font-size: 42px; font-weight: 800; letter-spacing: 0.4px;\">DocLens</div>\n",
    "  <div style=\"font-size: 16px; opacity: 0.92; margin-top: 8px;\">Turn legal text into clearer English.</div>\n",
    "</div>\n",
    "\"\"\")\n",
    "\n",
    "subtitle = widgets.HTML(\"\"\"\n",
    "<div style=\"text-align:center; color:#475569; margin-bottom: 14px;\">\n",
    "  Simple, centered, and built for easier reading.\n",
    "</div>\n",
    "\"\"\")\n",
    "\n",
    "input_box = widgets.Textarea(\n",
    "    value='',\n",
    "    placeholder='Paste a contract, lease, terms of service, or other legal text here...',\n",
    "    layout=widgets.Layout(width='100%', height='240px')\n",
    ")\n",
    "\n",
    "button = widgets.Button(\n",
    "    description='Simplify with DocLens',\n",
    "    button_style='info',\n",
    "    layout=widgets.Layout(width='240px', height='44px')\n",
    ")\n",
    "\n",
    "plans = widgets.HTML(\"\"\"\n",
    "<div style=\"\n",
    "    max-width: 900px;\n",
    "    margin: 18px auto 0 auto;\n",
    "    display: grid;\n",
    "    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));\n",
    "    gap: 12px;\n",
    "\">\n",
    "  <div style=\"background:white;border:1px solid #e5e7eb;border-radius:18px;padding:16px;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.04);\">\n",
    "    <div style=\"font-weight:700;font-size:18px;\">Free</div>\n",
    "    <div style=\"color:#64748b;margin-top:8px;\">1 document per day</div>\n",
    "  </div>\n",
    "  <div style=\"background:white;border:1px solid #c7d2fe;border-radius:18px;padding:16px;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.04);\">\n",
    "    <div style=\"font-weight:700;font-size:18px;\">Pro</div>\n",
    "    <div style=\"color:#64748b;margin-top:8px;\">Unlimited docs + saved history</div>\n",
    "  </div>\n",
    "  <div style=\"background:white;border:1px solid #bae6fd;border-radius:18px;padding:16px;text-align:center;box-shadow:0 4px 16px rgba(0,0,0,0.04);\">\n",
    "    <div style=\"font-weight:700;font-size:18px;\">Business</div>\n",
    "    <div style=\"color:#64748b;margin-top:8px;\">Team tools + contract review</div>\n",
    "  </div>\n",
    "</div>\n",
    "\"\"\")\n",
    "\n",
    "output = widgets.Output()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 38,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "a437c00f54c94845b70a5719afdbcbc3",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HTML(value='\\n<div style=\"\\n    max-width: 900px;\\n    margin: 0 auto 18px auto;\\n    padding: 26px 22px;\\n   …"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "ab53f9eed4bf41929f3e4e7c118434cf",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HTML(value='\\n<div style=\"text-align:center; color:#475569; margin-bottom: 14px;\">\\n  Simple, centered, and bu…"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "4fa30c63caa34b2f9faa90d8999e2646",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "VBox(children=(Textarea(value='', layout=Layout(height='240px', width='100%'), placeholder='Paste a contract, …"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "b32536f2696545d98889e91e08c43744",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "Output()"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "data": {
      "application/vnd.jupyter.widget-view+json": {
       "model_id": "2be9c147a52245d1ab9ebde03533bb8a",
       "version_major": 2,
       "version_minor": 0
      },
      "text/plain": [
       "HTML(value='\\n<div style=\"\\n    max-width: 900px;\\n    margin: 18px auto 0 auto;\\n    display: grid;\\n    grid…"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "title = widgets.HTML(f\"\"\"\n",
    "<div style=\"\n",
    "    max-width: 900px;\n",
    "    margin: 0 auto 18px auto;\n",
    "    padding: 26px 22px;\n",
    "    border-radius: 24px;\n",
    "    background: linear-gradient(135deg, #0f172a, #2563eb);\n",
    "    color: white;\n",
    "    text-align: center;\n",
    "    box-shadow: 0 14px 40px rgba(15,23,42,0.22);\n",
    "\">\n",
    "  <div style=\"font-size: 42px; font-weight: 800; letter-spacing: 0.4px;\">DocLens</div>\n",
    "  <div style=\"font-size: 16px; opacity: 0.92; margin-top: 8px;\">Turn legal text into clearer English.</div>\n",
    "</div>\n",
    "\"\"\")\n",
    "\n",
    "subtitle = widgets.HTML(\"\"\"\n",
    "<div style=\"text-align:center; color:#475569; margin-bottom: 14px;\">\n",
    "  Simple, centered, and built for easier reading.\n",
    "</div>\n",
    "\"\"\")\n",
    "def on_click(b):\n",
    "    with output:\n",
    "        clear_output()\n",
    "        doc = input_box.value.strip()\n",
    "\n",
    "        if not doc:\n",
    "            display(IPHTML(\"<div style='text-align:center;color:#b91c1c;font-weight:700;'>Paste some legal text first.</div>\"))\n",
    "            return\n",
    "\n",
    "        summary = summarize(doc)\n",
    "        points = extract_points(doc)\n",
    "\n",
    "        display(IPHTML(f\"\"\"\n",
    "        <div style=\"max-width: 900px; margin: 0 auto;\">\n",
    "          <div style=\"background:white;border:1px solid #e5e7eb;border-radius:20px;padding:18px;box-shadow:0 4px 16px rgba(0,0,0,0.04);margin-top:14px;text-align:center;\">\n",
    "            <h2 style=\"margin-top:0;color:#0f172a;\">What it means</h2>\n",
    "            <p style=\"line-height:1.9;font-size:16px;text-align:left;\">{summary}</p>\n",
    "          </div>\n",
    "        </div>\n",
    "        \"\"\"))\n",
    "\n",
    "        bullets = \"\".join([f\"<li style='margin-bottom:8px;'>{p}</li>\" for p in points]) if points else \"<li>No clear key points found yet.</li>\"\n",
    "        display(IPHTML(f\"\"\"\n",
    "        <div style=\"max-width: 900px; margin: 0 auto;\">\n",
    "          <div style=\"background:white;border:1px solid #e5e7eb;border-radius:20px;padding:18px;box-shadow:0 4px 16px rgba(0,0,0,0.04);margin-top:14px;text-align:center;\">\n",
    "            <h2 style=\"margin-top:0;color:#0f172a;\">Important points</h2>\n",
    "            <ul style=\"line-height:1.7;text-align:left;\">{bullets}</ul>\n",
    "          </div>\n",
    "        </div>\n",
    "        \"\"\"))\n",
    "\n",
    "        display(IPHTML(\"\"\"\n",
    "        <div style=\"max-width: 900px; margin: 14px auto 0 auto; padding: 12px 14px; border-radius: 14px; background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; font-size: 14px; text-align:center;\">\n",
    "          Not legal advice. This is for easier understanding only.\n",
    "        </div>\n",
    "        \"\"\"))\n",
    "\n",
    "button.on_click(on_click)\n",
    "display(title, subtitle, widgets.VBox([input_box, widgets.HBox([button], layout=widgets.Layout(justify_content='center'))]), output, plans)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.1+"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
