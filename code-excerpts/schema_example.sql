-- ======================================================
-- Promplab Database Schema Excerpt: AI Model Management
-- ======================================================

/* 
[ES] Este extracto ilustra cómo Promplab gestiona la persistencia de 
modelos entrenados, garantizando aislamiento entre usuarios (RLS) y 
almacenamiento eficiente de métricas de performance (JSONB).

[EN] This excerpt illustrates how Promplab manages the persistence of 
trained models, ensuring user isolation (RLS) and efficient storage 
of performance metrics using JSONB.
*/

CREATE TABLE public.trained_models (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  
  -- Identificación del modelo / Model Identification
  model_name TEXT NOT NULL,             -- Ej: "Random Forest"
  model_display_name TEXT NOT NULL,     -- Nombre dado por el usuario / User-defined name
  project_name TEXT NOT NULL,           -- Organización lógica / Logical grouping
  
  -- Referencia a archivos y datos / Data & File References
  model_storage_path TEXT NOT NULL UNIQUE, 
  source_dataset_id UUID, 
  
  -- Datos complejos (Estructura flexible) / Complex Data (Flexible structure)
  feature_cols JSONB,           -- Lista de variables / List of independent variables
  evaluation_results JSONB,     -- Métricas: Accuracy, R2, etc. / Metrics report
  
  CONSTRAINT unique_model_per_user_project UNIQUE (user_id, project_name, model_display_name)
);

-- Documentación interna / Internal Documentation
COMMENT ON COLUMN public.trained_models.evaluation_results IS 'Stores the metrics report obtained after training / Almacena el reporte de métricas.';

-- ======================================================
-- Security Layer: Row Level Security (RLS)
-- ======================================================

-- Habilitar seguridad a nivel de fila / Enable Row Level Security
ALTER TABLE public.trained_models ENABLE ROW LEVEL SECURITY;

-- Política de aislamiento total / Full isolation policy
CREATE POLICY "Allow full access for own models"
ON public.trained_models
FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);