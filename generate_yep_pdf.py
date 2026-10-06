# -*- coding: utf-8 -*-
import sys
import os

# Add local site-packages
sys.path.insert(0, './site-packages')

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Devanagari font
font_path = '/usr/share/fonts/truetype/Gargi/Gargi.ttf'
pdfmetrics.registerFont(TTFont('Gargi', font_path))

PAGE_WIDTH, PAGE_HEIGHT = A4 # 595.28 x 841.89 pt
MARGIN_X = 36
BOX_WIDTH = PAGE_WIDTH - 2 * MARGIN_X # 523.28 pt

# Box coordinates (2 boxes per page)
TOP_BOX_Y = 422
TOP_BOX_H = 366

BOT_BOX_Y = 40
BOT_BOX_H = 366

# Define Typography Styles
title_style = ParagraphStyle(
    'BoxTitle',
    fontName='Gargi',
    fontSize=10.5,
    leading=14,
    alignment=1, # Center
    textColor=colors.HexColor('#0f172a')
)

prompt_style = ParagraphStyle(
    'BoxPrompt',
    fontName='Gargi',
    fontSize=7.6,
    leading=10.2,
    alignment=1, # Center
    textColor=colors.HexColor('#334155')
)

head_style = ParagraphStyle(
    'SectionHead',
    fontName='Gargi',
    fontSize=8.3,
    leading=11.2,
    textColor=colors.HexColor('#1e40af')
)

body_style = ParagraphStyle(
    'BodyText',
    fontName='Gargi',
    fontSize=7.4,
    leading=10.0,
    textColor=colors.HexColor('#0f172a')
)

bullet_style = ParagraphStyle(
    'BulletText',
    fontName='Gargi',
    fontSize=7.2,
    leading=9.8,
    textColor=colors.HexColor('#1e293b')
)

def draw_header_footer(c, page_num):
    # Top Header
    c.saveState()
    c.setFont('Helvetica-Bold', 9.5)
    c.setFillColor(colors.HexColor('#1e293b'))
    c.drawString(MARGIN_X, 816, "YEP_ArogyaMitra AI_IET DDU Gorakhpur University")
    
    # Right: Aavishkaar Foundation
    c.setFont('Helvetica-Bold', 10.5)
    c.setFillColor(colors.HexColor('#0f172a'))
    c.drawRightString(PAGE_WIDTH - MARGIN_X, 818, "Aavishkaar Foundation")
    c.setFont('Helvetica', 7.2)
    c.setFillColor(colors.HexColor('#475569'))
    c.drawRightString(PAGE_WIDTH - MARGIN_X, 808, "AAVISHKAAR GROUP")
    
    # Decorative line under header
    c.setStrokeColor(colors.HexColor('#cbd5e1'))
    c.setLineWidth(0.6)
    c.line(MARGIN_X, 800, PAGE_WIDTH - MARGIN_X, 800)
    
    # Bottom Footer
    c.setFont('Helvetica', 7.5)
    c.setFillColor(colors.HexColor('#64748b'))
    c.drawString(MARGIN_X, 24, "ArogyaMitra AI • Aavishkaar YEP 2026 Business Proposal • Confidential")
    c.drawRightString(PAGE_WIDTH - MARGIN_X, 24, f"Page {page_num} of 5")
    c.restoreState()

def draw_box(c, x, y, w, h, title, prompt, elements):
    # Outer Border
    c.saveState()
    c.setStrokeColor(colors.HexColor('#1e293b'))
    c.setLineWidth(0.8)
    c.setFillColor(colors.HexColor('#ffffff'))
    c.rect(x, y, w, h, stroke=1, fill=1)
    
    # Inner padding
    pad = 10
    inner_w = w - 2 * pad
    cur_y = y + h - pad
    
    # Title
    p_title = Paragraph(f"<b><u>{title}</u></b>", title_style)
    tw, th = p_title.wrap(inner_w, 40)
    cur_y -= th
    p_title.drawOn(c, x + pad, cur_y)
    cur_y -= 4
    
    # Prompt
    p_prompt = Paragraph(f"<i>{prompt}</i>", prompt_style)
    pw, ph = p_prompt.wrap(inner_w, 60)
    cur_y -= ph
    p_prompt.drawOn(c, x + pad, cur_y)
    cur_y -= 6
    
    # Thin divider line
    c.setStrokeColor(colors.HexColor('#e2e8f0'))
    c.setLineWidth(0.5)
    c.line(x + pad, cur_y, x + w - pad, cur_y)
    cur_y -= 8
    
    # Render element list
    for el in elements:
        if isinstance(el, (Paragraph, Table)):
            ew, eh = el.wrap(inner_w, cur_y - (y + pad))
            cur_y -= eh
            el.drawOn(c, x + pad, cur_y)
            cur_y -= 4 # spacing between items
        elif isinstance(el, (int, float)):
            cur_y -= el # spacing spacer
            
    c.restoreState()

