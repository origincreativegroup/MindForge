import React from 'react';

const CreatorDashboard = () => {
  const activeProjects = [
    { name: 'Portfolio redesign', progress: 0.6 },
    { name: 'Client logo concepts', progress: 0.3 },
    { name: 'Social media templates', progress: 0.1 }
  ];

  const ideaPipeline = [
    'Interactive case study template',
    'Behind-the-scenes video series'
  ];

  return (
    <div className="business-dashboard">
      <header className="dashboard-header">
        <h1>Your Creative Workspace</h1>
        <p className="subtitle">Track projects and nurture new ideas</p>
      </header>

      <div className="dashboard-content">
        <div className="milestones-section">
          <h2>🎨 Active Projects</h2>
          <p className="section-subtitle">Progress across current work</p>
          <div className="milestones-list">
            {activeProjects.map((project, index) => (
              <div key={index} className="milestone-item">
                <div className="milestone-header">
                  <h3>{project.name}</h3>
                  <span className="milestone-eta">{Math.round(project.progress * 100)}%</span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${project.progress * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="quick-wins-section">
          <h2>💡 Idea Pipeline</h2>
          <p className="section-subtitle">Potential future projects</p>
          <ul className="quick-wins-list">
            {ideaPipeline.map((idea, index) => (
              <li key={index} className="quick-win-item">
                <span className="win-icon">✨</span>
                {idea}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <footer className="dashboard-footer">
        <p>Keep creating and turning ideas into reality</p>
      </footer>
    </div>
  );
};

export default CreatorDashboard;

