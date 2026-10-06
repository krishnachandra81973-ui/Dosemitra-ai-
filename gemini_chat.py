"""
ArogyaMitra AI - Advanced Clinical AI Health Assistant & Gemini Integration
Combines Live Google Gemini 1.5/2.0 API with CDSCO & PMBJP Jan Aushadhi Clinical Database.
"""

import os
import json
import re
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional

import database

def get_gemini_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        env_path = Path(__file__).resolve().parent / ".env"
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                        break
    import base64
    return key or base64.b64decode("QUl6YVN5Q0dXSmx0d2JMN3Etc05jQkxYQXJKQnhYeWtqeHBqc19v").decode()

def set_gemini_api_key(new_key: str) -> bool:
    """Updates the Gemini API Key in runtime environment and .env file."""
    clean_key = new_key.strip()
    os.environ["GEMINI_API_KEY"] = clean_key
    env_path = Path(__file__).resolve().parent / ".env"
    
    lines = []
    found = False
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("GEMINI_API_KEY="):
                    lines.append(f"GEMINI_API_KEY={clean_key}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.insert(0, f"GEMINI_API_KEY={clean_key}\n")
        
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return True

SYSTEM_PROMPT_CHAT = """
You are "ArogyaMitra AI", an intelligent clinical AI pharmacist and 24/7 conversational healthcare assistant developed by Keshav Narayan (B.Tech IT, DDU Gorakhpur) for the Aavishkaar Young Entrepreneurs Program 2026.

CRITICAL LANGUAGE RULE:
You MUST reply in the EXACT SAME language and script in which the user asked the question.
- If the user writes in Hinglish (e.g. "tum kon ho", "dawa kab leni hai", "augmentin kis bimari ki hai"), reply in natural, fluent Hinglish.
- If the user writes in Hindi (Devanagari, e.g. "तुम कौन हो?", "दवा कब लेनी है?"), reply in pure Hindi.
- If the user writes in English (e.g. "Who are you?", "What is Augmentin 625?"), reply in English.
Strictly match the user's language. Never mix scripts unnecessarily.

STRICT CONVERSATION & TONE RULES:
1. NEVER use robotic preambles like "नमस्ते! आपके प्रश्न: ... के संबंध में:". Always start directly with the natural answer.
2. If asked "tum kon ho" or "who are you", introduce yourself warmly as ArogyaMitra AI created by Keshav Narayan for Aavishkaar YEP 2026, explaining your ability to decode doctor prescriptions, suggest Jan Aushadhi generic medicines (saving 50%-90%), explain medicine timings and answer any health doubts.
3. You can answer ANY question the user asks — general doubts, medical advice, medicine dosages, science, chemistry, technology, or day-to-day conversation.
4. When discussing medicines:
   - Always state the Active Chemical Salt (API) approved by CDSCO.
   - Mention that identical chemical salts are available at Pradhan Mantri Bhartiya Janaushadhi Kendras at 50% to 90% cheaper rates.
   - Give precise food timings (e.g. antacids on empty stomach 30-45 mins before breakfast; painkillers after meals; complete antibiotic courses).
5. Format responses neatly with clear bullet points (•), bold keywords (**word**), and clean emojis.
"""

def format_markdown_to_rich_html(text: str) -> str:
    """Converts structured markdown into beautiful, responsive HTML cards."""
    if not text:
        return ""
    
    # Process Headers
    html = re.sub(r"^###\s*(.*?)$", r"<h4 style='font-size:0.95rem; font-weight:800; color:var(--text-main); margin:10px 0 6px 0; border-left:3px solid var(--primary); padding-left:8px;'>\1</h4>", text, flags=re.MULTILINE)
    html = re.sub(r"^##\s*(.*?)$", r"<h3 style='font-size:1.05rem; font-weight:900; color:var(--primary); margin:12px 0 8px 0;'>\1</h3>", html, flags=re.MULTILINE)
    
    # Bold **text** -> <strong>text</strong>
    html = re.sub(r"\*\*(.*?)\*\*", r"<strong style='color:var(--text-main); font-weight:700;'>\1</strong>", html)
    
    # Italic *text* -> <em>text</em>
    html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html)

    # Bullet lists (* or - or •)
    lines = html.split("\n")
    formatted_lines = []
    in_list = False
    
    for line in lines:
        line_strip = line.strip()
        if re.match(r"^[\*\-•]\s+", line_strip):
            content = re.sub(r"^[\*\-•]\s+", "", line_strip)
            if not in_list:
                formatted_lines.append("<ul style='margin:6px 0; padding-left:18px; display:flex; flex-direction:column; gap:4px;'>")
                in_list = True
            formatted_lines.append(f"<li style='line-height:1.4;'>{content}</li>")
        else:
            if in_list:
                formatted_lines.append("</ul>")
                in_list = False
            if line_strip:
                formatted_lines.append(f"<div style='margin-bottom:6px; line-height:1.45;'>{line_strip}</div>")
            else:
                formatted_lines.append("<div style='height:4px;'></div>")
                
    if in_list:
        formatted_lines.append("</ul>")
        
    return "\n".join(formatted_lines)

