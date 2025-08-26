jiimport subprocess
import sys
import os
import json
from datetime import datetime
import re

# --- Auto-install function ---
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# --- Try imports and auto-install if missing ---
try:
    from flask import Flask, render_template_string, request, send_file
except ImportError:
    install("flask")
    from flask import Flask, render_template_string, request, send_file

try:
    from fpdf import FPDF
except ImportError:
    install("fpdf")
    from fpdf import FPDF

# --- Flask App ---
app = Flask(__name__)
JSON_FILE = "submissions.json"

# Ensure JSON file exists
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w") as f:
        json.dump([], f)

form_html = """ 
   <!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hackathon Team Registration</title>
<style>
  :root{
    --bg1:#0f172a; /* slate-900 */
    --bg2:#1e293b; /* slate-800 */
    --glass: rgba(255,255,255,0.08);
    --border: rgba(255,255,255,0.16);
    --text:#e5e7eb; /* gray-200 */
    --muted:#94a3b8; /* slate-400 */
    --accent1:#22d3ee; /* cyan-400 */
    --accent2:#a78bfa; /* violet-400 */
    --accent3:#f472b6; /* pink-400 */
    --ok:#34d399; /* green-400 */
    --warn:#f59e0b; /* amber-400 */
  }

  * { box-sizing: border-box; }

  body{
    margin:0;
    min-height:100vh;
    color:var(--text);
    background:
      radial-gradient(1200px 600px at 10% -10%, rgba(167,139,250,0.25), transparent 60%),
      radial-gradient(900px 600px at 110% 10%, rgba(34,211,238,0.25), transparent 60%),
      linear-gradient(180deg, var(--bg1), var(--bg2));
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji";
    display:flex;
    align-items:center;
    justify-content:center;
    padding:32px;
  }

  .card{
    width:min(980px, 100%);
    background:linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
    border:1px solid var(--border);
    border-radius:20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06);
    padding:28px;
  }

  .title{
    font-weight:800;
    font-size: clamp(1.4rem, 2.8vw, 2.1rem);
    line-height:1.15;
    margin:0 0 8px 0;
    background: linear-gradient(90deg, var(--accent1), var(--accent2), var(--accent3));
    -webkit-background-clip: text;
    background-clip:text;
    color: transparent;
    letter-spacing: .5px;
    position: relative;
  }

  .subtitle{
    margin:0 0 24px 0;
    color:var(--muted);
    font-size: .98rem;
  }

  form{
    display:grid;
    gap:18px;
  }

  .grid-2{
    display:grid;
    grid-template-columns: 1fr 1fr;
    gap:16px;
  }

  .grid-3{
    display:grid;
    grid-template-columns: 1.2fr .8fr 1.2fr;
    gap:12px;
  }

  @media (max-width: 780px){
    .grid-2, .grid-3{ grid-template-columns: 1fr; }
  }

  .field{
    position:relative;
  }

  .input, .select{
    width:100%;
    padding:14px 14px 14px 14px;
    border-radius:12px;
    border:1px solid var(--border);
    background: rgba(15, 23, 42, 0.55);
    color:var(--text);
    outline:none;
    transition: border .2s ease, box-shadow .2s ease, transform .05s ease;
    box-shadow: inset 0 0 0 9999px rgba(255,255,255,0.02);
  }

  .input::placeholder { color: #64748b; }

  .input:focus, .select:focus{
    border-color: var(--accent2);
    box-shadow: 0 0 0 4px rgba(167,139,250,0.20), 0 8px 24px rgba(167,139,250,0.10);
  }

  .floating label{
    position:absolute;
    left:12px;
    top:12px;
    color:#8b9bb5;
    background: linear-gradient(180deg, rgba(15,23,42,0.9), rgba(15,23,42,0.35));
    padding:0 6px;
    transform-origin:left top;
    transition: all .15s ease;
    pointer-events:none;
    border-radius:6px;
  }

  .floating .input:not(:placeholder-shown) + label,
  .floating .input:focus + label,
  .floating .select:focus + label{
    transform: translateY(-18px) scale(0.88);
    color: var(--accent1);
    box-shadow: 0 0 0 2px rgba(34,211,238,0.25);
  }

  .section{
    margin-top:8px;
    padding:16px;
    border:1px dashed rgba(255,255,255,0.16);
    border-radius:16px;
    background: rgba(255,255,255,0.03);
  }

  details{
    background: rgba(255,255,255,0.04);
    border:1px solid var(--border);
    border-radius:14px;
    padding:12px 14px;
    transition: transform .1s ease;
  }
  details:hover{ transform: translateY(-1px); }
  summary{
    cursor:pointer;
    list-style:none;
    font-weight:700;
    user-select:none;
  }
  summary::-webkit-details-marker{ display:none; }
  .badge{
    display:inline-block;
    padding:2px 8px;
    border-radius:999px;
    font-size:.75rem;
    background: rgba(34,211,238,0.15);
    border:1px solid rgba(34,211,238,0.35);
    color:#a5f3fc;
    vertical-align: middle;
    margin-left:8px;
  }

  .row{
    display:grid;
    gap:12px;
    margin-top:12px;
  }

  .actions{
    display:flex;
    gap:12px;
    align-items:center;
    justify-content:flex-end;
    margin-top:6px;
  }

  .btn{
    appearance:none;
    border:0;
    padding:12px 18px;
    border-radius:12px;
    font-weight:700;
    cursor:pointer;
    transition: transform .06s ease, box-shadow .2s ease, background .2s ease;
    background: linear-gradient(90deg, var(--accent2), var(--accent3));
    color:#0b1020;
    text-shadow: 0 1px 0 rgba(255,255,255,0.35);
    box-shadow: 0 8px 20px rgba(167,139,250,0.25);
  }
  .btn:hover{ transform: translateY(-1px); box-shadow: 0 14px 26px rgba(244,114,182,0.22); }
  .btn:active{ transform: translateY(0px) scale(.99); }

  .hint{ color:var(--muted); font-size:.85rem; }

  .pill{
    display:inline-block;
    padding:6px 10px;
    border-radius:999px;
    font-size:.8rem;
    color:#0b1020;
    background: linear-gradient(90deg, var(--ok), #60a5fa);
    border:1px solid rgba(255,255,255,0.25);
    margin-left:8px;
  }

  .kicker{
    display:flex; align-items:center; gap:10px; margin-bottom:10px;
    color:#cbd5e1; font-size:.9rem;
  }
  .dot{
    width:8px; height:8px; border-radius:50%;
    background: radial-gradient(circle at 35% 35%, white, #22d3ee 60%, rgba(34,211,238,0.2));
    box-shadow: 0 0 12px rgba(34,211,238,0.6);
  }
</style>
</head>
<body>
  <div class="card">
    <div class="kicker"><span class="dot"></span> Tech Fest • Team Registration</div>
    <h2 class="title">Hackathon Team Registration</h2>
    <p class="subtitle">Register your squad. Make sure emails and register numbers are correct—this will be used for all event communication.</p>

    <form method="POST" action="/submit" id="regForm" novalidate>
      <div class="grid-2">
        <div class="field floating">
          <input class="input" name="team_name" placeholder=" " required>
          <label>Team Name</label>
        </div>
        <div class="field floating">
          <input class="input" name="team_size" type="number" min="4" max="5" placeholder=" " required>
          <label>Team Size (4–5)</label>
        </div>
      </div>

      <div class="grid-2">
        <div class="field floating">
          <input class="input" name="year" placeholder=" " required>
          <label>Year (e.g., II CSE)</label>
        </div>
        <div class="field floating">
          <input class="input" name="problem_code" placeholder=" " required>
          <label>Problem Code</label>
        </div>
      </div>

      <div class="field floating">
        <input class="input" name="category" placeholder=" " required>
        <label>Category (e.g., GenAI, Web, Mobile)</label>
      </div>

      <div class="section">
        <h3 style="margin:0 0 8px 0;">Team Lead <span class="badge">Required</span></h3>
        <div class="grid-3">
          <div class="field floating">
            <input class="input" name="lead_name" placeholder=" " required>
            <label>Name</label>
          </div>
          <div class="field floating">
            <input class="input" name="lead_reg" placeholder=" " required>
            <label>Register No</label>
          </div>
          <div class="field floating">
            <input class="input" name="lead_email" placeholder=" " type="email" required>
            <label>Email</label>
          </div>
        </div>
      </div>

      <div class="section">
        <h3 style="margin:0 0 8px 0;">Members <span class="badge">4 Required</span><span class="pill">+1 optional</span></h3>

        <details open>
          <summary>Member 1</summary>
          <div class="row grid-3">
            <div class="field floating"><input class="input" name="m1_name" placeholder=" " required><label>Name</label></div>
            <div class="field floating"><input class="input" name="m1_reg" placeholder=" " required><label>Reg No</label></div>
            <div class="field floating"><input class="input" name="m1_email" placeholder=" " type="email" required><label>Email</label></div>
          </div>
        </details>

        <details>
          <summary>Member 2</summary>
          <div class="row grid-3">
            <div class="field floating"><input class="input" name="m2_name" placeholder=" " required><label>Name</label></div>
            <div class="field floating"><input class="input" name="m2_reg" placeholder=" " required><label>Reg No</label></div>
            <div class="field floating"><input class="input" name="m2_email" placeholder=" " type="email" required><label>Email</label></div>
          </div>
        </details>

        <details>
          <summary>Member 3</summary>
          <div class="row grid-3">
            <div class="field floating"><input class="input" name="m3_name" placeholder=" " required><label>Name</label></div>
            <div class="field floating"><input class="input" name="m3_reg" placeholder=" " required><label>Reg No</label></div>
            <div class="field floating"><input class="input" name="m3_email" placeholder=" " type="email" required><label>Email</label></div>
          </div>
        </details>

        <details>
          <summary>Member 4</summary>
          <div class="row grid-3">
            <div class="field floating"><input class="input" name="m4_name" placeholder=" " required><label>Name</label></div>
            <div class="field floating"><input class="input" name="m4_reg" placeholder=" " required><label>Reg No</label></div>
            <div class="field floating"><input class="input" name="m4_email" placeholder=" " type="email" required><label>Email</label></div>
          </div>
        </details>

        <details id="m5_wrap" style="display:none;">
          <summary>Member 5 (Optional)</summary>
          <div class="row grid-3">
            <div class="field floating"><input class="input" name="m5_name" placeholder=" "><label>Name</label></div>
            <div class="field floating"><input class="input" name="m5_reg" placeholder=" "><label>Reg No</label></div>
            <div class="field floating"><input class="input" name="m5_email" placeholder=" " type="email"><label>Email</label></div>
          </div>
        </details>
        <p class="hint">Tip: Set “Team Size” to 5 to reveal Member 5 fields.</p>
      </div>

      <div class="actions">
        <button type="submit" class="btn">Submit Registration</button>
      </div>
    </form>
  </div>

<script>
  // Toggle Member 5 visibility based on team size
  const teamSize = document.querySelector('input[name="team_size"]');
  const m5Wrap = document.getElementById('m5_wrap');
  const m5Inputs = ['m5_name','m5_reg','m5_email'].map(n => document.querySelector('[name="'+n+'"]'));

  function toggleM5(){
    const size = parseInt(teamSize.value || "0", 10);
    const show = size === 5;
    m5Wrap.style.display = show ? 'block' : 'none';
    m5Inputs.forEach(inp => {
      if(!inp) return;
      inp.required = false; // keep optional even when shown
      if(!show){ inp.value = ''; }
    });
  }
  teamSize.addEventListener('input', toggleM5);
  toggleM5();

  // Simple client-side sanity check for size range (4–5)
  const form = document.getElementById('regForm');
  form.addEventListener('submit', (e) => {
    const size = parseInt(teamSize.value || "0", 10);
    if(size < 4 || size > 5){
      e.preventDefault();
      teamSize.focus();
      alert('Team Size must be 4 or 5.');
    }
  });

  // Auto-open details when focusing inside
  document.querySelectorAll('details').forEach(d => {
    d.addEventListener('click', (ev) => {
      // allow normal toggle
    });
    d.querySelectorAll('input').forEach(inp => {
      inp.addEventListener('focus', () => { d.open = true; }, { once:false });
    });
  });
</script>
</body>
</html>

"""
@app.route('/')
def index():
    return render_template_string(form_html)

