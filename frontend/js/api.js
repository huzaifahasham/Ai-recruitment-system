const API_BASE = '/api';

const ApiService = {
    async getDashboardStats() {
        const res = await fetch(`${API_BASE}/dashboard/stats`);
        if (!res.ok) throw new Error('Failed to fetch dashboard stats');
        return await res.json();
    },

    async getDomains() {
        const res = await fetch(`${API_BASE}/domains`);
        if (!res.ok) throw new Error('Failed to fetch domain stats');
        return await res.json();
    },

    async getCandidates(params = {}) {
        const query = new URLSearchParams();
        if (params.search) query.append('search', params.search);
        if (params.domain) query.append('domain', params.domain);
        if (params.recommendation) query.append('recommendation', params.recommendation);
        if (params.status) query.append('status', params.status);

        const url = `${API_BASE}/candidates?${query.toString()}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to fetch candidate list');
        return await res.json();
    },

    async getCandidateDetail(candidateId) {
        const res = await fetch(`${API_BASE}/candidates/${candidateId}`);
        if (!res.ok) throw new Error('Failed to fetch candidate details');
        return await res.json();
    },

    async uploadFiles(files) {
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        const res = await fetch(`${API_BASE}/candidates/upload`, {
            method: 'POST',
            body: formData
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Upload failed');
        }

        return await res.json();
    }
};
