// src/components/InputBox.jsx

import { useState } from 'react';
import './InputBox.css';

function InputBox({ onSend }) {
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!input.trim() || loading) return;
        const question = input.trim();
        setInput('');
        setLoading(true);
        try {
            await onSend(question);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="input-container">
            <div className="input-wrapper">
                <textarea
                    className="input-box"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Tulis pertanyaan..."
                    rows={1}
                    disabled={loading}
                />
                <button
                    className={`send-btn ${loading ? 'loading' : ''}`}
                    onClick={handleSend}
                    disabled={loading || !input.trim()}
                >
                    {loading ? (
                        <span className="send-spinner"></span>
                    ) : (
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <line x1="22" y1="2" x2="11" y2="13" strokeLinecap="round" />
                            <polygon points="22 2 15 22 11 13 2 9 22 2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    )}
                </button>
            </div>
        </div>
    );
}

export default InputBox;