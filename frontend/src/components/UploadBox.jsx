// src/components/UploadBox.jsx

import { useState } from 'react';
import { uploadFile } from '../services/api';
import './UploadBox.css';

function UploadBox() {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setMessage('');
    };

    const handleUpload = async () => {
        if (!file) {
            setMessage('Pilih file terlebih dahulu');
            return;
        }

        setUploading(true);
        setMessage('');

        try {
            const response = await uploadFile(file);
            setMessage(`✅ ${response.data.message}`);
            setFile(null);
            // Refresh sidebar
            if (window.refreshSidebar) window.refreshSidebar();
        } catch (error) {
            const detail = error.response?.data?.detail || 'Upload gagal';
            setMessage(`❌ ${detail}`);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="upload-box">
            <div className="upload-content">
                <div className="upload-icon">📤</div>
                <h4>Upload Dokumen</h4>
                <div className="upload-input-group">
                    <label className="upload-label">
                        <span>Pilih File</span>
                        <input type="file" onChange={handleFileChange} accept=".pdf,.docx,.txt" />
                    </label>
                    <button onClick={handleUpload} disabled={!file || uploading}>
                        {uploading ? '⏳ Uploading...' : 'Upload'}
                    </button>
                </div>
                {file && <span className="file-name">📎 {file.name}</span>}
                {message && <span className={`upload-message ${message.includes('✅') ? 'success' : 'error'}`}>{message}</span>}
            </div>
        </div>
    );
}

export default UploadBox;