# Output PDF path
pdf_path = "ArogyaMitra_AI_Aavishkaar_YEP_Proposal.pdf"
c = canvas.Canvas(pdf_path, pagesize=A4)

print("Starting PDF creation...")

# ========================================================
# PAGE 1: Problem Statement & Business Idea
# ========================================================
draw_header_footer(c, 1)

# P1 - Box 1: Problem Statement
p1_b1_title = "Problem Statement/ समस्या का विवरण"
p1_b1_prompt = "Share social issue/s or problem/s identified by your team. Who does it affect the most? Use charts/statistics/pictures to explain the same. (सामाजिक मुद्दे या अपनी टीम द्वारा पहचानी गई समस्या को साझा करें। यह सबसे ज्यादा किसे प्रभावित करता है? इसे समझाने के लिए चार्ट/सांख्यिकी/चित्रों का उपयोग करें।)"

p1_b1_elements = [
    Paragraph("<b>1. मुख्य सामाजिक समस्याएं (Core Social Issues Identified):</b>", head_style),
    Paragraph("• <b>अपठनीय हैंडराइटिंग पर्चियां (Illegible Prescriptions):</b> भारत में 80% से अधिक डॉक्टरों के प्रिस्क्रिप्शन हस्तलिखित होते हैं, जिन्हें पढ़ना सामान्य मरीज के लिए असंभव होता है। इसके कारण 15-20% मामलों में गलत दवा वितरण (Dispensing Errors) का गंभीर जोखिम रहता है।", bullet_style),
    Paragraph("• <b>दवाओं पर अत्यधिक जेब-खर्च (Catastrophic Healthcare Spend):</b> भारत में कुल आउट-ऑफ-पॉकेट स्वास्थ्य खर्च का 67% केवल दवाइयों पर होता है। ब्रांडेड दवाओं के भारी मुनाफे के कारण हर साल लगभग 5.5 करोड़ भारतीय गरीबी रेखा से नीचे चले जाते हैं।", bullet_style),
    Paragraph("• <b>सरकारी जन औषधि (PMBJP) के प्रति अज्ञानता:</b> मरीजों को यह जानकारी नहीं होती कि डॉक्टर द्वारा लिखी गई महंगी ब्रांडेड दवा का वही समान बायोइक्विवेलेंट साल्ट जन औषधि केंद्र पर 50% से 90% कम कीमत पर उपलब्ध है।", bullet_style),
    3,
    Paragraph("<b>2. यह सबसे ज्यादा किसे प्रभावित करता है? (Who Does it Affect the Most?):</b>", head_style),
    Paragraph("• <b>क्रोनिक मरीज एवं वरिष्ठ नागरिक:</b> डायबिटीज, बीपी और हृदय रोग से पीड़ित बुजुर्ग, जिनका जीवनभर का मासिक दवा खर्च ₹2,000 से ₹4,000 होता है।", bullet_style),
    Paragraph("• <b>टियर-2/3 शहर एवं ग्रामीण पूर्वांचल:</b> दैनिक वेतनभोगी मजदूर, छोटे किसान व मध्यमवर्गीय परिवार जिनकी आय का 30-40% हिस्सा केवल मेडिकल स्टोर पर खर्च हो जाता है।", bullet_style),
    3,
    Paragraph("<b>3. प्रभाव सांख्यिकी (Key Statistics):</b> 67% स्वास्थ्य बजट केवल दवाओं पर • 50-90% मूल्य अंतर ब्रांडेड बनाम जेनेरिक में • ₹1,420 औसत मासिक बचत प्रति परिवार।", bullet_style)
]
draw_box(c, MARGIN_X, TOP_BOX_Y, BOX_WIDTH, TOP_BOX_H, p1_b1_title, p1_b1_prompt, p1_b1_elements)

# P1 - Box 2: Business Idea & Market Size
p1_b2_title = "Business Idea/ बिजनेस आइडिया"
p1_b2_prompt = "Explain your business idea and how it solves the problem. Share details of your products and/or services. Also, briefly explain the market size of your business. (अपने व्यावसायिक योजना की व्याख्या करें और यह समस्या का समाधान कैसे करेगा। उत्पादों और/या सेवाओं का विवरण साझा करें। इसके अलावा, अपने व्यवसाय के बाजार के आकार के बारे में संक्षेप में बताएं।)"