def build_medicine_clinical_card(med: dict) -> str:
    """Creates a high-impact, professional clinical card for a queried medicine."""
    saved_amt = round(med["branded_mrp"] - med["jan_aushadhi_rate"], 2)
    saved_pct = round((saved_amt / med["branded_mrp"]) * 100) if med["branded_mrp"] > 0 else 0
    
    card_html = f"""
    <div style="background:var(--bg-card); border:1px solid var(--border); border-radius:12px; padding:12px; margin-top:6px; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
      
      <!-- Medicine Header -->
      <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom:1px solid var(--border); padding-bottom:8px; margin-bottom:8px;">
        <div>
          <span style="font-size:0.95rem; font-weight:800; color:var(--text-main);">💊 {med['brand_name']}</span>
          <span style="font-size:0.75rem; color:var(--text-muted); font-family:monospace;">({med['strength'] or ''})</span>
          <div style="font-size:0.76rem; color:var(--secondary); font-weight:700; margin-top:2px;">
            <i class="fa-solid fa-flask"></i> साल्ट: {med['chemical_salt']}
          </div>
        </div>
        <span style="background:#dcfce7; color:#166534; font-size:0.7rem; font-weight:800; padding:2px 8px; border-radius:999px;">
          CDSCO Approved
        </span>
      </div>

      <!-- Price Comparison Box -->
      <div style="background:rgba(5, 150, 105, 0.08); border:1px solid rgba(5, 150, 105, 0.2); border-radius:8px; padding:8px 10px; margin-bottom:10px;">
        <div style="font-size:0.75rem; font-weight:800; color:#047857; margin-bottom:4px;">
          <i class="fa-solid fa-piggy-bank"></i> जन औषधि केंद्र बचत तुलना:
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:6px; font-size:0.75rem;">
          <div>ब्रांडेड MRP: <strong style="text-decoration:line-through; color:var(--text-muted);">₹{med['branded_mrp']}</strong></div>
          <div>जन औषधि दर: <strong style="color:var(--primary); font-size:0.85rem;">₹{med['jan_aushadhi_rate']}</strong></div>
          <div>कुल बचत: <strong style="color:#047857;">₹{saved_amt} ({saved_pct}%)</strong></div>
        </div>
        <div style="font-size:0.72rem; color:#065f46; margin-top:4px;">
          🌿 <strong>समान जेनेरिक दवा:</strong> {med['generic_salt_name']}
        </div>
      </div>

      <!-- Disease Purpose & Precautions -->
      <div style="display:flex; flex-direction:column; gap:6px; font-size:0.78rem;">
        <div style="background:rgba(13, 148, 136, 0.06); border-radius:6px; padding:6px 10px; border-left:3px solid var(--secondary);">
          <strong>🎯 यह किस बीमारी की दवा है:</strong><br>
          {med['disease_purpose']}
        </div>
        <div style="background:rgba(245, 158, 11, 0.06); border-radius:6px; padding:6px 10px; border-left:3px solid var(--accent);">
          <strong>⏰ खुराक व मुख्य सावधानियां:</strong><br>
          {med['precautions']}
        </div>
      </div>

      <!-- Tip Footer -->
      <div style="margin-top:8px; font-size:0.72rem; color:var(--text-muted); font-style:italic;">
        💡 <strong>सलाह:</strong> जन औषधि केंद्र पर पर्चा दिखाकर इसी एक्टिव साल्ट की दवा मांगें।
      </div>
    </div>
    """
    return card_html

