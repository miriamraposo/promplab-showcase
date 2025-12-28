
# Decisiones de Diseño y Trade-offs Técnicos

Este documento detalla algunas de las decisiones arquitectónicas tomadas para equilibrar la experiencia de usuario (UX), los costos operativos y la eficiencia técnica en Promplab.

## 🚀 Optimización y Eficiencia

## 🛠️ Flujos de Procesamiento de Datos (Data Pipelines)
A diferencia de herramientas básicas, Promplab ofrece tres niveles de orquestación para el tratamiento de datos:

Asistido por IA (Heuristic-AI Hybrid): Creación de pipelines iterativos para usuarios inexpertos, donde el sistema sugiere transformaciones basadas en heurísticas y análisis inteligente del dataset.

Pipeline Configurable para usuarios intermedios (Advanced UX): Flujo técnico completo donde el usuario configura cada paso con Live Preview del archivo limpio, gestión de historial detallado y capacidad de deshacer/eliminar transformaciones específicas.

Modo Manual (Granular Control): Control absoluto sobre operaciones atómicas para usuarios que requieren ajustes precisos antes de la exportación o el entrenamiento.

### Persistencia de Análisis Documental (Write-Once, Read-Many)
**Decisión:** El análisis costoso de documentos (como PDFs extensos) se ejecuta una única vez.
**Impacto:** Los resultados vectoriales o estructurados se almacenan para su reutilización. Esto reduce drásticamente la latencia en consultas posteriores y minimiza el consumo de créditos de APIs de IA externas.

### Cache Transitoria para Experimentación
**Decisión:** En flujos iterativos (como clustering de imágenes), los modelos se mantienen temporalmente en memoria o caché rápida.
**Impacto:** Permite al usuario ajustar hiperparámetros y re-ejecutar procesos en tiempo real sin la sobrecarga de I/O de base de datos hasta que decide guardar el resultado final.

### Carga de Modelos "On-Demand"
**Decisión:** Implementación de mecanismos de control de instancias para evitar inicializaciones redundantes.
**Impacto:** Mejora la estabilidad del sistema en entornos de recursos compartidos.

## 🧠 Interacción Humano-IA (Human-in-the-Loop)

### Abstracción de Datos Estructurados
**Decisión:** Las consultas en lenguaje natural del usuario se traducen a operaciones estructuradas (Pandas/SQL) en el backend.
**Impacto:** Habilita la exploración de datos compleja sin exponer al usuario a la sintaxis técnica, manteniendo la seguridad al no ejecutar código arbitrario directamente.

### Persistencia Controlada por el Usuario
**Decisión:** Los modelos entrenados y los datasets limpios no se guardan permanentemente hasta que el usuario valida el resultado.
**Impacto:** Fomenta la experimentación sin miedo a "ensuciar" el espacio de trabajo o incurrir en costos de almacenamiento innecesarios.

## 🏗️ Modularidad y Flujos

### Diseño de Componentes Interconectados
**Decisión:** Los módulos no son silos aislados. Un PDF analizado puede convertirse en un dataset, que luego pasa al módulo de limpieza y finalmente al de predicción.
**Impacto:** Favorece la coherencia de los datos a lo largo de todo el ciclo de vida del proyecto y maximiza la reutilización de recursos.

## ⚖️ Gestión de Costos y Limitaciones (Free Tier)

### Trade-offs Conscientes
**Decisión:** Establecer límites estrictos de tamaño de archivo y volumen de filas para la versión gratuita, ejecutando operaciones intensivas en CPU en lugar de GPU.
**Impacto:** Garantiza la sostenibilidad operativa del SaaS y la compatibilidad con infraestructura de bajo costo, permitiendo escalar a hardware dedicado solo para usuarios premium.