p1_b2_elements = [
    Paragraph("<b>1. व्यावसायिक योजना व समाधान (Business Idea & Solution):</b>", head_style),
    Paragraph("ArogyaMitra AI एक अत्याधुनिक क्लिनिकल AI प्लेटफॉर्म है। मरीज अपने मोबाइल से डॉक्टर के पर्चे की फोटो खींचता है -> Google Gemini 1.5 Flash Vision AI 2.4 सेकंड में हस्तलेख को डिकोड करता है -> CDSCO और PMBJP डेटाबेस से मैच करके 50-90% सस्ती जन औषधि दवाओं की रसीद तैयार करता है -> फार्मासिस्ट (HITL) सत्यापन करता है -> मरीज को हिंदी ऑडियो और WhatsApp पर रसीद मिलती है।", body_style),
    3,
    Paragraph("<b>2. उत्पाद एवं सेवाएं (Products and Services):</b>", head_style),
    Paragraph("• <b>ArogyaMitra Citizen Web/PWA App:</b> आम नागरिकों के लिए नि:शुल्क पर्ची स्कैनर, हिंदी ऑडियो खुराक गाइड, और नजदीकी जन औषधि केंद्र लोकेटर।", bullet_style),
    Paragraph("• <b>ArogyaMitra Kendra SaaS / POS Terminal:</b> जन औषधि केंद्र संचालकों के लिए डिजिटल फुटफॉल, इन्वेंटरी अलर्ट और स्मार्ट बिलिंग सॉफ्टवेयर (₹299/माह)।", bullet_style),
    Paragraph("• <b>B2B Clinical API:</b> टेलीमेडिसिन कंपनियों, इंश्योरेंस फर्मों और अस्पतालों के लिए प्रिस्क्रिप्शन डिजिटाइजेशन API।", bullet_style),
    3,
    Paragraph("<b>3. बाजार का आकार (Market Size):</b>", head_style),
    Paragraph("• <b>TAM (Total Addressable Market):</b> ₹1.8 लाख करोड़ ($22 Billion) - संपूर्ण भारतीय रिटेल दवा बाजार।", bullet_style),
    Paragraph("• <b>SAM (Serviceable Addressable Market):</b> ₹35,000 करोड़ - भारत में जेनेरिक दवाएं और क्रोनिक डिजीज केयर बाजार।", bullet_style),
    Paragraph("• <b>SOM (Serviceable Obtainable Market):</b> ₹180 करोड़ - उत्तर प्रदेश व पूर्वांचल के 12,000+ जन औषधि केंद्रों से जुड़े 50 लाख मरीज।", bullet_style)
]
draw_box(c, MARGIN_X, BOT_BOX_Y, BOX_WIDTH, BOT_BOX_H, p1_b2_title, p1_b2_prompt, p1_b2_elements)

c.showPage()

# ========================================================
# PAGE 2: Main Resources & Marketing and Sales Strategy
# ========================================================
draw_header_footer(c, 2)

# P2 - Box 1: Main Resources
p2_b1_title = "Main Resources/ मुख्य संसाधन"
p2_b1_prompt = "Provide a list of major resources required to start & operate your business with reasons. (अपने व्यवसाय को शुरू करने और संचालित करने के लिए प्रमुख संसाधनों की सूची बनाएं और उनके कारण बताए।)"

p2_b1_elements = [
    Paragraph("<b>1. तकनीकी एवं डिजिटल संसाधन (Technological Resources):</b>", head_style),
    Paragraph("• <b>Google Gemini 1.5 Flash Vision API:</b> हस्तलिखित पर्चियों को 2.4s में डिकोड करने हेतु।", bullet_style),
    Paragraph("• <b>CDSCO व PMBJP ड्रग मास्टर डेटाबेस:</b> 1,800+ सक्रिय साल्ट के साथ 100% सटीक बायोइक्विवेलेंस मैपिंग हेतु।", bullet_style),
    Paragraph("• <b>Vercel Edge & Cloud Hosting:</b> 24x7 हाई-स्पीड सर्वर रनवे व डेटा एन्क्रिप्शन हेतु।", bullet_style),
    Paragraph("• <b>WhatsApp Cloud API:</b> बिना ऐप डाउनलोड किए सीधे WhatsApp पर बचत रसीद भेजने हेतु।", bullet_style),
    3,
    Paragraph("<b>2. मानव संसाधन (Human Resources):</b>", head_style),
    Paragraph("• <b>AI/ML एवं वेब इंजीनियर्स (Lead: Keshav Narayan):</b> एल्गोरिदम, विज़न मॉडल ट्यूनिंग व आर्किटेक्चर हेतु।", bullet_style),
    Paragraph("• <b>रजिस्टर्ड फार्मासिस्ट (B.Pharm/D.Pharm):</b> Human-in-the-Loop (HITL) क्लिनिकल सुरक्षा जांच व ड्रग रिएक्शन रोकने हेतु।", bullet_style),
    Paragraph("• <b>मेडिकल एडवाइजरी बोर्ड:</b> क्लिनिकल नियमों एवं शेड्यूलिंग के मार्गदर्शन हेतु 2 कंसल्टिंग डॉक्टर।", bullet_style),
    3,
    Paragraph("<b>3. संस्थागत व भौतिक संसाधन (Physical & Institutional):</b>", head_style),
    Paragraph("• <b>इंक्यूबेशन ऑफिस:</b> IET DDU गोरखपुर विश्वविद्यालय का इंक्यूबेशन सेल (कम लागत में इंफ्रास्ट्रक्चर व विश्वसनीयता)।", bullet_style),
    Paragraph("• <b>हार्डवेयर टेस्टबेड:</b> विभिन्न मोबाइल कैमरों पर टेस्टिंग हेतु डिवाइसेस व POS थर्मल प्रिंटर।", bullet_style),
    3,
    Paragraph("<b>4. कानूनी व विधिक (Legal & IPR):</b> ArogyaMitra AI™ ट्रेडमार्क, Pharmacy Act 1948 व IT Act 2000 डेटा सुरक्षा अनुपालन।", bullet_style)
]
draw_box(c, MARGIN_X, TOP_BOX_Y, BOX_WIDTH, TOP_BOX_H, p2_b1_title, p2_b1_prompt, p2_b1_elements)

