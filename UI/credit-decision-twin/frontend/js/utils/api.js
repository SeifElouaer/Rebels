// API utility functions for communicating with Python backend

const api = {
    // Get API status
    async getStatus() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/status`);
            if (!response.ok) throw new Error('API not available');
            return await response.json();
        } catch (error) {
            console.error('API Status Error:', error);
            return { api_status: 'disconnected', qdrant_status: 'disconnected', case_count: 0 };
        }
    },

    // Get data source info
    async getDataSource() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/data-source`);
            if (!response.ok) throw new Error('Failed to get data source');
            return await response.json();
        } catch (error) {
            console.error('Data Source Error:', error);
            return { type: 'none', count: 0, label: 'No data loaded' };
        }
    },

    // Process credit application
    async processApplication(application) {
        const response = await fetch(`${API_BASE_URL}/api/process-application`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(application)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to process application');
        }
        
        return await response.json();
    },

    // Get database statistics
    async getStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/api/stats`);
            if (!response.ok) throw new Error('Failed to get stats');
            return await response.json();
        } catch (error) {
            console.error('Stats Error:', error);
            return { total: 0, repaid: 0, defaulted: 0, purpose_counts: {} };
        }
    },

    // Get sample cases
    async getSampleCases(count = 20) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/sample-cases?count=${count}`);
            if (!response.ok) throw new Error('Failed to get sample cases');
            return await response.json();
        } catch (error) {
            console.error('Sample Cases Error:', error);
            return [];
        }
    },

    // Upload file for preview
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE_URL}/api/upload-file`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to upload file');
        }
        
        return await response.json();
    },

    // Import dataset with mappings
    async importDataset(mappings) {
        const response = await fetch(`${API_BASE_URL}/api/import-dataset`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(mappings)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to import dataset');
        }
        
        return await response.json();
    },

    // Clear all data
    async clearData() {
        const response = await fetch(`${API_BASE_URL}/api/clear-data`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to clear data');
        }
        
        return await response.json();
    },

    // Export data as CSV
    exportDataUrl() {
        return `${API_BASE_URL}/api/export-data`;
    },

    // Download template
    downloadTemplateUrl() {
        return `${API_BASE_URL}/api/download-template`;
    }
};
