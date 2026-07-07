# AI Medicare Governance System

A secure Flask-based AI healthcare application powered by Meta-LLaMA-3 with multi-layer guardrails for safe, compliant medical responses.

## Architecture

- **LLM Backend** — Meta-LLaMA-3 for medical query understanding and response generation
- **Guardrail Layers**:
  - Toxicity detection — filters harmful or abusive content
  - Keyword filtering — blocks sensitive medical disclaimers and unauthorized advice
  - Role-based access control — restricts features by user role
  - Output auditing — logs all interactions for compliance review
- **Web Interface** — Flask frontend for user interaction and moderation dashboards

## Features

- Safe, compliant AI-powered medical information system
- Multi-layer content moderation pipeline
- Role-based access for patients, doctors, and admins
- Full audit trail for regulatory compliance
- Deployed on Render for scalable access

## Tech Stack

- Python (Flask)
- Meta-LLaMA-3
- HTML / CSS / JavaScript
- Render (Hosting)

## Getting Started

```bash
git clone https://github.com/harrish1709/AI-Medicare.git
cd AI-Medicare
pip install -r requirements.txt
python app.py
```

## Live Demo

[https://ai-medicare-9410.onrender.com](https://ai-medicare-9410.onrender.com)
