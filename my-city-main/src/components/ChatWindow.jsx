import React, { useEffect, useState } from 'react';

import { API_BASE_URL } from '../api';

export default function ChatWindow({ currentUser }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);

  const fetchMessages = async () => {
    const response = await fetch(`${API_BASE_URL}/messages`);
    if (!response.ok) {
      throw new Error('Failed to load messages');
    }

    const data = await response.json();
    setMessages(data);
  };

  useEffect(() => {
    fetchMessages().catch(() => {});
    const timer = setInterval(() => {
      fetchMessages().catch(() => {});
    }, 3000);

    return () => clearInterval(timer);
  }, []);

  const send = async () => {
    const text = input.trim();
    if (!text || !currentUser || isSending) {
      return;
    }

    setIsSending(true);

    try {
      await fetch(`${API_BASE_URL}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sender: currentUser, text }),
      });
      setInput('');
      await fetchMessages();
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="chat-panel panel-card">
      <div className="section-heading">
        <span className="eyebrow">Community Chat</span>
        <strong>{currentUser ? `Online: ${currentUser}` : 'Guest'}</strong>
      </div>

      <div className="messages-list">
        {messages.map((m, i) => (
          <div key={m.id ?? i} className={`message-item ${m.sender === currentUser ? 'message-item--own' : ''}`}>
            <b>{m.sender}:</b> {m.text}
          </div>
        ))}
      </div>

      <div className="chat-compose">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Напишите сообщение..."
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              send();
            }
          }}
        />
        <button onClick={send} disabled={isSending || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
