// src/services/api.js

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: { 'Content-Type': 'application/json' },
});

export const exportChat = async (format) => {
    console.log('📤 Exporting chat...');
    return api.post('/export', { format }, { 
        responseType: 'blob',
        timeout: 30000,
    });
};

export const sendQuestion = async (question) => {
    return api.post('/chat', { question });
};

export const getDocuments = async () => {
    return api.get('/documents');
};

export const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
};

export const deleteDocument = async (filename) => {
    return api.delete(`/documents/${encodeURIComponent(filename)}`);
};

export const deleteAllDocuments = async () => {
    return api.delete('/documents');
};