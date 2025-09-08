import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Area, AreaChart
} from 'recharts';
import {
  TrendingUp, Users, Clock, CheckCircle, AlertCircle,
  Download, Share2, Filter, Calendar, Search,
  Eye, MessageCircle, FileText, Video, Palette, Zap
} from 'lucide-react';

const ProjectDashboard = () => {
  const [projects, setProjects] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d');
  const [selectedProjectType, setSelectedProjectType] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, [selectedTimeRange, selectedProjectType]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Mock data for demonstration - in real app would fetch from API
      const mockProjects = [
        {
          id: 1,
          name: "Brand Identity Redesign",
          project_type: "branding",
          status: "in_progress",
          updated_at: "2024-01-15T10:30:00Z"
        },
        {
          id: 2,
          name: "Social Media Campaign",
          project_type: "social_media",
          status: "completed",
          updated_at: "2024-01-14T15:45:00Z"
        },
        {
          id: 3,
          name: "Website Landing Page",
          project_type: "website_mockup",
          status: "review",
          updated_at: "2024-01-13T09:20:00Z"
        },
        {
          id: 4,
          name: "Product Catalog",
          project_type: "print_graphic",
          status: "planning",
          updated_at: "2024-01-12T14:10:00Z"
        },
        {
          id: 5,
          name: "Promotional Video",
          project_type: "video",
          status: "in_progress",
          updated_at: "2024-01-11T11:30:00Z"
        }
      ];

      const mockAnalytics = {
        summary: {
          totalProjects: 25,
          completedProjects: 18,
          inProgress: 5,
          avgCompletionTime: "4.2 days",
          teamProductivity: 0.87
        },
        projectsByType: [
          { name: "Website Mockups", value: 8, color: "#3B82F6" },
          { name: "Social Media", value: 6, color: "#10B981" },
          { name: "Print Graphics", value: 4, color: "#F59E0B" },
          { name: "Video", value: 3, color: "#EF4444" },
          { name: "Branding", value: 3, color: "#8B5CF6" },
          { name: "Other", value: 1, color: "#6B7280" }
        ],
        completionTrend: [
          { day: "Mon", completed: 3, started: 2 },
          { day: "Tue", completed: 5, started: 4 },
          { day: "Wed", completed: 2, started: 3 },
          { day: "Thu", completed: 4, started: 1 },
          { day: "Fri", completed: 6, started: 5 },
          { day: "Sat", completed: 1, started: 2 },
          { day: "Sun", completed: 2, started: 1 }
        ],
        qualityScores: [
          { project: "Brand Identity Redesign", score: 0.95 },
          { project: "Social Media Campaign", score: 0.88 },
          { project: "Website Landing Page", score: 0.92 },
          { project: "Product Catalog", score: 0.85 },
          { project: "Promotional Video", score: 0.91 }
        ]
      };

      setProjects(mockProjects);
      setAnalytics(mockAnalytics);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const projectTypeIcons = {
    website_mockup: Eye,
    social_media: MessageCircle,
    print_graphic: FileText,
    video: Video,
    branding: Palette,
    other: Zap
  };

  const getProjectTypeIcon = (type) => {
    const IconComponent = projectTypeIcons[type] || Zap;
    return <IconComponent className="w-4 h-4 text-gray-600" />;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'review':
        return 'bg-yellow-100 text-yellow-800';
      case 'planning':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
          <p className="mt-4 text-gray-600">Failed to load dashboard data</p>
        </div>
      </div>
    );
  }

  const currentAnalytics = analytics;

  return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Creative Projects Dashboard</h1>
          <p className="text-gray-600 mt-1">Track and analyze your creative project performance</p>
        </div>
        <div className="flex items-center space-x-4">
          <select 
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          
          <button className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
            <Download className="w-4 h-4 mr-2" />
            Export Report
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Projects</p>
              <p className="text-2xl font-bold text-gray-900">{currentAnalytics.summary.totalProjects}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
            <span className="text-green-600">+12% from last month</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Completed</p>
              <p className="text-2xl font-bold text-gray-900">{currentAnalytics.summary.completedProjects}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-gray-600">
              {Math.round((currentAnalytics.summary.completedProjects / currentAnalytics.summary.totalProjects) * 100)}% completion rate
            </span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">In Progress</p>
              <p className="text-2xl font-bold text-gray-900">{currentAnalytics.summary.inProgress}</p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className="text-gray-600">Avg: {currentAnalytics.summary.avgCompletionTime}</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Team Productivity</p>
              <p className="text-2xl font-bold text-gray-900">
                {Math.round(currentAnalytics.summary.teamProductivity * 100)}%
              </p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
            <span className="text-green-600">+5% this week</span>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Project Types Distribution */}
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Projects by Type</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={currentAnalytics.projectsByType}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  dataKey="value"
                  nameKey="name"
                >
                  {currentAnalytics.projectsByType.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {currentAnalytics.projectsByType.map((type, index) => (
              <div key={index} className="flex items-center text-sm">
                <div 
                  className="w-3 h-3 rounded-full mr-2" 
                  style={{ backgroundColor: type.color }}
                ></div>
                <span>{type.name}: {type.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Completion Trend */}
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Weekly Activity</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={currentAnalytics.completionTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="completed" fill="#10B981" name="Completed" />
                <Bar dataKey="started" fill="#3B82F6" name="Started" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Quality Scores and Recent Projects */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quality Scores */}
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Top Quality Scores</h3>
          <div className="space-y-3">
            {currentAnalytics.qualityScores.map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 truncate flex-1 mr-2">{item.project}</span>
                <div className="flex items-center">
                  <span className={`text-sm font-medium ${getPriorityColor(item.score)}`}>
                    {Math.round(item.score * 100)}%
                  </span>
                  <div className="w-16 h-2 bg-gray-200 rounded-full ml-2">
                    <div 
                      className={`h-2 rounded-full ${
                        item.score >= 0.8 ? 'bg-green-500' : 
                        item.score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${item.score * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Projects */}
        <div className="lg:col-span-2 bg-white p-6 rounded-lg border">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Recent Projects</h3>
            <button className="text-sm text-blue-600 hover:text-blue-800">View All</button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left pb-2 font-medium text-gray-700">Project</th>
                  <th className="text-left pb-2 font-medium text-gray-700">Type</th>
                  <th className="text-left pb-2 font-medium text-gray-700">Status</th>
                  <th className="text-left pb-2 font-medium text-gray-700">Progress</th>
                  <th className="text-left pb-2 font-medium text-gray-700">Updated</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {projects.slice(0, 5).map((project) => (
                  <tr key={project.id} className="hover:bg-gray-50">
                    <td className="py-3">
                      <div className="flex items-center">
                        {getProjectTypeIcon(project.project_type)}
                        <span className="ml-2 font-medium text-gray-900 truncate">
                          {project.name}
                        </span>
                      </div>
                    </td>
                    <td className="py-3">
                      <span className="capitalize text-gray-600">
                        {project.project_type.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(project.status)}`}>
                        {project.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3">
                      <div className="flex items-center">
                        <div className="w-12 h-2 bg-gray-200 rounded-full mr-2">
                          <div 
                            className="h-2 bg-blue-500 rounded-full"
                            style={{ 
                              width: project.status === 'completed' ? '100%' : 
                                     project.status === 'in_progress' ? '60%' :
                                     project.status === 'review' ? '80%' : '30%'
                            }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-600">
                          {project.status === 'completed' ? '100%' : 
                           project.status === 'in_progress' ? '60%' :
                           project.status === 'review' ? '80%' : '30%'}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 text-gray-600">
                      {new Date(project.updated_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors">
            <div className="p-2 bg-blue-100 rounded-lg mr-3">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div className="text-left">
              <div className="font-medium text-gray-900">New Project</div>
              <div className="text-sm text-gray-500">Upload & analyze</div>
            </div>
          </button>

          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:bg-green-50 transition-colors">
            <div className="p-2 bg-green-100 rounded-lg mr-3">
              <Download className="w-5 h-5 text-green-600" />
            </div>
            <div className="text-left">
              <div className="font-medium text-gray-900">Export Report</div>
              <div className="text-sm text-gray-500">Download insights</div>
            </div>
          </button>

          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-colors">
            <div className="p-2 bg-purple-100 rounded-lg mr-3">
              <Users className="w-5 h-5 text-purple-600" />
            </div>
            <div className="text-left">
              <div className="font-medium text-gray-900">Team View</div>
              <div className="text-sm text-gray-500">Collaboration</div>
            </div>
          </button>

          <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:border-yellow-300 hover:bg-yellow-50 transition-colors">
            <div className="p-2 bg-yellow-100 rounded-lg mr-3">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
            </div>
            <div className="text-left">
              <div className="font-medium text-gray-900">Alerts</div>
              <div className="text-sm text-gray-500">Review pending</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProjectDashboard;