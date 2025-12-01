# 🧠 **FX-Aware Marketing & Pricing Strategy Agent** 

## 🧩 Problem: FX-Driven Pricing Decisions Are Manual & Hard to Scale

Global consumer-electronics companies have **long international supply chains** 🌍. Devices like TVs, laptops, and smartphones are often **purchased in one currency** (e.g. CNY) and **sold in many others** (USD, EUR, local currencies). Even small FX moves can **change landed cost and squeeze margins** in already competitive segments 💸.

Today, the workflow to set or update a price is mostly **manual** and **spread across people and tools**:

- pull internal cost in the procurement currency,
- convert it to the target currency using current FX rates,
- collect competitor prices from dashboards, sites, or local teams,
- maintain an Excel with a few ad-hoc FX scenarios,
- calculate margins for several candidate prices,
- write an email or slide with the final recommendation.

This procedure is repeated for **dozens of SKUs and regions**, for each change or launch.
This leads to structural problems for the business ⚠️:

- **FX risk is under-modeled** – assumptions live in personal spreadsheets, not in a shared, auditable workflow.  
- **Logic is fragmented** – market view, competition, FX scenarios, and margin targets live in different places, making decisions inconsistent.  
- **Poor scalability & traceability** – careful analysis is possible for one “hero” device, but not for hundreds of products, and months later it’s hard to say *why* a specific price was chosen.  
- **High opportunity cost** – managers spend hours on repetitive calculations instead of scenarios, strategy, and alignment 🚦.

In short, the issue is not a lack of data, but the lack of a **robust, FX-aware, repeatable pricing decision workflow**.

---

## 💡 Solution: FX-Aware Marketing & Pricing Strategy Agent

The **FX-Aware Marketing & Pricing Strategy Agent** turns this manual workflow into a **standardized multi-agent pipeline** 🧠.

Given a product configuration (device, region, procurement cost & currency, target margin, current or planned price), the agent:

- summarizes **market and competitor positioning** for this device 📊,
- builds **FX scenarios** (base / adverse / favorable) and recomputes landed cost 💱,
- simulates **margins for candidate prices** under these FX paths 🧮,
- recommends a **pricing strategy** (match / undercut / premium) and a specific price or narrow band,
- produces a short **decision brief** plus a **structured JSON summary** for downstream systems.

This improves the enterprise workflow 🚀:

- replaces ad-hoc Excel models with a **consistent decision flow**,  
- treats **FX risk as a first-class input**,  
- scales from one SKU to **portfolio-level runs** (e.g. 1,000 devices),  
- adds an **explanation and audit trail** for each recommendation,  
- frees managers from low-level calculations so they can focus on **strategy and scenario discussions**.

The end result is a faster, more transparent and clearly **FX-aware** pricing process, where the final decision still rests with the people.

---
### 🧩 Features Implemented

✅ 🧠 LLM-Powered Multi-Agent System (sequential pipeline + coordinator agent)  
✅ 🧭 Sequential Orchestration (planner → specialized agents → evaluator)  
✅ 🛠️ Custom Domain Tools (market snapshots, FX scenarios, margin planner, observability helpers)  
✅ 🔍 Built-In Google Search Tool (`google.adk.tools.google_search`) for external market context  
✅ 📦 Sessions & State Management (per-run FX pricing context object)  
✅ 🧾 Long-Term FX Memory Service (per product & region, with stored sessions and aggregates)  
✅ 🧩 Context Engineering via Consolidated Memory Summaries (compact “FX memory summary” per key)  
✅ 📊 Observability: Logging, Basic Metrics & Run Statistics (per agent / tool / session)  
✅ ✅ Dedicated Evaluation Agent-as-Judge (coverage, consistency, clarity, actionability)  
✅ 🌐 A2A Protocol Integration (FX microservice exposed/consumed via A2A-style service wrapper)  
✅ 🚀 Batch-Friendly Design for Long-Running Portfolio Runs (same pipeline for 1 or 1,000+ devices)

---
### 🚀 How to Run & How to Read This Notebook

#### 🔧 Prerequisites

- A valid **Gemini API key** available to the notebook  
  (e.g. via Kaggle Secrets or environment variable – see `SETUP` cell).  
- Internet access enabled if you want **live tools** (e.g. FX / search).  
- Optional: turn off external calls by toggling the config flag in the setup section.

---

#### ▶️ How to Run

1. Run the **`SETUP`** section (imports, config, clients). ⚙️  
2. Run **`TOOLS`** and **`AGENT DEFINITIONS`** to register all tools and agents. 🧠🛠️  
3. Use the **“Demo / Single Run”** cell in the `FINAL PIPELINE` section to see a full example for one device and region. 📈  
4. (Optional) Run the **batch / N devices** cell in `TESTING` to reproduce portfolio-scale results. 📊

---

#### 📚 How to Read

- Start with: `Problem & Solution` → `Multi-Agent Architecture` → `Features`.  
- Then skim: `TOOLS` → `AGENT DEFINITIONS` → `FINAL PIPELINE`.  
- For deeper details, see: `TESTING & EVALUATION` and `PROJECT JOURNEY` at the end. ✨

### **Architecture** 

![Arc](https://github.com/user-attachments/assets/1f1c0fa8-6c20-459f-acd4-8bb70bf7dce3)
