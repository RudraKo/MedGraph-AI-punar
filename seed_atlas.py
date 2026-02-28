import os
import sys
import pandas as pd
import numpy as np
import json
import re
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from tqdm import tqdm
from fuzzywuzzy import process, fuzz

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')

if not MONGO_URI:
    print("❌ ERROR: MONGO_URI not found in .env file.")
    print("Please add 'MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/' to your .env file.")
    sys.exit(1)

print("⏳ Initializing MedGraph.AI Local Atlas Import...")

# Connect to Atlas
import certifi
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tls=True, tlsCAFile=certifi.where())
    client.admin.command('ping')
    db = client['medgraph_ai']
    print("✅ Successfully connected to MongoDB Atlas (medgraph_ai).")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)

# Helper function to clear and import
def bulk_import_collection(df, collection_name, id_index=None):
    if df is None or df.empty:
        print(f"⚠️ Skipping {collection_name} - dataframe is empty.")
        return 0
        
    print(f"📦 Dropping collection '{collection_name}'...")
    db[collection_name].drop()
    
    records = df.to_dict('records')
    if records:
        print(f"🚀 Inserting {len(records)} documents into '{collection_name}'...")
        # Batch inserting to avoid payload blocks
        batch_size = 5000
        for i in tqdm(range(0, len(records), batch_size), desc=f"Seeding {collection_name}"):
            db[collection_name].insert_many(records[i:i+batch_size], ordered=False)
            
    if id_index:
        db[collection_name].create_index([(id_index, 1)])
        
    return len(records)

# Safe string cleaner
def clean_string(x):
    if pd.isna(x): return x
    return str(x).strip().lower()

# -------------------------------------------------------------------------
# STAGE 1: MEDICINE DETAILS (Kaggle) -> `drugs` & `compositions`
# -------------------------------------------------------------------------
print("\\n🔄 Processing Medicine Details...")
try:
    meds_path = 'Data/medicine_details.csv'
    if not os.path.exists(meds_path): meds_path = 'Data/medicine_dataset.csv' # Fallback to unzipped larger one
    
    df_meds = pd.read_csv(meds_path, low_memory=False)
    
    # Auto-detect generic/brand column names
    cols = df_meds.columns.str.lower()
    df_meds.columns = cols
    
    brand_col = next((c for c in cols if 'name' in c or 'brand' in c), cols[0])
    generic_col = next((c for c in cols if 'salt' in c or 'composition' in c or 'generic' in c), cols[1])
    
    print(f"  Mapped brand -> '{brand_col}', generic -> '{generic_col}'")
    
    df_meds['brand_name'] = df_meds[brand_col].apply(clean_string)
    df_meds['generic_name'] = df_meds[generic_col].apply(clean_string)
    
    # Deduplicate strictly based on combined exactness
    df_meds = df_meds.drop_duplicates(subset=['brand_name', 'generic_name'])
    
    # Compositions Generation (Basic NLP logic)
    print("  Extracting compositions mapping...")
    def parse_composition(string):
        if pd.isna(string): return []
        string = str(string).lower()
        comps = re.split(r'\\+|\\/| and ', string)
        parsed = []
        for c in comps:
            c = c.strip()
            c = re.sub(r'\\(.*?\\)', '', c) # remove brackets
            name = re.sub(r'[0-9\\.%]+\\s*(mg|g|mcg|ml|w/v|%|iu|w/w)', '', c).strip()
            amt = re.search(r'([0-9\\.]+)\\s*(mg|g|mcg|ml|w/v|%|iu|w/w)', c)
            if name:
                parsed.append({"component": name, "amount": amt.group(1) if amt else None, "unit": amt.group(2) if amt else None})
        return parsed

    # Sub-dataframe for just the compositions
    comps_df = df_meds[['generic_name']].drop_duplicates().copy()
    comps_df['composition_array'] = comps_df['generic_name'].apply(parse_composition)
    comps_df = comps_df[comps_df['generic_name'].notna()]
    
    inserted_drugs = bulk_import_collection(df_meds, 'drugs', id_index='generic_name')
    inserted_comps = bulk_import_collection(comps_df, 'compositions', id_index='generic_name')

except Exception as e:
    print(f"❌ Failed processing medicine_details: {e}")
    inserted_drugs, inserted_comps = 0, 0

# -------------------------------------------------------------------------
# STAGE 2: DDI DATA (Mendeley Interactions) -> `interactions`
# -------------------------------------------------------------------------
print("\\n🔄 Processing Drug-Drug Interactions...")
try:
    df_ddi = pd.read_csv('Data/DDI_data.csv', low_memory=False)
    
    # Auto-detect desc column
    desc_col = next((c for c in df_ddi.columns if 'desc' in c.lower() or 'text' in c.lower() or 'interact' in c.lower()), df_ddi.columns[-1])
    
    def classify_severity(description):
        if not isinstance(description, str): return "MILD"
        desc = description.lower()
        if any(k in desc for k in ["contraindicated", "do not use", "must not", "never combine"]): return "CONTRAINDICATED"
        elif any(k in desc for k in ["severe", "life-threatening", "fatal", "major", "critical"]): return "SEVERE"
        elif any(k in desc for k in ["moderate", "caution", "monitor", "increased risk", "may increase"]): return "MODERATE"
        return "MILD"

    print("  Applying severity classifier...")
    df_ddi['severity'] = df_ddi[desc_col].apply(classify_severity)
    
    inserted_ints = bulk_import_collection(df_ddi, 'interactions', id_index='severity')
except Exception as e:
    print(f"❌ Failed processing DDI_data: {e}")
    inserted_ints = 0


# -------------------------------------------------------------------------
# STAGE 3: SIDER DATA (Side Effects) -> `side_effects`
# -------------------------------------------------------------------------
print("\\n🔄 Processing SIDER / MedDRA Side Effects...")
try:
    df_se = pd.read_csv('Data/meddra_all_se.tsv.gz', sep='\t', header=None, low_memory=False)
    # Adding naive column names (SIDER typical format: stitch_id_flat, stitch_id_stereo, umls_concept_id_label, meddra_concept_type, umls_concept_id_meddra, side_effect_name)
    df_se.columns = ['stitch_id_flat', 'stitch_id_stereo', 'umls_from_label', 'meddra_type', 'umls_meddra', 'side_effect_name']
    
    inserted_se = bulk_import_collection(df_se, 'side_effects', id_index='side_effect_name')
except Exception as e:
    print(f"❌ Failed processing meddra_all_se: {e}")
    inserted_se = 0

# -------------------------------------------------------------------------
# SUMMARY
# -------------------------------------------------------------------------
print("\\n" + "="*50)
print("📊 MedGraph.AI Local Seed Complete")
print("="*50)
print(f"✅ Drugs imported: {inserted_drugs}")
print(f"✅ Compositions mapped: {inserted_comps}")
print(f"✅ Interactions imported: {inserted_ints}")
print(f"✅ Side Effects imported: {inserted_se}")
print("="*50)
print("The backend DB is now fully loaded for ML training!")
