"""Generate sample PDFs for testing IDP App pipeline with different document types."""

from fpdf import FPDF
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_pdf(filename: str, title: str, content_fn):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    content_fn(pdf)
    path = os.path.join(OUTPUT_DIR, filename)
    pdf.output(path)
    print(f"Created: {path}")


# ─────────────────────────────────────────────
# 1. CONTRACT - Software Development Agreement
# ─────────────────────────────────────────────
def contract_content(pdf: FPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "SOFTWARE DEVELOPMENT AGREEMENT", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Contract No: SDA-2025-0847", ln=True, align="C")
    pdf.cell(0, 6, "Effective Date: January 15, 2025", ln=True, align="C")
    pdf.ln(10)

    sections = [
        ("1. PARTIES", """This Software Development Agreement ("Agreement") is entered into by and between:

TechVision Solutions Inc., a Delaware corporation with principal offices at 1200 Innovation Drive, Suite 400, San Francisco, CA 94107 ("Developer")

AND

GlobalRetail Corp., a New York corporation with principal offices at 500 Commerce Avenue, Floor 22, New York, NY 10001 ("Client")

Collectively referred to as the "Parties"."""),
        ("2. SCOPE OF WORK", """The Developer agrees to design, develop, test, and deploy a custom e-commerce platform ("the Software") with the following specifications:

a) Multi-tenant architecture supporting 10,000+ concurrent users
b) Real-time inventory management system with warehouse integration
c) AI-powered product recommendation engine using machine learning
d) Payment gateway integration (Stripe, PayPal, Apple Pay, Google Pay)
e) Mobile-responsive Progressive Web Application (PWA)
f) Administrative dashboard with analytics and reporting
g) RESTful API layer for third-party integrations

The detailed technical specifications are outlined in Exhibit A attached hereto."""),
        ("3. PROJECT TIMELINE", """The project shall be completed in the following phases:

Phase 1 - Discovery & Architecture: January 15 - February 28, 2025
Phase 2 - Core Development: March 1 - June 30, 2025
Phase 3 - Integration & Testing: July 1 - August 31, 2025
Phase 4 - User Acceptance Testing: September 1 - September 30, 2025
Phase 5 - Deployment & Launch: October 1 - October 31, 2025

Total project duration: 10 months from the Effective Date."""),
        ("4. COMPENSATION", """The Client agrees to pay the Developer a total of $485,000.00 (Four Hundred Eighty-Five Thousand US Dollars) as follows:

- 20% upon signing ($97,000.00)
- 15% upon completion of Phase 1 ($72,750.00)
- 25% upon completion of Phase 2 ($121,250.00)
- 20% upon completion of Phase 3 ($97,000.00)
- 10% upon completion of Phase 4 ($48,500.00)
- 10% upon final delivery and acceptance ($48,500.00)

Late payments shall accrue interest at 1.5% per month."""),
        ("5. INTELLECTUAL PROPERTY", """Upon full payment, all intellectual property rights in the Software shall transfer to the Client. The Developer retains the right to use general knowledge, techniques, and non-proprietary tools developed during the project.

The Developer warrants that the Software will not infringe upon any third-party intellectual property rights."""),
        ("6. CONFIDENTIALITY", """Both Parties agree to maintain the confidentiality of all proprietary information exchanged during the term of this Agreement. This obligation shall survive termination for a period of three (3) years.

Confidential information includes but is not limited to: trade secrets, business plans, customer data, technical specifications, and financial information."""),
        ("7. WARRANTIES AND LIABILITY", """The Developer warrants that the Software will substantially conform to the specifications for a period of 12 months following delivery. The Developer's total liability under this Agreement shall not exceed the total compensation paid.

NEITHER PARTY SHALL BE LIABLE FOR INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES."""),
    ]

    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, heading, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, body)
        pdf.ln(5)

    # Signature page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "SIGNATURES", ln=True, align="C")
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 10)
    for party, name, title in [
        ("TechVision Solutions Inc.", "Sarah Chen", "Chief Executive Officer"),
        ("GlobalRetail Corp.", "Michael Rodriguez", "Vice President of Technology"),
    ]:
        pdf.cell(90, 6, f"For and on behalf of {party}:")
        pdf.ln(20)
        pdf.cell(90, 6, "_" * 40)
        pdf.ln(6)
        pdf.cell(90, 6, f"Name: {name}")
        pdf.ln(6)
        pdf.cell(90, 6, f"Title: {title}")
        pdf.ln(6)
        pdf.cell(90, 6, "Date: January 15, 2025")
        pdf.ln(15)


