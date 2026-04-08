import json
import os
import re
import random
import numpy as np
from collections import Counter

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

# ==========================================
# 1. DATA GENERATION & AUGMENTATION
# ==========================================
def clean_code(code):
    if not code: return ""
    # Remove C-style and Python comments, then normalize whitespace
    code = re.sub(r'//.*|#.*|/\*[\s\S]*?\*/', '', str(code))
    return " ".join(code.split()).strip()

def augment_variables(code):
    """Creates variations of variable names to prevent overfitting."""
    transformations = [
        {"arr": "data", "i": "idx", "j": "k", "temp": "val", "n": "sz", "nums": "vec"},
        {"nums": "items", "key": "target", "mid": "m", "l": "start", "r": "end", "a": "arr_a"},
        {"arr": "vec", "i": "x", "j": "y", "res": "out", "count": "total"}
    ]
    variants = []
    for mapping in transformations:
        new_code = code
        for old, new in mapping.items():
            new_code = re.sub(rf'\b{old}\b', new, new_code)
        variants.append(new_code)
    return variants

def prepare_master_dataset(input_files):
    print("🧹 Cleaning and augmenting data...")
    all_data = []
    seen = set()
    
    for file in input_files:
        if not os.path.exists(file):
            print(f"⚠️ Warning: File not found: {file}")
            continue
            
        try:
            with open(file, 'r') as f:
                content = json.load(f)
                print(f"📂 Found {len(content)} items in {file}")
                for item in content:
                    code_text = item.get('code', '')
                    label_text = item.get('label', '')
                    
                    cleaned = clean_code(code_text)
                    if not cleaned or cleaned in seen: continue
                    
                    seen.add(cleaned)
                    all_data.append({"code": cleaned, "label": label_text})
                    
                    # Add augmented versions for logic-rich snippets
                    if len(cleaned) > 15:
                        for v in augment_variables(cleaned):
                            if v not in seen:
                                all_data.append({"code": v, "label": label_text})
                                seen.add(v)
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
            
    return all_data

# ==========================================
# 2. MODEL ARCHITECTURE
# ==========================================
class CodeStructureExtractor(BaseEstimator, TransformerMixin):
    """Extracts structural 'fingerprints' to understand algorithm complexity."""
    def fit(self, x, y=None): return self
    def transform(self, posts):
        features = []
        for code in posts:
            f = [
                len(re.findall(r'\bfor\b', code)),
                len(re.findall(r'\bwhile\b', code)),
                len(re.findall(r'\bif\b', code)),
                len(re.findall(r'return', code)),
                # Triple nesting detection (Common in Matrix Multiply)
                len(re.findall(r'(for|while).*(for|while).*(for|while)', code, re.DOTALL)), 
                # 2D Array Access detection (Crucial for Matrix Multiply vs Nested Sums)
                len(re.findall(r'\[.*\]\s*\[.*\]', code)), 
                len(re.findall(r'[+\-*/%]', code)), 
                len(re.findall(r'\[.*\]', code))    
            ]
            features.append(f)
        return np.array(features)

# ==========================================
# 3. MAIN TRAINING EXECUTION
# ==========================================
if __name__ == "__main__":
    datasets = ["dataset.json", "dataset1.json", "dataset3.json", "dataset4.json", "dataset6.json"]
    
    raw_data = prepare_master_dataset(datasets)
    
    if not raw_data:
        print("🛑 FATAL ERROR: No data was loaded.")
    else:
        # STEP 1: Filter classes with < 2 members to allow stratification
        labels_raw = [item['label'] for item in raw_data]
        counts = Counter(labels_raw)
        valid_labels = {l for l, c in counts.items() if c >= 2}
        
        filtered_data = [item for item in raw_data if item['label'] in valid_labels]
        X = [item['code'] for item in filtered_data]
        y = [item['label'] for item in filtered_data]
        
        print(f"✅ Final Samples: {len(X)} | Unique Classes: {len(valid_labels)}")

        # STEP 2: Encode Labels and Split Data
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        # STEP 3: Build Pipeline (Hybrid Character N-Gram + Structural Logic)
        clf = Pipeline([
            ('features', FeatureUnion([
                ('struct', CodeStructureExtractor()),
                ('text', TfidfVectorizer(analyzer='char', ngram_range=(3, 5), max_features=3000))
            ])),
            ('rf', RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=42))
        ])

        print("🏋️ Training model...")
        clf.fit(X_train, y_train)

        # STEP 4: Robust Evaluation
        y_pred = clf.predict(X_test)
        print(f"\n🚀 Final Accuracy: {accuracy_score(y_test, y_pred):.2%}")
        
        # Identify classes actually tested to avoid printing errors
        present_classes = np.unique(np.concatenate((y_test, y_pred)))
        present_names = [le.classes_[i] for i in present_classes]

        print("\n📊 Classification Report:")
        print(classification_report(
            y_test, 
            y_pred, 
            labels=present_classes, 
            target_names=present_names
        ))

        # STEP 5: Interactive Interactive Testing
        print("\n🔍 Test a snippet (or type 'exit'):")
        while True:
            user_input = input("Code> ")
            if user_input.lower() == 'exit': break
            
            cleaned_input = clean_code(user_input)
            pred_idx = clf.predict([cleaned_input])[0]
            probs = clf.predict_proba([cleaned_input])[0]
            
            top_idx = np.argmax(probs)
            confidence = probs[top_idx]
            
            print(f"➡️  Prediction: {le.inverse_transform([pred_idx])[0]} ({confidence:.1%} confidence)")