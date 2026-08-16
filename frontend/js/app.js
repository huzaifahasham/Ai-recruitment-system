/* 
   app.js — Frontend Application Logic for AI Recruitment System
*/

let currentInterviewToken = null;
let currentInterviewQuestions = [];
let timerInterval = null;
let remainingSeconds = 600; // 10 minutes

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkHashRoute();
    window.addEventListener('hashchange', checkHashRoute);

    // Update file input name indicator
    const fileInput = document.getElementById('cv-file-input');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const fileName = e.target.files[0]?.name || 'Choose CV PDF file...';
            document.getElementById('file-name-text').textContent = fileName;
        });
    }
});

// Hash-based Simple Router
function checkHashRoute() {
    const hash = window.location.hash;
    const topNav = document.querySelector('.top-nav');

    if (hash.startsWith('#interview/')) {
        const token = hash.replace('#interview/', '');
        
        // ISOLATE CANDIDATE VIEW: Hide HR navbar & dashboard
        if (topNav) topNav.style.display = 'none';
        
        showView('interview');
        openCandidateInterviewPage(token);
    } else {
        // Show HR navbar for HR admin
        if (topNav) topNav.style.display = 'block';
        
        showView('dashboard');
        loadDashboardStats();
        loadCandidates();
    }
}

// Switch between HR Dashboard & Candidate Interview View
function showView(viewName) {
    document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

    if (viewName === 'dashboard') {
        document.getElementById('dashboard-view').classList.add('active');
        document.getElementById('nav-dashboard').classList.add('active');
    } else if (viewName === 'interview') {
        document.getElementById('interview-view').classList.add('active');
    }
}

