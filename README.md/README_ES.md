# 🚀 Promplab: Plataforma Integral de IA No-Code

> **Contexto:** Proyecto final de la Tecnicatura en Ciencia de Datos e IA.
> **Nota:** Este repositorio contiene **documentación de arquitectura** y **ejemplos de código seleccionados**. El código fuente completo se mantiene privado por ser un producto SaaS en fase de lanzamiento.

## 📖 Visión General

**Promplab** es una plataforma SaaS nativa en español diseñada para resolver la fragmentación de herramientas de datos. Permite a usuarios no técnicos ejecutar flujos de **Limpieza, NLP, Visión por Computadora y Modelado Predictivo** en una única interfaz, bajo un enfoque **Human-in-the-loop**.

### 🔄 Ecosistema Interconectado (Modularidad)

La arquitectura de Promplab permite flujos de trabajo no lineales. Los módulos pueden combinarse libremente según la necesidad del usuario.

**Caso de Uso: De Documento Crudo a Predicción de Negocio**
Un ejemplo de la interoperabilidad completa de la plataforma:
1.  **Ingesta:** Carga de una factura en PDF → Extracción con OCR e IA.
2.  **Estructuración:** Edición humana en el Catalogador → Exportación a CSV limpio.
3.  **Modelado:** El CSV alimenta el módulo de ML → Entrenamiento y validación de modelos.
4.  **Aplicación:** El modelo guardado se utiliza para realizar un **Análisis de Sensibilidad**, cerrando el ciclo de valor al permitir la inferencia sobre nuevos conjuntos de datos.

### Alcance Funcional
A diferencia de herramientas aisladas, Promplab integra:
*   📊 **Datos Tabulares:** Limpieza automática, imputación y análisis exploratorio.
*   🧠 **Machine Learning:** Modelado supervisado, clustering, validación cruzada y motores de inferencia.
*   👁️ **Visión por Computadora:** OCR, detección de objetos y segmentación.
*   💬 **NLP & Chat:** Análisis de sentimiento, tópicos y chat semántico sobre documentos (RAG).
*   🕸️ **Grafos:** Análisis de redes y detección de comunidades.

---

## 🏗️ Arquitectura y Decisiones Técnicas

La plataforma prioriza la optimización de costos y la latencia mediante persistencia de análisis y caché temporal.

*   📄 **[Ver Diagrama de Arquitectura](architecture/architecture_ES.md)** (Microservicios, Flask, React).
*   🧠 **[Leer Decisiones de Diseño](architecture/DESIGN_DECISIONS_ES.md)** (Trade-offs sobre inferencia y almacenamiento).

---

## 💻 Ejemplos de Código (Code Highlights)

Se han seleccionado módulos específicos para ilustrar la capacidad de orquestación y seguridad.

| Componente | Descripción Técnica | Archivo |
| :--- | :--- | :--- |
| **Backend & IA** | Orquestación de modelos con **Lazy Loading** (Singleton), aislamiento de cuotas (Multi-tenant) y patrón Dispatcher. | [📄 backend_example.py](code-excerpts/backend_example.py) |
| **Frontend (React)** | Arquitectura asíncrona, máquinas de estado para procesos largos y seguridad vía JWT headers. | [📄 frontend_sample.jsx](code-excerpts/frontend_sample.jsx) |
| **Base de Datos** | Implementación de políticas **RLS (Row Level Security)** y estructuras JSONB para métricas flexibles. | [📄 schema_example.sql](code-excerpts/schema_example.sql) |

---

## 🗄️ Esquema de Datos y Seguridad

La persistencia se gestiona en **Supabase (PostgreSQL)**. El diseño garantiza que cada usuario opere en un entorno aislado, encriptado en reposo y tránsito.

![Database Schema](asset/supabase-schema.jpg)

*   **Seguridad:** Ver `schema_example.sql` para detalles sobre cómo las políticas RLS aseguran el aislamiento total de modelos y predicciones por usuario.

---

## 🚀 Estado del Proyecto

*   **Estado:** MVP funcional operativo en entorno local.
*   **Roadmap:** Despliegue en la nube (Dockerización) y lanzamiento de versión pública (Freemium).
*   **Modelo:** SaaS sostenible con bajo costo operativo por usuario (ejecución diferida y optimización de instancias).

---

## 🛠️ Stack Tecnológico

Lista detallada en [`requirements.txt`](requirements.txt).

*   **Backend:** Python, Flask, Supabase, Google Gemini API.
*   **Data Science:** Pandas, Scikit-learn, Torch, Polars, NetworkX.
*   **Frontend:** React, Vite, Material-UI, Plotly.js.

---

## 🤖 Metodología de Desarrollo: AI-First

Este proyecto fue concebido y ejecutado bajo una filosofía de **Desarrollo Aumentado por IA**.
Como único desarrollador (Solo-Founder), utilicé herramientas de IA Generativa (Gemini/ChatGPT) para actuar como multiplicadores de fuerza.

**Mi rol principal fue:**
*   **Arquitecto de Soluciones:** Diseño del sistema, base de datos y flujos de datos.
*   **Prompt Engineering Técnico:** Traducción de requerimientos de negocio a especificaciones técnicas precisas para la generación de código.
*   **Integrador:** Ensamblaje de módulos (Frontend, Backend, DB), debugging y validación de la lógica generada.

Este enfoque permitió construir un MVP de nivel comercial en un plazo de **6 meses**, demostrando capacidad de gestión de producto y eficiencia técnica.

---

## 👤 Autor

**Miriam Raposo**  
*Data Science & AI Technician | Solutions Architect*

Desarrollado como una solución integral End-to-End. Si tienes preguntas sobre la implementación técnica, la arquitectura o la metodología AI-First utilizada, no dudes en contactarme.