# ─────────────────────────────────────────────
# 2. INVOICE - Consulting Services
# ─────────────────────────────────────────────
def invoice_content(pdf: FPDF):
    pdf.add_page()
    # Header
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 14, "INVOICE", ln=True, align="R")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Invoice #: INV-2025-03421", ln=True, align="R")
    pdf.cell(0, 6, "Date: February 28, 2025", ln=True, align="R")
    pdf.cell(0, 6, "Due Date: March 30, 2025", ln=True, align="R")
    pdf.ln(10)

    # From
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(95, 6, "FROM:")
    pdf.cell(95, 6, "BILL TO:")
    pdf.ln(7)
    pdf.set_font("Helvetica", "", 10)
    from_lines = [
        "Nexus Consulting Group LLC",
        "2100 Market Street, Suite 300",
        "Philadelphia, PA 19103",
        "Tax ID: 23-4567890",
        "Phone: (215) 555-0142",
    ]
    to_lines = [
        "Meridian Healthcare Systems",
        "Attn: Accounts Payable",
        "800 Hospital Boulevard",
        "Boston, MA 02115",
        "PO Number: PO-2025-1187",
    ]
    for f, t in zip(from_lines, to_lines):
        pdf.cell(95, 5, f)
        pdf.cell(95, 5, t)
        pdf.ln(5)

    pdf.ln(10)

    # Table header
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(41, 65, 122)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 8, "  Description", fill=True)
    pdf.cell(25, 8, "Hours", fill=True, align="C")
    pdf.cell(35, 8, "Rate", fill=True, align="C")
    pdf.cell(40, 8, "Amount", fill=True, align="C")
    pdf.ln(8)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)

    items = [
        ("EHR System Architecture Review", "24.0", "$275.00", "$6,600.00"),
        ("HIPAA Compliance Assessment", "16.5", "$300.00", "$4,950.00"),
        ("Database Migration Planning (Oracle to PostgreSQL)", "32.0", "$250.00", "$8,000.00"),
        ("API Security Audit & Penetration Testing", "20.0", "$325.00", "$6,500.00"),
        ("Staff Training - Cloud Infrastructure (3 sessions)", "12.0", "$200.00", "$2,400.00"),
        ("Project Management & Coordination", "18.0", "$225.00", "$4,050.00"),
        ("Documentation & Knowledge Transfer", "8.5", "$200.00", "$1,700.00"),
    ]

    for i, (desc, hrs, rate, amt) in enumerate(items):
        fill = i % 2 == 0
        if fill:
            pdf.set_fill_color(240, 240, 245)
        pdf.cell(80, 7, f"  {desc}", fill=fill)
        pdf.cell(25, 7, hrs, fill=fill, align="C")
        pdf.cell(35, 7, rate, fill=fill, align="C")
        pdf.cell(40, 7, amt, fill=fill, align="C")
        pdf.ln(7)

    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(140, 7, "Subtotal:", align="R")
    pdf.cell(40, 7, "$34,200.00", align="C")
    pdf.ln(7)
    pdf.cell(140, 7, "Discount (5% - Long-term Client):", align="R")
    pdf.cell(40, 7, "-$1,710.00", align="C")
    pdf.ln(7)
    pdf.cell(140, 7, "Tax (6% PA Sales Tax):", align="R")
    pdf.cell(40, 7, "$1,949.40", align="C")
    pdf.ln(7)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(140, 9, "TOTAL DUE:", align="R")
    pdf.cell(40, 9, "$34,439.40", align="C")
    pdf.ln(15)

    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, """Payment Terms: Net 30 days. Please remit payment via wire transfer to:
Bank: First National Bank of Philadelphia | Account: 78234501 | Routing: 031000053
Or mail check to the address above. Thank you for your business.""")