// Load Dashboard Statistics
async function loadDashboardStats() {
    try {
        const res = await fetch('/api/dashboard/stats');
        if (res.ok) {
            const data = await res.json();
            document.getElementById('stat-total').textContent = data.total;
            document.getElementById('stat-pending').textContent = data.pending;
            document.getElementById('stat-passed').textContent = data.passed;
            document.getElementById('stat-failed').textContent = data.failed;
        }
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

// Load Candidate Table Records
async function loadCandidates() {
    const tbody = document.getElementById('candidates-tbody');
    try {
        const res = await fetch('/api/candidates');
        const candidates = await res.json();

        if (!candidates || candidates.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; color: #64748b; padding: 24px;">
                        No candidate records found. Click <strong>"Screen CV with Agent 1"</strong> above or <strong>"Load Demo Candidates"</strong> to test!
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = candidates.map(c => {
            const status = c.status || 'Pending';
            let badgeClass = 'badge-pending';
            if (status.includes('Generated')) badgeClass = 'badge-generated';
            if (status.includes('Sent')) badgeClass = 'badge-sent';
            if (status.includes('Passed')) badgeClass = 'badge-pass';
            if (status.includes('Failed')) badgeClass = 'badge-fail';

            const scoreDisplay = (c.interview_score !== null && c.interview_score !== undefined) 
                ? `<strong>${c.interview_score}</strong>/100` 
                : '-';

            // Action Buttons
            let actionButtons = '';
            
            if (status === 'Pending') {
                actionButtons = `
                    <button class="btn btn-primary btn-sm" onclick="generateInterview(${c.id})">
                        <i class="fa-solid fa-gears"></i> Generate Interview (Agent 2)
                    </button>
                `;
            } else if (status === 'Interview Generated') {
                actionButtons = `
                    <button class="btn btn-warning btn-sm" onclick="sendInterviewLinkEmail(${c.id})">
                        <i class="fa-solid fa-paper-plane"></i> Send Link Email
                    </button>
                    ${c.interview_token ? `
                        <a href="/#interview/${c.interview_token}" target="_blank" class="btn btn-secondary btn-sm">
                            <i class="fa-solid fa-arrow-up-right-from-square"></i> Open Interview
                        </a>
                    ` : ''}
                `;
            } else if (status === 'Interview Sent') {
                actionButtons = `
                    <a href="/#interview/${c.interview_token}" target="_blank" class="btn btn-secondary btn-sm">
                        <i class="fa-solid fa-arrow-up-right-from-square"></i> Open Interview
                    </a>
                `;
            } else if (status.includes('Passed')) {
                actionButtons = `
                    <button class="btn btn-success btn-sm" onclick="sendFinalEmail(${c.id})">
                        <i class="fa-solid fa-envelope-circle-check"></i> Send Final Interview Email
                    </button>
                `;
            } else if (status.includes('Failed')) {
                actionButtons = `
                    <span style="font-size: 0.8rem; color: #ef4444; font-weight: 500;">
                        <i class="fa-solid fa-ban"></i> Not Selected
                    </span>
                `;
            }

            return `
                <tr>
                    <td class="cand-name">${escapeHtml(c.name)}</td>
                    <td>${escapeHtml(c.email)}</td>
                    <td>${escapeHtml(c.phone)}</td>
                    <td>${renderSkills(c.skills)}</td>
                    <td>${escapeHtml(c.experience)}</td>
                    <td><span class="badge ${badgeClass}">${escapeHtml(status)}</span></td>
                    <td>${scoreDisplay}</td>
                    <td>
                        <div style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap;">
                            <button class="btn btn-secondary btn-sm" onclick="viewCandidateModal(${c.id})">
                                <i class="fa-solid fa-eye"></i> Details
                            </button>
                            ${actionButtons}
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

    } catch (err) {
        console.error('Error loading candidates:', err);
        tbody.innerHTML = `<tr><td colspan="8" style="color:red; text-align:center;">Failed to load candidate records.</td></tr>`;
    }
}

// AGENT 1: Handle CV Upload
async function handleCVUpload(event) {
    event.preventDefault();
    const fileInput = document.getElementById('cv-file-input');
    const uploadBtn = document.getElementById('upload-btn');

    if (!fileInput.files[0]) {
        alert('Please select a PDF CV file to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    uploadBtn.disabled = true;
    uploadBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Agent 1 Screening CV...`;

    try {
        const res = await fetch('/api/upload-cv', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if (res.ok) {
            alert(`Success! Agent 1 extracted CV details for ${data.candidate.name}`);
            fileInput.value = '';
            document.getElementById('file-name-text').textContent = 'Choose CV PDF file...';
            loadCandidates();
            loadDashboardStats();
        } else {
            alert(`Upload Error: ${data.detail || 'Failed to process CV.'}`);
        }
    } catch (err) {
        alert(`Error uploading file: ${err.message}`);
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = `<i class="fa-solid fa-bolt"></i> Screen CV with Agent 1`;
    }
}

// AGENT 2: Generate 10 Questions
async function generateInterview(candidateId) {
    if (!confirm('Generate 10 tailored interview questions using Agent 2?')) return;

    try {
        const res = await fetch(`/api/candidates/${candidateId}/generate-interview`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            alert('Success! Agent 2 generated 10 interview questions and unique link.');
            loadCandidates();
            loadDashboardStats();
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (err) {
        alert(`Failed to generate interview: ${err.message}`);
    }
}

// EMAIL 1: Send Interview Link Email
async function sendInterviewLinkEmail(candidateId) {
    try {
        const res = await fetch(`/api/candidates/${candidateId}/send-interview-email`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            loadCandidates();
            loadDashboardStats();

            const details = data.email_details || {};
            const link = data.interview_link;

            const modalBody = document.getElementById('sent-success-body');
            modalBody.innerHTML = `
                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <div style="font-weight: 700; color: #166534; font-size: 1rem;">
                        <i class="fa-solid fa-circle-check"></i> Interview Link Email Generated
                    </div>
                    <div style="font-size: 0.88rem; color: #15803d; margin-top: 4px;">
                        <strong>Recipient:</strong> ${escapeHtml(details.recipient || 'Candidate')} <br>
                        <strong>Status:</strong> ${escapeHtml(details.delivery_status || 'Sent')}
                    </div>
                </div>

                <p style="font-size: 0.9rem; color: #475569; margin-bottom: 16px;">
                    The interview invitation email has been processed. The candidate can open the test by clicking the link below:
                </p>

                <div style="text-align: center; margin: 20px 0;">
                    <a href="${link}" target="_blank" class="btn btn-success btn-lg" style="text-decoration: none; font-size: 1rem; padding: 12px 20px;">
                        <i class="fa-solid fa-arrow-up-right-from-square"></i> Open Candidate Interview Test
                    </a>
                </div>

                <div style="font-size: 0.8rem; background: #f8fafc; padding: 10px; border-radius: 6px; border: 1px solid #e2e8f0; word-break: break-all;">
                    <strong>Interview Link URL:</strong><br>
                    <a href="${link}" target="_blank" style="color: #2563eb;">${link}</a>
                </div>
            `;

            openModal('sent-success-modal');

        } else {
            alert(`Email error: ${data.detail}`);
        }
    } catch (err) {
        alert(`Failed to send email: ${err.message}`);
    }
}

// AGENT 3: Send Final Interview Email
async function sendFinalEmail(candidateId) {
    try {
        const res = await fetch(`/api/candidates/${candidateId}/send-final-email`, { method: 'POST' });
        const data = await res.json();
        if (res.ok) {
            alert('Success! Agent 3 sent the Final Interview Invitation email to the candidate.');
            openEmailLogsModal();
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (err) {
        alert(`Failed to send final email: ${err.message}`);
    }
}

// SMTP Settings Functions
async function openSmtpModal() {
    openModal('smtp-modal');
    const msg = document.getElementById('smtp-status-msg');
    msg.textContent = 'Loading current settings...';
    msg.style.color = '#64748b';

    try {
        const res = await fetch('/api/smtp-config');
        const data = await res.json();
        document.getElementById('smtp-server-input').value = data.server || '';
        document.getElementById('smtp-port-input').value = data.port || 587;
        document.getElementById('smtp-user-input').value = data.user || '';
        
        if (data.is_configured) {
            msg.textContent = `✓ Active SMTP Configured (${data.user} via ${data.server})`;
            msg.style.color = '#10b981';
        } else {
            msg.textContent = 'ℹ Mock Email Mode Active (Configure real SMTP below to send live emails to inbox)';
            msg.style.color = '#d97706';
        }
    } catch (err) {
        msg.textContent = 'Could not load SMTP settings.';
    }
}

async function saveSmtpSettings(event) {
    event.preventDefault();
    const server = document.getElementById('smtp-server-input').value.trim();
    const port = parseInt(document.getElementById('smtp-port-input').value.trim()) || 587;
    const user = document.getElementById('smtp-user-input').value.trim();
    const password = document.getElementById('smtp-pass-input').value.trim();

    const msg = document.getElementById('smtp-status-msg');
    msg.textContent = 'Saving settings...';

    try {
        const res = await fetch('/api/smtp-config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ server, port, user, password })
        });
        const data = await res.json();

        if (res.ok) {
            msg.textContent = '✓ SMTP Settings saved successfully! Real emails will now be sent via SMTP.';
            msg.style.color = '#10b981';
        } else {
            msg.textContent = `Error: ${data.detail}`;
            msg.style.color = '#ef4444';
        }
    } catch (err) {
        msg.textContent = `Failed to save: ${err.message}`;
        msg.style.color = '#ef4444';
    }
}

// OPEN CANDIDATE INTERVIEW PAGE (ISOLATED VIEW WITH 10 MIN TIMER)
async function openCandidateInterviewPage(token) {
    showView('interview');
    currentInterviewToken = token;

    const form = document.getElementById('interview-form');
    const resultCard = document.getElementById('interview-result-card');
    const qContainer = document.getElementById('questions-container');

    form.classList.remove('hidden');
    resultCard.classList.add('hidden');
    qContainer.innerHTML = '<div style="text-align:center; padding:30px;"><i class="fa-solid fa-spinner fa-spin fa-2x"></i><br><br>Loading candidate assessment...</div>';

    try {
        const res = await fetch(`/api/interview-data/${token}`);
        if (!res.ok) {
            const err = await res.json();
            qContainer.innerHTML = `<div style="color:red; text-align:center; padding:30px;">Error: ${err.detail || 'Invalid or expired link'}</div>`;
            return;
        }

        const data = await res.json();
        document.getElementById('interview-candidate-name').textContent = `Assessment: ${data.candidate_name}`;

        if (data.status === 'Completed' || data.status === 'PASS' || data.status === 'FAIL') {
            // Already completed interview - show candidate summary without HR options
            stopTimer();
            document.getElementById('timer-box').style.display = 'none';
            form.classList.add('hidden');
            resultCard.classList.remove('hidden');
            displayEvaluationResult(data.score, data.status, data.feedback);
            return;
        }

        document.getElementById('timer-box').style.display = 'flex';
        currentInterviewQuestions = data.questions || [];
        qContainer.innerHTML = currentInterviewQuestions.map((q, idx) => `
            <div class="question-card">
                <div class="question-title">
                    Question ${idx + 1}: ${escapeHtml(q.replace(/^\d+\.\s*/, ''))}
                </div>
                <textarea 
                    class="answer-textarea" 
                    id="q-ans-${idx}" 
                    placeholder="Write your answer here..."
                    required
                ></textarea>
            </div>
        `).join('');

        // Start 10-minute timer for candidate
        start10MinuteTimer();

    } catch (err) {
        qContainer.innerHTML = `<div style="color:red; text-align:center; padding:30px;">Failed to load interview.</div>`;
    }
}

// 10-Minute Timer Functions
function start10MinuteTimer() {
    stopTimer();
    remainingSeconds = 600; // 10 minutes = 600 seconds
    updateTimerDisplay();

    timerInterval = setInterval(() => {
        remainingSeconds--;
        updateTimerDisplay();

        if (remainingSeconds <= 0) {
            stopTimer();
            alert('⏱ 10 Minutes Time Limit Exceeded!\nYour interview answers are being automatically submitted now.');
            autoSubmitInterview();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(Math.max(0, remainingSeconds) / 60);
    const seconds = Math.max(0, remainingSeconds) % 60;
    const formatted = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    const display = document.getElementById('timer-display');
    const timerBox = document.getElementById('timer-box');

    if (display) display.textContent = formatted;
    if (timerBox) {
        if (remainingSeconds <= 120) {
            timerBox.classList.add('warning');
        } else {
            timerBox.classList.remove('warning');
        }
    }
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// Auto-submit when 10 minutes expire
function autoSubmitInterview() {
    const form = document.getElementById('interview-form');
    if (form) {
        form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }
}

// SUBMIT INTERVIEW ANSWERS
async function handleInterviewSubmit(event) {
    if (event) event.preventDefault();
    if (!currentInterviewToken) return;

    stopTimer(); // Stop timer on submission

    const answers = [];
    for (let i = 0; i < currentInterviewQuestions.length; i++) {
        const val = document.getElementById(`q-ans-${i}`)?.value || '';
        answers.push(val.trim() || 'No answer provided (time expired)');
    }

    const submitBtn = document.getElementById('submit-interview-btn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> AI Evaluating Answers...`;
    }

    try {
        const res = await fetch(`/api/interview/${currentInterviewToken}/submit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: answers })
        });

        const data = await res.json();

        if (res.ok) {
            document.getElementById('timer-box').style.display = 'none';
            document.getElementById('interview-form').classList.add('hidden');
            document.getElementById('interview-result-card').classList.remove('hidden');

            const score = data.evaluation.score;
            const status = data.evaluation.status;
            const feedback = data.evaluation.feedback;

            displayEvaluationResult(score, status, feedback);
        } else {
            alert(`Submission Error: ${data.detail}`);
        }
    } catch (err) {
        alert(`Error submitting interview: ${err.message}`);
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Submit Interview Answers`;
        }
    }
}

function displayEvaluationResult(score, status, feedback) {
    const iconBox = document.getElementById('result-icon-box');
    const icon = document.getElementById('result-icon');
    const scoreNum = document.getElementById('result-score');
    const statusBadge = document.getElementById('result-status-badge');
    const feedbackText = document.getElementById('result-feedback');

    scoreNum.textContent = score;
    feedbackText.textContent = feedback || 'Interview completed.';

    const isPass = (status === 'PASS' || status === 'Passed' || score >= 60);

    if (isPass) {
        iconBox.className = 'result-icon-wrapper pass';
        icon.className = 'fa-solid fa-circle-check';
        statusBadge.className = 'status-badge-lg pass';
        statusBadge.textContent = 'PASSED — Candidate Qualified';
    } else {
        iconBox.className = 'result-icon-wrapper fail';
        icon.className = 'fa-solid fa-circle-xmark';
        statusBadge.className = 'status-badge-lg fail';
        statusBadge.textContent = 'FAILED — Not Selected';
    }
}

// VIEW CANDIDATE PROFILE MODAL
async function viewCandidateModal(candidateId) {
    const modalBody = document.getElementById('candidate-modal-body');
    modalBody.innerHTML = '<div style="text-align:center; padding:20px;">Loading profile...</div>';
    openModal('candidate-modal');

    try {
        const res = await fetch(`/api/candidates/${candidateId}`);
        const data = await res.json();

        const c = data.candidate;
        modalBody.innerHTML = `
            <div class="detail-row">
                <div class="detail-label">Full Name</div>
                <div class="detail-val"><strong>${escapeHtml(c.name)}</strong></div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Email Address</div>
                <div class="detail-val">${escapeHtml(c.email)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Phone Number</div>
                <div class="detail-val">${escapeHtml(c.phone)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Education</div>
                <div class="detail-val">${escapeHtml(c.education)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Skills</div>
                <div class="detail-val">${renderSkills(c.skills)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Work Experience</div>
                <div class="detail-val">${escapeHtml(c.experience)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Certifications</div>
                <div class="detail-val">${escapeHtml(c.certifications)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">CV File</div>
                <div class="detail-val"><code>${escapeHtml(c.cv_filename)}</code></div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Current Recruitment Status</div>
                <div class="detail-val"><strong>${escapeHtml(c.status)}</strong></div>
            </div>
        `;
    } catch (err) {
        modalBody.innerHTML = '<div style="color:red;">Failed to load candidate details.</div>';
    }
}

// OPEN MOCK EMAIL LOGS MODAL
async function openEmailLogsModal() {
    const container = document.getElementById('email-logs-container');
    container.innerHTML = '<div style="text-align:center; padding:20px;">Loading email logs...</div>';
    openModal('emails-modal');

    try {
        const res = await fetch('/api/emails');
        const logs = await res.json();

        if (!logs || logs.length === 0) {
            container.innerHTML = '<div style="text-align:center; color:#64748b; padding:20px;">No emails logged yet.</div>';
            return;
        }

        container.innerHTML = logs.map(l => {
            let bodyContent = l.body || '';
            // If body starts with HTML doctype or tags, render as HTML preview, otherwise linkify plain URLs
            if (!bodyContent.includes('<html') && !bodyContent.includes('<div')) {
                bodyContent = escapeHtml(bodyContent).replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" style="color:#2563eb; font-weight:bold;">$1</a>');
            }
            
            return `
                <div class="email-log-item">
                    <div class="email-meta">
                        <span><strong>To Candidate:</strong> ${escapeHtml(l.recipient_email)} (${escapeHtml(l.email_type)})</span>
                        <span>${escapeHtml(l.sent_at)}</span>
                    </div>
                    <div class="email-subject"><i class="fa-solid fa-paperclip"></i> ${escapeHtml(l.subject)}</div>
                    <div class="email-body-text" style="max-height: 250px; overflow-y: auto;">${bodyContent}</div>
                </div>
            `;
        }).join('');

    } catch (err) {
        container.innerHTML = '<div style="color:red;">Failed to load email logs.</div>';
    }
}

// DEMO SEED ACTION
async function triggerDemoSeed() {
    try {
        const res = await fetch('/api/demo/seed', { method: 'POST' });
        if (res.ok) {
            alert('Loaded sample candidate CVs successfully!');
            loadCandidates();
            loadDashboardStats();
        }
    } catch (err) {
        alert('Failed to load demo candidates.');
    }
}

// Modal Helper Functions
function openModal(id) {
    document.getElementById(id).classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

function renderSkills(skillsStr) {
    if (!skillsStr || skillsStr === 'Not Available') return '<span style="color:#94a3b8">Not Available</span>';
    return skillsStr.split(',').map(s => `<span class="skill-tag">${escapeHtml(s.trim())}</span>`).join('');
}

function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
