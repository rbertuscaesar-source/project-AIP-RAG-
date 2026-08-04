// src/components/UploadBox.jsx

import { useState } from 'react';
import { uploadFile } from '../services/api';
import './UploadBox.css';

function UploadBox() {
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [messages, setMessages] = useState([]);

    const handleFileChange = (e) => {
        setFiles(Array.from(e.target.files));
        setMessages([]);
    };

    const handleUpload = async () => {
        if (files.length === 0) {
            setMessages([{ text: 'Pilih file terlebih dahulu', success: false }]);
            return;
        }

        setUploading(true);
        setMessages([]);

        const results = [];
        for (const file of files) {
            try {
                const response = await uploadFile(file);
                results.push({ text: `✅ ${file.name} — ${response.data.message}`, success: true });
            } catch (error) {
                const detail = error.response?.data?.detail || 'Upload gagal';
                results.push({ text: `❌ ${file.name} — ${detail}`, success: false });
            }
        }

        setMessages(results);
        setFiles([]);
        setUploading(false);
        if (window.refreshSidebar) window.refreshSidebar();
    };

    return (
        <div className="upload-box">
            <div className="upload-content">
                <div className="upload-icon">📤</div>
                <h4>Upload Dokumen</h4>
                <div className="upload-input-group">
                    <label className="upload-label">
                        <span>Pilih File</span>
                        <input
                            type="file"
                            onChange={handleFileChange}
                            accept=".pdf,.docx,.txt"
                            multiple
                        />
                    </label>
                    <button onClick={handleUpload} disabled={files.length === 0 || uploading}>
                        {uploading ? '⏳ Uploading...' : 'Upload'}
                    </button>
                </div>
                {files.length > 0 && (
                    <div className="file-names">
                        {files.map((f, i) => (
                            <span key={i} className="file-name">📎 {f.name}</span>
                        ))}
                    </div>
                )}
                {messages.map((msg, i) => (
                    <span key={i} className={`upload-message ${msg.success ? 'success' : 'error'}`}>
                        {msg.text}
                    </span>
                ))}
            </div>
        </div>
    );
}

export default UploadBox;