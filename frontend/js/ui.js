/**
 * LegalGuardian AI — UI Utilities
 * DOM helpers, status updates, navigation, and form management
 */

const UI = {
    // ─── DOM References ──────────────────────────────────────────
    elements: {},

    /** Cache frequently used DOM elements */
    cacheElements() {
        this.elements = {
            // Input
            docType: document.getElementById('document-type'),
            userRole: document.getElementById('user-role'),
            contractText: document.getElementById('contract-text'),
            analyzeBtn: document.getElementById('analyze-btn'),
            fileUpload: document.getElementById('file-upload'),
            uploadFilename: document.getElementById('upload-filename'),
            charCount: document.getElementById('char-count'),
            // Sections
            inputSection: document.getElementById('input-section'),
            resultsSection: document.getElementById('results-section'),
            qaSection: document.getElementById('qa-section'),
            // Nav
            navStatus: document.getElementById('nav-status'),
            navLinks: document.querySelectorAll('.nav-link'),
        };
    },

    // ─── Navigation ──────────────────────────────────────────────
    
    /** Show a specific section and update nav */
    showSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
        
        // Show target section
        const target = document.getElementById(sectionId);
        if (target) {
            target.classList.remove('hidden');
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        // Update nav links
        this.elements.navLinks.forEach(link => {
            link.classList.toggle('active', link.dataset.section === sectionId.replace('-section', ''));
        });
    },

    // ─── Status Updates ──────────────────────────────────────────
    
    /** Update the navbar status indicator */
    setStatus(text, state = 'ready') {
        const statusEl = this.elements.navStatus;
        if (!statusEl) return;
        
        const dot = statusEl.querySelector('.status-dot');
        const label = statusEl.querySelector('.status-text');
        
        label.textContent = text;
        
        const colors = {
            ready: 'var(--risk-low)',
            loading: 'var(--risk-medium)',
            error: 'var(--risk-high)',
            success: 'var(--accent-primary)'
        };
        dot.style.background = colors[state] || colors.ready;
    },

    // ─── Form Management ─────────────────────────────────────────
    
    /** Populate document type dropdown */
    populateDocTypes(docTypes) {
        const select = this.elements.docType;
        select.innerHTML = '<option value="" disabled selected>Select document type...</option>';
        
        Object.entries(docTypes).forEach(([key, val]) => {
            const opt = document.createElement('option');
            opt.value = key;
            opt.textContent = val.label;
            select.appendChild(opt);
        });
    },

    /** Populate role dropdown based on selected doc type */
    populateRoles(roles) {
        const select = this.elements.userRole;
        select.innerHTML = '<option value="" disabled selected>Select your role...</option>';
        
        Object.entries(roles).forEach(([key, val]) => {
            const opt = document.createElement('option');
            opt.value = key;
            opt.textContent = val;
            select.appendChild(opt);
        });
        
        select.disabled = false;
    },

    /** Update character count display */
    updateCharCount() {
        const text = this.elements.contractText.value;
        this.elements.charCount.textContent = `${text.length.toLocaleString()} characters`;
    },

    /** Check if the form is ready to submit */
    validateForm() {
        const hasDocType = this.elements.docType.value;
        const hasRole = this.elements.userRole.value;
        const hasText = this.elements.contractText.value.trim().length >= 50;
        
        this.elements.analyzeBtn.disabled = !(hasDocType && hasRole && hasText);
    },

    /** Set analyze button loading state */
    setLoading(isLoading) {
        const btn = this.elements.analyzeBtn;
        if (isLoading) {
            btn.classList.add('loading');
            btn.disabled = true;
        } else {
            btn.classList.remove('loading');
            this.validateForm();
        }
    },

    /** Show error notification */
    showError(message) {
        // Simple alert for now — could be upgraded to toast
        this.setStatus('Error', 'error');
        alert(`❌ ${message}`);
    },

    /** Animate a number counting up */
    animateNumber(element, target, duration = 1000) {
        const start = 0;
        const startTime = performance.now();
        
        const update = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(start + (target - start) * eased);
            
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        };
        
        requestAnimationFrame(update);
    }
};
