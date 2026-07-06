import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { exportChat } from '../services/api';
import './ChatBox.css';

function ChatBox({ messages }) {
    const chatEndRef = useRef(null);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }, [messages]);

    const handleExport = async (format) => {
    console.log('🔄 Exporting chat as', format);
    
    try {
        const response = await exportChat(format);
        console.log('✅ Response received:', response);
        
        const blob = new Blob([response.data]);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        let filename = `chat_history.${format}`;
        const contentDisposition = response.headers['content-disposition'];
        if (contentDisposition) {
            const match = contentDisposition.match(/filename=(.+)/);
            if (match) filename = match[1];
        }
        
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
    } catch (error) {
        console.error('❌ Export error:', error);
        alert(`Gagal export chat: ${error.message}`);
    }
};

    return (
        <div className="chat-messages">
            {messages.length > 0 && (
                <div className="export-buttons">
                    <button className="export-btn txt-btn" onClick={() => handleExport('txt')}>
                        📄 Export TXT
                    </button>
                    <button className="export-btn pdf-btn" onClick={() => handleExport('pdf')}>
                        📄 Export PDF
                    </button>
                </div>
            )}

            {messages.length === 0 ? (
                <div className="empty-chat">
                    <div className="empty-icon">💬</div>
                    <h3>Mulai Percakapan</h3>
                    <p>Tanyakan tentang SOP universitas</p>
                    <div className="suggestion-chips">
                        <span>📋 Pendaftaran</span>
                        <span>📝 Judul TA</span>
                        <span>🏢 Peminjaman Ruang</span>
                    </div>
                </div>
            ) : (
                messages.map((msg, index) => (
                    <div key={index} className={`message-wrapper ${msg.role === 'User' ? 'user-wrapper' : 'assistant-wrapper'} fade-in`}>
                        {msg.role === 'User' && (
                            <div className="user-message">
                                <div className="message-sender">👤 Anda</div>
                                <div className="message-content">{msg.text}</div>
                            </div>
                        )}

                        {msg.role === 'Assistant' && (
                            <div className="assistant-message">
                                <div className="message-sender">🤖 Asisten</div>
                                <div className="message-content">
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            ul: ({ ...props }) => <ul style={{ paddingLeft: '20px', margin: '6px 0' }} {...props} />,
                                            ol: ({ ...props }) => <ol style={{ paddingLeft: '20px', margin: '6px 0' }} {...props} />,
                                            li: ({ ...props }) => <li style={{ marginBottom: '3px' }} {...props} />,
                                            strong: ({ ...props }) => <strong style={{ color: '#667eea' }} {...props} />,
                                            p: ({ ...props }) => <p style={{ margin: '6px 0', lineHeight: '1.6' }} {...props} />,
                                        }}
                                    >
                                        {msg.text}
                                    </ReactMarkdown>
                                </div>
                            </div>
                        )}
                    </div>
                ))
            )}
            <div ref={chatEndRef} />
        </div>
    );
}

export default ChatBox;