# ─────────────────────────────────────────────
# 3. MEDICAL REPORT - Patient Discharge Summary
# ─────────────────────────────────────────────
def medical_content(pdf: FPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "PATIENT DISCHARGE SUMMARY", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "St. Mary's General Hospital - Department of Internal Medicine", ln=True, align="C")
    pdf.cell(0, 5, "1500 Healthcare Parkway, Chicago, IL 60601", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(0, 8, "  PATIENT INFORMATION", fill=True, ln=True)
    pdf.set_font("Helvetica", "", 10)
    info = [
        ("Patient Name", "Robert James Thompson"),
        ("Date of Birth", "March 14, 1958 (Age: 66)"),
        ("Medical Record #", "MRN-2025-087432"),
        ("Admission Date", "February 10, 2025"),
        ("Discharge Date", "February 17, 2025"),
        ("Length of Stay", "7 days"),
        ("Attending Physician", "Dr. Amanda Patel, MD, FACP"),
        ("Primary Insurance", "Blue Cross Blue Shield - Policy #BCB-445-2210"),
    ]
    for label, value in info:
        pdf.cell(55, 6, f"  {label}:")
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, value, ln=True)
        pdf.set_font("Helvetica", "", 10)

    pdf.ln(5)
    sections = [
        ("ADMITTING DIAGNOSIS", """1. Acute exacerbation of Chronic Obstructive Pulmonary Disease (COPD) - ICD-10: J44.1
2. Community-acquired pneumonia, right lower lobe - ICD-10: J18.9
3. Type 2 Diabetes Mellitus, uncontrolled - ICD-10: E11.65
4. Essential Hypertension - ICD-10: I10"""),
        ("HISTORY OF PRESENT ILLNESS", """Mr. Thompson is a 66-year-old male with a 40-pack-year smoking history (quit 2019) who presented to the Emergency Department on February 10, 2025, with a 3-day history of progressively worsening dyspnea, productive cough with yellow-green sputum, fever (101.8F), and decreased oxygen saturation (SpO2 88% on room air).

The patient reports increased use of his albuterol inhaler over the past week (6-8 times daily vs. usual 2-3 times). He denies hemoptysis, chest pain, or recent travel. His last COPD exacerbation requiring hospitalization was in September 2024."""),
        ("HOSPITAL COURSE", """Day 1-2: Patient admitted to medical floor. Started on IV ceftriaxone 1g q24h and azithromycin 500mg q24h for CAP. Nebulized albuterol/ipratropium q4h. Supplemental O2 via nasal cannula at 3L/min. Prednisone 40mg PO daily initiated. Blood glucose monitored q6h with sliding scale insulin.

Day 3-4: Chest X-ray showed improvement in right lower lobe infiltrate. Temperature normalized. SpO2 improved to 93% on 2L O2. Transitioned to oral antibiotics. Blood glucose remained elevated (180-240 mg/dL); endocrinology consulted for diabetes management.

Day 5-6: Significant clinical improvement. Weaned to room air with SpO2 94-96%. Ambulatory without assistance. Endocrinology recommended adjustment of home diabetes regimen. Pulmonary function test performed: FEV1 52% predicted (baseline 58%).

Day 7: Patient stable for discharge. Tolerating oral medications. Ambulating independently. SpO2 95% on room air."""),
        ("DISCHARGE MEDICATIONS", """1. Albuterol MDI 90mcg - 2 puffs q4-6h PRN shortness of breath
2. Tiotropium (Spiriva) 18mcg - 1 capsule inhaled daily
3. Fluticasone/Salmeterol (Advair) 250/50 - 1 puff BID
4. Prednisone 20mg PO daily x 5 days, then 10mg x 5 days, then discontinue
5. Amoxicillin/Clavulanate 875/125mg PO BID x 5 more days
6. Metformin 1000mg PO BID (increased from 500mg BID)
7. Glipizide 10mg PO daily (new)
8. Lisinopril 20mg PO daily (unchanged)
9. Atorvastatin 40mg PO daily (unchanged)"""),
        ("FOLLOW-UP INSTRUCTIONS", """1. Primary Care (Dr. Williams): Within 7 days of discharge
2. Pulmonology (Dr. Patel): 2 weeks post-discharge for PFT review
3. Endocrinology (Dr. Kim): 3 weeks post-discharge for A1C and medication adjustment
4. Chest X-ray: Repeat in 6 weeks
5. Labs: CBC, BMP, HbA1c in 2 weeks

Patient educated on smoking cessation maintenance, inhaler technique, and diabetes self-management. Home oxygen NOT required at this time."""),
    ]

    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(230, 240, 250)
        pdf.cell(0, 8, f"  {heading}", fill=True, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, body)
        pdf.ln(3)


