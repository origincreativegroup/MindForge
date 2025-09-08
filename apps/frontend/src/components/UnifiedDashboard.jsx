import React from 'react';
import BusinessDashboard from './BusinessDashboard.jsx';
import CreatorDashboard from './CreatorDashboard.jsx';
import './BusinessDashboard.css';

const UnifiedDashboard = () => {
  return (
    <div className="unified-dashboard">
      <BusinessDashboard />
      <CreatorDashboard />
    </div>
  );
};

export default UnifiedDashboard;

