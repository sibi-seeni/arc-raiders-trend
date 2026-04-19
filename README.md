# Arc Raiders YouTube Sentiment Analysis

### Event-Driven Sentiment Analysis using Hybrid AI Labeling

Project for CAP5771 – Introduction to Data Science

---

## Project Overview

This project implements an end-to-end **data engineering, NLP, and hybrid AI labeling pipeline** to analyze community sentiment toward *Arc Raiders* using YouTube comments. The goal is not just sentiment classification, but understanding **how sentiment changes around major game announcements and AI-related controversies**.

The pipeline combines:

* Automated YouTube data collection
* Structured data wrangling and feature engineering
* Hybrid LLM + transformer labeling workflow
* Confidence-aware sentiment filtering
* Event-driven temporal sentiment analysis

The study spans major events from the game's reveal through launch and post-release updates, enabling longitudinal sentiment tracking. 

---

## Repository Structure

```text
CAP5771_SI.SEENIVASAN/
│
├── data/                            # Processed datasets
│   ├── comments_data.csv            # Raw dataset used for EDA
│   ├── comments_for_analysis.csv    # Cleaned dataset after wrangling
│   ├── comments_labeled.csv         # Final labeled dataset
│   ├── comments_llama_labeled.csv        
│   ├── comments_llama_labeled.jsonl # LLM labeling outputs
│   └── roberta_classifications.csv  # Baseline transformer predictions
│
├── preprocessing/                   # Data preparation notebooks
│   ├── Data_Wrangling.ipynb
│   ├── EDA.ipynb
│   ├── Llama_Labeler.ipynb
│   ├── Manual_Labeling_Analysis.ipynb
│   ├── roberta_classification.py
│   └── absa_labeler.log
│
├── figures/                         # EDA visualizations
│   ├── 01_text_characteristic.png
│   ├── 02_language_distribution.png
│   ├── 03_temporal_patterns.png
│   └── 04_video_analysis.png
│
├── src/                             # Data collection pipeline
│   ├── database.py
│   ├── discovery.py
│   └── collector.py
│
├── diary/                           # Coursework reflections
│
├── arc_raiders_sentiment.db         # SQLite database
├── main.py                          # Pipeline entrypoint
├── collection_log.txt               # Collection logs
├── comments.txt                     # Raw export
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Methodology

### 1. Data Collection Pipeline

Data was collected using the YouTube Data API v3 through a custom pipeline that performs:

**Video discovery**

* Keyword-driven search
* Incremental discovery logic
* API quota optimization

**Comment collection**

* Thread expansion
* Reply collection
* Metadata extraction

**Database storage**

* SQLite relational schema
* Deduplication safeguards
* Collection state tracking

All user identifiers are anonymized using SHA-256 hashing to ensure ethical data usage.

### 2. Exploratory Data Analysis

EDA was performed to understand dataset characteristics before modeling:

**Text analysis**

* Comment length distribution
* Word frequency analysis
* Multilingual distribution
* Token limits for transformer models

**Temporal analysis**

* Comment spikes around announcements
* Engagement concentration patterns
* Heavy-tail interaction distribution

**Content analysis**

* Domain keyword frequency
* AI discussion detection
* Feature discussion trends

Results confirmed suitability for event-driven sentiment modeling. 

### 3. Data Wrangling

The Data_Wrangling.ipynb notebook implements the structured preprocessing workflow used to prepare the modeling dataset.

#### Data cleaning

* Removed missing comments
* Filtered empty text fields
* Standardized datetime columns
* Sorted for time-series analysis

#### Feature engineering

##### **Event features**

Binary indicators detecting discussion of:

* Game announcements
* Generative AI usage
* Business model changes
* Launch events

Temporal features include:

* Days from major announcements
* Comment timing relative to events
* Sentiment decay preparation variables

#### Engagement features

Engineered variables including:

* Log-transformed like counts
* Engagement tiers
* Comment latency after upload
* Interaction timing categories

#### Text preprocessing

Text prepared for NLP models:

* URL normalization
* Mention removal
* Whitespace normalization
* Token-safe formatting

#### Conversational context enrichment

Added contextual features:

* Video description context
* Parent comment text for replies
* Conversation structure information

This enables future conversational NLP experiments.

#### Dataset quality filtering

High quality subset created using:

* English language filtering
* Minimum word thresholds
* Duplicate removal
* Missing value removal

Final modeling dataset exported as:

```
data/comments_for_analysis.csv
```

### 4. Hybrid Sentiment Labeling Workflow

A hybrid labeling approach was implemented to improve reliability beyond single-model classification.

#### Stage 1 – Baseline transformer labeling

RoBERTa sentiment model used as baseline:

Model:

```
cardiffnlp/twitter-roberta-base-sentiment-latest
```

Purpose:

* Benchmark performance
* Compare with LLM labeling
* Identify difficult samples

Output:

```
roberta_classifications.csv
```

#### Stage 2 – Silver dataset (LLM labeling)

A large language model was used to generate higher quality labels:

Model:

Llama-3.3-70B (UF HiPerGator NaviGator)

Advantages:

* Better sarcasm detection
* Context awareness
* Multi-topic understanding
* Gaming domain reasoning

Output:

```
comments_llama_labeled.jsonl
comments_llama_labeled.csv
```

#### Stage 3 – Gold dataset (manual validation)

Manual annotation performed on a subset to:

* Validate LLM reliability
* Measure agreement
* Identify failure modes
* Improve prompt design

This subset was generated and analysed after labeling in `Manual_Labeling_Analysis.ipynb`
This creates a gold evaluation dataset.

#### Stage 4 – Final labeled dataset

Combined outputs merged into:

```
comments_labeled.csv
```

This dataset enables:

* Model comparison
* Confidence analysis
* Error analysis
* Research experiments

### 5. Confidence-Aware Sentiment Analysis

The project explores **confidence-aware labeling**, where uncertain predictions can be flagged or filtered.

Implemented ideas include:

* Confidence threshold filtering
* Reject option classification
* Reliability comparison between models
* Confidence distribution analysis

This supports research into hybrid AI supervision workflows.

### 6. Research Contributions

This project contributes:

* Event-driven sentiment analysis pipeline for gaming communities
* Hybrid LLM + transformer labeling workflow
* Confidence-aware sentiment filtering approach
* Temporal sentiment spike analysis framework
* Dataset for studying AI controversy reactions in games

## How to Run the Project

### 1. Setup

Clone repository:

```bash
git clone https://github.com/sibi-seeni/CAP5771_si.seenivasan.git
cd CAP5771_si.seenivasan
```

Create environment:

```bash
uv venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
uv pip install -r requirements.txt
```

Configure API key:

```
YOUTUBE_API_KEY=your_key
NAVIGATOR_API_KEYS=your_key,your_key
```

### 2. Running the data collection pipeline

- **Run data collection**:

```bash
python main.py full
```

  - Alternative:

  If you want to skip the data collection pipeline, and directly start from data exploration, the database can be downloaded directly from [HuggingFace](https://huggingface.co/datasets/persona-156/arc-raiders-sentiment/tree/main): `persona-156/arc-raiders-sentiment/arc_raiders_sentiment.db`, and storing it in the root directory after cloning (In Step 2).

- **Run EDA**:

```
preprocessing/EDA.ipynb
```

- **Run wrangling**:

```
preprocessing/Data_Wrangling.ipynb
```

- **Run RoBERTa baseline**:

```bash
python preprocessing/roberta_classification.py
```

- **Run labeling**:

```
preprocessing/Llama_Labeler.ipynb
```

- **Creating and comparing 'Gold labels'**

```
preprocessing/Manual_Labeling_Analysis.ipynb
```

### Expected Outputs

Main outputs produced:

**Datasets**

* comments_data.csv
* comments_for_analysis.csv
* comments_llama_labeled.csv
* comments_llama_labeled.jsonl
* roberta_classifications.csv
* comments_labeled.csv

**Database**

* arc_raiders_sentiment.db

**Figures**

* Text analysis plots
* Language distribution
* Temporal analysis charts
* Video engagement analysis

**Logs**

* collection_log.txt
* absa_labeler.log

---

## Future Work

Planned extensions include:

* Confidence-aware model training
* RoBERTa and DeBERTa fine-tuning experiments
* Temporal sentiment forecasting

---

## References

* **Singh, R. K., & Thomas, A. (2025).** *A Systematic Literature Review of YouTube Comments Sentiment Analysis: Challenges and Emerging Trends.* ICTACT Journal on Data Science and Machine Learning, 7(1). [https://doi.org/10.21917/ijdsml.2025.0184](https://doi.org/10.21917/ijdsml.2025.0184)

* **Tohidi, K., Dashtipour, K., Rebora, S., & Pourfaramarz, S. (2025).** *A Comparative Evaluation of Large Language Models for Persian Sentiment Analysis and Emotion Detection in Social Media Texts.* arXiv preprint arXiv:2509.14922. [https://arxiv.org/abs/2509.14922](https://arxiv.org/abs/2509.14922)

* **He, Y., He, Z., Gu, T., Gu, B., Wan, Y., & Li, M. (2025).** *Multi-Chain of Thought Prompt Learning for Aspect-Based Sentiment Analysis.* Applied Sciences, 15, 12225. [https://doi.org/10.3390/app152212225](https://doi.org/10.3390/app152212225)

* **Schmitt, M., Schwerk, A., & Lempert, S. (2026).** *Enhancing Sentiment Classification and Irony Detection in Large Language Models through Advanced Prompt Engineering Techniques.* arXiv preprint arXiv:2601.08302. [https://arxiv.org/abs/2601.08302](https://arxiv.org/abs/2601.08302)

* **Silveira, P. S. P., & Siqueira, J. O. (2023).** *Better to Be in Agreement Than in Bad Company: A Critical Analysis of Many Kappa-Like Tests.* Behavior Research Methods, 55, 3326–3347. [https://doi.org/10.3758/s13428-022-01950-0](https://doi.org/10.3758/s13428-022-01950-0)

* **Loureiro, D., Barbieri, F., Neves, L., Espinosa Anke, L., & Camacho-Collados, J. (2022).** *TimeLMs: Diachronic Language Models from Twitter.* arXiv preprint arXiv:2202.03829. [https://arxiv.org/abs/2202.03829](https://arxiv.org/abs/2202.03829)

* **Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017).** *On Calibration of Modern Neural Networks.* arXiv preprint arXiv:1706.04599. [https://arxiv.org/abs/1706.04599](https://arxiv.org/abs/1706.04599)

* **Giachanou, A., & Crestani, F. (2016).** *Like It or Not: A Survey of Twitter Sentiment Analysis Methods.* ACM Computing Surveys, 49(2), Article 28, 41 pages. [https://doi.org/10.1145/2938640](https://doi.org/10.1145/2938640)

---

*This project is submitted as part of the MS in Applied Data Science coursework at the University of Florida. It adheres to YouTube API Terms of Service and ethical guidelines regarding public data collection.*
