import { useState, useEffect } from 'react';
import UnifiedDashboard from './UnifiedDashboard.jsx';
import './BusinessDashboard.css';

export default function CaseyAi() {
  const [activeView, setActiveView] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [conversationId, setConversationId] = useState(null);

  useEffect(() => {
    const initConversation = async () => {
      try {
        const res = await fetch('http://localhost:8000/conversations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title: '' })
        });
        const conv = await res.json();
        setConversationId(conv.id);
        const initialMessages = [
          { sender: 'casey', text: "Hi, I'm Casey. Let's map how your work *actually* happens." }
        ];
        const qRes = await fetch(`http://localhost:8000/conversations/${conv.id}/next_question`);
        const qData = await qRes.json();
        initialMessages.push({ sender: 'casey', text: qData.question });
        setMessages(initialMessages);
      } catch (err) {
        console.error('Failed to initialize conversation', err);
      }
    };
    initConversation();
  }, []);

  const sendMessage = async () => {
    if (!newMessage.trim() || !conversationId) return;
    const userText = newMessage;
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setNewMessage('');
    try {
      const res = await fetch(`http://localhost:8000/conversations/${conversationId}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_text: userText })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { sender: 'casey', text: data.assistant }]);
    } catch (err) {
      console.error('Failed to send message', err);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <nav className="flex justify-around bg-gray-800 text-white p-4 md:justify-start md:space-x-4">
        <button className="hover:text-blue-300" onClick={() => setActiveView('chat')}>Chat</button>
        <button className="hover:text-blue-300" onClick={() => setActiveView('dashboard')}>Dashboard</button>
      </nav>
      <main className="flex-1 overflow-auto">
        {activeView === 'chat' ? (
          <div className="flex flex-col items-center justify-center p-4">
            <h1 className="text-2xl mb-4 text-center">Ready when you are.</h1>
            <div className="w-full max-w-md space-y-4">
              <div className="border p-2 h-64 overflow-auto">
                {messages.map((m, idx) => (
                  <div key={idx} className={`my-1 ${m.sender === 'user' ? 'text-right' : 'text-left'}`}>
                    <span className={`inline-block px-2 py-1 rounded ${m.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}>{m.text}</span>
                  </div>
                ))}
              </div>
              <div className="flex w-full">
                <input
                  className="flex-1 p-2 border"
                  type="text"
                  placeholder="Ask anything"
                  value={newMessage}
                  onChange={e => setNewMessage(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && sendMessage()}
                />
                <button className="px-4 bg-blue-500 text-white" onClick={sendMessage}>+</button>
              </div>
            </div>
          </div>
        ) : (
          <UnifiedDashboard />
        )}
      </main>
    </div>
  );
}
