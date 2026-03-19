export default function ChatWindow({ currentUser }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const fetchMessages = () => {
    fetch('http://localhost:8000/messages').then(r => r.json()).then(setMessages);
  };

  useEffect(() => {
    const timer = setInterval(fetchMessages, 3000); // Обновляем чат каждые 3 сек
    return () => clearInterval(timer);
  }, []);

  const send = () => {
    fetch('http://localhost:8000/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sender: currentUser, text: input })
    });
    setInput('');
  };

  return (
    <div className="chat-panel">
      <div className="messages-list">
        {messages.map((m, i) => (
          <div key={i}><b>{m.sender}:</b> {m.text}</div>
        ))}
      </div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={send}>📨</button>
    </div>
  );
}