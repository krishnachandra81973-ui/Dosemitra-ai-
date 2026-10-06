"""
DoseMitra AI Database Engine (SQLite)
Defines schema for:
- medicines_master: CDSCO approved brands, chemical salts, and PMBJP Jan Aushadhi rates
- scans: Human-in-the-loop tracking of prescription scans
"""

import sqlite3
import os
import json
from typing import Dict, Any, List, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dosemitra.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Table 1: medicines_master
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicines_master (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_name TEXT NOT NULL UNIQUE,
        chemical_salt TEXT NOT NULL,
        strength TEXT,
        branded_mrp REAL NOT NULL,
        generic_salt_name TEXT NOT NULL,
        jan_aushadhi_rate REAL NOT NULL,
        precautions TEXT,
        disease_purpose TEXT
    );
    """)

    # Table 2: scans
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id TEXT PRIMARY KEY,
        user_whatsapp TEXT,
        image_url TEXT,
        ocr_json TEXT,
        confidence_score REAL,
        status TEXT, -- 'AUTO_VERIFIED' | 'PENDING_PHARMACIST_REVIEW' | 'PHARMACIST_APPROVED'
        pharmacist_id TEXT,
        hindi_explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    seed_medicines(cursor, conn)
    conn.close()

def seed_medicines(cursor, conn):
    cursor.execute("SELECT COUNT(*) FROM medicines_master;")
    count = cursor.fetchone()[0]
    if count > 0:
        return

    medicines = [
        # 1. Pain & Fever
        ("Dolo 650", "Paracetamol IP 650mg", "650mg", 34.0, "Paracetamol Tablets IP 650mg (PMBJP)", 9.5, 
         "भोजन के बाद लें। 24 घंटे में 4 से अधिक गोलियाँ न लें। लिवर के रोगी डॉक्टर की सलाह से लें।",
         "तेज़ बुखार, सिरदर्द, बदन दर्द, दांत दर्द और वायरल फीवर के दर्द को कम करने के लिए।"),
        
        ("Crocin 500", "Paracetamol IP 500mg", "500mg", 24.0, "Paracetamol Tablets IP 500mg (PMBJP)", 6.0,
         "खाना खाने के बाद पानी के साथ लें। खाली पेट न लें।",
         "हल्के से मध्यम बुखार, बदन दर्द और सिरदर्द के इलाज के लिए।"),

        ("Combiflam", "Ibuprofen (400mg) + Paracetamol (325mg)", "400mg + 325mg", 52.0, "Ibuprofen 400mg + Paracetamol 325mg Tablets", 11.2,
         "हमेशा भोजन के बाद भरपूर पानी से लें। पेट में अल्सर हो तो न लें।",
         "मांसपेशियों के दर्द, दांत दर्द, मोच, जोड़ों के दर्द और सूजन को दूर करने के लिए।"),

        ("Zerodol-SP", "Aceclofenac (100mg) + Paracetamol (325mg) + Serratiopeptidase (15mg)", "100mg+325mg+15mg", 132.0, "Aceclofenac 100mg + Paracetamol 325mg + Serratiopeptidase 15mg Tablets", 26.5,
         "कड़े पेट या भोजन के बाद ही लें। इसके साथ एंटासिड लेना सुरक्षित रहता है।",
         "चोट की सूजन, ऑपरेशन के बाद का दर्द, गठिया (Arthritis) और गंभीर जोड़ों के दर्द के लिए।"),

        ("Zerodol-P", "Aceclofenac (100mg) + Paracetamol (325mg)", "100mg + 325mg", 72.0, "Aceclofenac 100mg + Paracetamol 325mg Tablets", 15.0,
         "भोजन के बाद लें। चक्कर आने पर गाड़ी न चलाएं।",
         "गठिया, दांत दर्द, कमर दर्द और जोड़ों के दर्द से राहत के लिए।"),

        ("Meftal-Spas", "Mefenamic Acid (250mg) + Dicyclomine (10mg)", "250mg + 10mg", 52.0, "Dicyclomine 10mg + Mefenamic Acid 250mg Tablets", 9.8,
         "पेट में अत्यधिक जलन होने पर एंटासिड के साथ लें।",
         "पेट में तेज मरोड़, ऐंठन, आंतों के दर्द और मासिक धर्म (Periods) के दर्द से राहत के लिए।"),

        ("Voveran 50", "Diclofenac Sodium IP 50mg", "50mg", 96.0, "Diclofenac Gastro-resistant Tablets IP 50mg", 6.5,
         "भोजन के बाद लें। दिल व किडनी के मरीज डॉक्टर की सलाह से लें।",
         "हड्डियों के गंभीर दर्द, फ्रैक्चर के दर्द और तीव्र गठिया के दर्द के लिए।"),

        # 2. Gastro & Acidity
        ("Pan-D", "Pantoprazole (40mg) + Domperidone (30mg SR)", "40mg + 30mg", 195.0, "Pantoprazole 40mg + Domperidone 30mg SR Capsules", 27.0,
         "सुबह उठते ही बासी मुँह (नाश्ते से 30 मिनट पहले खाली पेट) लें।",
         "पेट में भयंकर गैस, सीने में जलन (Heartburn), खट्टी डकारें, एसिड रिफ्लक्स और जी मिचलाने के लिए।"),

        ("Pan 40", "Pantoprazole Sodium IP 40mg", "40mg", 98.0, "Pantoprazole Gastro-resistant Tablets IP 40mg", 12.5,
         "रोजाना सुबह नाश्ते से 30 मिनट पहले खाली पेट लें।",
         "पेट के अल्सर, सीने की जलन, एसिडिटी और भारीपन को शांत करने के लिए।"),

        ("Omez 20", "Omeprazole IP 20mg", "20mg", 62.0, "Omeprazole Capsules IP 20mg", 6.2,
         "सुबह खाली पेट एक कैप्सूल सादे पानी से लें। कैप्सूल चबाएं नहीं।",
         "पेट में अत्यधिक एसिड बनना, अपच और खट्टी डकारों को रोकने के लिए।"),

        ("Razo-D", "Rabeprazole (20mg) + Domperidone (30mg SR)", "20mg + 30mg", 225.0, "Rabeprazole 20mg + Domperidone 30mg SR Capsules", 28.5,
         "सुबह नाश्ते से पहले खाली पेट लें।",
         "तीव्र एसिडिटी, गले में जलन और उल्टी जैसा महसूस होने से तुरंत राहत के लिए।"),

        ("Emeset 4", "Ondansetron Hydrochloride 4mg", "4mg", 58.0, "Ondansetron Tablets IP 4mg", 8.0,
         "उल्टी महसूस होने पर या खाने से 30 मिनट पहले लें।",
         "उल्टी, मतली, चक्कर और सफर में उल्टी आने की समस्या को रोकने के लिए।"),

        # 3. Hypertension & Heart (Blood Pressure)
        ("Telma 40", "Telmisartan IP 40mg", "40mg", 138.0, "Telmisartan Tablets IP 40mg", 22.0,
         "रोजाना सुबह नाश्ते के बाद एक निश्चित समय पर लें। अचानक बंद न करें।",
         "उच्च रक्तचाप (High BP) को नियंत्रित रखने और दिल का दौरा (Heart Attack) व स्ट्रोक से बचाने के लिए।"),

        ("Telma-H", "Telmisartan (40mg) + Hydrochlorothiazide (12.5mg)", "40mg + 12.5mg", 182.0, "Telmisartan 40mg + Hydrochlorothiazide 12.5mg Tablets", 29.5,
         "सुबह नाश्ते के बाद लें। दिन में पर्याप्त पानी पिएं।",
         "अनियंत्रित हाई ब्लड प्रेशर में नसों को रिलैक्स करने और शरीर से एक्स्ट्रा नमक बाहर निकालने के लिए।"),

        ("Telma-AM", "Telmisartan (40mg) + Amlodipine (5mg)", "40mg + 5mg", 210.0, "Telmisartan 40mg + Amlodipine 5mg Tablets", 32.0,
         "सुबह एक समय पर लें। पैरों में सूजन दिखे तो डॉक्टर को बताएं।",
         "डबल एक्शन से जिद्दी हाई ब्लड प्रेशर को नॉर्मल रेंज में बनाए रखने के लिए।"),

        ("Amlong 5", "Amlodipine Besylate IP 5mg", "5mg", 58.0, "Amlodipine Tablets IP 5mg", 6.8,
         "रोजाना रात को सोते समय या सुबह नाश्ते के बाद लें।",
         "रक्त वाहिकाओं को चौड़ा करके ब्लड प्रेशर घटाने और दिल पर दबाव कम करने के लिए।"),

        ("Concor 5", "Bisoprolol Fumarate 5mg", "5mg", 128.0, "Bisoprolol Tablets IP 5mg", 19.5,
         "सुबह नाश्ते के बाद लें। नब्ज (Pulse rate) नियमित चेक करें।",
         "दिल की तेज धड़कन (Palpitations) को सामान्य करने और हार्ट अटैक के खतरे को घटाने के लिए।"),

        ("Ecosprin 75", "Aspirin (Acetylsalicylic Acid) 75mg", "75mg", 9.5, "Aspirin Gastro-resistant Tablets IP 75mg", 3.8,
         "हमेशा रात के भोजन के बाद लें। खाली पेट कभी न लें।",
         "खून में थक्के (Clots) बनने से रोकने, हार्ट अटैक और पैरालिसिस (Stroke) से बचाव के लिए।"),

        # 4. Diabetes (Blood Sugar)
        ("Glycomet 500", "Metformin Hydrochloride IP 500mg SR", "500mg", 42.0, "Metformin Hydrochloride Sustained Release Tablets IP 500mg", 8.5,
         "सुबह और शाम खाना खाने के साथ या तुरंत बाद लें। खाली पेट न लें।",
         "टाइप-2 डायबिटीज में बढ़े हुए ब्लड शुगर को नियंत्रित रखने और इंसुलिन सेंसिटिविटी बढ़ाने के लिए।"),

        ("Glycomet-GP 2", "Metformin (500mg) + Glimepiride (2mg)", "500mg + 2mg", 145.0, "Glimepiride 2mg + Metformin 500mg Tablets", 28.0,
         "सुबह नाश्ते से 10 मिनट पहले लें। दवा लेने के बाद नाश्ता न छोड़ें।",
         "पैंक्रियाज से इंसुलिन रिलीज करवाकर अनियंत्रित शुगर को तेजी से नॉर्मल रेंज में लाने के लिए।"),

        ("Amaryl 1mg", "Glimepiride IP 1mg", "1mg", 88.0, "Glimepiride Tablets IP 1mg", 11.5,
         "सुबह नाश्ते के पहले निवाले के साथ लें।",
         "टाइप-2 डायबिटीज में पैंक्रियाज से इंसुलिन की मात्रा बढ़ाने के लिए।"),

        ("Forxiga 10", "Dapagliflozin 10mg", "10mg", 480.0, "Dapagliflozin Tablets 10mg", 65.0,
         "सुबह एक गोली पानी के साथ लें। दिनभर खूब पानी पिएं।",
         "यूरिन के रास्ते एक्स्ट्रा शुगर बाहर निकालने और डायबिटीज मरीजों की किडनी व दिल की सुरक्षा के लिए।"),

        ("Januvia 100", "Sitagliptin Phosphate 100mg", "100mg", 385.0, "Sitagliptin Tablets IP 100mg", 48.0,
         "दिन में एक बार भोजन के साथ या बिना लें।",
         "भोजन के बाद अचानक बढ़ने वाली शुगर (Postprandial) को कंट्रोल करने के लिए।"),

        # 5. Cholesterol & Heart
        ("Atorva 10", "Atorvastatin Calcium IP 10mg", "10mg", 115.0, "Atorvastatin Tablets IP 10mg", 14.2,
         "रात को सोने से पहले भोजन के बाद लें। तली-भुनी चीजों से परहेज करें।",
         "खून में बैड कोलेस्ट्रॉल (LDL) और ट्राइग्लिसराइड्स घटाकर नसों को ब्लॉक होने से बचाने के लिए।"),

        ("Rosuvas 10", "Rosuvastatin IP 10mg", "10mg", 178.0, "Rosuvastatin Tablets IP 10mg", 26.0,
         "रात को भोजन के बाद लें।",
         "धमनियों में जमी चर्बी को साफ करने और दिल की बीमारियों का रिस्क कम करने के लिए।"),

        # 6. Antibiotics & Anti-infectives
        ("Augmentin 625 Duo", "Amoxicillin (500mg) + Clavulanic Acid (125mg)", "625mg", 205.0, "Amoxicillin 500mg + Potassium Clavulanate 125mg Tablets IP", 60.0,
         "सुबह-शाम भोजन के बाद लें। डॉक्टर द्वारा बताया गया 5 दिन का पूरा कोर्स करें।",
         "गले में इन्फेक्शन, टॉन्सिल, छाती में कफ, फेफड़ों में इन्फेक्शन, कान व दांत के मवाद के इलाज के लिए।"),

        ("Azithral 500", "Azithromycin IP 500mg", "500mg", 135.0, "Azithromycin Tablets IP 500mg", 38.0,
         "दिन में एक बार, खाना खाने से 1 घंटा पहले या 2 घंटे बाद लें (3 से 5 दिन)।",
         "गले की खराश, खांसी, ब्रोंकाइटिस, निमोनिया और नाक-कान के बैक्टीरियल इन्फेक्शन के लिए।"),

        ("Taxim-O 200", "Cefixime IP 200mg", "200mg", 118.0, "Cefixime Dispersible Tablets IP 200mg", 42.0,
         "सुबह-शाम भोजन के बाद पानी के साथ लें।",
         "टाइफाइड बुखार, यूरिनरी ट्रैक्ट इन्फेक्शन (UTI) और सांस नली के संक्रमण के लिए।"),

        ("Cifran 500", "Ciprofloxacin IP 500mg", "500mg", 45.0, "Ciprofloxacin Tablets IP 500mg", 14.5,
         "सुबह-शाम भोजन के 2 घंटे बाद लें। दूध के साथ न लें।",
         "दस्त (Diarrhea), फूड पॉइजनिंग, पेट के कीड़े व पेशाब में इन्फेक्शन के खात्मे के लिए।"),

        ("Flagyl 400", "Metronidazole IP 400mg", "400mg", 24.0, "Metronidazole Tablets IP 400mg", 7.5,
         "भोजन के बाद लें। दवा के दौरान शराब का सेवन बिल्कुल न करें।",
         "पेट के इन्फेक्शन, अमीबिक पेचिश (खूनी दस्त) और मसूड़ों के इन्फेक्शन के लिए।"),

        # 7. Allergy, Cold & Cough
        ("Montair-LC", "Montelukast (10mg) + Levocetirizine (5mg)", "10mg + 5mg", 198.0, "Levocetirizine 5mg + Montelukast 10mg Tablets", 31.0,
         "रोजाना रात को सोते समय लें।",
         "लगातार छींकें आना, नाक बहना, आंखों से पानी आना, धूल-धुएं की एलर्जी और अस्थमा से बचाव के लिए।"),

        ("Cetzine 10", "Cetirizine Hydrochloride IP 10mg", "10mg", 24.0, "Cetirizine Tablets IP 10mg", 4.5,
         "रात को एक गोली लें। इससे हल्की नींद आ सकती है।",
         "त्वचा की खुजली, पित्ती (Hives), सर्दी-जुकाम और एलर्जिक छींकों से राहत के लिए।"),

        ("Allegra 120", "Fexofenadine Hydrochloride 120mg", "120mg", 218.0, "Fexofenadine Tablets IP 120mg", 34.0,
         "दिन में एक बार भोजन के बाद लें। इससे नींद नहीं आती।",
         "त्वचा पर लाल चकत्ते, तेज खुजली और मौसमी एलर्जी के लिए।"),

        ("Ascoril-LS", "Levosalbutamol + Ambroxol + Guaiphenesin", "100ml Syrup", 125.0, "Ambroxol + Levosalbutamol + Guaiphenesin Syrup", 28.0,
         "दिन में 3 बार 10ml भोजन के बाद गुनगुने पानी के साथ लें।",
         "छाती में जमे गाढ़े बलगम को पिघलाकर बाहर निकालने और सांस नली खोलने के लिए।"),

        # 8. Thyroid & Nutrition
        ("Thyronorm 50mcg", "Thyroxine Sodium IP 50mcg", "50mcg", 165.0, "Thyroxine Sodium Tablets IP 50mcg", 24.0,
         "सुबह आँख खुलते ही खाली पेट केवल सादे पानी से लें (चाय से 45 मिनट पहले)।",
         "हाइपोथायरायडिज्म (कम थायरॉयड बनना), सुस्ती, वजन बढ़ना और हार्मोनल असंतुलन ठीक करने के लिए।"),

        ("Shelcal 500", "Calcium Carbonate (500mg) + Vitamin D3 (250 IU)", "500mg + 250IU", 131.0, "Calcium 500mg with Vitamin D3 250 IU Tablets IP", 20.0,
         "दोपहर या रात को भोजन के बाद पानी से लें।",
         "कमजोर हड्डियां, जोड़ों में कटकट की आवाज, ऑस्टियोपोरोसिस और कैल्शियम की कमी दूर करने के लिए।"),

        ("Becosules Z", "Vitamin B-Complex + Vitamin C + Zinc", "Capsule", 56.0, "Vitamin B Complex with Vitamin C & Zinc Capsules", 12.0,
         "दोपहर भोजन के बाद एक कैप्सूल लें।",
         "मुंह में बार-बार छाले होना, कमजोरी, भूख न लगना और रोग प्रतिरोधक क्षमता बढ़ाने के लिए।"),

        ("Neurobion Forte", "Vitamin B1 + B6 + B12 (Cyanocobalamin)", "Tablet", 42.0, "Vitamin B1 + B6 + B12 Tablets", 9.2,
         "रात को भोजन के बाद लें।",
         "हाथ-पैरों में सुन्नपन, चींटी रेंगने जैसी झनझनाहट, नसों की कमजोरी और साइटिका के लिए।"),

        ("Orofer-XT", "Ferrous Ascorbate (100mg Iron) + Folic Acid (1.5mg)", "100mg + 1.5mg", 185.0, "Ferrous Ascorbate 100mg + Folic Acid 1.5mg Tablets", 24.5,
         "रात को भोजन के बाद पानी से लें। चाय या दूध के साथ न लें।",
         "खून की कमी (Anemia), लो हीमोग्लोबिन, चक्कर आना और अत्यधिक थकान दूर करने के लिए।"),

        ("Uprise-D3 60K", "Cholecalciferol (Vitamin D3) 60,000 IU", "60,000 IU", 310.0, "Cholecalciferol (Vitamin D3) Capsules IP 60,000 IU", 45.0,
         "सप्ताह में केवल एक बार (Weekly 1 Capsule) रात को गर्म दूध के साथ लें।",
         "शरीर में विटामिन D की गंभीर कमी, कमर दर्द, थकान और हड्डियों की कमजोरी के लिए।")
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO medicines_master 
    (brand_name, chemical_salt, strength, branded_mrp, generic_salt_name, jan_aushadhi_rate, precautions, disease_purpose)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, medicines)
    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized and seeded successfully.")


def save_scan(scan_data: dict) -> bool:
    """Inserts a new prescription scan into the scans table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO scans 
    (id, user_whatsapp, image_url, ocr_json, confidence_score, status, pharmacist_id, hindi_explanation)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        scan_data.get("id"),
        scan_data.get("user_whatsapp", ""),
        scan_data.get("image_url", ""),
        json.dumps(scan_data.get("ocr_json", {}), ensure_ascii=False) if isinstance(scan_data.get("ocr_json"), (dict, list)) else scan_data.get("ocr_json", "{}"),
        scan_data.get("confidence_score", 0.0),
        scan_data.get("status", "PENDING_PHARMACIST_REVIEW"),
        scan_data.get("pharmacist_id", ""),
        scan_data.get("hindi_explanation", "")
    ))
    conn.commit()
    conn.close()
    return True

