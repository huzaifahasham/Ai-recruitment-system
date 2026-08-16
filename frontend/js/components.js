const Components = {
    renderRecommendationBadge(recommendation) {
        if (!recommendation) return '<span class="badge info">Pending</span>';
        switch (recommendation) {
            case 'Strong Match':
                return '<span class="badge strong">★ Strong Match</span>';
            case 'Potential Match':
                return '<span class="badge potential">✓ Potential Match</span>';
            case 'Needs HR Review':
                return '<span class="badge review">! Needs Review</span>';
            case 'Low Match':
                return '<span class="badge low">✕ Low Match</span>';
            default:
                return `<span class="badge info">${recommendation}</span>`;
        }
    },

    renderStatusPill(status) {
        switch (status) {
            case 'PROCESSED':
                return '<span class="badge success">Processed</span>';
            case 'PROCESSING':
                return '<span class="badge info">Processing...</span>';
            case 'UPLOADED':
                return '<span class="badge info">Uploaded</span>';
            case 'FAILED':
                return '<span class="badge low">Failed</span>';
            default:
                return `<span class="badge">${status}</span>`;
        }
    },

    renderCandidateTableRow(c, isCompact = false) {
        const domain = c.primary_domain || 'Pending Analysis';
        const confidence = c.primary_confidence ? `${c.primary_confidence}%` : '-';
        const score = c.screening_score !== null && c.screening_score !== undefined ? `${c.screening_score}/100` : '-';
        const recBadge = Components.renderRecommendationBadge(c.recommendation);
        const statusBadge = Components.renderStatusPill(c.status);
        const dateStr = c.created_at ? new Date(c.created_at).toLocaleDateString() : '-';

        if (isCompact) {
            return `
                <tr>
                    <td class="fw-600">${c.name}</td>
                    <td><span class="tech-tag">${domain}</span></td>
                    <td>${confidence}</td>
                    <td><strong>${score}</strong></td>
                    <td>${recBadge}</td>
                    <td>${statusBadge}</td>
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick="App.openCandidateModal('${c.id}')">View</button>
                    </td>
                </tr>
            `;
        }

        return `
            <tr>
                <td class="fw-600">${c.name}</td>
                <td class="text-secondary">${c.email}</td>
                <td><span class="tech-tag">${domain}</span></td>
                <td>${confidence}</td>
                <td><strong>${score}</strong></td>
                <td>${recBadge}</td>
                <td>${statusBadge}</td>
                <td>${dateStr}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="App.openCandidateModal('${c.id}')">Profile</button>
                </td>
            </tr>
        `;
    },

    renderCandidateModalContent(c) {
        const domainInfo = c.domain_classification || {};
        const screeningInfo = c.screening_result || {};
        const primaryDomain = domainInfo.primary_domain || 'Unclassified';
        const confidence = domainInfo.primary_confidence || 0;
        const evidenceList = domainInfo.evidence || [];
        const secondaryDomains = domainInfo.secondary_domains || [];

        const skillsTags = c.skills.map(s => `<span class="tech-tag">${s.skill_name}</span>`).join(' ');

        const evidenceItems = evidenceList.length > 0 
            ? evidenceList.map(e => `<li class="evidence-item"><span class="evidence-bullet">•</span> <span>${e}</span></li>`).join('')
            : '<li class="evidence-item">General technical competencies extracted.</li>';

        const secondaryItems = secondaryDomains.map(s => 
            `<div class="flex-between mt-2" style="font-size: 0.88rem;"><span>${s.domain}</span><strong style="color:#38BDF8;">${s.confidence}%</strong></div>`
        ).join('');

        const eduHtml = c.education.length > 0
            ? c.education.map(e => `<p style="margin-bottom:0.4rem;"><strong>${e.degree}</strong> - ${e.institution} (${e.year})</p>`).join('')
            : '<p class="text-secondary">Not Provided</p>';

        const expHtml = c.experience.length > 0
            ? c.experience.map(ex => `<div style="margin-bottom:0.6rem;"><strong>${ex.role}</strong> at ${ex.company} (${ex.duration})<p class="text-secondary" style="font-size:0.85rem;">${ex.description}</p></div>`).join('')
            : '<p class="text-secondary">Not Provided</p>';

        const projHtml = c.projects.length > 0
            ? c.projects.map(p => `<div style="margin-bottom:0.5rem;"><strong>${p.title}</strong><p class="text-secondary" style="font-size:0.85rem;">${p.description}</p></div>`).join('')
            : '<p class="text-secondary">Not Provided</p>';

        const certHtml = c.certifications.length > 0
            ? c.certifications.map(cert => `<span class="tech-tag" style="background:rgba(16,185,129,0.15); color:#34D399;">${cert.title}</span> `).join('')
            : '<p class="text-secondary">Not Provided</p>';

        return `
            <div class="detail-grid">
                <!-- Left Column: Classification & AI Screening -->
                <div style="display:flex; flex-direction:column; gap:1.25rem;">
                    <!-- Domain Card -->
                    <div class="detail-box">
                        <div class="flex-between">
                            <span class="card-subtitle">PRIMARY DOMAIN CLASSIFICATION</span>
                            <span class="badge info">${confidence}% Confidence</span>
                        </div>
                        <h3 style="font-size:1.4rem; font-family:'Outfit'; margin-top:0.4rem; color:#38BDF8;">${primaryDomain}</h3>

                        <div style="margin-top:1rem;">
                            <span class="card-subtitle">TOP 3 ALTERNATIVE DOMAINS</span>
                            ${secondaryItems || '<p class="text-secondary">None</p>'}
                        </div>
                    </div>

                    <!-- Evidence Card -->
                    <div class="detail-box">
                        <span class="card-subtitle">SUPPORTING EVIDENCE</span>
                        <ul class="evidence-list">
                            ${evidenceItems}
                        </ul>
                    </div>

                    <!-- AI Screening Summary Card -->
                    <div class="detail-box">
                        <span class="card-subtitle">AI PRELIMINARY SCREENING SUMMARY</span>
                        <p style="font-size:0.9rem; margin-top:0.5rem; line-height:1.5;">${screeningInfo.summary || 'Summary unavailable.'}</p>
                    </div>
                </div>

                <!-- Right Column: Scores & Recommendation -->
                <div style="display:flex; flex-direction:column; gap:1.25rem;">
                    <div class="detail-box score-display">
                        <span class="card-subtitle">AI PRELIMINARY SCREENING SCORE</span>
                        <div class="score-number">${screeningInfo.screening_score || 0}<span style="font-size:1.5rem;">/100</span></div>
                        <div style="margin-top:0.75rem;">
                            ${Components.renderRecommendationBadge(screeningInfo.recommendation)}
                        </div>
                    </div>

                    <div class="detail-box">
                        <span class="card-subtitle">CANDIDATE DETAILS</span>
                        <p style="font-size:0.88rem; margin-top:0.5rem;"><strong>Phone:</strong> ${c.phone}</p>
                        <p style="font-size:0.88rem; margin-top:0.3rem;"><strong>Location:</strong> ${c.location}</p>
                        <p style="font-size:0.88rem; margin-top:0.3rem;"><strong>Experience:</strong> ${c.years_of_experience} Years</p>
                        <p style="font-size:0.88rem; margin-top:0.3rem;"><strong>CV File:</strong> ${c.cv_filename}</p>
                        <div style="margin-top:1rem;">
                            <a href="/api/candidates/${c.id}/cv" target="_blank" class="btn btn-secondary btn-sm">Download Original CV</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Full Profile Sections -->
            <div class="detail-box mt-4">
                <h4 style="margin-bottom:0.5rem;">Identified Skills (${c.skills.length})</h4>
                <div class="tech-tags">${skillsTags || 'Not Provided'}</div>
            </div>

            <div class="detail-grid mt-4">
                <div class="detail-box">
                    <h4 style="margin-bottom:0.5rem;">Education</h4>
                    ${eduHtml}
                </div>
                <div class="detail-box">
                    <h4 style="margin-bottom:0.5rem;">Certifications</h4>
                    ${certHtml}
                </div>
            </div>

            <div class="detail-grid mt-4">
                <div class="detail-box">
                    <h4 style="margin-bottom:0.5rem;">Work Experience</h4>
                    ${expHtml}
                </div>
                <div class="detail-box">
                    <h4 style="margin-bottom:0.5rem;">Key Projects</h4>
                    ${projHtml}
                </div>
            </div>

            <div class="disclaimer-box">
                <strong>Disclaimer:</strong> This result is an <strong>AI-assisted preliminary screening recommendation</strong>. The AI does not make final hiring decisions. HR heads are advised to conduct comprehensive manual interviews before finalizing recruitment decisions.
            </div>
        `;
    }
};
