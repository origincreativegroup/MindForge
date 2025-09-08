import React, { useState, useEffect } from 'react';
import './BusinessDashboard.css';

// Fallback data used when the API isn't available
const defaultData = {
  summary: {
    active_opportunities: 0,
    revenue_potential: '$0',
    optimization_score: 0,
    business_stage: 'N/A'
  },
  quick_wins: [
    'Set up your first project',
    'Invite collaborators'
  ],
  next_milestones: [
    { milestone: 'Complete onboarding', eta: 'Today', progress: 0.1 },
    { milestone: 'Connect portfolio', eta: 'Soon', progress: 0 }
  ]
};

const BusinessDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/business/dashboard');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Use fallback data so the dashboard can still render
      setDashboardData(defaultData);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="business-dashboard loading">
        <div className="loading-spinner">Loading your business intelligence...</div>
      </div>
    );
  }

  const { summary, quick_wins, next_milestones } = dashboardData || defaultData;

  return (
    <div className="business-dashboard">
      <header className="dashboard-header">
        <h1>Your AI Business Partner Dashboard</h1>
        <p className="subtitle">Transforming your creative business with intelligent insights</p>
      </header>

      <div className="dashboard-content">
        <div className="summary-cards">
          <div className="summary-card opportunities">
            <div className="card-icon">💼</div>
            <div className="card-content">
              <h3>{summary.active_opportunities}</h3>
              <p>Active Opportunities</p>
            </div>
          </div>

          <div className="summary-card revenue">
            <div className="card-icon">💰</div>
            <div className="card-content">
              <h3>{summary.revenue_potential}</h3>
              <p>Revenue Potential</p>
            </div>
          </div>

          <div className="summary-card optimization">
            <div className="card-icon">📈</div>
            <div className="card-content">
              <h3>{Math.round(summary.optimization_score * 100)}%</h3>
              <p>Optimization Score</p>
            </div>
          </div>

          <div className="summary-card stage">
            <div className="card-icon">🎯</div>
            <div className="card-content">
              <h3>{summary.business_stage}</h3>
              <p>Business Stage</p>
            </div>
          </div>
        </div>

        <div className="quick-wins-section">
          <h2>🚀 Quick Wins</h2>
          <p className="section-subtitle">High-impact actions you can take today</p>
          <ul className="quick-wins-list">
            {quick_wins.map((win, index) => (
              <li key={index} className="quick-win-item">
                <span className="win-icon">✅</span>
                {win}
              </li>
            ))}
          </ul>
        </div>

        <div className="milestones-section">
          <h2>🎯 Next Milestones</h2>
          <p className="section-subtitle">Your path to business growth</p>
          <div className="milestones-list">
            {next_milestones.map((milestone, index) => (
              <div key={index} className="milestone-item">
                <div className="milestone-header">
                  <h3>{milestone.milestone}</h3>
                  <span className="milestone-eta">{milestone.eta}</span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${milestone.progress * 100}%` }}
                  ></div>
                </div>
                <span className="progress-text">{Math.round(milestone.progress * 100)}% complete</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <footer className="dashboard-footer">
        <p>💡 Your AI Business Partner is working 24/7 to find opportunities and optimize your business</p>
      </footer>
    </div>
  );
};

export default BusinessDashboard;