def get_scan(scan_id: str) -> Optional[dict]:
    """Retrieves a single scan by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        if d.get("ocr_json"):
            try:
                d["ocr_json"] = json.loads(d["ocr_json"])
            except Exception:
                pass
        return d
    return None

def get_pending_scans() -> List[dict]:
    """Returns scans waiting for pharmacist verification."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE status = 'PENDING_PHARMACIST_REVIEW' ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        if d.get("ocr_json"):
            try:
                d["ocr_json"] = json.loads(d["ocr_json"])
            except Exception:
                pass
        result.append(d)
    return result

def get_all_scans(limit: int = 50) -> List[dict]:
    """Returns all scans for reporting / queue."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        if d.get("ocr_json"):
            try:
                d["ocr_json"] = json.loads(d["ocr_json"])
            except Exception:
                pass
        result.append(d)
    return result

def approve_scan(scan_id: str, pharmacist_id: str, approved_medicines: list = None, notes: str = None) -> bool:
    """Pharmacist HITL approval or correction of a scan."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT ocr_json FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
        
    ocr_data = {}
    if row[0]:
        try:
            ocr_data = json.loads(row[0])
        except Exception:
            pass
            
    if approved_medicines is not None:
        ocr_data["approved_medicines"] = approved_medicines
        ocr_data["pharmacist_notes"] = notes or "Pharmacist verified dosage and salt substitution."
        ocr_data["verified_by"] = pharmacist_id or "PHARM-LIC-8821"

    cursor.execute("""
    UPDATE scans 
    SET status = 'PHARMACIST_APPROVED',
        pharmacist_id = ?,
        ocr_json = ?
    WHERE id = ?;
    """, (pharmacist_id, json.dumps(ocr_data, ensure_ascii=False), scan_id))
    
    conn.commit()
    conn.close()
    return True

def search_medicines_db(query: str, limit: int = 20) -> List[dict]:
    """Searches medicines_master by brand name, chemical salt, or generic name."""
    conn = get_connection()
    cursor = conn.cursor()
    like_q = f"%{query}%"
    cursor.execute("""
    SELECT * FROM medicines_master 
    WHERE brand_name LIKE ? OR chemical_salt LIKE ? OR generic_salt_name LIKE ? OR disease_purpose LIKE ?
    LIMIT ?;
    """, (like_q, like_q, like_q, like_q, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_medicines() -> List[dict]:
    """Returns all medicines from catalog."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicines_master ORDER BY brand_name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
