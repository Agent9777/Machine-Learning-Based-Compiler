import json
import os
import re
import uuid
import numpy as np
from collections import Counter

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

# ==========================================
# 1. CLEAN OPTIMIZATION TEMPLATES
# ==========================================
# Note: These are now the "bodies" of the new functions
OPTIMIZATION_LIB = {
    "bubble_sort": """
    // Replaced with qsort
    int _cmp(const void *a, const void *b) {{ return (*(int*)a - *(int*)b); }}
    qsort({arr}, {n}, sizeof({arr}[0]), _cmp);""",

    "selection_sort": """
    // Replaced with qsort
    int _cmp(const void *a, const void *b) {{ return (*(int*)a - *(int*)b); }}
    qsort({arr}, {n}, sizeof({arr}[0]), _cmp);""",

    "linear_search": """
    int low = 0, high = {n} - 1;
    int found_idx = -1;
    while (low <= high) {{
        int mid = low + (high - low) / 2;
        if ({arr}[mid] == target) {{ found_idx = mid; break; }}
        if ({arr}[mid] < target) low = mid + 1; else high = mid - 1;
    }}
    // Logic to handle result can be added here"""
}

# ==========================================
# 2. MODEL COMPONENTS
# ==========================================
def clean_code(code):
    if not code: return ""
    code = re.sub(r'//.*|#.*|/\*[\s\S]*?\*/', '', str(code))
    return " ".join(code.split()).strip()

class CodeStructureExtractor(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None): return self
    def transform(self, posts):
        features = []
        for code in posts:
            f = [
                len(re.findall(r'\bfor\b', code)),
                len(re.findall(r'\bwhile\b', code)),
                len(re.findall(r'\bif\b', code)),
                len(re.findall(r'\[.*\]\s*\[.*\]', code)), 
                len(re.findall(r'[+\-*/%]', code))
            ]
            features.append(f)
        return np.array(features)

# ==========================================
# 3. REFACTOR ENGINE (The "Function Injected")
# ==========================================
def extract_context_vars(code_block):
    arr_name = re.search(r'(\w+)\[', code_block)
    size_var = re.search(r'<\s*(\w+)', code_block)
    return {
        "arr": arr_name.group(1) if arr_name else "data",
        "n": size_var.group(1) if size_var else "n"
    }

def refactor_source_file(input_path, output_path, clf, le):
    if not os.path.exists(input_path):
        print(f"❌ Source file {input_path} not found.")
        return

    with open(input_path, 'r') as f:
        source = f.read()

    # Regex to find the whole loop block including braces
    block_pattern = r'((?:for|while)\s*\(.*?\)\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
    blocks = re.findall(block_pattern, source, re.DOTALL)

    final_code = source
    new_function_definitions = []
    
    print(f"\n🔬 Analyzing {input_path}...")

    for original_block in blocks:
        cleaned = clean_code(original_block)
        probs = clf.predict_proba([cleaned])[0]
        idx = np.argmax(probs)
        label = le.inverse_transform([idx])[0]
        conf = probs[idx]
        
        # We use a 40% threshold for the prototype to ensure it triggers
        if conf > 0.15 and label in OPTIMIZATION_LIB:
            print(f"✅ Identified {label} ({conf:.1%}). Creating new function...")
            
            vars = extract_context_vars(original_block)
            
            # Generate a unique name for the new function
            unique_id = str(uuid.uuid4())[:4]
            func_name = f"ai_optimized_{label}_{unique_id}"
            
            # Create the function call to replace the loop
            func_call = f"{func_name}({vars['arr']}, {vars['n']});"
            
            # Create the actual function body to append at the end
            func_body = f"""
void {func_name}(int *{vars['arr']}, int {vars['n']}) {{
{OPTIMIZATION_LIB[label].format(arr=vars['arr'], n=vars['n'])}
}}"""
            new_function_definitions.append(func_body)
            
            # Replace the old loop block with the new call
            final_code = final_code.replace(original_block, func_call)

    # Append new functions to the end of the file
    if new_function_definitions:
        final_code += "\n\n// ======= AI OPTIMIZED FUNCTIONS =======\n"
        final_code += "\n".join(new_function_definitions)

    with open(output_path, 'w') as f:
        f.write(final_code)
    print(f"🏁 Refactoring complete! Check {output_path}")

# ==========================================
# 4. MAIN WORKFLOW
# ==========================================
if __name__ == "__main__":
    # --- STEP A: Load & Train ---
    datasets = ["dataset.json", "dataset1.json", "dataset3.json", "dataset4.json", "dataset6.json"]
    all_data = []
    
    for d_file in datasets:
        if os.path.exists(d_file):
            with open(d_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    all_data.append({"code": clean_code(item['code']), "label": item['label']})
    
    if not all_data:
        print("❌ No data found to train on!")
    else:
        X = [i['code'] for i in all_data]
        y = [i['label'] for i in all_data]
        
        le = LabelEncoder()
        y_enc = le.fit_transform(y)
        
        clf = Pipeline([
            ('feats', FeatureUnion([
                ('struct', CodeStructureExtractor()),
                ('text', TfidfVectorizer(analyzer='char', ngram_range=(3, 5), max_features=3000))
            ])),
            ('rf', RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=42))
        ])
        
        print("🏋️ Training model...")
        clf.fit(X, y_enc)

        # --- STEP B: Refactor the Input File ---
        refactor_source_file("input.c", "optimized_code.c", clf, le)