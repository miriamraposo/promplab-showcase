import React, { useState, useCallback } from 'react';
import { 
  Box, Button, CircularProgress, Alert, 
  Typography, Paper, List, ListItem 
} from '@mui/material';
import { supabase } from '../supabaseClient'; // Simulated import for context
import { useNotification } from '../hooks/useNotification';

/**
 * ============================================================================
 * SAMPLE COMPONENT: DataPipelineManager
 * ============================================================================
 * 
 * [EN] This component demonstrates the handling of complex asynchronous 
 * state transitions in a SaaS environment. It manages the user's intent 
 * to apply a transformation pipeline to a dataset.
 * 
 * [ES] Este componente demuestra el manejo de transiciones de estado 
 * asíncronas complejas. Gestiona la intención del usuario de aplicar un 
 * pipeline de transformación a un dataset.
 * 
 * KEY FEATURES / CARACTERÍSTICAS CLAVE:
 * 1. Secure API communication (Bearer Tokens/JWT).
 * 2. State Machine Pattern (Planning -> Executing -> Review).
 * 3. Optimistic UI & Error Boundaries.
 */

export default function DataPipelineManager({ datasetId, initialData }) {
    // State machine for the pipeline process: 'IDLE' | 'EXECUTING' | 'COMPLETED' | 'ERROR'
    const [pipelineStatus, setPipelineStatus] = useState('IDLE');
    const [cleaningHistory, setCleaningHistory] = useState([]);
    const [previewData, setPreviewData] = useState(initialData);
    
    // Custom hook for unified toast notifications across the app
    const { showNotification } = useNotification();

    /**
     * Executes the transformation pipeline.
     * Handles authentication, API communication, and state updates.
     */
    const handleExecutePipeline = useCallback(async (steps) => {
        if (!steps || steps.length === 0) return;

        // 1. UX: Immediate feedback to the user (Optimistic UI)
        setPipelineStatus('EXECUTING');
        showNotification("Applying transformation rules...", "info");

        try {
            // 2. SECURITY: Retrieve current session token for secure backend communication
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) throw new Error("Unauthorized: Session expired.");

            // 3. API CALL: Send the transformation logic to the Flask/Python backend
            const response = await fetch(`${process.env.VITE_API_URL}/api/datasets/${datasetId}/apply-pipeline`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${session.access_token}`, // JWT for security
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ steps })
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || "Pipeline execution failed.");
            }

            // 4. STATE UPDATE: Atomic update of data and history based on backend response
            // Using functional updates to ensure consistency
            setCleaningHistory(prev => [
                ...prev, 
                ...result.execution_details.map(d => ({
                    action: d.action,
                    status: 'success',
                    timestamp: new Date().toISOString()
                }))
            ]);
            
            setPreviewData(result.new_preview_data);
            setPipelineStatus('COMPLETED');
            showNotification("Pipeline executed successfully!", "success");

        } catch (error) {
            // 5. ERROR HANDLING: Graceful degradation
            console.error("Pipeline Error:", error);
            setPipelineStatus('ERROR');
            showNotification(error.message, "error");
        }
    }, [datasetId, showNotification]);

    // --- RENDER LOGIC ---

    if (pipelineStatus === 'EXECUTING') {
        return (
            <Box display="flex" flexDirection="column" alignItems="center" p={4}>
                <CircularProgress size={60} />
                <Typography variant="h6" sx={{ mt: 2 }}>
                    Processing Data...
                </Typography>
                <Typography variant="body2" color="text.secondary">
                    Running Python transformation engine.
                </Typography>
            </Box>
        );
    }

    return (
        <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
                Data Transformation Pipeline
            </Typography>

            {/* Error Feedback */}
            {pipelineStatus === 'ERROR' && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    An error occurred while processing your data. Please try again.
                </Alert>
            )}

            {/* Action Area */}
            <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
                <Button 
                    variant="contained" 
                    color="primary"
                    onClick={() => handleExecutePipeline([{ action: 'remove_duplicates' }])}
                >
                    Run Deduplication
                </Button>
                <Button 
                    variant="outlined" 
                    color="secondary"
                    onClick={() => handleExecutePipeline([{ action: 'impute_nulls', method: 'mean' }])}
                >
                    Impute Missing Values
                </Button>
            </Box>

            {/* Live Data Preview */}
            <Typography variant="subtitle1" fontWeight="bold">
                Live Data Preview (Initial 5 rows)
            </Typography>
            <pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '4px' }}>
                {JSON.stringify(previewData?.slice(0, 5), null, 2)}
            </pre>
        </Paper>
    );
}