/**
 * LegalGuardian AI — Main Application Controller
 * Initializes the app, wires up event listeners, and orchestrates the flow
 */

document.addEventListener('DOMContentLoaded', () => {
    // ─── Initialize ──────────────────────────────────────────────
    UI.cacheElements();
    QA.init();
    Pipeline.init();
    loadDocumentTypes();

    // ─── Event Listeners ─────────────────────────────────────────

    // Step 1: Document type change → populate roles
    UI.elements.docType.addEventListener('change', (e) => {
        const docType = e.target.value;
        const docTypes = UI.elements.docType._docTypes;
        
        if (docTypes && docTypes[docType]) {
            UI.populateRoles(docTypes[docType].roles);
        }
        UI.validateForm();
    });

    // Step 2: Role change → validate form
    UI.elements.userRole.addEventListener('change', () => UI.validateForm());

    // Step 3: Text input → update char count & validate
    UI.elements.contractText.addEventListener('input', () => {
        UI.updateCharCount();
        UI.validateForm();
    });

    // File upload
    UI.elements.fileUpload.addEventListener('change', handleFileUpload);

    // Sample contract buttons
    document.querySelectorAll('.sample-btn').forEach(btn => {
        btn.addEventListener('click', () => loadSampleContract(btn.dataset.sample));
    });

    // Analyze button
    UI.elements.analyzeBtn.addEventListener('click', handleAnalyze);

    // Nav links
    UI.elements.navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section + '-section';
            UI.showSection(section);
        });
    });

    // ─── Functions ───────────────────────────────────────────────

    /** Load document types from API or use fallback */
    async function loadDocumentTypes() {
        try {
            const data = await API.getDocumentTypes();
            UI.elements.docType._docTypes = data.document_types;
            UI.populateDocTypes(data.document_types);
            UI.setStatus('Connected', 'success');
        } catch {
            // Fallback: use hardcoded doc types
            const fallbackTypes = {
                employment_contract: { label: "Employment Contract", roles: { employee: "I am the Employee", employer: "I am the Employer" }},
                rental_agreement: { label: "Rental/Lease Agreement", roles: { tenant: "I am the Tenant", landlord: "I am the Landlord" }},
                freelance_agreement: { label: "Freelance/Service Agreement", roles: { service_provider: "I am the Service Provider", client: "I am the Client" }},
                loan_agreement: { label: "Loan/EMI Agreement", roles: { borrower: "I am the Borrower", lender: "I am the Lender" }},
                nda: { label: "NDA (Non-Disclosure Agreement)", roles: { disclosing_party: "I am the Disclosing Party", receiving_party: "I am the Receiving Party" }},
                insurance_policy: { label: "Insurance Policy", roles: { policyholder: "I am the Policyholder", insurer: "I am the Insurer" }},
                terms_of_service: { label: "Terms of Service", roles: { user: "I am the User", platform: "I am the Platform" }},
                partnership_agreement: { label: "Partnership Agreement", roles: { partner_a: "I am Partner A", partner_b: "I am Partner B" }},
                other: { label: "Other", roles: { general: "General Analysis" }}
            };
            UI.elements.docType._docTypes = fallbackTypes;
            UI.populateDocTypes(fallbackTypes);
            UI.setStatus('Offline Mode', 'error');
        }
    }

    /** Handle file upload */
    function handleFileUpload(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        UI.elements.uploadFilename.textContent = file.name;
        
        // For text files, read and populate textarea
        if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
            const reader = new FileReader();
            reader.onload = (event) => {
                UI.elements.contractText.value = event.target.result;
                UI.updateCharCount();
                UI.validateForm();
            };
            reader.readAsText(file);
        }
    }

    /** Load a sample contract */
    function loadSampleContract(type) {
        const contract = SAMPLE_CONTRACTS[type];
        if (!contract) return;
        
        UI.elements.contractText.value = contract;
        UI.updateCharCount();
        
        // Auto-select document type and first role
        const typeMap = {
            employment: 'employment_contract',
            rental: 'rental_agreement',
            freelance: 'freelance_agreement'
        };
        
        const docTypeKey = typeMap[type];
        if (docTypeKey) {
            UI.elements.docType.value = docTypeKey;
            UI.elements.docType.dispatchEvent(new Event('change'));
            
            // Auto-select the first (vulnerable) role
            setTimeout(() => {
                const roleSelect = UI.elements.userRole;
                if (roleSelect.options.length > 1) {
                    roleSelect.selectedIndex = 1; // First actual role
                    UI.validateForm();
                }
            }, 100);
        }
    }

    /** Handle the analyze button click */
    async function handleAnalyze() {
        const contractText = UI.elements.contractText.value.trim();
        const documentType = UI.elements.docType.value;
        const userRole = UI.elements.userRole.value;
        
        if (!contractText || !documentType || !userRole) return;
        
        // Start loading
        UI.setLoading(true);
        UI.setStatus('Analyzing...', 'loading');
        
        try {
            // Call API
            const data = await API.analyzeContract(contractText, documentType, userRole);
            
            // Render results
            Results.render(data);
            
            // Show results section
            UI.showSection('results-section');
            
            // Enable Q&A
            QA.enable();
            
            // Update status
            UI.setStatus('Analysis Complete', 'success');
            
        } catch (error) {
            console.error('Analysis error:', error);
            UI.showError(error.message || 'Failed to analyze contract. Make sure the backend is running.');
        } finally {
            UI.setLoading(false);
        }
    }
});