# P2 - Box 2: Marketing and Sales Strategy
p2_b2_title = "Marketing and Sales Strategy/ प्रचार और बिक्री योजना"
p2_b2_prompt = "Explain the marketing and sales strategy to reach your customers. (अपने ग्राहकों तक पहुंचने के लिए मार्केटिंग और बिक्री रणनीति की समझाएं।)"

p2_b2_elements = [
    Paragraph("<b>1. ज़ीरो-CAC पार्टनरशिप चैनल (Zero-CAC Kendra Partner Network):</b>", head_style),
    Paragraph("जन औषधि केंद्रों पर 'पर्ची स्कैन करें और दवा खर्च 80% घटाएं' के क्यूआर (QR) कोड स्टैंडी और काउंटर बोर्ड लगाना। केंद्र संचालक इसे स्वयं प्रमोट करेंगे क्योंकि इससे उनकी ग्राहक संख्या और दवा बिक्री में 3 गुना वृद्धि होती है।", body_style),
    3,
    Paragraph("<b>2. अस्पताल ओपीडी व कैम्प आउटरीच (Hospital OPD & Pharmacy Outreach):</b>", head_style),
    Paragraph("गोरखपुर व पूर्वांचल के प्रमुख सरकारी अस्पतालों (जैसे BRD मेडिकल कॉलेज, जिला अस्पताल) और सामुदायिक स्वास्थ्य केंद्रों के बाहर मरीजों को लाइव डेमो दिखाना और बचत पर्चे बांटना।", body_style),
    3,
    Paragraph("<b>3. वायरल कम्युनिटी व WhatsApp मार्केटिंग (Viral WhatsApp Loop):</b>", head_style),
    Paragraph("मरीज द्वारा WhatsApp पर प्राप्त बचत रसीद ('मेरी पर्ची पर ₹960 की बचत हुई') को परिवार और पड़ोसियों के ग्रुप्स में शेयर करने का ऑर्गेनिक लूप। स्थानीय भाषा (हिंदी व भोजपुरी) में जागरूकता रील्स व वीडियोज।", body_style),
    3,
    Paragraph("<b>4. बी2बी बिक्री रणनीति (B2B SaaS Sales Model):</b>", head_style),
    Paragraph("जन औषधि केंद्र संचालकों को 30-दिन का नि:शुल्क ट्रायल देकर ऑनबोर्ड करना, तत्पश्चात ₹299/माह का नाममात्र सब्सक्रिप्शन शुल्क लेकर रिटेंशन बनाए रखना।", body_style)
]
draw_box(c, MARGIN_X, BOT_BOX_Y, BOX_WIDTH, BOT_BOX_H, p2_b2_title, p2_b2_prompt, p2_b2_elements)

c.showPage()

# ========================================================
# PAGE 3: Competitive Perspective & Fund Required
# ========================================================
draw_header_footer(c, 3)

# P3 - Box 1: Competitive Perspective / USP
p3_b1_title = "Competitive Perspective/ USP/ प्रतियोगी परिदृश्य"
p3_b1_prompt = "Explain about your competitors and brief your USP- unique selling point to manage the competition. (अपने प्रतियोगी के बारे मे बताएं और आप उनसे कैसे बेहतर है। अपनी यूएसपी-अद्वितीय मोल प्रस्ताव को संक्षेप में लिखे।)"