# ─────────────────────────────────────────────
# 4. FINANCIAL REPORT - Q4 Earnings
# ─────────────────────────────────────────────
def financial_content(pdf: FPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "QUARTERLY FINANCIAL REPORT", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, "Apex Manufacturing Holdings, Inc.", ln=True, align="C")
    pdf.cell(0, 7, "Fourth Quarter & Full Year 2024", ln=True, align="C")
    pdf.cell(0, 7, "Period Ending December 31, 2024", ln=True, align="C")
    pdf.ln(10)

    sections = [
        ("EXECUTIVE SUMMARY", """Apex Manufacturing Holdings delivered strong fourth quarter results, exceeding analyst expectations across all key metrics. Revenue grew 12.3% year-over-year to $2.87 billion, driven by robust demand in our Industrial Automation and Clean Energy segments. Operating margin expanded 180 basis points to 18.4%, reflecting operational efficiency improvements and favorable product mix.

Full-year 2024 revenue reached $10.92 billion, representing 9.7% growth over 2023. Net income increased 15.2% to $1.34 billion, or $8.42 per diluted share, compared to $7.31 per diluted share in the prior year."""),
        ("Q4 2024 FINANCIAL HIGHLIGHTS", """Revenue: $2.87B (vs. $2.56B Q4 2023, +12.3% YoY)
Gross Profit: $1.12B (Gross Margin: 39.0%, up from 37.6%)
Operating Income: $528M (Operating Margin: 18.4%, up from 16.6%)
Net Income: $387M (Net Margin: 13.5%)
Earnings Per Share: $2.43 diluted (vs. $2.01 Q4 2023)
Free Cash Flow: $412M (14.4% of revenue)
Backlog: $4.2B (up 18% from prior year)
Employees: 34,200 globally"""),
        ("SEGMENT PERFORMANCE", """Industrial Automation (42% of revenue):
- Revenue: $1.21B (+15.7% YoY)
- Operating margin: 22.1%
- Driven by strong demand for robotics and smart factory solutions
- New contract wins with 3 major automotive manufacturers
- Backlog increased 24% to $1.8B

Clean Energy Solutions (28% of revenue):
- Revenue: $803M (+18.2% YoY)
- Operating margin: 16.8%
- Solar inverter shipments up 32%
- Battery storage systems revenue doubled YoY
- Secured $340M Department of Energy contract

Precision Components (20% of revenue):
- Revenue: $574M (+4.1% YoY)
- Operating margin: 15.2%
- Aerospace sector recovery continues
- Medical device components growing 12% YoY

Legacy Systems & Services (10% of revenue):
- Revenue: $287M (-3.2% YoY)
- Operating margin: 19.5%
- Planned decline as customers migrate to newer platforms
- High-margin service contracts provide stable cash flow"""),
        ("BALANCE SHEET SUMMARY (as of Dec 31, 2024)", """Total Assets: $14.8B
Cash & Equivalents: $1.92B
Total Debt: $3.1B (Net Debt/EBITDA: 0.8x)
Shareholders' Equity: $8.4B
Current Ratio: 2.1x
Return on Equity: 16.0%
Return on Invested Capital: 14.2%"""),
        ("2025 OUTLOOK", """Management provides the following guidance for fiscal year 2025:

- Revenue: $11.8B - $12.2B (8-12% growth)
- Operating Margin: 18.5% - 19.5%
- EPS: $9.00 - $9.50 (7-13% growth)
- Capital Expenditure: $650M - $700M
- Share Repurchase Program: $500M authorized

Key growth drivers include expansion of AI-enabled automation products, scaling of energy storage solutions, and geographic expansion in Southeast Asia and India. The company plans to open a new manufacturing facility in Vietnam (Q3 2025) and expand its R&D center in Munich, Germany."""),
    ]

    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, heading, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, body)
        pdf.ln(5)


