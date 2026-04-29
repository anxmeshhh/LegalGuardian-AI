/**
 * LegalGuardian AI — Pipeline Demo Controller
 * Interactive visualization of the NLP processing pipeline
 */

const Pipeline = {
    /** Pipeline step definitions */
    steps: [
        {
            id: 'input',
            icon: '📄',
            name: 'Smart Input',
            detail: 'Document Type + User Role + Contract Text',
            description: `
                <p>The user provides <strong>3 simple inputs</strong> — two clicks and one paste:</p>
                <p><strong>1. Document Type</strong> — What kind of contract (Employment, Rental, Freelance, etc.)</p>
                <p><strong>2. User Role</strong> — Which party you are (Employee vs. Employer, Tenant vs. Landlord)</p>
                <p><strong>3. Contract Text</strong> — Paste text or upload PDF/DOCX file</p>
                <br>
                <p>These two extra inputs enable <strong>personalized, role-aware analysis</strong> — the same clause gets different risk scores depending on which party you represent.</p>
                <div style="margin-top:8px;">
                    <span class="tech-tag">PDF Parser</span>
                    <span class="tech-tag">DOCX Parser</span>
                    <span class="tech-tag">Text Input</span>
                </div>
            `
        },
        {
            id: 'preprocess',
            icon: '🔧',
            name: 'Preprocessing',
            detail: 'Text Extraction + Clause Segmentation',
            description: `
                <p>The raw contract text goes through <strong>cleaning and segmentation</strong>:</p>
                <p>• <strong>Text Extraction</strong> — Extract clean text from PDF (PyMuPDF) or DOCX (python-docx)</p>
                <p>• <strong>Noise Removal</strong> — Strip page numbers, headers, excessive whitespace</p>
                <p>• <strong>Clause Segmentation</strong> — Split the contract into individual clauses using:</p>
                <p>&nbsp;&nbsp;→ Section header detection (regex: "Section X", "Article X")</p>
                <p>&nbsp;&nbsp;→ Paragraph-level fallback for unstructured text</p>
                <br>
                <p>A 12-page contract typically produces <strong>10–20 individual clauses</strong> for analysis.</p>
                <div style="margin-top:8px;">
                    <span class="tech-tag">PyMuPDF</span>
                    <span class="tech-tag">python-docx</span>
                    <span class="tech-tag">Regex</span>
                    <span class="tech-tag">spaCy</span>
                </div>
            `
        },
        {
            id: 'classify',
            icon: '🏷️',
            name: 'Clause Classification',
            detail: '41 CUAD Categories via Legal-BERT',
            description: `
                <p>Each clause is classified into one of <strong>41 CUAD (Contract Understanding Atticus Dataset) categories</strong>:</p>
                <p>• Indemnification, Non-Compete, Termination, IP Assignment, Liability Limitation, etc.</p>
                <br>
                <p><strong>Dual-mode classifier:</strong></p>
                <p>• <strong>Primary:</strong> Keyword-based classification using 400+ legal phrase patterns — works instantly, no model download</p>
                <p>• <strong>Upgrade:</strong> Fine-tuned <code>Legal-BERT</code> (nlpaueb/legal-bert-small-uncased) for higher accuracy</p>
                <br>
                <p>Each classification includes a <strong>confidence score</strong> and matched keywords for transparency.</p>
                <div style="margin-top:8px;">
                    <span class="tech-tag">Legal-BERT</span>
                    <span class="tech-tag">CUAD Dataset</span>
                    <span class="tech-tag">NLP Classification</span>
                </div>
            `
        },
        {
            id: 'risk',
            icon: '⚠️',
            name: 'Role-Aware Risk Scoring',
            detail: 'Personalized risk based on your role',
            description: `
                <p>Risk scoring is the <strong>key innovation</strong> — the same clause gets <strong>different risk scores</strong> depending on your role:</p>
                <br>
                <p>Example: <em>"Termination for Convenience"</em> clause</p>
                <p>&nbsp;&nbsp;🔴 As <strong>Employee</strong>: HIGH RISK (score: 85) — "They can fire you anytime"</p>
                <p>&nbsp;&nbsp;🟢 As <strong>Employer</strong>: LOW RISK (score: 20) — "You retain flexibility"</p>
                <br>
                <p>Risk is computed from <strong>3 factors</strong>:</p>
                <p>• Base risk — inherent clause type severity</p>
                <p>• Role modifier — how it affects YOUR position</p>
                <p>• Text amplifiers — words like "unlimited", "irrevocable", "sole discretion"</p>
                <div style="margin-top:8px;">
                    <span class="tech-tag">Role-Aware Engine</span>
                    <span class="tech-tag">Risk Amplifiers</span>
                    <span class="tech-tag">One-Sidedness Detection</span>
                </div>
            `
        },
        {
            id: 'explain',
            icon: '📖',
            name: 'Explanation Generator',
            detail: 'Plain-English + Legal Dictionary',
            description: `
                <p>Every clause gets a <strong>plain-English explanation</strong> personalized to your role:</p>
                <br>
                <p>• ⚠️ <strong>Risk indicator</strong> — HIGH / MEDIUM / LOW with color coding</p>
                <p>• 📖 <strong>What it means</strong> — Clause type description in simple language</p>
                <p>• 👤 <strong>Impact on YOU</strong> — Role-specific consequences</p>
                <p>• 🔍 <strong>Key concerns</strong> — Duration, financial penalties, one-sidedness</p>
                <p>• 📘 <strong>Legal terms</strong> — Dictionary lookup with definitions and risk notes</p>
                <br>
                <p>Uses a curated <strong>legal dictionary of 30+ terms</strong> with plain-English translations.</p>
                <div style="margin-top:8px;">
                    <span class="tech-tag">Legal Dictionary</span>
                    <span class="tech-tag">Role Templates</span>
                    <span class="tech-tag">Pattern Extraction</span>
                </div>
            `
        },
        {
            id: 'output',
            icon: '📊',
            name: 'Risk Dashboard',
            detail: 'Visual report + Q&A panel',
            description: `
                <p>The final output is a <strong>comprehensive, interactive risk report</strong>:</p>
                <br>
                <p>• 🎯 <strong>Overall Risk Score</strong> — Animated gauge (0–100) with weighted aggregation</p>
                <p>• 🗺️ <strong>Clause Heatmap</strong> — Color-coded overview of all clauses</p>
                <p>• 📋 <strong>Clause Cards</strong> — Expandable cards with full explanation, key terms, and recommendations</p>
                <p>• 💡 <strong>Actionable Recommendations</strong> — What to negotiate, what to watch for</p>
                <p>• 💬 <strong>Interactive Q&A</strong> — Ask questions about the contract using BERT-based extractive QA</p>
                <br>
                <p>High-risk clauses are <strong>highlighted with pulse animations</strong> and attention words are <strong>marked in the text</strong>.</p>
                <div style="margin-top:8px;">
                    <span class="tech-tag">Risk Gauge</span>
                    <span class="tech-tag">Heatmap</span>
                    <span class="tech-tag">BERT Q&A</span>
                    <span class="tech-tag">Flask API</span>
                </div>
            `
        }
    ],

    currentStep: 0,
    autoPlayInterval: null,
    isPlaying: false,

    /** Initialize the pipeline demo */
    init() {
        this.renderSteps();
        this.selectStep(0);
        this.bindEvents();
    },

    /** Render pipeline step cards */
    renderSteps() {
        const flow = document.getElementById('pipeline-flow');
        if (!flow) return;
        flow.innerHTML = '';

        this.steps.forEach((step, i) => {
            // Step card
            const stepEl = document.createElement('div');
            stepEl.className = 'pipeline-step';
            stepEl.innerHTML = `
                <div class="pipeline-step-card" data-step="${i}">
                    <span class="step-badge">${i + 1}</span>
                    <span class="step-icon">${step.icon}</span>
                    <span class="step-name">${step.name}</span>
                    <span class="step-detail">${step.detail}</span>
                </div>
            `;
            flow.appendChild(stepEl);

            // Arrow (except after last step)
            if (i < this.steps.length - 1) {
                const arrow = document.createElement('div');
                arrow.className = 'pipeline-arrow';
                arrow.dataset.after = i;
                flow.appendChild(arrow);
            }
        });
    },

    /** Select and highlight a step */
    selectStep(index) {
        this.currentStep = index;
        const step = this.steps[index];

        // Update step cards
        document.querySelectorAll('.pipeline-step-card').forEach((card, i) => {
            card.classList.remove('active', 'completed');
            if (i === index) card.classList.add('active');
            else if (i < index) card.classList.add('completed');
        });

        // Update arrows
        document.querySelectorAll('.pipeline-arrow').forEach((arrow, i) => {
            arrow.classList.remove('active', 'completed');
            if (i < index) arrow.classList.add('completed');
            else if (i === index - 1) arrow.classList.add('active');
        });

        // Update detail panel
        const detail = document.getElementById('pipeline-detail');
        if (detail) {
            detail.innerHTML = `
                <div class="pipeline-detail-header">
                    <span class="pipeline-detail-icon">${step.icon}</span>
                    <span class="pipeline-detail-title">Stage ${index + 1}: ${step.name}</span>
                </div>
                <div class="pipeline-detail-body">${step.description}</div>
            `;
        }
    },

    /** Bind click and autoplay events */
    bindEvents() {
        // Click on step cards
        document.addEventListener('click', (e) => {
            const card = e.target.closest('.pipeline-step-card');
            if (card) {
                const stepIndex = parseInt(card.dataset.step);
                this.selectStep(stepIndex);
                this.stopAutoPlay();
            }
        });

        // Auto-play button
        const playBtn = document.getElementById('pipeline-play-btn');
        if (playBtn) {
            playBtn.addEventListener('click', () => this.toggleAutoPlay());
        }
    },

    /** Toggle auto-play through steps */
    toggleAutoPlay() {
        if (this.isPlaying) {
            this.stopAutoPlay();
        } else {
            this.startAutoPlay();
        }
    },

    startAutoPlay() {
        const btn = document.getElementById('pipeline-play-btn');
        this.isPlaying = true;
        if (btn) {
            btn.classList.add('playing');
            btn.innerHTML = '⏸ Pause Demo';
        }

        this.selectStep(0);
        this.autoPlayInterval = setInterval(() => {
            const next = (this.currentStep + 1) % this.steps.length;
            this.selectStep(next);
            if (next === 0) this.stopAutoPlay();  // Stop after full cycle
        }, 3000);
    },

    stopAutoPlay() {
        const btn = document.getElementById('pipeline-play-btn');
        this.isPlaying = false;
        if (btn) {
            btn.classList.remove('playing');
            btn.innerHTML = '▶ Play Pipeline Demo';
        }
        if (this.autoPlayInterval) {
            clearInterval(this.autoPlayInterval);
            this.autoPlayInterval = null;
        }
    }
};
