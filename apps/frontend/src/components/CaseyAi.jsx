import { useState } from 'react';
import BusinessDashboard from './BusinessDashboard.jsx';
import CreativeWorkspace from './CreativeWorkspace.jsx';
import ProcessVisualizer from './ProcessVisualizer.jsx';
import './BusinessDashboard.css';

export default function CaseyAi() {
  const [activeView, setActiveView] = useState('chat');

  return (
    <div className="flex flex-col h-screen">
      <nav className="flex justify-around bg-gray-800 text-white p-4 md:justify-start md:space-x-4">
        <button className="hover:text-blue-300" onClick={() => setActiveView('chat')}>Chat</button>
        <button className="hover:text-blue-300" onClick={() => setActiveView('creative')}>Creative</button>
        <button className="hover:text-blue-300" onClick={() => setActiveView('business')}>Business</button>
      </nav>
      <main className="flex-1 overflow-auto">
        {activeView === 'chat' ? (
          <>
            <ProcessVisualizer />
            <div className="flex flex-col items-center justify-center p-4">
              <h1 className="text-2xl mb-4 text-center">Ready when you are.</h1>
              <div className="flex w-full max-w-md">
                <input className="flex-1 p-2 border" type="text" placeholder="Ask anything" />
                <button className="px-4 bg-blue-500 text-white">+</button>
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
