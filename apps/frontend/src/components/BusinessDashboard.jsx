import React, { useState, useEffect } from 'react';

const BusinessDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/business/dashboard');
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
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

  if (!dashboardData) {
    return (
      <div className="business-dashboard error">
        <div className="error-message">Unable to load business dashboard</div>
      </div>
    );
  }

  const { summary, quick_wins, opportunities, intelligence, next_milestones } = dashboardData;

  return (
    <div className="business-dashboard">
      <header className="dashboard-header">
        <h1>Your AI Business Partner Dashboard</h1>
        <p className="subtitle">Transforming your creative business with intelligent insights</p>
      </header>

      <div className="dashboard-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'opportunities' ? 'active' : ''}`}
          onClick={() => setActiveTab('opportunities')}
        >
          Opportunities
        </button>
        <button 
          className={`tab ${activeTab === 'intelligence' ? 'active' : ''}`}
          onClick={() => setActiveTab('intelligence')}
        >
          Intelligence
        </button>
      </div>

      <div className="dashboard-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
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
        )}

        {activeTab === 'opportunities' && (
          <div className="opportunities-tab">
            <h2>💼 Business Opportunities</h2>
            <p className="section-subtitle">Curated opportunities matched to your skills</p>
            
            {opportunities.length === 0 ? (
              <div className="no-opportunities">
                <p>No opportunities found. Let's chat about your skills to find better matches!</p>
              </div>
            ) : (
              <div className="opportunities-list">
                {opportunities.map((opp, index) => (
                  <div key={index} className="opportunity-card">
                    <div className="opportunity-header">
                      <h3>{opp.title}</h3>
                      <span className={`urgency ${opp.urgency}`}>{opp.urgency} priority</span>
                    </div>
                    <div className="opportunity-details">
                      <p className="opportunity-type">{opp.type.replace('_', ' ')}</p>
                      <p className="opportunity-budget">{opp.budget_range}</p>
                    </div>
                    <button className="opportunity-action">View Details</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'intelligence' && (
          <div className="intelligence-tab">
            <h2>🧠 Business Intelligence</h2>
            <p className="section-subtitle">Data-driven insights about your business</p>
            
            <div className="intelligence-grid">
              {intelligence.performance_insights && (
                <div className="intelligence-card">
                  <h3>📊 Performance Insights</h3>
                  <div className="insight-content">
                    <p><strong>Revenue Trends:</strong> {intelligence.performance_insights.revenue_trends?.monthly_growth || 'Analyzing...'}</p>
                    <p><strong>Client Analysis:</strong> {intelligence.performance_insights.client_analysis?.repeat_rate || 'Building data...'}</p>
                  </div>
                </div>
              )}
              
              <div className="intelligence-card">
                <h3>🎯 Growth Trajectory</h3>
                <div className="insight-content">
                  <p><strong>Current Stage:</strong> {intelligence.growth_trajectory?.current_stage || summary.business_stage}</p>
                  <p><strong>Growth Potential:</strong> {intelligence.growth_trajectory?.growth_multiplier || '2-3x revenue'}</p>
                </div>
              </div>
              
              {intelligence.risk_assessment && (
                <div className="intelligence-card">
                  <h3>⚠️ Risk Assessment</h3>
                  <div className="insight-content">
                    {intelligence.risk_assessment.slice(0, 2).map((risk, index) => (
                      <p key={index}><strong>{risk.risk}:</strong> {risk.impact} impact</p>
                    ))}
                  </div>
                </div>
              )}
              
              {intelligence.optimization_opportunities && (
                <div className="intelligence-card">
                  <h3>🚀 Optimization</h3>
                  <div className="insight-content">
                    {intelligence.optimization_opportunities.slice(0, 2).map((opp, index) => (
                      <p key={index}><strong>{opp.area}:</strong> {opp.potential}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <footer className="dashboard-footer">
        <p>💡 Your AI Business Partner is working 24/7 to find opportunities and optimize your business</p>
      </footer>
    </div>
  );
};

export default BusinessDashboard;