p3_b1_elements = [
    Paragraph("<b>1. प्रतियोगी विश्लेषण (Competitor Landscape):</b>", head_style),
    Paragraph("• <b>1mg / Pharmeasy / Apollo 247:</b> मुख्य रूप से महंगी ब्रांडेड दवाएं 15-20% डिस्काउंट पर बेचते हैं; सरकारी जन औषधि के 90% सस्ते विकल्प नहीं सुझाते।", bullet_style),
    Paragraph("• <b>Google Lens / Generic OCR:</b> सामान्य लिखावट पढ़ सकता है लेकिन मेडिकल एब्रिविएशन (OD, BD, TDS), ड्रग बायोइक्विवेलेंस और क्लिनिकल सुरक्षा नहीं समझता।", bullet_style),
    Paragraph("• <b>Jan Aushadhi Sugam App:</b> केवल केंद्रों की लिस्ट दिखाता है; डॉक्टर की हस्तलिखित पर्ची डिकोड करने की सुविधा नहीं है।", bullet_style),
    3,
    Paragraph("<b>2. ArogyaMitra AI की अनूठी USP (Unique Selling Propositions):</b>", head_style),
    Paragraph("• <b>50% से 90% की सीधी बचत (Direct Price Relief):</b> ब्रांडेड दवाओं को सरकारी PMBJP जेनेरिक दवाओं में बदलने वाला भारत का पहला समर्पित क्लिनिकल AI।", bullet_style),
    Paragraph("• <b>95%+ क्लिनिकल सुरक्षा द्वार (HITL Architecture):</b> केवल AI पर निर्भर न रहकर रजिस्टर्ड फार्मासिस्ट द्वारा दवा मिलान व सुरक्षित खुराक का प्रमाणीकरण।", bullet_style),
    Paragraph("• <b>हिंदी व वॉइस-फर्स्ट इंटरफेस (Voice & WhatsApp Delivery):</b> बुजुर्गों और निरक्षर मरीजों के लिए हिंदी में ऑडियो खुराक और 1-क्लिक WhatsApp शेयर।", bullet_style),
    Paragraph("• <b>हाइपरलोकल केंद्र मैपिंग:</b> मरीज के निकटतम 3 जन औषधि केंद्रों की लाइव लोकेशन, दिशा और संपर्क सूत्र।", bullet_style)
]
draw_box(c, MARGIN_X, TOP_BOX_Y, BOX_WIDTH, TOP_BOX_H, p3_b1_title, p3_b1_prompt, p3_b1_elements)

# P3 - Box 2: Fund Required & Utilization
p3_b2_title = "Fund required to start your business (One-time investment)/ अपना व्यवसाय शुरू करने के लिए आवश्यक पूंजी"
p3_b2_prompt = "How much funding do you require to start your business? Tell about the initial fund requirement to start your business. Detail out the usage of funds. (अपना व्यवसाय शुरू करने के लिए कितनी पहली पूंजी की आवश्यकता है? अपना व्यवसाय शुरू करने के लिए आवश्यक प्रारंभिक लागत के बारे में बताएं। पूंजी के उपयोग का विवरण दें?)"

p3_b2_elements = [
    Paragraph("<b>1. आवश्यक कुल प्रारंभिक पूंजी (Total Initial Fund Required): ₹5,00,000 (₹5.00 लाख)</b>", head_style),
    Paragraph("Aavishkaar YEP 2026 सीड ग्रांट / Startup India Seed Fund द्वारा 12-18 माह के पायलट संचालन हेतु।", body_style),
    3,
    Paragraph("<b>2. पूंजी के उपयोग का विस्तृत विवरण (Detailed Usage of Funds):</b>", head_style),
    Paragraph("• <b>AI API एवं क्लाउड सर्वर इंफ्रास्ट्रक्चर (30% - ₹1,50,000):</b> Google Cloud / Gemini 1.5 Flash Vision API टोकन्स, Vercel Edge सर्वर, डेटाबेस मेंटेनेंस व SSL सर्टिफिकेशन।", bullet_style),
    Paragraph("• <b>प्रोडक्ट डेवलपमेंट व टेक इंटीग्रेशन (25% - ₹1,25,000):</b> एडवांस्ड क्लिनिकल फजी मैचर, WhatsApp Business API इंटीग्रेशन, PWA मोबाइल ऐप ऑप्टिमाइजेशन।", bullet_style),
    Paragraph("• <b>फार्मासिस्ट मानदेय व क्लिनिकल सेफ्टी ऑडिट (20% - ₹1,00,000):</b> 50,000 पर्चियों की HITL समीक्षा हेतु अंशकालिक रजिस्टर्ड फार्मासिस्ट मानदेय।", bullet_style),
    Paragraph("• <b>पायलट टेस्टिंग व केंद्र ब्रांडिंग किट (15% - ₹75,000):</b> गोरखपुर व पूर्वी यूपी के 100 जन औषधि केंद्रों पर क्यूआर स्टैंडी, लीफलेट्स, और जागरूकता बोर्ड।", bullet_style),
    Paragraph("• <b>विधिक, डेटा सुरक्षा व रिजर्व फंड (10% - ₹50,000):</b> ट्रेडमार्क फाइलिंग, डेटा सिक्योरिटी ऑडिट, आपातकालीन बैकअप फंड।", bullet_style)
]
draw_box(c, MARGIN_X, BOT_BOX_Y, BOX_WIDTH, BOT_BOX_H, p3_b2_title, p3_b2_prompt, p3_b2_elements)

