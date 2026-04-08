import json
import os
import re
import random

# CONFIG
INPUT_FILES = ["dataset.json", "dataset1.json", "dataset3.json", "dataset4.json", "dataset6.json"]
OUTPUT_FILE = "master_dataset.json"

def clean_code(code):
    # Remove C-style and Python comments
    code = re.sub(r'//.*|#.*|/\*[\s\S]*?\*/', '', code)
    # Collapse whitespace
    code = " ".join(code.split())
    return code.strip()

def augment_variables(code):
    """
    Creates variations of the code by swapping common variable names.
    This prevents the model from overfitting to specific names.
    """
    variations = []
    # Transformation maps: (Target Word -> Replacement)
    transformations = [
        {"arr": "data", "i": "idx", "j": "k", "temp": "val"},
        {"arr": "vec", "i": "x", "j": "y", "n": "size"},
        {"nums": "items", "key": "target", "mid": "m"}
    ]
    
    for mapping in transformations:
        new_code = code
        for old, new in mapping.items():
            # Use regex to replace whole words only
            new_code = re.sub(rf'\b{old}\b', new, new_code)
        variations.append(new_code)
        
    return variations

def generate_master_dataset():
    all_data = []
    seen_code = set()
    
    print("🚀 Starting Dataset Generation...")

    for file_name in INPUT_FILES:
        if not os.path.exists(file_name):
            print(f"⚠️ Skipping {file_name} (not found)")
            continue
            
        with open(file_name, 'r') as f:
            data = json.load(f)
            for item in data:
                original_code = item['code']
                label = item['label']
                
                # 1. Clean the code
                cleaned = clean_code(original_code)
                
                # 2. Skip if it's an exact duplicate
                if cleaned in seen_code or not cleaned:
                    continue
                
                seen_code.add(cleaned)
                
                # 3. Add the cleaned original
                all_data.append({"code": cleaned, "label": label})
                
                # 4. Data Augmentation: Generate 2-3 variations per snippet
                # Only augment if it's an algorithm (length > 20 chars)
                if len(cleaned) > 20:
                    variants = augment_variables(cleaned)
                    for v in variants:
                        if v not in seen_code:
                            all_data.append({"code": v, "label": label})
                            seen_code.add(v)

    # Shuffle the dataset so classes are mixed
    random.shuffle(all_data)

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"✅ Success! Generated {len(all_data)} unique samples in {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_master_dataset()