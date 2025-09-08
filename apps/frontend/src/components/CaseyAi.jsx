import { useState } from 'react';
import UnifiedDashboard from './UnifiedDashboard.jsx';
import ProcessVisualizer from './ProcessVisualizer.jsx';
import './BusinessDashboard.css';

export default function CaseyAi() {
  const [activeView, setActiveView] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  const sendMessage = () => {
    if (!newMessage.trim()) return;
    setMessages(prev => [
      ...prev,
      { sender: 'user', text: newMessage },
      { sender: 'casey', text: 'Thanks for your message!' }
    ]);
    setNewMessage('');
  };

  return (
    <div className="flex flex-col h-screen">
      <nav className="flex justify-around bg-gray-800 text-white p-4 md:justify-start md:space-x-4">
        <button className="hover:text-blue-300" onClick={() => setActiveView('chat')}>Chat</button>
        <button className="hover:text-blue-300" onClick={() => setActiveView('dashboard')}>Dashboard</button>
      </nav>
      <main className="flex-1 overflow-auto">
        {activeView === 'chat' ? (
          <>
            <ProcessVisualizer />
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
          </>
        ) : (
          <UnifiedDashboard />
        )}
      </main>
    </div>
  );
}