c.showPage()

# ========================================================
# PAGE 4: Financial Planning & Core Team
# ========================================================
draw_header_footer(c, 4)

# P4 - Box 1: Financial Planning (Income, Exp & Profit)
p4_b1_title = "Financial Planning- Income, Expenditure and Profit Structure/ वित्तीय योजना- आय, व्यय और लाभ संरचना"
p4_b1_prompt = "How will the products or services offered by you offer generate revenue? Tell about your variable costs to run the business. Detail out how much profit/ loss will be generated in 1 year. (पेश किए गए उत्पाद या सेवाएं राजस्व कैसे उत्पन्न करती हैं? व्यवसाय चलाने के लिए अपनी परिवर्तनीय लागतों के बारे में बताएं। विस्तार से बताएं कि 1 वर्ष में कितना लाभ/हानि उत्पन्न होगी।)"

# Small Table for Year 1 Financials
p4_table_data = [
    [Paragraph("<b>मद (Component)</b>", bullet_style), Paragraph("<b>1 वर्ष का वित्तीय विवरण (Year 1 Figures)</b>", bullet_style)],
    [Paragraph("प्रोजेक्टेड उपयोगकर्ता / स्कैन", bullet_style), Paragraph("50,000 सक्रिय मरीज | 1,80,000 प्रिस्क्रिप्शन स्कैन", bullet_style)],
    [Paragraph("कुल राजस्व (Gross Revenue)", bullet_style), Paragraph("<b>₹15,20,000</b> (120 पेड केंद्र + B2B API पायलट + ग्रांट्स)", bullet_style)],
    [Paragraph("कुल परिचालन व्यय (OpEx)", bullet_style), Paragraph("₹9,80,000 (API ₹2.5L + ऑपरेशंस ₹4.8L + मार्केटिंग ₹2.5L)", bullet_style)],
    [Paragraph("शुद्ध लाभ (Net Profit Year 1)", bullet_style), Paragraph("<b>₹5,40,000 (35.5% शुद्ध लाभ मार्जिन)</b>", bullet_style)],
    [Paragraph("सामाजिक प्रभाव (Social Impact)", bullet_style), Paragraph("मरीजों की शुद्ध दवा बचत: <b>₹1.8 करोड़</b>", bullet_style)]
]
p4_t = Table(p4_table_data, colWidths=[180, 310])
p4_t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
]))

p4_b1_elements = [
    Paragraph("<b>1. राजस्व मॉडल (Revenue Model):</b>", head_style),
    Paragraph("• <b>Kendra SaaS Subscription:</b> जन औषधि केंद्रों से ₹299/माह (डिजिटल इन्वेंटरी, फुटफॉल एनालिटिक्स हेतु)।", bullet_style),
    Paragraph("• <b>B2B Clinical API:</b> टेलीमेडिसिन कंपनियों व इंश्योरेंस फर्मों को प्रति प्रिस्क्रिप्शन स्कैन ₹2 शुल्क।", bullet_style),
    Paragraph("• <b>Affiliate Convenience Fee:</b> मेडिसिन होम डिलीवरी पार्टनरशिप से 2-3% सुविधा शुल्क।", bullet_style),
    2,
    Paragraph("<b>2. परिवर्तनीय लागत (Variable Cost per Scan):</b> AI विज़न टोकन ₹0.15 + सर्वर/डेटाबेस ₹0.05 + WhatsApp मैसेज ₹0.08 = <b>₹0.28 / स्कैन</b>।", body_style),
    2,
    Paragraph("<b>3. प्रथम वर्ष का लाभ/हानि विवरण (1-Year P&L Structure):</b>", head_style),
    p4_t
]
draw_box(c, MARGIN_X, TOP_BOX_Y, BOX_WIDTH, TOP_BOX_H, p4_b1_title, p4_b1_prompt, p4_b1_elements)

# P4 - Box 2: Core Team
p4_b2_title = "Core Team/ कोर टीम"
p4_b2_prompt = "List down team members. Briefly write what is special about each member? What is the distribution of work amongst the team members? (टीम के सदस्यों की सूची बनाएं। संक्षेप में लिखें कि प्रत्येक सदस्य के बारे में क्या खास है? टीम के सदस्यों के बीच काम का वितरण क्या है?)"

