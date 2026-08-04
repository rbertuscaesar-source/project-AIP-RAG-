// src/components/Sidebar.jsx

import { useEffect, useState } from 'react';
import { getDocuments, deleteDocument } from '../services/api';
import './Sidebar.css';

function Sidebar({ className = '' }) {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [deleting, setDeleting] = useState(null);

    const loadDocuments = async () => {
        setLoading(true);
        try {
            const response = await getDocuments();
            setDocuments(response.data.documents || []);
        } catch (error) {
            console.error('Error loading documents:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (filename) => {
        if (!window.confirm(`Hapus "${filename}"?`)) return;
        setDeleting(filename);
        try {
            await deleteDocument(filename);
            await loadDocuments();
        } catch (error) {
            console.error('Error deleting:', error);
        } finally {
            setDeleting(null);
        }
    };

    useEffect(() => {
        loadDocuments();
        window.refreshSidebar = loadDocuments;
    }, []);

    return (
        <div className={`sidebar ${className}`}>
            <div className="sidebar-header">
                <h3>📂 Documents</h3>
                <button className="refresh-btn" onClick={loadDocuments} disabled={loading}>
                    {loading ? '⏳' : '🔄'}
                </button>
            </div>

            <div className="sidebar-stats">
                <span>{documents.length} dokumen</span>
                <span>
                    {documents.reduce((acc, doc) => acc + (doc.chunks || 0), 0)} chunks
                </span>
            </div>

            <div className="sidebar-list">
                {loading ? (
                    <div className="sidebar-loading">
                        <span className="spinner"></span>
                        <p>Memuat...</p>
                    </div>
                ) : documents.length === 0 ? (
                    <div className="sidebar-empty">
                        <span>📭</span>
                        <p>Belum ada dokumen</p>
                        <p className="hint">Upload untuk mulai</p>
                    </div>
                ) : (
                    documents.map((doc) => (
                        <div key={doc.filename} className="doc-item">
                            <div className="doc-info">
                                <span className="doc-icon">📄</span>
                                <div className="doc-details">
                                    <span className="doc-name" title={doc.filename}>
                                        {doc.filename}
                                    </span>
                                    <span className="doc-chunks">
                                        {doc.chunks || 0} chunks
                                    </span>
                                </div>
                            </div>
                            <button
                                className="doc-delete"
                                onClick={() => handleDelete(doc.filename)}
                                disabled={deleting === doc.filename}
                            >
                                {deleting === doc.filename ? '⏳' : '✕'}
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default Sidebar;