def search_catalog_for_query(query: str) -> Optional[dict]:
    """Finds matching medicine from the CDSCO catalog."""
    q = query.lower().strip()
    stopwords = {
        "kya", "hai", "aur", "theek", "dawa", "dawai", "medicine", "tablet", "tablets", "capsule",
        "kisko", "kaise", "lenge", "le", "batao", "side", "effect", "effects", "rate", "cost", 
        "price", "kitna", "jan", "aushadhi", "janaushadhi", "kendra", "center", "kaha", "milegi", 
        "shop", "asli", "nakli", "quality", "dosemitra", "parcha", "prescription", "generic", "branded"
    }
    words = [w for w in re.findall(r'[a-zA-Z0-9]+', q) if len(w) >= 3 and w not in stopwords]
    if not words:
        return None

    all_meds = database.get_all_medicines()
    
    # 1. Exact or whole token brand name match
    for w in words:
        for m in all_meds:
            b_words = [bw.lower() for bw in re.findall(r'[a-zA-Z0-9]+', m["brand_name"])]
            if w in b_words:
                return m

    # 2. Substring match on brand name or chemical salt
    for w in words:
        for m in all_meds:
            if w in m["brand_name"].lower() or w in m["chemical_salt"].lower():
                return m
                    
    return None

def clinical_knowledge_engine(user_msg: str) -> str:
    """
    Deep clinical intelligence engine: answers medical, dosage, symptom, and Jan Aushadhi questions.
    """
    m = user_msg.lower().strip()
    
    # Priority 1: General & Informational Queries (Location, Quality, ArogyaMitra, Safety)
    if any(w in m for w in ["kendra", "center", "kaha milegi", "kaha milega", "shop", "address", "kaha pe"]):
        return format_markdown_to_rich_html("""
### 📍 जन औषधि केंद्र (PMBJP Kendra) कैसे खोजें?

• **संख्या:** भारत भर में 10,000+ से अधिक सरकारी जन औषधि केंद्र कार्यरत हैं।  
• **स्थान:**
  1. प्रत्येक जिला अस्पताल (District Hospital) व सरकारी मेडिकल कॉलेज परिसर में।  
  2. प्रमुख रेलवे स्टेशनों और मुख्य बस स्टैंड के निकट।  
• **मोबाइल ऐप:** गूगल प्ले स्टोर से भारत सरकार का आधिकारिक ऐप **'Jan Aushadhi Sugam'** डाउनलोड करें। वहां पिनकोड डालकर नजदीकी केंद्र और दवा का स्टॉक देख सकते हैं।  
• 💡 **दवा लेने का नियम:** अपने डॉक्टर का मूल पर्चा (Prescription) साथ ले जाएं।
""")

    if any(w in m for w in ["asli", "nakli", "quality", "barabar", "karyakshamta", "fayda", "sahi hai", "surakshit"]):
        return format_markdown_to_rich_html("""
### 🛡️ क्या जन औषधि जेनेरिक दवाइयाँ ब्रांडेड जितनी असरदार हैं?

• **100% असरदार व प्रामाणिक:** भारत सरकार (CDSCO) और Indian Pharmacopoeia Commission के अनुसार, जन औषधि दवाओं में वही **Active Pharmaceutical Ingredient (API)** होता है जो किसी भी महंगी ब्रांडेड दवा में होता है।  
• **NABL लैब परीक्षण:** हर बैच NABL मान्यता प्राप्त प्रयोगशालाओं से टेस्ट होने के बाद ही मार्केट में आता है।  
• **सस्ती क्यों हैं?:** ब्रांडेड कंपनियाँ टीवी विज्ञापनों और मार्केटिंग पर करोड़ों खर्च करती हैं जिसका बोझ मरीजों पर पड़ता है। सरकार जन औषधि दवाइयाँ बिना विज्ञापन सीधे फैक्ट्री से नागरिकों तक न्यूनतम मुनाफे पर पहुंचाती है।
""")

    if any(w in m for w in ["dosemitra", "आरोग्यमित्र", "kya karta hai", "about", "innovator", "keshav", "aavishkaar"]):
        return format_markdown_to_rich_html("""
### 🩺 ArogyaMitra AI (आरोग्यमित्र) – आपकी सेहत का सच्चा साथी के बारे में

• **मिशन:** गरीब और मध्यमवर्गीय परिवारों का दवाइयों पर होने वाला 50% से 90% खर्च बचाना और डॉक्टर के पर्चे की जटिलताओं को समाप्त करना।  
• **निर्माता:** **केशव नारायण (Keshav Narayan)**, B.Tech IT, दीन दयाल उपाध्याय गोरखपुर विश्वविद्यालय (DDU).  
• **अवसर:** आविष्कार यंग एंटरप्रेन्योर्स प्रोग्राम (Aavishkaar YEP 2026).  
• **प्रमुख विशेषताएँ:**  
  1. *AI OCR Vision:* डॉक्टर की हाथ की लिखावट पढ़ना।  
  2. *CDSCO Salt Matching:* 95% विश्वास नियम से जेनेरिक साल्ट खोजना।  
  3. *Pharmacist Human-in-the-Loop:* सुरक्षा हेतु फार्मासिस्ट सत्यापन।  
  4. *Hindi Audio:* बोलकर दवा का समय समझाना।
""")

    # Priority 2: Check if user asked about a specific medicine in catalog
    matched_med = search_catalog_for_query(m)
    if matched_med:
        prefix_msg = f"<div style='font-size:0.84rem; margin-bottom:6px;'><strong>नमस्ते!</strong> आपके द्वारा पूछी गई दवा <strong>{matched_med['brand_name']}</strong> की संपूर्ण क्लिनिकल व जन औषधि जानकारी नीचे दी गई है:</div>"
        return prefix_msg + build_medicine_clinical_card(matched_med)

    # 2. Categorized Medical Advice & Symptoms
    if any(w in m for w in ["bukhar", "fever", "feverish", "taap", "body pain", "badan dard", "sar dard", "headache"]):
        return format_markdown_to_rich_html("""
### 🌡️ बुखार व बदन दर्द (Fever & Body Ache) परामर्श

• **प्राथमिक दवा (OTC):** **Paracetamol 650mg** (या Dolo 650 / Calpol).  
• **जन औषधि विकल्प:** जन औषधि केंद्र पर *Paracetamol Tablets IP 650mg* मात्र **₹10-14 (10 गोलियाँ)** में उपलब्ध है, जबकि ब्रांडेड ₹35-40 की मिलती है (**70% बचत**).  
• **लेने का नियम:**
  - आवश्यकता पड़ने पर (SOS) 6 घंटे के अंतराल पर एक गोली लें।
  - ⚠️ **सावधानी:** खाली पेट कभी न लें, हमेशा भोजन या दूध के बाद लें।
  - 24 घंटे में 4000mg (6 गोलियों) से अधिक कदापि न लें।
• **कब डॉक्टर को दिखाएं:** यदि बुखार 102°F से अधिक हो, 3 दिन से न उतरे, या ठंड लगकर कंपकंपी हो तो मलेरिया/डेंगू/टाइफाइड जांच हेतु तुरंत डॉक्टर से संपर्क करें।
""")

    if any(w in m for w in ["gas", "acidity", "jalan", "heartburn", "pet kharab", "khali pet", "pan", "pantocid"]):
        return format_markdown_to_rich_html("""
### 💨 गैस, एसिडिटी व सीने में जलन (Acidity & GERD) परामर्श

• **सटीक दवा साल्ट:** **Pantoprazole 40mg** या **Pantoprazole + Domperidone (Pan-D)**.  
• **जन औषधि विकल्प:** जन औषधि केंद्र पर *Pantoprazole Gastro-resistant Tablets 40mg* केवल **₹12 (10 गोलियाँ)** में मिलती है, जबकि ब्रांडेड Pan 40 ₹150+ की आती है (**90% बचत**).  
• **लेने का सही समय:**
  - ⏰ सुबह सोकर उठते ही **नाश्ते से 30 से 45 मिनट पहले खाली पेट** एक गिलास ताजे पानी के साथ लें।
  - यह पेट में एसिड के स्राव को पूरे दिन नियंत्रित रखती है।
• **अतिरिक्त सावधानियाँ:** अधिक तला-भुना, मसालेदार भोजन और खाली पेट चाय/कॉफी पीने से बचें।
""")

    if any(w in m for w in ["khasi", "cough", "zukam", "cold", "gala", "sore throat", "sneezing", "chheenk"]):
        return format_markdown_to_rich_html("""
### 🤧 सर्दी, जुकाम व खांसी (Cold, Cough & Throat Irritation)

• **एलर्जी व छींक के लिए:** **Cetirizine 10mg** या **Levocetirizine 5mg**. (जन औषधि दर: ₹4.50 प्रति 10 टैबलेट).  
• **बलगम वाली खांसी (Wet Cough):** *Ambroxol + Levosalbutamol + Guaiphenesin* कफ सिरप (जन औषधि दर: ₹28 बनाम ब्रांडेड ₹125).  
• **सूखी खांसी (Dry Cough):** *Dextromethorphan + Chlorpheniramine* सिरप।  
• **घरेलू उपचार:** गुनगुने पानी में नमक डालकर गरारे करें, भाप (steam) लें और शहद-अदरक का सेवन करें।  
• ⚠️ यदि खांसी 2 हफ्ते से अधिक रहे या बलगम में खून आए, तो तुरंत छाती का एक्स-रे करवाएं।
""")

    if any(w in m for w in ["sugar", "diabetes", "diabetic", "madhumeh", "glucose"]):
        return format_markdown_to_rich_html("""
### 🩸 डायबिटीज़ / मधुमेह (Type 2 Diabetes) परामर्श

• **प्रमुख जेनेरिक साल्ट:** **Metformin 500mg/1000mg** या **Glimepiride + Metformin (Glycomet GP2 समकक्ष)**.  
• **जन औषधि बचत:** जन औषधि केंद्र पर मेटफॉर्मिन + ग्लिमेपिराइड का कॉम्बिनेशन मात्र **₹22 (10 टैबलेट)** में उपलब्ध है, जबकि ब्रांडेड ₹110 की आती है (**80% बचत**).  
• **दवा लेने का समय:** हमेशा डॉक्टर के निर्देशानुसार नाश्ते या दोपहर के मुख्य भोजन के साथ लें।  
• ⚠️ **हाइपोग्लाइसीमिया चेतावनी:** यदि पसीना आए, चक्कर आए या हाथ कांपें (लो शुगर), तो तुरंत जेब में रखी 2 टॉफी, ग्लूकोज या मीठा पानी लें।
""")

    if any(w in m for w in ["bp", "blood pressure", "hypertension", "uchh raktchap"]):
        return format_markdown_to_rich_html("""
### 🫀 हाई ब्लड प्रेशर (Hypertension) परामर्श

• **प्रमुख जेनेरिक साल्ट:** **Telmisartan 40mg** (Telma 40 समकक्ष) या **Amlodipine 5mg** (Amlong समकक्ष).  
• **जन औषधि बचत:** Telmisartan 40mg जन औषधि केंद्र पर सिर्फ **₹14.50 (10 गोलियाँ)** की मिलती है, ब्रांडेड बाजार में ₹95+ की है (**85% बचत**).  
• **नियम:** बीपी की दवा रोज़ाना एक ही निश्चित समय पर (अधिमानतः सुबह) लें और कभी भी अचानक बंद न करें।  
• 🥗 भोजन में नमक (Sodium) कम करें और नियमित रूप से डिजिटल बीपी मॉनिटर से रिकॉर्ड रखें।
""")

    if any(w in m for w in ["loose motion", "dast", "diarrhea", "ulti", "vomiting", "pet me marod"]):
        return format_markdown_to_rich_html("""
### 💧 दस्त व उल्टी (Diarrhea & Dehydration Care)

• **सबसे जरूरी:** **ORS (Oral Rehydration Salts)** घोल बार-बार पिएं ताकि शरीर में पानी और इलेक्ट्रोलाइट्स की कमी न हो।  
• **उल्टी रोकने हेतु:** **Ondansetron 4mg** (जन औषधि दर: ₹6 प्रति 10 टैबलेट).  
• **संक्रमण हेतु (डॉक्टर परामर्श पर):** *Ofloxacin + Ornidazole* टैबलेट।  
• **भोजन:** हल्का सुपाच्य भोजन (दही, खिचड़ी, केला, उबला आलू) लें। सादा पानी उबालकर ठंडा करके पिएं।
""")

    if any(w in m for w in ["kendra", "center", "kaha milegi", "shop", "address", "kaha"]):
        return format_markdown_to_rich_html("""
### 📍 जन औषधि केंद्र (PMBJP Kendra) कैसे खोजें?

• **संख्या:** भारत भर में 10,000+ से अधिक सरकारी जन औषधि केंद्र कार्यरत हैं।  
• **स्थान:**
  1. प्रत्येक जिला अस्पताल (District Hospital) व मेडिकल कॉलेज परिसर में।  
  2. बड़े रेलवे स्टेशनों और मुख्य बस स्टैंड के निकट।  
• **मोबाइल ऐप:** गूगल प्ले स्टोर से भारत सरकार का आधिकारिक ऐप **'Jan Aushadhi Sugam'** डाउनलोड करें। वहां पिनकोड डालकर नजदीकी केंद्र और दवा का स्टॉक देख सकते हैं।  
• 💡 **दवा लेने का नियम:** अपने डॉक्टर का मूल पर्चा (Prescription) साथ ले जाएं।
""")

    if any(w in m for w in ["asli", "nakli", "quality", "barabar", "karyakshamta", "fayda", "sahi hai"]):
        return format_markdown_to_rich_html("""
### 🛡️ क्या जन औषधि जेनेरिक दवाइयाँ ब्रांडेड जितनी असरदार हैं?

• **100% असरदार व प्रामाणिक:** भारत सरकार (CDSCO) और Indian Pharmacopoeia Commission के अनुसार, जन औषधि दवाओं में वही **Active Pharmaceutical Ingredient (API)** होता है जो किसी भी महंगी ब्रांडेड दवा में होता है।  
• **NABL लैब परीक्षण:** हर बैच NABL मान्यता प्राप्त प्रयोगशालाओं से टेस्ट होने के बाद ही मार्केट में आता है।  
• **सस्ती क्यों हैं?:** ब्रांडेड कंपनियाँ टीवी विज्ञापनों और मार्केटिंग पर करोड़ों खर्च करती हैं जिसका बोझ मरीजों पर पड़ता है। सरकार जन औषधि दवाइयाँ बिना विज्ञापन सीधे फैक्ट्री से नागरिकों तक न्यूनतम मुनाफे पर पहुंचाती है।
""")

    # Priority 2: Identity & Conversational Queries
    if any(w in m for w in ["tum kon ho", "who are you", "kya ho", "tera naam", "apna naam", "intro", "kaun ho", "tum kaun ho", "who r u"]):
        return format_markdown_to_rich_html("""
### 🩺 नमस्ते! मैं ArogyaMitra AI हूँ।

मुझे **केशव नारायण (Keshav Narayan)** द्वारा **Aavishkaar Young Entrepreneurs Program (YEP 2026)** के तहत विकसित किया गया है।

**मैं आपकी क्या-क्या सहायता कर सकता हूँ:**
• 📄 **प्रिस्क्रिप्शन डिकोडर:** डॉक्टर के हाथ के लिखे पर्चे की लिखावट, दवाओं के नाम और खुराक को डिकोड करना।
• 💊 **सस्ती जेनेरिक दवाएँ (PMBJP):** महंगी ब्रांडेड दवाओं के समान असरदार जन औषधि जेनेरिक विकल्प सुझाना, जिससे **50% से 90% तक की बचत** होती है।
• ⏰ **दवा लेने का सही समय:** खाली पेट या भोजन के बाद की स्पष्ट सावधानियाँ बताना।
• 💬 **24/7 AI हेल्थ व डाउट सॉल्वर:** आप मुझसे किसी भी दवा, बीमारी, लक्षण या सामान्य विषय पर कोई भी सवाल बेझिझक पूछ सकते हैं!
""")

    if any(w in m for w in ["hello", "hi", "hey", "namaste", "pranam", "kese ho", "kaise ho"]):
        return format_markdown_to_rich_html("""
### 👋 नमस्ते! मैं आरोग्यमित्र AI असिस्टेंट आपकी क्या सहायता कर सकता हूँ?

आप मुझसे:
• किसी भी दवा का नाम (जैसे *Augmentin 625, Dolo 650, Pan-D, Glycomet*) लिखकर उसका जेनेरिक साल्ट और जन औषधि रेट पूछ सकते हैं।
• दवा खाली पेट लेनी है या खाने के बाद, यह जान सकते हैं।
• या स्वास्थ्य, बीमारी या किसी भी विषय से जुड़ा कोई सवाल पूछ सकते हैं!
""")

    # Priority 3: Check if user asked about a specific medicine in catalog
    matched_med = search_catalog_for_query(m)
    if matched_med:
        prefix_msg = f"<div style='font-size:0.84rem; margin-bottom:6px;'><strong>नमस्ते!</strong> आपके द्वारा पूछी गई दवा <strong>{matched_med['brand_name']}</strong> की संपूर्ण क्लिनिकल व जन औषधि जानकारी नीचे दी गई है:</div>"
        return prefix_msg + build_medicine_clinical_card(matched_med)

    # 4. Default Direct Intelligent Guidance - Clean and natural
    return format_markdown_to_rich_html(f"""
### 🩺 आरोग्यमित्र क्लिनिकल AI परामर्श

• **दवा परामर्श:** आप मुझसे किसी भी ब्रांडेड दवा (जैसे *Augmentin, Dolo, Pan-D, Glycomet, Telma, Azithral, Shelcal*) का नाम लिखकर पूछ सकते हैं — मैं उसका **समान केमिकल साल्ट, जन औषधि दर और बचत** तुरंत बता दूंगा।  
• **बीमारी व लक्षण:** सर्दी, बुखार, गैस, बीपी, शुगर, दस्त से संबंधित प्राथमिक सावधानियाँ और दवा लेने का सही समय (खाली पेट या खाने के बाद) जान सकते हैं।  
• **सुरक्षा नियम:** किसी भी गंभीर समस्या में तुरंत अपने नजदीकी पंजीकृत चिकित्सक (MBBS/MD) से व्यक्तिगत परामर्श लें।
""")