p4_b2_elements = [
    Paragraph("<b>1. केशव नारायण (Keshav Narayan) - Founder & Technical Lead:</b>", head_style),
    Paragraph("• <b>योग्यता व विशेषता:</b> B.Tech CSE (AI & ML), IET, DDU गोरखपुर विश्वविद्यालय। फुल-स्टैक वेब आर्किटेक्चर, Google Gemini API इंटीग्रेशन और बड़े डेटाबेस सिस्टम्स के अनुभवी निर्माता (Creator of DDU Notes Hub)।", bullet_style),
    Paragraph("• <b>काम का वितरण:</b> AI विज़न पाइपलाइन, वेब आर्किटेक्चर, CDSCO डेटाबेस मैपिंग, और तकनीकी ऑपरेशंस।", bullet_style),
    3,
    Paragraph("<b>2. क्लिनिकल सेफ्टी को-फाउंडर (Clinical Safety & Pharmacist Lead):</b>", head_style),
    Paragraph("• <b>योग्यता व विशेषता:</b> B.Pharm ग्रेजुएट, CDSCO नेशनल ड्रग फॉर्म्युलेरी, ड्रग-ड्रग रिएक्शन और शेड्यूल दवाओं का गहन अनुभव।", bullet_style),
    Paragraph("• <b>काम का वितरण:</b> क्लिनिकल सेफ्टी ऑडिट, HITL फार्मासिस्ट प्रोटोकॉल डिजाइन, और जन औषधि केंद्र समन्वय।", bullet_style),
    3,
    Paragraph("<b>3. ऑपरेशंस व कम्युनिटी लीड (Operations & Growth Lead):</b>", head_style),
    Paragraph("• <b>योग्यता व विशेषता:</b> कम्युनिटी मोबिलाइजेशन, हॉस्पिटल ओपीडी आउटरीच और ग्राउंड एग्जीक्यूशन में निपुण।", bullet_style),
    Paragraph("• <b>काम का वितरण:</b> जन औषधि केंद्र ऑनबोर्डिंग, यूजर फीडबैक कलेक्शन, लोकल पार्टनरशिप्स और सपोर्ट।", bullet_style),
    3,
    Paragraph("<b>4. मेंटरशिप व एडवाइजरी:</b> IET DDU गोरखपुर विश्वविद्यालय के प्रोफेसर और वरिष्ठ मेडिकल कंसल्टेंट्स।", bullet_style)
]
draw_box(c, MARGIN_X, BOT_BOX_Y, BOX_WIDTH, BOT_BOX_H, p4_b2_title, p4_b2_prompt, p4_b2_elements)

c.showPage()

# ========================================================
# PAGE 5: Scale-up Plan & Key Risks and Mitigation
# ========================================================
draw_header_footer(c, 5)

# P5 - Box 1: Scale-up Plan
p5_b1_title = "Scale-up Plan/ स्केल-अप योजना"
p5_b1_prompt = "How do you plan to expand your service/product offerings? Provide a financial projection of the business for the next five years. (आप अपनी सेवा/उत्पाद की पेशकश का विस्तार करने की योजना कैसे बनाते हैं? अगले पांच वर्षों के लिए व्यवसाय का वित्तीय प्रक्षेपण प्रदान करें।)"

# 5-Year Financial Projection Table
p5_table_data = [
    [Paragraph("<b>वर्ष (Year)</b>", bullet_style), Paragraph("<b>सक्रिय परिवार</b>", bullet_style), Paragraph("<b>वार्षिक स्कैन</b>", bullet_style), Paragraph("<b>प्रोजेक्टेड राजस्व</b>", bullet_style), Paragraph("<b>नागरिकों की शुद्ध बचत</b>", bullet_style)],
    [Paragraph("<b>वर्ष 1 (2026)</b>", bullet_style), Paragraph("50,000", bullet_style), Paragraph("1.8 लाख", bullet_style), Paragraph("₹15.2 लाख", bullet_style), Paragraph("₹1.8 करोड़", bullet_style)],
    [Paragraph("<b>वर्ष 2 (2027)</b>", bullet_style), Paragraph("2,50,000", bullet_style), Paragraph("12.0 लाख", bullet_style), Paragraph("₹85.0 लाख", bullet_style), Paragraph("₹12.5 करोड़", bullet_style)],
    [Paragraph("<b>वर्ष 3 (2028)</b>", bullet_style), Paragraph("10,00,000", bullet_style), Paragraph("55.0 लाख", bullet_style), Paragraph("₹3.60 करोड़", bullet_style), Paragraph("₹58.0 करोड़", bullet_style)],
    [Paragraph("<b>वर्ष 4 (2029)</b>", bullet_style), Paragraph("50,00,000", bullet_style), Paragraph("2.8 करोड़", bullet_style), Paragraph("₹18.5 करोड़", bullet_style), Paragraph("₹310 करोड़", bullet_style)],
    [Paragraph("<b>वर्ष 5 (2030)</b>", bullet_style), Paragraph("<b>2,00,00,000</b>", bullet_style), Paragraph("<b>11.5 करोड़</b>", bullet_style), Paragraph("<b>₹72.0 करोड़</b>", bullet_style), Paragraph("<b>₹1,280 करोड़</b>", bullet_style)]
]
p5_t = Table(p5_table_data, colWidths=[80, 95, 95, 105, 115])
p5_t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 2),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
]))

