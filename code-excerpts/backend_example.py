# ======================================================
# Selected Backend Architecture Excerpts – PrompLab
# ======================================================
#This file intentionally groups excerpts from different layers to showcase architectural decisions.


"""
Alternative: process-level model registry or dependency injection in larger deployments.

[EN] BACKEND ARCHITECTURE OVERVIEW
This file showcases architectural decisions designed for a scalable AI SaaS (Cloud Run):
- Thread-safe Singleton pattern for Model Management.
- Cloud-native Lazy Loading to minimize cold start times.
- Multi-tenant API Key handling (User Key > System Key).
- Strict file validation layers for security.

[ES] VISIÓN GENERAL DE LA ARQUITECTURA BACKEND
Este archivo muestra decisiones de arquitectura diseñadas para un SaaS de IA escalable (Cloud Run):
- Patrón Singleton thread-safe para la gestión de modelos pesados.
- Carga perezosa (Lazy Loading) orientada a reducir tiempos de arranque en entornos serverless.
- Manejo multi-tenant de claves API (clave de usuario con prioridad sobre clave del sistema).
- Capas estrictas de validación de archivos enfocadas en seguridad y estabilidad.



NOTE: This is a showcase of production logic. Imports and specific implementation details 
have been simplified for readability.
"""


import threading
import logging
from collections import OrderedDict
from transformers import pipeline
from typing import Optional,Any
from flask import has_request_context, g 

# Alternative: process-level model registry or dependency injection in larger deployments.

"""
[EN] BACKEND ARCHITECTURE OVERVIEW
...
"""

logger = logging.getLogger(__name__)



class ModelManager:
    """
    Centralized manager for AI models and external API clients.
    
    [Pattern] Thread-safe Singleton.
    Reason: We need a single source of truth for heavy models to avoid 
    memory overflows in containerized environments (Cloud Run).
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # Double-checked locking pattern for thread safety
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Prevent re-initialization
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._lock = threading.Lock()
        logger.info("Initializing ModelManager (Cloud Native Mode)...")
        
        # Tools Registry
        self.AVAILABLE_TOOLS = {
            "API: Google Gemini Pro": "models/gemini-flash-latest",
            "API: OpenAI GPT-4o": "gpt-4o",
            "Local: Image Classifier (ViT)": "google/vit-base-patch16-224",
            "Local: Object Detector (YOLOv8n)": "yolov8n.pt",
        }
        
        # Lazy Loading Placeholders (Save RAM on startup)
        self._image_classifier = None
        self._object_detector = None
        
        # ❌ PRELOAD REMOVED: self._preload_all_local_models() 
        # Reason: Optimization for Serverless Cold Starts.
        
        self._initialized = True

    # -------------------------------------------------------------------------
    # LAZY LOADING IMPLEMENTATION
    # Only consume RAM (~500MB+) when the user actually requests the feature.
    # -------------------------------------------------------------------------

    def _get_or_load_image_classifier(self):
        if self._image_classifier is None:
            with self._lock:
                if self._image_classifier is None:
                    try:
                        logger.info("🚀 Loading ViT Model into RAM...")
                        # device=-1 forces CPU usage (Cloud Run has no GPU)
                        self._image_classifier = pipeline(
                            "image-classification",
                            model="google/vit-base-patch16-224", 
                            device=-1 
                        )
                        logger.info("✅ Model Loaded.")
                    except Exception as e:
                        logger.exception("❌ Vision Model Load Failed")
                        self._image_classifier = None
        return self._image_classifier

    # -------------------------------------------------------------------------
    # MULTI-TENANT SECURITY & ROUTING
    # -------------------------------------------------------------------------
    
    def get_tool(self, tool_display_name: str, user_context_keys: dict = None) -> dict:
        """
        Resolves the tool and applies the correct API Key strategy.
        Priority: User's Custom Key (BYOK) > System Fallback Key.
        """
        tool_id = self.AVAILABLE_TOOLS.get(tool_display_name)
        if not tool_id:
            return {"success": False, "error": "Unknown tool"}

        provider = self._resolve_provider(tool_display_name) # Helper function
        tool_type = self._resolve_type(tool_display_name)

        # 1. API Handling (BYOK Strategy)
        if tool_type == "api":
            # Check if user provided their own key in the request context
            api_key_override = user_context_keys.get(provider) if user_context_keys else None
            
            if api_key_override:
                logger.info(f"👤 Using USER-PROVIDED KEY for {provider}.")
                client = self._build_client(provider, api_key_override)
            else:
                # Fallback to system key (Free tier / Demo)
                client = self._api_clients_cache.get(provider)
            
            return {"success": True, "tool_object": client, "model_id": tool_id}

        # 2. Local Model Handling
        elif tool_type == "local_vision_classification":
            model = self._get_or_load_image_classifier()
            return {"success": True, "tool_object": model} if model else {"success": False, "error": "Model Load Failed"}

        return {"success": False, "error": "Invalid Tool Type"}
    


# NOTE:
# This string-based dispatcher is intentionally explicit and whitelist-based.
# ACTION_MAP defines a closed set of ~30 cleaning actions validated during development.
# Only predefined actions are executable, preventing arbitrary dynamic execution.
# Each action is unit-tested in isolation to ensure safety and predictable behavior.
# This design is intended for production deployment without relying on open reflection.
#
# NOTA:
# Este despachador basado en strings es explícito y funciona con una lista blanca.
# ACTION_MAP define un conjunto cerrado de ~30 acciones validadas en desarrollo.
# Solo se permiten acciones predefinidas, evitando ejecuciones dinámicas arbitrarias.
# Cada acción se prueba de forma aislada para garantizar seguridad y comportamiento predecible.



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
# 2. Secure File Processing Strategy
# ======================================================

MAX_FILE_SIZE_MB = 5
MAX_ROWS = 10000 
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'pdf', 'txt'}

def process_uploaded_file(file_stream, filename: str) -> dict:
    """
    Strict validation layer before data ingestion.
    Prevents DOS attacks via large files and ensures data integrity.
    """
    # 1. Extension Validation
    if not _is_allowed_extension(filename):
        return {"success": False, "error": "Security: Extension not allowed."}

    # 2. Content-Type & Size Logic (Handled by Worker/Handler)
    # ... code omitted for brevity ...

    # 3. Safe Parsing based on Type
    try:
        if filename.endswith('.csv'):
            # Enforce row limits to prevent memory overflow
            df = pd.read_csv(file_stream, nrows=MAX_ROWS, on_bad_lines='warn')
            if df.empty: return {"success": False, "error": "Empty dataset"}
            
            return {
                "success": True, 
                "content": df.to_dict(orient="records"),
                "columns": list(df.columns)
            }
            
        elif filename.endswith('.pdf'):
            # Specific PDF extraction logic
            text = _extract_text_from_pdf(file_stream)
            validate_text_length(text) # Hard limit on tokens
            return {"success": True, "content": text}
            
    except Exception as e:
        logger.error(f"Processing Error: {e}")
        return {"success": False, "error": "File processing failed."}
    

# ======================================================
# 3. Secure Data Ingestion & Schema Isolation
# ======================================================

"""
Frontend (Declarative)
   ↓
