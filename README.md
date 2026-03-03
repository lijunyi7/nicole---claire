# EDUGEN

**AI-Native Infrastructure for Homeschool Education**

*Claire Li, Kary Zheng, Nicole Ying — Feb 26, 2026*

---

## Concept Overview

**Edugen** is an AI lesson production engine for homeschool families.

Today, homeschooling requires parents to act as curriculum designers, teachers, and assessment engineers. They spend 10–20 hours per week stitching together YouTube videos, PDFs, Pinterest worksheets, and marketplace content.

**Edugen replaces that entire workflow.**

A parent inputs the grade level and learning objective. Edugen generates structured lesson plans, slide decks, narrated instructional videos, worksheets, quizzes, and progress tracking in minutes.

Edugen is not a content library. It is a **vertically integrated lesson production system** embedding instructional design directly into the generation layer.

---

## Problem Statement

Homeschool parents are not trained educators, yet they are responsible for sequencing concepts correctly, scaffolding difficulty across grade levels, designing assessments, and teaching multiple children simultaneously.

Even families paying $300–$1,000/year for curriculum are still heavily supplemented with fragmented supplementary tools.

**The problem is not content scarcity. It is workflow fragmentation.**

There is no existing product that owns the full planning-to-delivery pipeline.

---

## Proposed Solution

Edugen turns a learning objective into a complete structured lesson.

Parents input the grade level and objective. Edugen generates a full instructional sequence:

**Hook → Instruction → Guided Practice → Independent Practice → Assessment → Recap.**

The system automatically produces:

- Lesson plans  
- Slides  
- Narrated videos  
- Worksheets  
- Quizzes  
- Progress tracking  

Student performance data is used to adapt future lessons and personalize learning over time.

---

## Structural Advantage

Existing platforms solve only parts of the homeschooling workflow:

| Platform | Limitation |
|----------|------------|
| Outschool | Live classes (expensive, synchronous) |
| Time4Learning | Fixed curriculum (inflexible) |
| Khan Academy | Content library (not structured for homeschooling) |
| Teachers Pay Teachers | Marketplace (inconsistent quality) |
| ChatGPT | Generic AI (requires manual lesson assembly) |

**None own the lesson production workflow.**

Edugen replaces this fragmented stack by converting learning objectives into complete structured lessons automatically.

---

## Market Potential

- The U.S. has **over 3 million homeschooled students**, with growth post-pandemic.
- Families typically spend **$500+ annually per child** on curriculum and supplementary tools.
- If **5% of families** adopt a **$29/month** subscription → ~**$52M** in annual domestic revenue.
- Homeschooling often spans 8–12 years → high retention and strong lifetime value.
- By embedding into planning and delivery, Edugen builds workflow lock-in and predictable recurring revenue.

---

## Business Model

- **Subscription**: Free limited trial with ads → **$19–$29/month** per family  
- **Tiers**: Single- and multi-child plans  
- **Future**: Institutional pricing for microschools  

**10,000 families at $29/month ≈ $3.5M ARR.**

Recurring lesson generation and performance tracking support long-term retention.

---

## Early Validation

- Structured interviews with homeschool parents have validated workflow pain points.
- Early prototype testing shows:
  - **Planning time reduction** is the primary value driver
  - **Structured sequencing** is preferred over raw content
  - Parents express **willingness to pay** for workflow replacement

**Next 60 days:**

- Closed beta with 25–50 families  
- Measure weekly planning time reduction  
- Test $19–$29 conversion  
- Track 4-week retention  

Initial users will be recruited through homeschool online communities, Facebook groups, and partnerships with homeschool content creators. We are prioritizing rapid iteration over premature scale.

---

## Why Us

Our team combines technical experience in AI systems with a strong interest in education and learning technologies. Through research and independent projects, we have built machine learning pipelines and AI applications that transform complex information into structured outputs. This allows us to design Edugen as a **structured lesson production system** rather than a generic content tool.

---

## Long-Term Vision

1. **Start** with homeschool families.  
2. **Expand** into microschools, hybrid pods, and international independent learners.  
3. **Long-term**: Edugen becomes the **operating system layer** for AI-native personalized education.

---

## Repository Structure

```
Edugen/
├── edu-gen/                    # Lesson & script generation web app
│   ├── backend/                # Flask API, generation, TTS
│   │   ├── core/               # Script generation, text-to-speech
│   │   ├── prompts/            # Prompt templates
│   │   ├── schema/             # JSON schemas
│   │   └── ...
│   ├── frontend/               # Web UI (templates, static assets)
│   └── run_web_app.py          # Start web application
├── edu-slides/                 # Slide deck generation & data
│   ├── backend/
│   ├── frontend/
│   ├── data/                   # Generated slides, raw data
│   └── run_web_app.py
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/lijunyi7/Edugen.git
   cd Edugen
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**  
   Create a `.env` in the project root (or in `edu-gen/` as needed):

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_for_flask_sessions
   ```

---

## Usage

**Run the lesson/script generation web app:**

```bash
python edu-gen/run_web_app.py
```

Then open **http://localhost:5000** in your browser.

**Run the slides app** (from repo root or `edu-slides/`):

```bash
python edu-slides/run_web_app.py
```

---

## Technologies

- **Backend**: Flask, SQLAlchemy, OpenAI API  
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript  
- **Database**: SQLite (upgradeable to PostgreSQL/MySQL)  
- **Audio**: OpenAI Text-to-Speech API  
- **Auth**: Flask-Bcrypt  

---

## License

This project is licensed under the MIT License.