p5_b1_elements = [
    Paragraph("<b>1. सेवा विस्तार के चरण (Expansion Phases):</b>", head_style),
    Paragraph("• <b>Phase 1 (माह 1-6):</b> गोरखपुर व पूर्वांचल के 10 जिलों में 120 केंद्रों पर लाइव पायलट (50K यूजर्स)।", bullet_style),
    Paragraph("• <b>Phase 2 (माह 7-18):</b> उत्तर प्रदेश के 2,400 केंद्रों तक विस्तार, राज्य स्वास्थ्य मिशन व CSC केंद्रों से एकीकरण।", bullet_style),
    Paragraph("• <b>Phase 3 (माह 19-36):</b> पैन-इंडिया विस्तार (हिंदी पट्टी: बिहार, एमपी, राजस्थान) व बहुभाषी वॉइस सपोर्ट।", bullet_style),
    2,
    Paragraph("<b>2. अगले 5 वर्षों का वित्तीय एवं प्रभाव प्रक्षेपण (5-Year Projections):</b>", head_style),
    p5_t
]
draw_box(c, MARGIN_X, TOP_BOX_Y, BOX_WIDTH, TOP_BOX_H, p5_b1_title, p5_b1_prompt, p5_b1_elements)

# P5 - Box 2: Key Risks and Mitigation
p5_b2_title = "Key Risks and Mitigation/ प्रमुख जोखिम और शमन"
p5_b2_prompt = "What are some of the key risks that your business might face? Please list the risks and how do you plan to solve them? (आपके व्यवसाय को किन प्रमुख जोखिमों का सामना करना पड़ सकता है? कृपया जोखिमों को सूचीबद्ध करें। उन्हें हल करने की आपकी क्या योजना हैं?)"

p5_b2_elements = [
    Paragraph("<b>1. जोखिम: हस्तलेख पठन में AI त्रुटि (AI Misinterpretation Risk):</b>", head_style),
    Paragraph("• <b>शमन (Mitigation):</b> 95%+ कॉन्फिडेंस थ्रेशोल्ड। धुंधली पर्चियों पर सिस्टम चेतावनी जारी करता है और अनिवार्य Human-in-the-Loop (HITL) फार्मासिस्ट समीक्षा के बिना अंतिम पर्चा जारी नहीं होता।", bullet_style),
    3,
    Paragraph("<b>2. जोखिम: जन औषधि केंद्र पर दवा अनुपलब्धता (Stockout Risk):</b>", head_style),
    Paragraph("• <b>शमन (Mitigation):</b> वैकल्पिक बायोइक्विवेलेंट साल्ट ब्रांड्स की सेकंडरी सूची दिखाना और मरीज को नजदीकी 2 अन्य केंद्रों की लाइव लोकेशन व फोन नंबर प्रदान करना।", bullet_style),
    3,
    Paragraph("<b>3. जोखिम: विधिक व फार्मेसी एक्ट संबंधी आपत्तियां (Regulatory Risk):</b>", head_style),
    Paragraph("• <b>शमन (Mitigation):</b> स्पष्ट कानूनी डिस्क्लेमर कि ArogyaMitra केवल एक 'सूचनात्मक व मूल्य तुलना उपकरण' है; दवा की वास्तविक बिक्री केवल लाइसेंसधारी फार्मासिस्ट द्वारा की जाती है।", bullet_style),
    3,
    Paragraph("<b>4. जोखिम: ग्रामीण बुजुर्गों द्वारा तकनीक अपनाने में बाधा (Adoption Barrier):</b>", head_style),
    Paragraph("• <b>शमन (Mitigation):</b> 1-क्लिक WhatsApp इंटरफेस और हिंदी ऑडियो वॉइस गाइड ताकि किसी ऐप को डाउनलोड या पढ़ने की आवश्यकता न पड़े।", bullet_style)
]
draw_box(c, MARGIN_X, BOT_BOX_Y, BOX_WIDTH, BOT_BOX_H, p5_b2_title, p5_b2_prompt, p5_b2_elements)

c.save()
print(f"PDF successfully generated at: {os.path.abspath(pdf_path)}")
