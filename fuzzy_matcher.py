"""
Fuzzy Matcher Engine for DoseMitra AI
Uses token_sort_ratio against SQLite medicines_master to match raw prescription strings.
Evaluates confidence threshold (95%) and generates Hindi vernacular explanations.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from difflib import SequenceMatcher

try:
    from rapidfuzz import fuzz
    def rapid_token_sort_ratio(s1: str, s2: str) -> float:
        return float(fuzz.token_sort_ratio(s1, s2))
except ImportError:
    def rapid_token_sort_ratio(s1: str, s2: str) -> float:
        """High-fidelity token_sort_ratio implementation"""
        def clean_and_sort(s: str) -> str:
            tokens = re.findall(r'[a-zA-Z0-9]+', s.lower())
            tokens.sort()
            return " ".join(tokens)
        t1 = clean_and_sort(s1)
        t2 = clean_and_sort(s2)
        if not t1 or not t2:
            return 0.0
        return round(SequenceMatcher(None, t1, t2).ratio() * 100, 2)

class PrescriptionFuzzyMatcher:
    CONFIDENCE_THRESHOLD = 95.0

    def __init__(self, db_conn):
        self.conn = db_conn
        self._load_master_catalog()

    def _load_master_catalog(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, brand_name, chemical_salt, strength, branded_mrp, 
                   generic_salt_name, jan_aushadhi_rate, precautions, disease_purpose 
            FROM medicines_master;
        """)
        self.catalog = [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        t = text.lower()
        t = re.sub(r'(\d+)\s*(mg|mcg|gm|ml)\b', r'\1 \2', t)
        t = re.sub(r'\b(tab|cap|capsule|tablet|syp|syrup|inj|injection|strip|oral|tablets|dr|rx)\b', ' ', t)
        t = re.sub(r'\b(mg|mcg|gm|ml|iu)\b', ' ', t)
        t = re.sub(r'[^a-z0-9\s]', ' ', t)
        return re.sub(r'\s+', ' ', t).strip()

    @staticmethod
    def extract_timing_and_frequency(text: str) -> Tuple[str, str]:
        t = text.lower()
        # Frequency
        freq = "1-0-0"
        freq_hi = "दिन में एक बार"
        if re.search(r'\b(1-0-1|1\s*-\s*0\s*-\s*1|bd|bid|twice daily|दो बार)\b', t):
            freq = "1-0-1"
            freq_hi = "दिन में 2 बार (सुबह और शाम)"
        elif re.search(r'\b(1-1-1|1\s*-\s*1\s*-\s*1|tds|tid|thrice daily|तीन बार)\b', t):
            freq = "1-1-1"
            freq_hi = "दिन में 3 बार (सुबह, दोपहर और रात)"
        elif re.search(r'\b(0-0-1|0\s*-\s*0\s*-\s*1|hs|bedtime|रात को|सोते समय)\b', t):
            freq = "0-0-1"
            freq_hi = "रात को सोते समय"
        elif re.search(r'\b(sos|as needed|जब ज़रूरत हो|दर्द होने पर)\b', t):
            freq = "1-1-1 (SOS)"
            freq_hi = "ज़रूरत पड़ने पर (SOS)"
        elif re.search(r'\b(1-0-0|1\s*-\s*0\s*-\s*0|od|once daily|सुबह)\b', t):
            freq = "1-0-0"
            freq_hi = "सुबह एक बार"

        # Food Relation
        food_hi = "भोजन के बाद (After food)"
        if re.search(r'\b(empty stomach|before food|before breakfast|khali pet|खाली पेट|ac)\b', t):
            food_hi = "सुबह खाली पेट (नाश्ते से 30 मिनट पहले)"
        elif re.search(r'\b(with food|with meals|खाने के साथ)\b', t):
            food_hi = "भोजन के साथ"
        elif re.search(r'\b(after food|after meals|after dinner|after lunch|khane ke baad|खाने के बाद|pc)\b', t):
            food_hi = "भोजन के बाद"

        return f"{freq} ({freq_hi})", food_hi

    def match_raw_medicine(self, raw_med_text: str) -> Dict[str, Any]:
        """
        Fuzzy matches raw text against medicines_master using token_sort_ratio.
        """
        clean_query = self.clean_text(raw_med_text)
        timing_str, food_str = self.extract_timing_and_frequency(raw_med_text)

        best_med = None
        best_ratio = 0.0

        for med in self.catalog:
            # Check ratio against brand_name
            clean_brand = self.clean_text(med["brand_name"])
            ratio_brand = rapid_token_sort_ratio(clean_query, clean_brand)

            # Check ratio against chemical salt
            clean_salt = self.clean_text(med["chemical_salt"])
            ratio_salt = rapid_token_sort_ratio(clean_query, clean_salt)

            # Substring exact boost
            sub_boost = 0.0
            if clean_brand in clean_query or clean_query in clean_brand:
                sub_boost = 15.0

            ratio = max(ratio_brand + sub_boost, ratio_salt)

            if ratio > best_ratio:
                best_ratio = min(ratio, 100.0)
                best_med = med

        # Build response item
        is_high_conf = best_ratio >= self.CONFIDENCE_THRESHOLD and best_med is not None

        if best_med and best_ratio >= 50.0:
            saving_amt = round(best_med["branded_mrp"] - best_med["jan_aushadhi_rate"], 2)
            saving_pct = round((saving_amt / best_med["branded_mrp"]) * 100, 1)

            return {
                "raw_text": raw_med_text,
                "matched": True,
                "confidence_score": round(best_ratio, 1),
                "is_confident": is_high_conf,
                "medicine_id": best_med["id"],
                "brand_name": best_med["brand_name"],
                "chemical_salt": best_med["chemical_salt"],
                "strength": best_med["strength"],
                "disease_purpose": best_med["disease_purpose"],
                "precautions": best_med["precautions"],
                "timing": timing_str,
                "food_instruction": food_str,
                "branded_mrp": best_med["branded_mrp"],
                "generic_salt_name": best_med["generic_salt_name"],
                "jan_aushadhi_rate": best_med["jan_aushadhi_rate"],
                "savings_amount": saving_amt,
                "savings_percentage": saving_pct
            }
        else:
            return {
                "raw_text": raw_med_text,
                "matched": False,
                "confidence_score": round(best_ratio, 1),
                "is_confident": False,
                "medicine_id": None,
                "brand_name": raw_med_text,
                "chemical_salt": "Unverified Salt",
                "strength": "-",
                "disease_purpose": "फार्मासिस्ट द्वारा सत्यापन आवश्यक है।",
                "precautions": "सत्यापन से पहले न लें।",
                "timing": timing_str,
                "food_instruction": food_str,
                "branded_mrp": 0.0,
                "generic_salt_name": "Pending Verification",
                "jan_aushadhi_rate": 0.0,
                "savings_amount": 0.0,
                "savings_percentage": 0.0
            }

    def process_extracted_medicines(self, raw_medicines_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processes list of raw medicines from Gemini Vision or OCR.
        Tags overall status as 'AUTO_VERIFIED' (all >=95%) or 'PENDING_PHARMACIST_REVIEW'.
        Generates Hindi vernacular explanation.
        """
        matched_items = []
        scores = []
        requires_review = False

        for item in raw_medicines_list:
            text = item.get("raw_text") or item.get("name") or str(item)
            match_res = self.match_raw_medicine(text)
            
            # If explicit dosage or timing was given by Gemini, overlay it
            if item.get("dosage"):
                match_res["timing"] = item.get("dosage") + " (" + match_res["timing"] + ")"
            if item.get("timing"):
                match_res["food_instruction"] = item.get("timing")

            matched_items.append(match_res)
            scores.append(match_res["confidence_score"])
            if not match_res["is_confident"]:
                requires_review = True

        overall_confidence = round(sum(scores) / len(scores), 1) if scores else 0.0
        status = "PENDING_PHARMACIST_REVIEW" if (requires_review or overall_confidence < self.CONFIDENCE_THRESHOLD) else "AUTO_VERIFIED"

        # Financial totals
        total_branded = sum(m["branded_mrp"] for m in matched_items)
        total_generic = sum(m["jan_aushadhi_rate"] for m in matched_items)
        total_saved_mo = round(total_branded - total_generic, 2)
        total_saved_yr = round(total_saved_mo * 12, 2)
        savings_pct = round((total_saved_mo / total_branded) * 100, 1) if total_branded > 0 else 0.0

        # Step D: Hindi Vernacular Explanation
        hindi_explanation = self.generate_hindi_speech_text(matched_items, total_branded, total_generic, total_saved_mo, savings_pct)

        return {
            "overall_confidence": overall_confidence,
            "status": status,
            "medicines": matched_items,
            "financials": {
                "total_branded_cost": total_branded,
                "total_jan_aushadhi_cost": total_generic,
                "monthly_savings": total_saved_mo,
                "yearly_savings": total_saved_yr,
                "savings_percentage": savings_pct
            },
            "hindi_explanation": hindi_explanation
        }

    @staticmethod
    def generate_hindi_speech_text(medicines: List[Dict[str, Any]], total_b: float, total_g: float, saved: float, pct: float) -> str:
        lines = [
            f"नमस्ते! DoseMitra AI ने आपके डॉक्टर के पर्चे की जांच पूरी कर ली है। आपके पर्चे में कुल {len(medicines)} दवाइयाँ पहचानी गई हैं:"
        ]
        for idx, m in enumerate(medicines, 1):
            if m["matched"]:
                lines.append(f"{idx}. {m['brand_name']} — यह {m['disease_purpose']} लेने का समय: {m['timing']}, {m['food_instruction']}।")
            else:
                lines.append(f"{idx}. {m['raw_text']} — यह दवा अस्पष्ट है, फार्मासिस्ट द्वारा जांच की जा रही है।")

        if total_b > 0:
            lines.append(
                f"जन औषधि बचत सूचना: इन ब्रांडेड दवाइयों का कुल खर्च लगभग ₹{total_b} है। वही समान असर वाली असली दवा प्रधानमंत्री जन औषधि केंद्र पर मात्र ₹{total_g} में उपलब्ध है। यानी आप हर महीने ₹{saved} (लगभग {pct}%) बचा सकते हैं!"
            )
        lines.append("ज़रूरी सुरक्षा सलाह: दवा लेते समय जन औषधि केंद्र के लाइसेंस प्राप्त फार्मासिस्ट को अपना मूल पर्चा ज़रूर दिखाएं।")
        return " ".join(lines)


def match_prescription_medicines(raw_medicines_list: list) -> dict:
    """Convenience module function that initializes DB connection and runs matcher."""
    import database
    conn = database.get_connection()
    try:
        matcher = PrescriptionFuzzyMatcher(conn)
        return matcher.process_extracted_medicines(raw_medicines_list)
    finally:
        conn.close()
