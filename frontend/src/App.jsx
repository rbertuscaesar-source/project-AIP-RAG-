// src/App.jsx

import { useState } from "react";
import "./App.css";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import UploadBox from "./components/UploadBox";
import ChatBox from "./components/ChatBox";
import InputBox from "./components/InputBox";
import { sendQuestion } from "./services/api";

function App() {
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSend = async (question) => {
        if (!question.trim()) return;

        setMessages((prev) => [
            ...prev,
            { role: "User", text: question }
        ]);

        setLoading(true);

        try {
            const response = await sendQuestion(question);
            setMessages((prev) => [
                ...prev,
                { role: "Assistant", text: response.data.answer }
            ]);
        } catch (error) {
            console.error(error);
            setMessages((prev) => [
                ...prev,
                { role: "Assistant", text: "Maaf, terjadi kesalahan. Silakan coba lagi." }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app">
            <Header />
            <div className="content">
                <Sidebar />
                <div className="main">
                    <UploadBox />
                    <ChatBox messages={messages} />
                    <InputBox onSend={handleSend} />
                </div>
            </div>
        </div>
    );
}

export default App;