API Layer
   ↓
Dispatcher / Orchestrator
   ↓
Models / SQL / Filesystem

"""

def create_and_populate_table_from_df(self, df: pd.DataFrame, table_name: str, schema: str = "private"):
    """
    Creates a temporary SQL table for AI analysis.
    
    [Security Architecture] Schema Isolation:
    - Forces creation in a 'private' schema.
    - RESULT: The table is completely invisible to the public Supabase API (PostgREST),
      preventing unauthorized access via the frontend.
      
    [AI Optimization] Data Normalization:
    - Normalizes column names (lowercase, no spaces) to ensure the LLM 
      can generate valid SQL queries reliably.
    """
    conn = None
    try:
        # 1. AI Optimization: Normalize columns for better SQL generation
        df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(' ', '_')
        
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor()

        # 2. Security: Ensure the isolation layer exists
        # If "private" schema doesn't exist, public access might leak.
        create_schema_query = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
            sql.Identifier(schema)
        )
        cursor.execute(create_schema_query)

        # 3. SQL Injection Protection
        # We use psycopg2.sql.Identifier to safely quote table and column names.
        table_identifier = sql.SQL("{}.{}").format(
            sql.Identifier(schema),
            sql.Identifier(table_name)
        )

        # 4. Dynamic Table Creation
        # ... (columns mapping logic omitted for brevity) ...
        
        create_table_query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({});").format(
            table_identifier,
            sql.SQL(", ").join(columns_sql_parts) # generated previously
        )
        cursor.execute(create_table_query)
        
        # 5. Bulk Insert
        # ... (insert logic omitted for brevity) ...
        
        conn.commit()
        return {"success": True, "table": f"{schema}.{table_name}"}

    except Exception as e:
        if conn: conn.rollback()
        return {"success": False, "error": str(e)}
    

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

7. Private Schema Isolation (SQL Chat)
   - DECISION: Temporary datasets are created in a `private` PostgreSQL schema.
   - WHY: Decouples analysis data from the public API, adding a layer of security against unauthorized access.


Overall Philosophy:
- Backend declarative, frontend declarative-light
- Security enforced server-side
- Human-in-the-loop for all AI-assisted workflows
- Scalability and multi-tenant readiness built-in
- UX-conscious error handling and system transparency
"""
