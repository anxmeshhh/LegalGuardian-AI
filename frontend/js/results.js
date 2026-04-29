/**
 * LegalGuardian AI — Results Renderer
 * Builds the risk dashboard, heatmap, and clause cards from API response
 */

const Results = {
    /** Current analysis data (stored for Q&A context) */
    currentData: null,

    /** Render the full results from an API response */
    render(data) {
        this.currentData = data;
        this.renderDashboard(data.document_summary);
        this.renderDocRecommendations(data.document_summary.document_recommendations);
        this.renderHeatmap(data.clauses);
        this.renderClauseCards(data.clauses);
        this.renderDisclaimer(data.disclaimer);
        this.setupFilters(data.clauses);
    },

    // ─── Risk Dashboard ──────────────────────────────────────────
    
    renderDashboard(summary) {
        const score = summary.overall_risk_score;
        const level = summary.overall_risk_level;
        
        // Animate gauge
        const gaugeFill = document.getElementById('gauge-fill');
        const circumference = 2 * Math.PI * 85; // r=85
        const offset = circumference - (score / 100) * circumference;
        
        setTimeout(() => {
            gaugeFill.style.strokeDashoffset = offset;
            gaugeFill.style.stroke = this.getRiskColor(level);
        }, 100);
        
        // Animate score number
        const gaugeScore = document.getElementById('gauge-score');
        gaugeScore.style.color = this.getRiskColor(level);
        UI.animateNumber(gaugeScore, score, 1500);
        
        // Risk level label
        const riskLevel = document.getElementById('gauge-risk-level');
        riskLevel.textContent = `${level} RISK`;
        riskLevel.style.color = this.getRiskColor(level);
        
        // Update subtitle
        document.getElementById('results-subtitle').textContent = 
            `${summary.document_type} · ${summary.total_clauses} clauses analyzed`;
        
        // Risk stats
        this.updateStat('stat-high', summary.risk_breakdown.high);
        this.updateStat('stat-medium', summary.risk_breakdown.medium);
        this.updateStat('stat-low', summary.risk_breakdown.low);
    },

    updateStat(elementId, count) {
        const el = document.getElementById(elementId);
        const countEl = el.querySelector('.risk-stat-count');
        UI.animateNumber(countEl, count, 1000);
    },

    // ─── Document Recommendations ────────────────────────────────
    
    renderDocRecommendations(recs) {
        const container = document.getElementById('doc-recommendations');
        if (!recs || recs.length === 0) {
            container.style.display = 'none';
            return;
        }
        
        container.style.display = 'block';
        container.innerHTML = '<h3 class="subsection-title">📋 Key Findings & Recommendations</h3>' +
            recs.map(rec => `<div class="doc-rec-item">${rec}</div>`).join('');
    },

    // ─── Heatmap ─────────────────────────────────────────────────
    
    renderHeatmap(clauses) {
        const container = document.getElementById('heatmap');
        container.innerHTML = '';
        
        clauses.forEach((clause, i) => {
            const cell = document.createElement('div');
            cell.className = `heatmap-cell ${clause.risk_level.toLowerCase()}`;
            cell.style.animationDelay = `${i * 0.05}s`;
            cell.innerHTML = `
                §${clause.id}
                <div class="heatmap-tooltip">
                    <strong>${clause.title}</strong><br>
                    ${clause.clause_type} · ${clause.risk_level} (${clause.risk_score}/100)
                </div>
            `;
            // Click to scroll to clause card
            cell.addEventListener('click', () => {
                const card = document.getElementById(`clause-card-${clause.id}`);
                if (card) {
                    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    card.classList.add('expanded');
                    card.style.boxShadow = `0 0 20px ${this.getRiskGlow(clause.risk_level)}`;
                    setTimeout(() => card.style.boxShadow = '', 2000);
                }
            });
            container.appendChild(cell);
        });
    },

    // ─── Clause Cards ────────────────────────────────────────────
    
    renderClauseCards(clauses) {
        const container = document.getElementById('clauses-container');
        container.innerHTML = '';
        
        clauses.forEach((clause, index) => {
            const card = this.createClauseCard(clause);
            card.style.animationDelay = `${index * 0.08}s`;
            container.appendChild(card);
            // Trigger animation
            requestAnimationFrame(() => card.classList.add('animate-in'));
        });
    },

    createClauseCard(clause) {
        const level = clause.risk_level.toLowerCase();
        const card = document.createElement('div');
        card.className = `clause-card ${level}`;
        card.id = `clause-card-${clause.id}`;
        card.dataset.riskLevel = clause.risk_level;
        
        // Add pulse for high-risk
        if (clause.risk_level === 'HIGH') card.classList.add('pulse-risk');
        
        // Header (clickable)
        const header = document.createElement('div');
        header.className = 'clause-header';
        header.innerHTML = `
            <span class="clause-risk-badge ${level}">${clause.risk_level}</span>
            <div class="clause-title-area">
                <div class="clause-title">
                    ${clause.title}
                    ${clause.is_one_sided ? '<span class="one-sided-badge">⚠️ One-Sided</span>' : ''}
                </div>
                <div class="clause-type">${clause.clause_type} · Confidence: ${Math.round(clause.classification_confidence * 100)}%</div>
            </div>
            <span class="clause-score ${level}">${clause.risk_score}</span>
            <span class="clause-expand-icon">▼</span>
        `;
        
        header.addEventListener('click', () => {
            card.classList.toggle('expanded');
        });
        
        // Body (expandable)
        const body = document.createElement('div');
        body.className = 'clause-body';
        body.innerHTML = this.buildClauseBody(clause);
        
        card.appendChild(header);
        card.appendChild(body);
        return card;
    },

    buildClauseBody(clause) {
        let html = '';
        
        // Clause text with highlighted attention words
        let highlightedText = this.escapeHtml(clause.text);
        if (clause.attention_words && clause.attention_words.length > 0) {
            clause.attention_words.forEach(word => {
                const regex = new RegExp(`(${this.escapeRegex(word)})`, 'gi');
                highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
            });
        }
        html += `<div class="clause-text-preview">${highlightedText}</div>`;
        
        // Explanation
        if (clause.explanation) {
            html += `<div class="clause-section-title">Explanation</div>`;
            html += `<div class="clause-explanation">${this.formatExplanation(clause.explanation)}</div>`;
        }
        
        // Key terms
        if (clause.key_terms && clause.key_terms.length > 0) {
            html += `<div class="clause-section-title">Key Legal Terms</div>`;
            html += `<div class="key-terms-list">`;
            clause.key_terms.forEach(term => {
                html += `
                    <span class="key-term">
                        📘 ${term.term}
                        <span class="key-term-tooltip">
                            <strong>${term.term}</strong><br>
                            ${term.plain_english}<br>
                            <em style="color: var(--risk-medium);">${term.risk_note}</em>
                        </span>
                    </span>
                `;
            });
            html += `</div>`;
        }
        
        // Risk factors
        if (clause.risk_factors && clause.risk_factors.length > 0) {
            html += `<div class="clause-section-title">Risk Factors</div>`;
            clause.risk_factors.forEach(factor => {
                html += `<div class="clause-rec">${factor}</div>`;
            });
        }
        
        // Recommendations
        if (clause.recommendations && clause.recommendations.length > 0) {
            html += `<div class="clause-section-title">Recommendations</div>`;
            clause.recommendations.forEach(rec => {
                html += `<div class="clause-rec">${rec}</div>`;
            });
        }
        
        return html;
    },

    // ─── Filters ─────────────────────────────────────────────────
    
    setupFilters(clauses) {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active state
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const filter = btn.dataset.filter;
                document.querySelectorAll('.clause-card').forEach(card => {
                    if (filter === 'all' || card.dataset.riskLevel === filter) {
                        card.style.display = '';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    },

    // ─── Disclaimer ──────────────────────────────────────────────
    
    renderDisclaimer(text) {
        document.getElementById('disclaimer').textContent = text;
    },

    // ─── Helpers ─────────────────────────────────────────────────
    
    getRiskColor(level) {
        const colors = { HIGH: '#ef4444', MEDIUM: '#f59e0b', LOW: '#22c55e' };
        return colors[level] || '#94a3b8';
    },

    getRiskGlow(level) {
        const glows = {
            HIGH: 'rgba(239, 68, 68, 0.3)',
            MEDIUM: 'rgba(245, 158, 11, 0.3)',
            LOW: 'rgba(34, 197, 94, 0.3)'
        };
        return glows[level] || 'transparent';
    },

    formatExplanation(text) {
        // Convert markdown-like bold to HTML
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n•/g, '<br>•');
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
};