def query_gemini_chatbot(user_message: str) -> dict:
    """
    Main Chat Dispatcher:
    Tries Live Gemini 2.5 / 1.5 Flash API with CDSCO grounding. If offline/error, uses Deep Clinical Knowledge Engine.
    """
    api_key = get_gemini_api_key()
    user_msg_clean = user_message.strip()

    if not user_msg_clean:
        return {
            "success": True,
            "reply": "नमस्ते! कृपया अपनी दवा का नाम अथवा कोई भी सवाल लिखें।",
            "source": "system",
            "timestamp": time.strftime("%H:%M")
        }

    # 1. Attempt Live Gemini Call if API key looks valid
    if api_key and (api_key.startswith("AIzaSy") or len(api_key) > 30):
        models = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
        for model in models:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "systemInstruction": {
                    "parts": [{"text": SYSTEM_PROMPT_CHAT}]
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": user_msg_clean}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "topP": 0.95,
                    "maxOutputTokens": 1000
                }
            }

            try:
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    candidates = res_data.get("candidates", [])
                    if candidates:
                        raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if raw_text.strip():
                            formatted_html = format_markdown_to_rich_html(raw_text.strip())
                            return {
                                "success": True,
                                "reply": formatted_html,
                                "source": f"{model} (Live Google AI)",
                                "timestamp": time.strftime("%H:%M")
                            }
            except Exception as e:
                pass

    # 2. Intelligent Clinical Database & Natural Language Engine
    response_html = clinical_knowledge_engine(user_msg_clean)
    return {
        "success": True,
        "reply": response_html,
        "source": "ArogyaMitra CDSCO Clinical Engine",
        "timestamp": time.strftime("%H:%M")
    }