# ─────────────────────────────────────────────
# 5. ACADEMIC PAPER - AI Research
# ─────────────────────────────────────────────
def academic_content(pdf: FPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.multi_cell(0, 7, "Adaptive Retrieval-Augmented Generation with Dynamic Confidence Thresholds for Domain-Specific Question Answering", align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Elena Vasquez(1), James Liu(2), Priya Sharma(1), Marcus Weber(3)", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, "(1) Stanford NLP Group, Stanford University", ln=True, align="C")
    pdf.cell(0, 5, "(2) Google DeepMind, London, UK", ln=True, align="C")
    pdf.cell(0, 5, "(3) Max Planck Institute for Intelligent Systems, Tubingen, Germany", ln=True, align="C")
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, "Proceedings of ACL 2025 | arXiv:2501.08934v2", ln=True, align="C")
    pdf.ln(8)

    sections = [
        ("Abstract", """We present AdaptRAG, a novel framework for retrieval-augmented generation that dynamically adjusts confidence thresholds based on query complexity and domain specificity. Unlike static RAG systems that apply uniform retrieval strategies, AdaptRAG employs a learned routing mechanism that classifies queries into complexity tiers (simple factual, multi-hop reasoning, and open-ended analytical) and adjusts the number of retrieved passages, re-ranking strategy, and generation parameters accordingly. We evaluate AdaptRAG on five domain-specific benchmarks spanning legal, medical, financial, scientific, and technical domains. Our approach achieves state-of-the-art results on all benchmarks, improving answer accuracy by 8.3% on average while reducing retrieval latency by 34% compared to existing methods. We further demonstrate that adaptive confidence thresholds reduce hallucination rates by 41% on adversarial evaluation sets. Code and models are available at github.com/stanford-nlp/adaptrag."""),
        ("1. Introduction", """Retrieval-Augmented Generation (RAG) has emerged as the predominant paradigm for building knowledge-intensive NLP systems that combine the parametric knowledge of large language models (LLMs) with non-parametric retrieval from external knowledge bases (Lewis et al., 2020; Borgeaud et al., 2022). However, current RAG implementations suffer from a fundamental limitation: they apply uniform retrieval and generation strategies regardless of query complexity.

Consider two queries in a medical domain: "What is the half-life of amoxicillin?" requires simple factual retrieval from a single passage, while "Compare treatment protocols for stage III non-small cell lung cancer in elderly patients with comorbidities" demands multi-hop reasoning across multiple documents with careful evidence synthesis. Applying the same retrieval pipeline to both queries leads to either over-retrieval (wasting compute and introducing noise for simple queries) or under-retrieval (missing critical context for complex queries).

In this paper, we introduce AdaptRAG, which addresses this limitation through three key contributions:

1) A query complexity classifier trained on 50,000 annotated queries across five professional domains
2) A dynamic threshold mechanism that adjusts retrieval depth (k), re-ranking aggressiveness, and chunk granularity based on predicted complexity
3) A confidence-aware generation module that calibrates output certainty and triggers additional retrieval when confidence falls below domain-specific thresholds"""),
        ("2. Related Work", """RAG Systems: The original RAG framework (Lewis et al., 2020) demonstrated that combining retrieval with generation improves factual accuracy. Subsequent work has explored dense passage retrieval (Karpukhin et al., 2020), iterative retrieval (Trivedi et al., 2023), and self-reflective retrieval (Asai et al., 2024). Our work differs by introducing adaptive complexity-based routing.

Confidence Estimation in NLP: Calibration of neural models has been studied extensively (Guo et al., 2017; Desai & Durrett, 2020). Recent work on LLM uncertainty estimation (Kadavath et al., 2022; Kuhn et al., 2023) provides foundations for our confidence-aware generation module.

Query Complexity: Prior work has classified queries by difficulty (Fan et al., 2019; Mallen et al., 2023), but primarily for routing between retrieval-augmented and parametric-only generation. We extend this to fine-grained control over the entire RAG pipeline."""),
        ("3. Methodology", """3.1 Query Complexity Classification

We define three complexity tiers based on the reasoning structure required:

Tier 1 - Simple Factual (SF): Single-hop retrieval, direct answer extraction. Example: "What year was GDPR enacted?"

Tier 2 - Multi-hop Reasoning (MHR): Requires synthesizing information from 2-5 passages with logical chaining. Example: "How does metformin interact with contrast dye in patients with reduced GFR?"

Tier 3 - Analytical Synthesis (AS): Open-ended analysis requiring comprehensive evidence gathering, comparison, and nuanced reasoning. Example: "Evaluate the pros and cons of transformer-based vs. graph neural network approaches for molecular property prediction."

Our classifier is a fine-tuned DeBERTa-v3-large model achieving 94.2% accuracy on a held-out test set of 5,000 queries.

3.2 Dynamic Threshold Mechanism

For each complexity tier t in {SF, MHR, AS}, we define:
- Retrieval depth k(t): SF=3, MHR=8, AS=15
- Re-ranking threshold tau(t): SF=0.7, MHR=0.5, AS=0.3
- Chunk size c(t): SF=256 tokens, MHR=512 tokens, AS=1024 tokens
- Confidence threshold theta(t): SF=0.9, MHR=0.75, AS=0.6

These are initial values learned through Bayesian optimization on validation sets and further adapted per-domain."""),
        ("4. Results", """Table 1: Performance comparison on domain-specific benchmarks (accuracy %)

                    Legal   Medical  Financial  Scientific  Technical  Avg
Vanilla RAG         71.2    68.4     73.1       69.8        72.5      71.0
Self-RAG            74.8    72.1     76.3       73.2        75.9      74.5
CRAG                76.1    74.5     77.8       75.0        77.2      76.1
AdaptRAG (ours)     82.4    81.2     84.1       80.7        83.5      82.4

AdaptRAG achieves consistent improvements across all domains, with the largest gains in medical (+6.7%) and financial (+6.3%) domains where query complexity varies most significantly.

Hallucination Rate (adversarial set):
Vanilla RAG: 23.4%, Self-RAG: 18.2%, CRAG: 15.7%, AdaptRAG: 9.3%

Latency (avg. ms per query):
Vanilla RAG: 2,340ms, Self-RAG: 3,120ms, CRAG: 2,890ms, AdaptRAG: 1,540ms"""),
        ("5. Conclusion", """We presented AdaptRAG, a framework that dynamically adjusts RAG pipeline parameters based on query complexity. By routing simple queries through lightweight retrieval and reserving deep retrieval for complex analytical queries, AdaptRAG achieves both improved accuracy and reduced latency. The confidence-aware generation module further reduces hallucinations by 41% through calibrated uncertainty estimation and iterative retrieval triggers.

Future work will explore: (1) extending AdaptRAG to multimodal retrieval, (2) online learning of threshold parameters, and (3) application to conversational multi-turn QA settings."""),
    ]

    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, heading, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, body)
        pdf.ln(4)


