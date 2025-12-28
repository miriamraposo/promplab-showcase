# ======================================================
# Selected Backend Architecture Excerpts – Promplab
# ======================================================

"""
[EN] BACKEND ARCHITECTURE OVERVIEW
This file showcases architectural decisions designed for a scalable AI SaaS:
- Model management and resource optimization (Singleton Pattern).
- Multi-user AI integration and quota isolation.
- Declarative "No-code" workflows for data cleaning.
- User-facing error abstraction (Technical -> Friendly Spanish).

[ES] VISIÓN GENERAL ARQUITECTURA BACKEND
Este archivo muestra decisiones de arquitectura diseñadas para un SaaS de IA escalable:
- Gestión de modelos y optimización de recursos (Patrón Singleton).
- Integración de IA multi-usuario y aislamiento de cuotas.
- Flujos de trabajo declarativos "No-code" para limpieza de datos.
- Abstracción de errores para el usuario (Técnico -> Español Amigable).

NOTE: The code is intentionally partial and non-executable.
"""

# ======================================================
# 1. Model Management & Resource Optimization
# ======================================================

import threading   

class ModelManager:
    """
    Centralized manager for AI models and external API clients.
    
    [Pattern] Singleton with Lazy Loading.
    - Prevents duplicate loading of heavy models (RAM optimization).
    - Ensures thread-safe access in a concurrent Flask environment.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._image_classifier = None
        return cls._instance

    def _get_or_load_image_classifier(self):
        """
        Lazy-loads the image classification model only on first use.
        """
        if self._image_classifier is None:
            with self._lock:
                # Double-checked locking
                if self._image_classifier is None:
                    # Abstracted loader function
                    self._image_classifier = load_image_model()  
        return self._image_classifier

# ======================================================
# 2. Multi-user AI Integration & Quota Isolation
# ======================================================

def get_tool(self, tool_name: str, user_keys: dict | None = None) -> dict:
    """
    Resolves the appropriate AI tool instance for a specific request.

    Priority Logic:
    1. User-provided API key (Ensures cost/quota isolation per tenant).
    2. System-level fallback key (For free-tier or demos).
    """
    tool_id = self.AVAILABLE_TOOLS.get(tool_name)
    if not tool_id:
        return {"success": False, "error": "Unknown tool"}

    provider = self._resolve_provider(tool_name)
    
    # Critical for SaaS: Use user's key if available
    api_key = user_keys.get(provider) if user_keys else None
    
    client = self._build_client(provider, api_key)

    return {
        "success": True,
        "provider": provider,
        "model_id": tool_id,
        "client": client
    }

# ======================================================
# 3. No-code Data Cleaning Dispatcher
# ======================================================

# Mapping frontend actions to internal Python functions
ACTION_MAP = {
    "general_drop_duplicates": "eliminar_duplicados", # Reference to internal func
    "numeric_impute_by_method": "imputar_nulos_numericos",
    "type_convert_to_date": "convertir_a_fecha",
    "general_create_calculated_column": "crear_columna_calculada_wrapper",
}

def cleaning_action(df, action, params):
    """
    Central dispatcher for no-code data cleaning actions.
    
    - Decouples frontend intent from backend logic.
    - Allows the frontend to be strictly declarative.
    """
    # Pre-processing step common to all actions
    df_prepared = preprocess_nulls_and_text(df)

    if action not in ACTION_MAP:
        raise ValueError(f"Unknown cleaning action: {action}")

    # Dynamic function execution
    func_name = ACTION_MAP[action]
    # In production: globals()[func_name](df, **params) or similar dispatch
    df_cleaned, message = execute_function(func_name, df_prepared, **params)
    
    # Re-run diagnostics to show immediate impact to user
    diagnostics = get_preliminary_analysis(df_cleaned)

    return df_cleaned, diagnostics

# ======================================================
# 4. Human-in-the-loop Pipeline Preview
# ======================================================

@app.route("/api/datasets/recalculate-pipeline-preview", methods=["POST"])
@token_required
@csrf_required
def recalculate_pipeline_preview(current_user):
    """
    Sandbox execution of a declarative data pipeline.
    
    Allows the user to see the result of their cleaning steps 
    WITHOUT persisting changes to the database yet.
    """
    # 1. Load original immutable state
    df_original = load_original_dataset(dataset_id, current_user.id)

    # 2. Apply all steps in memory
    df_processed, receipts = pipeline_orchestrator.execute_pipeline(
        df_original, steps
    )

    # 3. Return preview (Head) + Impact Analysis (Diagnostics)
    preview = df_processed.head(100)
    diagnostics = generate_smart_diagnostics(df_processed)

    return {
        "preview": preview,
        "diagnostics": diagnostics,
        "receipts": receipts
    }

# ======================================================
# 5. User-facing Error Abstraction (UX)
# ======================================================

def translate_error_to_user(e, provider):
    """
    Translates low-level technical errors from AI providers 
    into user-friendly Spanish messages.
    """
    error_str = str(e)

    # Example: Handling OpenAI or Gemini specific errors
    if "API_KEY_INVALID" in error_str:
        return f"⚠️ La clave API de {provider} no es válida. Por favor verifica tu configuración."

    if "quota_exceeded" in error_str:
        return f"⚠️ Te has quedado sin crédito en {provider}. Revisa tu plan de facturación."

    # Fallback for unknown errors
    return f"Error del proveedor {provider}: {error_str}"



# ======================================================
# Summary of Key Concepts
# ======================================================

"""
This section summarizes the architectural principles,
design trade-offs, and best practices illustrated
in the previous code excerpts.

1. Model Management & Resource Optimization
   - Singleton + lazy loading to prevent redundant heavy model loading
   - Thread-safe access for concurrent requests
   - Reduces memory footprint and latency
   - Trade-off: Slight initial load time on first use

2. Multi-user AI Integration & Quota Isolation
   - Users can operate with their own API keys
   - System-level keys only used as fallback
   - Isolates costs and quotas per user
   - Trade-off: Extra logic to handle missing or invalid keys

3. No-code Data Cleaning Dispatcher
   - Declarative, backend-executed actions
   - Frontend only declares actions and parameters
   - Fully auditable and reversible
   - Trade-off: Limited to predefined actions; advanced custom logic requires backend update

4. Human-in-the-loop Pipeline Preview
   - Non-destructive recalculation of pipelines
   - Users review previews and diagnostics before persisting changes
   - Ensures transparency and control
   - Trade-off: Larger datasets require sampling or chunking to maintain responsiveness

5. User-facing Error Abstraction
   - Translates provider-specific technical errors into friendly messages
   - Improves UX and reduces user frustration
   - Trade-off: Abstracts low-level details, so some advanced troubleshooting may require backend logs

6. File Upload Limits
   - Max 5 MB, max 10,000 rows
   - Protects server and ensures responsive previews
   - Trade-off: Users with very large datasets must preprocess offline or split files

Overall Philosophy:
- Backend declarative, frontend declarative-light
- Security enforced server-side
- Human-in-the-loop for all AI-assisted workflows
- Scalability and multi-tenant readiness built-in
- UX-conscious error handling and system transparency
"""
