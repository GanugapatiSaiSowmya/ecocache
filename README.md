# EcoCache

A semantic caching layer for LLM APIs that reduces water consumption and 
carbon emissions by avoiding redundant AI inference calls.

## The problem

Every LLM API call consumes ~5mL of water and generates ~4g of CO₂. 
A large percentage of real-world queries are semantically identical — 
"what is ML?" and "explain machine learning" should return the same 
answer without hitting the API twice.

## How it works

EcoCache converts queries into vector embeddings, searches for 
semantically similar past queries, and returns cached responses when 
a close match exists. Only genuinely new questions reach the LLM API.

## Quick start
```python
from ecocache.client import EcoCacheClient

client = EcoCacheClient(api_key="your-openai-key")

# First call — hits the API
r1 = client.chat("What is photosynthesis?")

# Semantically similar — served from cache, no API call, no water used
r2 = client.chat("Can you explain how photosynthesis works?")
print(r2["source"])   # → "cache"
print(r2["savings"])  # → water and carbon saved so far
```

## Installation
```bash
git clone https://github.com/GanugapatiSaiSowmya/ecocache
cd ecocache
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Add your OpenAI API key to a `.env` file:
```
OPENAI_API_KEY=your-key-here
```

## Dashboard
```bash
python3 dashboard/app.py
# open http://localhost:5000
```

## Motivation

Built as a side project to make a small but real dent in the 
environmental cost of AI. Data centers consume billions of liters 
of freshwater annually for cooling. Software efficiency is one of 
the few levers available at the application layer.

## Built by

Ganugapati Sai Sowmya — CS Engineering student, 3rd year.