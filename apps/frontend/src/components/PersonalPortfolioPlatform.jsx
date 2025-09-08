import React, { useState, useEffect } from 'react';
import {
  Briefcase, Eye, TrendingUp, DollarSign, Users, Award,
  Plus, Filter, Grid, List, Search, Share2, Download,
  MessageCircle, Calendar, Target, BarChart3, Zap,
  Camera, Palette, Code, PenTool, Video, Globe,
  Star, ThumbsUp, Clock, ArrowRight, ExternalLink,
  Mail, Phone, MapPin, Trophy, CheckCircle, AlertCircle
} from 'lucide-react';

const PersonalPortfolioPlatform = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [projects, setProjects] = useState([]);
  const [portfolio, setPortfolio] = useState(null);
  const [opportunities, setOpportunities] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    initializeData();
  }, []);

  const initializeData = () => {
    // Mock user profile
    setProfile({
      name: "Alex Chen",
      title: "UI/UX Designer & Brand Strategist",
      location: "San Francisco, CA",
      email: "alex@designstudio.com",
      phone: "+1 (555) 123-4567",
      website: "alexchen.design",
      avatar: "👩‍🎨",
      bio: "Passionate designer with 5+ years creating digital experiences that drive business results.",
      skills: ["UI Design", "UX Research", "Branding", "Prototyping", "Web Design"],
      rates: { hourly: 85, project: 2500 },
      availability: "Available for new projects"
    });

    // Mock projects with enhanced metadata
    setProjects([
      {
        id: 1,
        title: "E-commerce Mobile App Redesign",
        category: "UI/UX Design",
        client: "TechStart Inc.",
        completed_date: "2024-01-15",
        project_value: 8500,
        duration_weeks: 6,
        thumbnail: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzY2NjZmZiIvPjx0ZXh0IHg9IjE1MCIgeT0iMTAwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+TW9iaWxlIEFwcCBVSTwvdGV4dD48L3N2Zz4=",
        description: "Complete UI/UX redesign increasing user engagement by 40%",
        technologies: ["Figma", "Principle", "React Native"],
        results: {
          engagement_increase: "40%",
          conversion_rate: "25%",
          user_satisfaction: "4.8/5"
        },
        casey_score: 92,
        portfolio_ready: true,
        case_study_complete: true,
        testimonial: "Alex delivered an exceptional design that transformed our user experience. Highly recommended!"
      },
      {
        id: 2,
        title: "SaaS Dashboard Interface",
        category: "Web Design",
        client: "DataFlow Solutions",
        completed_date: "2024-02-20",
        project_value: 5200,
        duration_weeks: 4,
        thumbnail: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzEwYjk4MSIvPjx0ZXh0IHg9IjE1MCIgeT0iMTAwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+U2FhUyBEYXNoYm9hcmQ8L3RleHQ+PC9zdmc+",
        description: "Analytics dashboard with advanced data visualization",
        technologies: ["React", "D3.js", "Tailwind CSS"],
        results: {
          data_comprehension: "60% faster",
          user_efficiency: "35%",
          error_reduction: "50%"
        },
        casey_score: 88,
        portfolio_ready: true,
        case_study_complete: false,
        testimonial: "The dashboard completely changed how our team works with data."
      },
      {
        id: 3,
        title: "Brand Identity System",
        category: "Branding",
        client: "GreenLeaf Organics",
        completed_date: "2024-03-10",
        project_value: 6800,
        duration_weeks: 8,
        thumbnail: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iIzA1OWY2OSIvPjx0ZXh0IHg9IjE1MCIgeT0iMTAwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+QnJhbmQgSWRlbnRpdHk8L3RleHQ+PC9zdmc+",
        description: "Complete brand identity for organic food startup",
        technologies: ["Illustrator", "InDesign", "After Effects"],
        results: {
          brand_recognition: "85% increase",
          market_presence: "3x growth",
          customer_trust: "90% positive"
        },
        casey_score: 95,
        portfolio_ready: true,
        case_study_complete: true,
        testimonial: "Alex created a brand identity that perfectly captures our values and resonates with our customers."
      }
    ]);

    // Mock job opportunities
    setOpportunities([
      {
        id: 1,
        title: "Senior UI Designer",
        company: "Innovation Labs",
        type: "Full-time",
        location: "Remote",
        salary: "$95k - $120k",
        match_score: 95,
        posted_date: "2024-03-15",
        description: "Looking for a creative UI designer with mobile app experience",
        skills_match: ["UI Design", "Mobile Apps", "Prototyping"],
        casey_recommendation: "Perfect match! Your mobile app redesign project aligns perfectly with their needs."
      },
      {
        id: 2,
        title: "Brand Designer (Contract)",
        company: "StartupStudio",
        type: "Contract",
        location: "San Francisco, CA",
        salary: "$80/hour",
        match_score: 88,
        posted_date: "2024-03-14",
        description: "3-month contract for complete brand identity project",
        skills_match: ["Branding", "Identity Design"],
        casey_recommendation: "Great fit based on your GreenLeaf Organics project. Your brand work shows exactly what they need."
      },
      {
        id: 3,
        title: "UX Research Consultant",
        company: "DataCorp",
        type: "Freelance",
        location: "Hybrid",
        salary: "$90/hour",
        match_score: 72,
        posted_date: "2024-03-13",
        description: "User research for SaaS platform redesign",
        skills_match: ["UX Research", "SaaS"],
        casey_recommendation: "Consider this opportunity to expand your research skills. Your dashboard project shows relevant experience."
      }
    ]);

    // Mock analytics
    setAnalytics({
      portfolio_views: 1247,
      project_inquiries: 23,
      conversion_rate: 18.5,
      avg_project_value: 6833,
      total_earnings: 20500,
      client_satisfaction: 4.9,
      repeat_clients: 65,
      skills_in_demand: ["UI Design", "Mobile Apps", "SaaS Design"],
      market_rate: {
        current: 85,
        suggested: 95,
        percentile: 78
      }
    });
  };

  const generatePortfolioSite = () => {
    // Simulate portfolio generation
    const portfolioData = {
      url: "alexchen-portfolio.mindforge.ai",
      theme: "modern-minimal",
      sections: ["Hero", "Featured Work", "Case Studies", "About", "Contact"],
      projects: projects.filter(p => p.portfolio_ready),
      seo_optimized: true,
      mobile_responsive: true,
      load_speed: "A+",
      analytics_enabled: true
    };
    
    setPortfolio(portfolioData);
  };

  const getOpportunityIcon = (type) => {
    const icons = {
      'Full-time': Briefcase,
      'Contract': Clock,
      'Freelance': Users
    };
    return icons[type] || Briefcase;
  };

  const getCategoryIcon = (category) => {
    const icons = {
      'UI/UX Design': PenTool,
      'Web Design': Globe,
      'Branding': Palette,
      'Mobile Design': Camera
    };
    return icons[category] || PenTool;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Personal Portfolio Platform</h1>
          <p className="text-gray-600 mt-2">Manage your creative portfolio and career opportunities</p>
        </div>
        
        {/* Navigation */}
        <div className="flex space-x-1 mb-8 border-b">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
            { id: 'projects', label: 'Projects', icon: Grid },
            { id: 'portfolio', label: 'Portfolio', icon: Eye },
            { id: 'opportunities', label: 'Opportunities', icon: Target },
            { id: 'profile', label: 'Profile', icon: Users }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-4 py-3 border-b-2 text-sm font-medium transition-colors ${
                  activeTab === tab.id 
                    ? 'border-blue-500 text-blue-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">Dashboard Overview</h2>
            
            {/* Analytics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg p-6 border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Portfolio Views</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics.portfolio_views?.toLocaleString()}</p>
                  </div>
                  <Eye className="h-8 w-8 text-blue-500" />
                </div>
              </div>
              
              <div className="bg-white rounded-lg p-6 border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Project Inquiries</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics.project_inquiries}</p>
                  </div>
                  <MessageCircle className="h-8 w-8 text-green-500" />
                </div>
              </div>
              
              <div className="bg-white rounded-lg p-6 border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Avg Project Value</p>
                    <p className="text-2xl font-bold text-gray-900">${analytics.avg_project_value?.toLocaleString()}</p>
                  </div>
                  <DollarSign className="h-8 w-8 text-yellow-500" />
                </div>
              </div>
              
              <div className="bg-white rounded-lg p-6 border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">Client Satisfaction</p>
                    <p className="text-2xl font-bold text-gray-900">{analytics.client_satisfaction}/5</p>
                  </div>
                  <Star className="h-8 w-8 text-purple-500" />
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg p-6 border">
              <h3 className="text-lg font-semibold mb-4">Recent Projects</h3>
              <div className="space-y-4">
                {projects.slice(0, 3).map(project => {
                  const CategoryIcon = getCategoryIcon(project.category);
                  return (
                    <div key={project.id} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                      <CategoryIcon className="w-8 h-8 text-blue-500" />
                      <div className="flex-1">
                        <h4 className="font-medium">{project.title}</h4>
                        <p className="text-sm text-gray-600">{project.client} • ${project.project_value.toLocaleString()}</p>
                      </div>
                      <div className="text-right">
                        <div className={`px-2 py-1 rounded text-xs font-medium ${
                          project.casey_score >= 90 ? 'bg-green-100 text-green-800' :
                          project.casey_score >= 80 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          Casey Score: {project.casey_score}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Projects Tab */}
        {activeTab === 'projects' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Projects</h2>
              <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 flex items-center space-x-2">
                <Plus className="w-4 h-4" />
                <span>Add Project</span>
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map(project => {
                const CategoryIcon = getCategoryIcon(project.category);
                return (
                  <div key={project.id} className="bg-white rounded-lg border overflow-hidden">
                    <img 
                      src={project.thumbnail} 
                      alt={project.title}
                      className="w-full h-48 object-cover"
                    />
                    <div className="p-6">
                      <div className="flex items-center space-x-2 mb-2">
                        <CategoryIcon className="w-4 h-4 text-blue-500" />
                        <span className="text-sm text-gray-600">{project.category}</span>
                      </div>
                      <h3 className="font-semibold text-lg mb-2">{project.title}</h3>
                      <p className="text-gray-600 text-sm mb-3">{project.description}</p>
                      
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-lg font-bold text-green-600">
                          ${project.project_value.toLocaleString()}
                        </span>
                        <div className={`px-2 py-1 rounded text-xs font-medium ${
                          project.casey_score >= 90 ? 'bg-green-100 text-green-800' :
                          project.casey_score >= 80 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {project.casey_score}% Casey
                        </div>
                      </div>
                      
                      <div className="flex space-x-1 mb-3">
                        {project.technologies.map(tech => (
                          <span key={tech} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                            {tech}
                          </span>
                        ))}
                      </div>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>{project.completed_date}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="w-4 h-4" />
                          <span>{project.duration_weeks}w</span>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Portfolio Tab */}
        {activeTab === 'portfolio' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Portfolio Site</h2>
              <button 
                onClick={generatePortfolioSite}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 flex items-center space-x-2"
              >
                <Zap className="w-4 h-4" />
                <span>Generate Portfolio</span>
              </button>
            </div>
            
            {portfolio ? (
              <div className="bg-white rounded-lg p-6 border">
                <div className="flex items-center space-x-4 mb-6">
                  <CheckCircle className="w-8 h-8 text-green-500" />
                  <div>
                    <h3 className="text-lg font-semibold">Portfolio Generated Successfully!</h3>
                    <p className="text-gray-600">Your portfolio is live and ready to share</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium mb-3">Portfolio Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">URL:</span>
                        <a href="#" className="text-blue-600 hover:underline">{portfolio.url}</a>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Theme:</span>
                        <span>{portfolio.theme}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Projects:</span>
                        <span>{portfolio.projects.length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Load Speed:</span>
                        <span className="text-green-600">{portfolio.load_speed}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-3">Features</h4>
                    <div className="space-y-2">
                      {[
                        { label: 'SEO Optimized', enabled: portfolio.seo_optimized },
                        { label: 'Mobile Responsive', enabled: portfolio.mobile_responsive },
                        { label: 'Analytics Enabled', enabled: portfolio.analytics_enabled }
                      ].map(feature => (
                        <div key={feature.label} className="flex items-center space-x-2">
                          {feature.enabled ? (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-gray-400" />
                          )}
                          <span className="text-sm">{feature.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="flex space-x-3 mt-6">
                  <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 flex items-center space-x-2">
                    <Eye className="w-4 h-4" />
                    <span>View Portfolio</span>
                  </button>
                  <button className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 flex items-center space-x-2">
                    <Share2 className="w-4 h-4" />
                    <span>Share</span>
                  </button>
                  <button className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 flex items-center space-x-2">
                    <Download className="w-4 h-4" />
                    <span>Download</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg p-8 border text-center">
                <Globe className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Portfolio Generated Yet</h3>
                <p className="text-gray-600 mb-4">Generate your portfolio site to showcase your work to potential clients</p>
                <button 
                  onClick={generatePortfolioSite}
                  className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600"
                >
                  Generate Portfolio Site
                </button>
              </div>
            )}
          </div>
        )}

        {/* Opportunities Tab */}
        {activeTab === 'opportunities' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">Job Opportunities</h2>
              <div className="flex space-x-2">
                <button className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 flex items-center space-x-2">
                  <Filter className="w-4 h-4" />
                  <span>Filter</span>
                </button>
                <button className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 flex items-center space-x-2">
                  <Search className="w-4 h-4" />
                  <span>Search</span>
                </button>
              </div>
            </div>
            
            <div className="space-y-4">
              {opportunities.map(opp => {
                const TypeIcon = getOpportunityIcon(opp.type);
                return (
                  <div key={opp.id} className="bg-white rounded-lg p-6 border">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <TypeIcon className="w-5 h-5 text-gray-500" />
                          <h3 className="text-lg font-semibold">{opp.title}</h3>
                          <div className={`px-2 py-1 rounded text-xs font-medium ${
                            opp.match_score >= 90 ? 'bg-green-100 text-green-800' :
                            opp.match_score >= 80 ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {opp.match_score}% match
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-4 mb-3">
                          <span className="font-medium">{opp.company}</span>
                          <span className="text-gray-500">•</span>
                          <span className="text-gray-600">{opp.location}</span>
                          <span className="text-gray-500">•</span>
                          <span className="text-green-600 font-medium">{opp.salary}</span>
                        </div>
                        
                        <p className="text-gray-700 mb-3">{opp.description}</p>
                        
                        <div className="flex items-center space-x-4 mb-3">
                          <div>
                            <span className="text-sm text-gray-500">Skills Match:</span>
                            <div className="flex space-x-1 mt-1">
                              {opp.skills_match.map(skill => (
                                <span key={skill} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-blue-50 rounded-lg p-3">
                          <div className="flex items-start space-x-2">
                            <Zap className="w-4 h-4 text-blue-500 mt-0.5" />
                            <div>
                              <div className="text-sm font-medium text-blue-900">Casey's Recommendation</div>
                              <div className="text-sm text-blue-800">{opp.casey_recommendation}</div>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex flex-col space-y-2 ml-6">
                        <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 text-sm">
                          Apply Now
                        </button>
                        <button className="border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 text-sm">
                          Save
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">Professional Profile</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Profile Info */}
              <div className="lg:col-span-2 space-y-6">
                <div className="bg-white rounded-lg p-6 border">
                  <h3 className="font-semibold mb-4">Basic Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                      <input type="text" value={profile?.name} className="w-full p-2 border border-gray-300 rounded-lg" readOnly />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Professional Title</label>
                      <input type="text" value={profile?.title} className="w-full p-2 border border-gray-300 rounded-lg" readOnly />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                      <input type="email" value={profile?.email} className="w-full p-2 border border-gray-300 rounded-lg" readOnly />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                      <input type="tel" value={profile?.phone} className="w-full p-2 border border-gray-300 rounded-lg" readOnly />
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-lg p-6 border">
                  <h3 className="font-semibold mb-4">Skills & Expertise</h3>
                  <div className="flex flex-wrap gap-2">
                    {profile?.skills.map(skill => (
                      <span key={skill} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Rates & Availability */}
              <div className="space-y-6">
                <div className="bg-white rounded-lg p-6 border">
                  <h3 className="font-semibold mb-4">Rates & Availability</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Hourly Rate</label>
                      <div className="text-2xl font-bold text-green-600">${profile?.rates.hourly}/hour</div>
                      <div className="text-sm text-gray-500">78th percentile</div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Project Minimum</label>
                      <div className="text-lg font-semibold">${profile?.rates.project.toLocaleString()}</div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Availability</label>
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                        <span className="text-sm">{profile?.availability}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonalPortfolioPlatform;