/**
 * LegalGuardian AI — API Communication Layer
 * Handles all fetch calls to the FastAPI backend
 */

const API = {
    /**
     * Analyze a contract (text input)
     */
    async analyzeContract(contractText, documentType, userRole) {
        const response = await fetch(CONFIG.API_BASE + CONFIG.ENDPOINTS.ANALYZE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contract_text: contractText,
                document_type: documentType,
                user_role: userRole
            })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `Analysis failed (${response.status})`);
        }

        return response.json();
    },

    /**
     * Analyze an uploaded file
     */
    async analyzeFile(file, documentType, userRole) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', documentType);
        formData.append('user_role', userRole);

        const response = await fetch(CONFIG.API_BASE + CONFIG.ENDPOINTS.ANALYZE_FILE, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `File analysis failed (${response.status})`);
        }

        return response.json();
    },

    /**
     * Ask a question about the contract
     */
    async askQuestion(contractText, question) {
        const response = await fetch(CONFIG.API_BASE + CONFIG.ENDPOINTS.QA, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contract_text: contractText,
                question: question
            })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `Q&A failed (${response.status})`);
        }

        return response.json();
    },

    /**
     * Fetch available document types
     */
    async getDocumentTypes() {
        const response = await fetch(CONFIG.API_BASE + CONFIG.ENDPOINTS.DOC_TYPES);
        if (!response.ok) throw new Error('Failed to fetch document types');
        return response.json();
    },

    /**
     * Health check
     */
    async healthCheck() {
        try {
            const response = await fetch(CONFIG.API_BASE + CONFIG.ENDPOINTS.HEALTH);
            return response.ok;
        } catch {
            return false;
        }
    }
};
