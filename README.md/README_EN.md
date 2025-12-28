# 🚀 Promplab: Integral No-Code AI Platform

> **Context:** Final Project for Data Science & AI Degree.
> **Note:** This repository contains **architectural documentation** and **selected code excerpts**. The full source code remains private as it is a SaaS product in the launch phase.

## 📖 Overview

**Promplab** is a SaaS platform designed to solve data tool fragmentation. It enables non-technical users to execute **Cleaning, NLP, Computer Vision, and Predictive Modeling** workflows in a single interface, using a **Human-in-the-loop** approach.

### 🔄 Interconnected Ecosystem (Modularity)

Promplab's architecture enables non-linear workflows. Modules can be freely combined based on user needs.

**Use Case Example: From Raw Document to Business Prediction**
An illustration of the platform's full interoperability:
1.  **Ingestion:** PDF Invoice upload → OCR & AI Extraction.
2.  **Structuring:** Human editing in Cataloger → Export to clean CSV.
3.  **Modeling:** The CSV feeds the ML module → Model training and validation.
4.  **Application:** The saved model is used to perform a Sensitivity Analysis, closing the value loop by enabling predictions on new datasets.

### Functional Scope
Unlike isolated tools, Promplab integrates:
*   📊 **Tabular Data:** Automated cleaning, imputation, and exploratory analysis.
*   🧠 **Machine Learning:** Supervised modeling, clustering, and sensitivity analysis, including model validation and inference engines for new datasets.
*   👁️ **Computer Vision:** OCR, object detection, and segmentation.
*   💬 **NLP & Chat:** Sentiment analysis, topic modeling, and semantic chat (RAG).
*   🕸️ **Graphs:** Network analysis and community detection.

---

## 🏗️ Architecture & Technical Decisions

The platform prioritizes cost optimization and latency through analysis persistence and temporary caching.

*   📄 **[View Architecture Diagram](architecture/architecture_EN.md)** (Microservices, Flask, React).
*   🧠 **[Read Design Decisions](architecture/DESIGN_DECISIONS_EN.md)** (Trade-offs on inference and storage).

---

## 💻 Code Highlights

Specific modules have been selected to illustrate orchestration capabilities and security.

| Component | Technical Description | File |
| :--- | :--- | :--- |
| **Backend & AI** | Model orchestration with **Lazy Loading** (Singleton), quota isolation (Multi-tenant), and Dispatcher pattern. | [📄 backend_example.py](code-excerpts/backend_example.py) |
| **Frontend (React)** | Asynchronous architecture, state machines for long processes, and security via JWT headers. | [📄 frontend_sample.jsx](code-excerpts/frontend_sample.jsx) |
| **Database** | Implementation of **RLS (Row Level Security)** policies and JSONB structures for flexible metrics. | [📄 schema_example.sql](code-excerpts/schema_example.sql) |

---

## 🗄️ Data Schema & Security

Persistence is managed via **Supabase (PostgreSQL)**. The design ensures each user operates in an isolated environment, encrypted at rest and in transit.

![Database Schema](asset/supabase-schema.jpg)

*   **Security:** See `schema_example.sql` for details on how RLS policies ensure total isolation of models and predictions per user.

---

## 🚀 Project Status

*   **Status:** Functional MVP operating in a local environment.
*   **Roadmap:** Cloud deployment (Dockerization) and public launch (Freemium).
*   **Model:** Sustainable SaaS with low operating cost per user (deferred execution and instance optimization).

---

## 🛠️ Tech Stack

Detailed list in [`requirements.txt`](requirements.txt).

*   **Backend:** Python, Flask, Supabase, Google Gemini API.
*   **Data Science:** Pandas, Scikit-learn, Torch, Polars, NetworkX.
*   **Frontend:** React, Vite, Material-UI, Plotly.js.

---

## 🤖 Development Methodology: AI-First

This project was built using an **AI-Augmented Development** philosophy.
As a Solo-Founder, I leveraged Generative AI tools (Gemini/ChatGPT) as force multipliers to accelerate development.

**My core role focused on:**
*   **Solution Architecture:** System design, database modeling, and data flow strategy.
*   **Technical Prompt Engineering:** Translating business requirements into precise technical specifications for code generation.
*   **Integration:** Assembling modules, debugging, and validating the generated logic.

This approach enabled the delivery of a commercial-grade MVP in just **6 months**, showcasing product management skills and technical efficiency.

---

## 👤 Author

**Miriam Raposo**  
*Data Science & AI Technician | Solutions Architect*

Developed as a comprehensive End-to-End solution. If you have questions about the technical implementation or architecture, feel free to reach out.