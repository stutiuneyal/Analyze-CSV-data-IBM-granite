import os
import re
import textwrap

import matplotlib
matplotlib.use('Agg')  # headless backend
import pandas as pd
from flask import Blueprint, request, jsonify
from utils.granite_instructlab import query_granite
from utils.executor import execute_and_plot

api_blueprint = Blueprint('api', __name__)

def sanitize_code(generated: str) -> str:
    """
    Clean Granite's output to valid Python:
    - Strip leading prose until first code line
    - Remove markdown fences and docstrings
    - Filter out placeholder DataFrame instantiations, plt.show, .cat lines
    - Truncate after plt.savefig, or append save if missing
    - Dedent and strip
    """
    # 1) Keep only real code start
    lines = generated.splitlines()
    start = 0
    for i, L in enumerate(lines):
        if L.lstrip().startswith(('import ', 'df', 'plt', 'pd.')):
            start = i
            break
    code = '\n'.join(lines[start:])

    # 2) Remove markdown fences and docstrings
    code = re.sub(r"```(?:python)?", "", code)
    code = re.sub(r"'''[\s\S]*?'''", "", code)
    code = re.sub(r'"""[\s\S]*?"""', "", code)

    # 3) Filter unwanted lines
    filtered = []
    skip = False
    for line in code.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if 'pd.DataFrame(' in line:
            skip = True
            continue
        if skip:
            if ')' in line:
                skip = False
            continue
        # correctly apply match to stripped line:
        if re.match(r"^output_path\s*=", stripped) or 'plt.show' in stripped or '.cat.' in stripped:
            continue
        filtered.append(line)

    # 4) Truncate at last plt.savefig or append save
    last_save = next((i for i, l in enumerate(filtered) if 'plt.savefig' in l), None)
    if last_save is not None:
        filtered = filtered[:last_save+1]
    else:
        filtered.append('plt.savefig(output_path)')

    # 5) Dedent and strip
    return textwrap.dedent('\n'.join(filtered)).strip()

@api_blueprint.route('/process', methods=['POST'])
def process_csv_and_query():
    # Validate inputs
    if 'file' not in request.files or 'query' not in request.form:
        return jsonify(error='CSV file and query are required'), 400

    # Save uploaded CSV
    upload = request.files['file']
    query = request.form['query']
    os.makedirs('uploads', exist_ok=True)
    path = os.path.join('uploads', upload.filename)
    upload.save(path)

    # Load DataFrame
    try:
        df = pd.read_csv(path)
    except Exception as e:
        return jsonify(error=f'Failed to read CSV: {e}'), 400

    # Drop empty rows
    df = df.dropna(how='all')

    # Convert date-like and numeric-like columns
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass
        try:
            df[col] = pd.to_numeric(df[col], errors='ignore')
        except Exception:
            pass

    columns = df.columns.tolist()

    # Build prompt for code-only output
    prompt = (
        "Output ONLY Python code up through plt.savefig(output_path); no prose. "
        "Assume df & output_path exist. "
        f"I want: {query}. Use pandas & matplotlib."
    )
    raw = query_granite(prompt)
    clean = sanitize_code(raw)

    # Clear previous figures
    clean = 'import matplotlib.pyplot as plt\nplt.close("all")\n' + clean

    # Map guessed column literals to actual names
    literals = set(re.findall(r"'([^']*)'", clean))
    for lit in literals:
        if lit in columns:
            continue
        matches = [c for c in columns if lit.lower() in c.lower()]
        if len(matches) == 1:
            clean = clean.replace(f"'{lit}'", f"'{matches[0]}'")

    print("=== Executing Python ===\n", clean)

    # Execute and return plot path
    os.makedirs('output', exist_ok=True)
    output_path = os.path.join('output', 'plot.png')
    try:
        result = execute_and_plot(clean, df, output_path)
    except Exception as e:
        return jsonify(error=f'Execution failed: {e}'), 500

    return jsonify(plot_path=result), 200