# ─────────────────────────────────────────────
# 6. LEGAL - Terms of Service (short, low quality)
# ─────────────────────────────────────────────
def legal_content(pdf: FPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "TERMS OF SERVICE", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "CloudSync Platform - Version 3.2", ln=True, align="C")
    pdf.cell(0, 6, "Last Updated: December 1, 2024", ln=True, align="C")
    pdf.ln(8)

    sections = [
        ("1. ACCEPTANCE OF TERMS", """By accessing or using the CloudSync platform ("Service"), operated by CloudSync Technologies Ltd., registered in Dublin, Ireland (Company No. IE-789456), you agree to be bound by these Terms of Service ("Terms"). If you are accepting these Terms on behalf of an organization, you represent that you have authority to bind that organization.

These Terms constitute a legally binding agreement between you ("User") and CloudSync Technologies Ltd. ("Company", "we", "us", or "our"). IF YOU DO NOT AGREE TO ALL OF THESE TERMS, DO NOT USE THE SERVICE."""),
        ("2. SERVICE DESCRIPTION", """CloudSync provides cloud-based file synchronization, backup, and collaboration tools. The Service includes:
a) File storage and synchronization across devices (up to 5TB per account)
b) Real-time document collaboration for teams
c) Automated backup with point-in-time recovery (30-day retention)
d) End-to-end encryption (AES-256) for data at rest and in transit
e) API access for third-party integrations
f) Administrative console for enterprise accounts"""),
        ("3. DATA PROCESSING AND PRIVACY", """We process personal data in accordance with the EU General Data Protection Regulation (GDPR), the California Consumer Privacy Act (CCPA), and applicable data protection laws. Our Data Processing Agreement (DPA) is incorporated by reference.

Data Residency: Users may select data storage regions (EU, US-East, US-West, Asia-Pacific). Data will not be transferred outside the selected region without explicit consent.

Data Retention: Upon account termination, user data is retained for 90 days, after which it is permanently and irreversibly deleted from all systems including backups."""),
        ("4. LIMITATION OF LIABILITY", """TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, CLOUDSYNC TECHNOLOGIES LTD. SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING WITHOUT LIMITATION, LOSS OF PROFITS, DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES.

OUR TOTAL AGGREGATE LIABILITY FOR ALL CLAIMS RELATED TO THE SERVICE SHALL NOT EXCEED THE AMOUNT PAID BY YOU IN THE TWELVE (12) MONTHS PRECEDING THE CLAIM.

Nothing in these Terms excludes or limits liability for death or personal injury caused by negligence, fraud, or fraudulent misrepresentation."""),
        ("5. GOVERNING LAW AND JURISDICTION", """These Terms shall be governed by and construed in accordance with the laws of Ireland, without regard to conflict of law principles. Any disputes arising from these Terms shall be subject to the exclusive jurisdiction of the courts of Dublin, Ireland.

For EU consumers: Nothing in these Terms affects your statutory rights under applicable consumer protection laws of your country of residence.

For US users: Any dispute shall be resolved through binding arbitration under the rules of the American Arbitration Association, unless you opt out within 30 days of account creation."""),
    ]

    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, heading, ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, body)
        pdf.ln(4)


