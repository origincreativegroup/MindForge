import { useState } from 'react';
import BusinessDashboard from './components/BusinessDashboard.jsx';
import CreativeWorkspace from './components/CreativeWorkspace.jsx';
import ProcessVisualizer from './components/ProcessVisualizer.jsx';
import './components/BusinessDashboard.css';

export default function App() {
  const [activeView, setActiveView] = useState('chat');

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-item" onClick={() => setActiveView('chat')}>
          💬 New chat
        </div>
        <div className="sidebar-item">🔍 Search chats</div>
        <div className="sidebar-item">📚 Library</div>
        <div className="sidebar-item">📖 Docs</div>
        <hr />
        <div className="sidebar-item">📊 Data Analyst</div>
        <div className="sidebar-item">🧠 MindForge AI</div>
        <div className="sidebar-item">📄 Resume / Portfolio</div>
        <div className="sidebar-item" onClick={() => setActiveView('business')}>
          💼 Business Partner
        </div>
        <div className="sidebar-item" onClick={() => setActiveView('creative')}>
          🎨 Creative Workspace
        </div>
      </aside>
      <main className="main">
        {activeView === 'chat' ? (
          <>
            <ProcessVisualizer />
            <div className="welcome-overlay">
              <h1>Ready when you are.</h1>
              <div className="input-box">
                <input type="text" placeholder="Ask anything" />
                <button>+</button>
              </div>
            </div>
          </>
        ) : activeView === 'creative' ? (
          <CreativeWorkspace />
        ) : (
          <BusinessDashboard />
        )}
      </main>
    </div>
  );
}
