import React from 'react'
import ProcessVisualizer from './components/ProcessVisualizer.jsx'

export default function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-item">New chat</div>
        <div className="sidebar-item">Search chats</div>
        <div className="sidebar-item">Library</div>
        <div className="sidebar-item">Docs</div>
        <hr />
        <div className="sidebar-item">Data Analyst</div>
        <div className="sidebar-item">MindForge AI</div>
        <div className="sidebar-item">Resume / Portfolio</div>
      </aside>
      <main className="main">
        <ProcessVisualizer />
        <div className="welcome-overlay">
          <h1>Ready when you are.</h1>
          <div className="input-box">
            <input type="text" placeholder="Ask anything" />
            <button>+</button>
          </div>
        </div>
      </main>
    </div>
  )
}
