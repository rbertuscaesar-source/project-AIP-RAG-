// src/components/Header.jsx

import React from 'react';
import './Header.css';

function Header() {
    return (
        <header className="header">
            <div className="header-left">
                <div className="logo-icon">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                        <rect x="2" y="2" width="28" height="28" rx="8" fill="url(#gradient)" />
                        <path d="M10 22L16 10L22 22" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M12 18H20" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
                        <defs>
                            <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32">
                                <stop offset="0%" stopColor="#667eea" />
                                <stop offset="100%" stopColor="#764ba2" />
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <div className="header-title">
                    <h1>📚 Enterprise RAG Assistant</h1>
                    <span className="header-badge">v1.0</span>
                </div>
            </div>
            <div className="header-right">
                <div className="status-indicator">
                    <span className="status-dot"></span>
                    <span className="status-text">System Online</span>
                </div>
                <button className="header-btn" title="Refresh">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M23 4v6h-6" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M1 20v-6h6" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M3.51 9a9 9 0 0114.85-3.36L23 10" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M20.49 15a9 9 0 01-14.85 3.36L1 14" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </button>
            </div>
        </header>
    );
}

export default Header;