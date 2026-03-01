import os
import certifi
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def map_severity(interaction_type):
    it = str(interaction_type).lower()
    if 'bleeding' in it or 'fatal' in it:
        return "Severe"
    if 'contraindicated' in it:
        return "Contraindicated"
    if 'concentration' in it or 'serum' in it or 'metabolism' in it:
        return "Moderate"
    return "Mild"

def main():
    MONGO_URI = os.getenv("MONGO_URI")
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client.medgraph_ai
    print("Atlas Seeding Script running... connect success!")
    
    csv_path = "Data/DDI_data.csv"
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}")
        return
        
    print(f"Reading first 5000 rows from {csv_path}...")
    df = pd.read_csv(csv_path, nrows=5000)
    
    # Drop existing to ensure clean seed
    print("Dropping existing interactions collection...")
    db.interactions.drop()
    
    documents = []
    for _, row in df.iterrows():
        drug1 = str(row['drug1_name']).upper()
        drug2 = str(row['drug2_name']).upper()
        
        # Deduplicate mirrored edges A->B vs B->A happens in backend, 
        # but we store the raw record here matching the expected DB schema
        doc = {
            "drug_1": drug1,
            "drug_2": drug2,
            "severity": map_severity(row['interaction_type']),
            "description": str(row['interaction_type'])
        }
        documents.append(doc)
        
    if documents:
        print(f"Inserting {len(documents)} interaction records into MongoDB Atlas...")
        result = db.interactions.insert_many(documents)
        print(f"Successfully inserted {len(result.inserted_ids)} records.")
    else:
        print("No records found to insert.")

if __name__ == "__main__":
    main()