# ─────────────────────────────────────────────
# 7. TECHNICAL - API Documentation
# ─────────────────────────────────────────────
def technical_content(pdf: FPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "API TECHNICAL SPECIFICATION", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, "DataStream Analytics Platform - REST API v2.4", ln=True, align="C")
    pdf.cell(0, 7, "Document Version: 2.4.1 | Released: January 2025", ln=True, align="C")
    pdf.ln(10)

    sections = [
        ("1. OVERVIEW", """The DataStream Analytics REST API provides programmatic access to real-time data processing, analytics computation, and visualization services. This document covers authentication, endpoints, request/response formats, rate limiting, and error handling.

Base URL: https://api.datastream-analytics.com/v2
Content-Type: application/json
Authentication: Bearer token (OAuth 2.0) or API key (X-API-Key header)"""),
        ("2. AUTHENTICATION", """2.1 OAuth 2.0 Flow (Recommended)

POST /oauth/token
Request Body:
  grant_type: "client_credentials"
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  scope: "read write analytics:admin"

Response (200 OK):
  access_token: "eyJhbGciOi..."
  token_type: "bearer"
  expires_in: 3600
  scope: "read write analytics:admin"

2.2 API Key Authentication

Include in request header:
  X-API-Key: dsa_live_k8j2m9x4p1q7...

API keys can be generated from the Developer Portal. Keys are scoped to specific permissions and can be rotated without downtime."""),
        ("3. CORE ENDPOINTS", """3.1 Data Ingestion

POST /v2/streams/{stream_id}/events
Description: Ingest events into a data stream
Rate Limit: 10,000 requests/minute
Max Payload: 1MB per request, 100 events per batch

Request Body:
  stream_id: "user-activity-prod"
  events: [
    {
      event_id: "evt_a1b2c3",
      timestamp: "2025-01-15T10:30:00Z",
      event_type: "page_view",
      properties: { page: "/products", duration_ms: 4500 }
    }
  ]

Response (202 Accepted):
  accepted: 1, failed: 0, stream_id: "user-activity-prod"

3.2 Analytics Queries

POST /v2/analytics/query
Description: Execute analytical queries on ingested data
Rate Limit: 100 requests/minute
Timeout: 30 seconds

Request Body:
  query: "SELECT event_type, COUNT(*) as count, AVG(properties.duration_ms) as avg_duration FROM events WHERE timestamp >= '2025-01-01' GROUP BY event_type ORDER BY count DESC LIMIT 20"
  format: "json"
  cache_ttl: 300

3.3 Real-time Aggregations

GET /v2/streams/{stream_id}/metrics
Parameters: window (1m|5m|1h|1d), metrics (count|sum|avg|p95|p99)
Description: Get real-time sliding window aggregations
Rate Limit: 1,000 requests/minute"""),
        ("4. ERROR HANDLING", """Standard HTTP status codes with structured error bodies:

400 Bad Request:
  error: { code: "INVALID_QUERY", message: "Syntax error at position 45", details: {...} }

401 Unauthorized:
  error: { code: "AUTH_EXPIRED", message: "Token expired", action: "Refresh using /oauth/token" }

429 Too Many Requests:
  error: { code: "RATE_LIMITED", message: "Rate limit exceeded" }
  Headers: X-RateLimit-Remaining: 0, X-RateLimit-Reset: 1706234567, Retry-After: 42

500 Internal Server Error:
  error: { code: "INTERNAL_ERROR", message: "...", request_id: "req_x7k2..." }

All 5xx errors include a request_id for support tickets. Our SLA guarantees 99.95% uptime."""),
        ("5. WEBHOOKS", """Configure webhooks to receive real-time notifications:

POST /v2/webhooks
Request Body:
  url: "https://your-app.com/webhook"
  events: ["stream.anomaly_detected", "query.completed", "alert.triggered"]
  secret: "whsec_..."

Webhook payloads are signed using HMAC-SHA256. Verify signature:
  Expected: HMAC-SHA256(webhook_secret, request_body)
  Compare with: X-DataStream-Signature header

Delivery: At-least-once with exponential backoff (max 3 retries over 24h)."""),
        ("6. SDK SUPPORT", """Official SDKs available:
  Python: pip install datastream-sdk (v2.4.0)
  Node.js: npm install @datastream/sdk (v2.4.0)
  Go: go get github.com/datastream/sdk-go (v2.4.0)
  Java: Maven artifact com.datastream:sdk:2.4.0

All SDKs include automatic retry, connection pooling, and built-in metrics."""),
    ]

    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, heading, ln=True)
        pdf.set_font("Courier", "", 9) if "POST" in body[:20] or "GET" in body[:20] else pdf.set_font("Helvetica", "", 10)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 5, body)
        pdf.ln(4)