@app.route('/submit', methods=['POST'])
def submit():
    team = {
        "team_name": request.form["team_name"],
        "team_size": request.form["team_size"],
        "year": request.form["year"],
        "problem_code": request.form["problem_code"],
        "category": request.form["category"],
        "team_lead": {
            "name": request.form["lead_name"],
            "reg_no": request.form["lead_reg"],
            "email": request.form["lead_email"]
        },
        "members": [
            {"name": request.form["m1_name"], "reg_no": request.form["m1_reg"], "email": request.form["m1_email"]},
            {"name": request.form["m2_name"], "reg_no": request.form["m2_reg"], "email": request.form["m2_email"]},
            {"name": request.form["m3_name"], "reg_no": request.form["m3_reg"], "email": request.form["m3_email"]},
            {"name": request.form["m4_name"], "reg_no": request.form["m4_reg"], "email": request.form["m4_email"]}
        ]
    }

    # Optional 5th member
    if request.form.get("m5_name"):
        team["members"].append({
            "name": request.form.get("m5_name"),
            "reg_no": request.form.get("m5_reg"),
            "email": request.form.get("m5_email")
        })

    # Save team in JSON
    with open(JSON_FILE, "r") as f:
        submissions = json.load(f)
    submissions.append(team)
    with open(JSON_FILE, "w") as f:
        json.dump(submissions, f, indent=2)

    # Generate PDF for this team
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Team: {team['team_name']} | Size: {team['team_size']} | Year: {team['year']}", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Problem Code: {team['problem_code']} | Category: {team['category']}", ln=True)
    pdf.cell(0, 10, f"Team Lead: {team['team_lead']['name']} ({team['team_lead']['reg_no']}) | {team['team_lead']['email']}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 8, "Member Name", border=1)
    pdf.cell(40, 8, "Reg No", border=1)
    pdf.cell(80, 8, "Email", border=1)
    pdf.ln()
    pdf.set_font("Arial", '', 12)
    for m in team['members']:
        pdf.cell(60, 8, m['name'], border=1)
        pdf.cell(40, 8, m['reg_no'], border=1)
        pdf.cell(80, 8, m['email'], border=1)
        pdf.ln()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_team = re.sub(r'[^A-Za-z0-9_-]+', '_', team['team_name']).strip('_')
    pdf_file = f"{safe_team}_{timestamp}.pdf"
    pdf.output(pdf_file)

    # Send the PDF for download
    return send_file(pdf_file, as_attachment=True)

@app.route('/submit', methods=['POST'])
def submit():
    # ... your existing submission & PDF code ...
    return send_file(pdf_file, as_attachment=True)

# ---------------- NEW ROUTES ----------------
@app.route("/view_submissions")
def view_submissions():
    with open(JSON_FILE, "r") as f:
        data = json.load(f)
    return data  # shows JSON in browser

@app.route("/download_submissions")
def download_submissions():
    return send_file(JSON_FILE, as_attachment=True)
# ---------------- END NEW ROUTES -------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