# ─────────────────────────────────────────────
# 8. CORRESPONDENCE - Formal Business Letter
# ─────────────────────────────────────────────
def correspondence_content(pdf: FPDF):
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "GREENFIELD VENTURES CAPITAL", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "350 Sand Hill Road, Suite 200", ln=True)
    pdf.cell(0, 5, "Menlo Park, CA 94025", ln=True)
    pdf.cell(0, 5, "Tel: (650) 555-0198 | invest@greenfieldvc.com", ln=True)
    pdf.ln(10)

    pdf.cell(0, 6, "March 3, 2025", ln=True)
    pdf.ln(8)
    pdf.cell(0, 5, "Ms. Diana Thornton", ln=True)
    pdf.cell(0, 5, "Chief Executive Officer", ln=True)
    pdf.cell(0, 5, "NeuralPath Diagnostics, Inc.", ln=True)
    pdf.cell(0, 5, "420 Biotech Way", ln=True)
    pdf.cell(0, 5, "Cambridge, MA 02142", ln=True)
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Re: Series B Term Sheet - Proposed Investment of $45 Million", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 10)
    paragraphs = [
        "Dear Ms. Thornton,",

        "Following our productive meetings over the past several weeks and the completion of our preliminary due diligence, I am pleased to present this letter of intent outlining the proposed terms for Greenfield Ventures Capital's lead investment in NeuralPath Diagnostics' Series B financing round.",

        "We have been deeply impressed by NeuralPath's progress since your Series A round in 2023. Your AI-powered diagnostic platform has demonstrated remarkable clinical validation results, achieving 97.3% sensitivity and 94.8% specificity in detecting early-stage pancreatic cancer from routine blood panels - significantly outperforming current screening methods. The FDA Breakthrough Device Designation received in November 2024 further validates the transformative potential of your technology.",

        """Proposed Terms:

Investment Amount: $45,000,000 (Forty-Five Million US Dollars)
Lead Investor: Greenfield Ventures Capital ($30M)
Co-Investors: HealthTech Partners ($10M), BioFrontier Fund ($5M)
Pre-Money Valuation: $180,000,000
Post-Money Valuation: $225,000,000
Security: Series B Preferred Stock
Liquidation Preference: 1x non-participating
Board Seat: One seat for Greenfield Ventures (proposed: Jonathan Park, Partner)
Pro-Rata Rights: Standard pro-rata rights for all Series B investors
Anti-Dilution: Broad-based weighted average""",

        "Use of Proceeds: We understand the funding will be allocated approximately as follows: 40% for Phase III clinical trials ($18M), 25% for regulatory affairs and FDA submission preparation ($11.25M), 20% for commercial team build-out ($9M), and 15% for continued R&D and platform expansion ($6.75M).",

        "We believe NeuralPath is exceptionally well-positioned to transform early cancer detection. The combination of your proprietary biomarker panel, advanced machine learning models, and the growing body of clinical evidence creates a compelling value proposition for both patients and healthcare systems. With pancreatic cancer's current 5-year survival rate of just 12%, a reliable early detection tool represents a significant unmet medical need.",

        "This letter is non-binding and subject to completion of customary due diligence, definitive documentation, and approval by Greenfield Ventures' Investment Committee. We anticipate completing due diligence within 45 days and would aim to close the round by end of Q2 2025.",

        "We are genuinely excited about the opportunity to partner with you and the NeuralPath team on this journey. Please do not hesitate to reach out with any questions.",

        "Warm regards,",
    ]

    for p in paragraphs:
        pdf.multi_cell(0, 5, p)
        pdf.ln(4)

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Jonathan Park", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "Managing Partner", ln=True)
    pdf.cell(0, 5, "Greenfield Ventures Capital", ln=True)


# ─────────────────────────────────────────────
# Generate all PDFs
# ─────────────────────────────────────────────
if __name__ == "__main__":
    samples = [
        ("01_contract_software_development.pdf", "Contract", contract_content),
        ("02_invoice_consulting.pdf", "Invoice", invoice_content),
        ("03_medical_discharge_summary.pdf", "Medical", medical_content),
        ("04_financial_quarterly_report.pdf", "Financial", financial_content),
        ("05_academic_paper_ai_research.pdf", "Academic", academic_content),
        ("06_legal_terms_of_service.pdf", "Legal", legal_content),
        ("07_technical_api_specification.pdf", "Technical", technical_content),
        ("08_correspondence_investment_letter.pdf", "Correspondence", correspondence_content),
    ]

    print(f"Generating {len(samples)} sample PDFs...\n")
    for filename, doc_type, content_fn in samples:
        create_pdf(filename, doc_type, content_fn)

    print(f"\nDone! All PDFs saved to {OUTPUT_DIR}/")
    print("\nExpected pipeline results:")
    print("  01 - Contract:       HIGH confidence (clear structure, legal language)")
    print("  02 - Invoice:        HIGH confidence (structured, financial data)")
    print("  03 - Medical:        HIGH confidence (clinical terminology, structured)")
    print("  04 - Financial:      HIGH confidence (numbers, metrics, clear format)")
    print("  05 - Academic:       HIGH confidence (paper format, abstract, references)")
    print("  06 - Legal:          HIGH confidence (legal terminology, clauses)")
    print("  07 - Technical:      HIGH/MEDIUM (API docs, code examples)")
    print("  08 - Correspondence: MEDIUM confidence (less structured, letter format)")
