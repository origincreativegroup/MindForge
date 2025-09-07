import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Upload, MessageCircle, Eye, Palette, FileText, Video, Image,
  Users, Settings, BarChart3, Download, Share2, Zap, Bell,
  MousePointer2, Mic, MicOff, Camera, CameraOff,
  Maximize2, Minimize2, RefreshCw, Send, Bot,
  Clock, CheckCircle, AlertCircle, Info, X, Plus,
  ThumbsUp, ThumbsDown, Flag, Edit3, Trash2, Reply,
  Circle, Square, ArrowRight, Type, Highlighter
} from 'lucide-react';

const CreativeWorkspace = () => {
  // State management
  const [selectedProject, setSelectedProject] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [projects, setProjects] = useState([]);
  const [teamMembers, setTeamMembers] = useState([]);
  const [comments, setComments] = useState([]);
  const [activities, setActivities] = useState([]);
  const [insights, setInsights] = useState([]);
  const [caseyMessages, setCaseyMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [connectedUsers, setConnectedUsers] = useState([]);
  const [userCursors, setUserCursors] = useState({});
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState([]);

  // Refs
  const fileInputRef = useRef(null);
  const websocketRef = useRef(null);
  const canvasRef = useRef(null);
  const messagesEndRef = useRef(null);

  // WebSocket connection
  useEffect(() => {
    if (selectedProject) {
      connectWebSocket(selectedProject.id);
    }

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, [selectedProject]);

  const connectWebSocket = (projectId) => {
    const wsUrl = `ws://localhost:8000/ws/project/${projectId}?user_id=1`;
    websocketRef.current = new WebSocket(wsUrl);

    websocketRef.current.onopen = () => {
      console.log('WebSocket connected');
    };

    websocketRef.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };

    websocketRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocketRef.current.onclose = () => {
      console.log('WebSocket disconnected');
    };
  };

  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'connection_established':
        setConnectedUsers(message.connected_users || []);
        break;
      case 'user_presence':
        setConnectedUsers(Object.keys(message.users || {}));
        break;
      case 'cursor_update':
        setUserCursors(prev => ({
          ...prev,
          [message.user_id]: message.position
        }));
        break;
      case 'new_comment':
        setComments(prev => [message.comment, ...prev]);
        addNotification('New comment added', 'info');
        break;
      case 'casey_analysis_start':
        setIsAnalyzing(true);
        addNotification('Casey is analyzing your project…', 'info');
        break;
      case 'casey_analysis_complete':
        setIsAnalyzing(false);
        addNotification(`Casey found ${message.insights_count} insights!`, 'success');
        fetchInsights();
        break;
      case 'project_update':
        addNotification('Project updated', 'info');
        break;
      default:
        console.log('Unhandled message type:', message.type);
    }
  };

  const sendWebSocketMessage = (message) => {
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify(message));
    }
  };

  // Mock data initialization
  useEffect(() => {
    initializeMockData();
  }, []);

  const initializeMockData = () => {
    setProjects([
      {
        id: 1,
        name: 'Brand Redesign Project',
        type: 'branding',
        status: 'in_progress',
        thumbnail: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEyMCIgZmlsbD0iIzM5OGY3OSIvPjx0ZXh0IHg9IjEwMCIgeT0iNjAiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5CcmFuZCBEZXNpZ248L3RleHQ+PC9zdmc+',
        created_at: '2024-01-15',
        team_count: 4,
        progress: 75
      },
      {
        id: 2,
        name: 'Social Media Campaign',
        type: 'social_media',
        status: 'review',
        thumbnail: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEyMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEyMCIgZmlsbD0iIzZiNzNmZiIvPjx0ZXh0IHg9IjEwMCIgeT0iNjAiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5Tb2NpYWwgTWVkaWE8L3RleHQ+PC9zdmc+',
        created_at: '2024-01-20',
        team_count: 3,
        progress: 90
      }
    ]);

    setTeamMembers([
      { id: 1, name: 'You', email: 'you@company.com', role: 'Designer', avatar: '👤', online: true },
      { id: 2, name: 'Sarah Chen', email: 'sarah@company.com', role: 'Creative Director', avatar: '👩‍🎨', online: true },
      { id: 3, name: 'Mike Johnson', email: 'mike@company.com', role: 'Developer', avatar: '👨‍💻', online: false },
      { id: 4, name: 'Casey AI', email: 'casey@mindforge.ai', role: 'AI Assistant', avatar: '🤖', online: true }
    ]);

    setCaseyMessages([
      {
        id: 1,
        sender: 'casey',
        content: "Hi! I've analyzed your project and I'm excited to share some insights. Your brand redesign shows strong visual hierarchy and excellent color harmony. Ready to dive into the details?",
        timestamp: new Date(Date.now() - 300000),
        type: 'analysis'
      }
    ]);

    setComments([
      {
        id: 1,
        author: { name: 'Sarah Chen', avatar: '👩‍🎨' },
        content: 'Love the new color palette! The blue gradients work really well with the brand personality.',
        timestamp: new Date(Date.now() - 120000),
        type: 'approval',
        resolved: false,
        coordinates: { x: 45, y: 30 }
      }
    ]);

    setInsights([
      {
        id: 1,
        type: 'color_harmony',
        title: 'Excellent Color Harmony',
        description: 'Your color palette demonstrates strong complementary relationships',
        score: 0.92,
        category: 'design'
      },
      {
        id: 2,
        type: 'accessibility',
        title: 'Accessibility Compliance',
        description: 'Text contrast meets WCAG AA standards',
        score: 0.88,
        category: 'accessibility'
      }
    ]);
  };

  // Utility functions
  const addNotification = (message, type = 'info') => {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date()
    };
    setNotifications(prev => [notification, ...prev.slice(0, 4)]);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  };

  const fetchInsights = async () => {
    // Simulate API call
    setTimeout(() => {
      setInsights(prev => [...prev, {
        id: Date.now(),
        type: 'new_analysis',
        title: 'Typography Enhancement',
        description: 'Consider increasing font weight for better readability',
        score: 0.76,
        category: 'typography'
      }]);
    }, 1000);
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Simulate upload process
    setIsAnalyzing(true);

    setTimeout(() => {
      const newProject = {
        id: Date.now(),
        name: file.name.split('.')[0],
        type: 'website_mockup',
        status: 'analyzing',
        thumbnail: URL.createObjectURL(file),
        created_at: new Date().toISOString().split('T')[0],
        team_count: 1,
        progress: 0
      };
      
      setProjects(prev => [newProject, ...prev]);
      setSelectedProject(newProject);
      setIsAnalyzing(false);
      addNotification('Project uploaded successfully!', 'success');
    }, 2000);
  };

  const sendMessage = () => {
    if (!newMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      content: newMessage,
      timestamp: new Date(),
      type: 'question'
    };

    setCaseyMessages(prev => [...prev, userMessage]);
    setNewMessage('');

    // Simulate Casey's response
    setTimeout(() => {
      const caseyResponse = {
        id: Date.now() + 1,
        sender: 'casey',
        content: generateCaseyResponse(newMessage),
        timestamp: new Date(),
        type: 'response'
      };
      setCaseyMessages(prev => [...prev, caseyResponse]);
    }, 1500);
  };

  const generateCaseyResponse = (userMessage) => {
    const responses = {
      'color': "Great question about colors! Your current palette has strong harmony. I'd suggest considering accessibility - ensure sufficient contrast for text readability. Would you like me to analyze specific color combinations?",
      'improve': "I see several opportunities for improvement: 1) Enhance visual hierarchy with better spacing, 2) Consider mobile responsiveness, 3) Add micro-interactions for engagement. Which area interests you most?",
      'feedback': "Your project shows excellent creative direction! The composition follows solid design principles. I'm particularly impressed with your use of white space and typography choices. Any specific aspects you'd like me to dive deeper into?"
    };

    for (const [key, response] of Object.entries(responses)) {
      if (userMessage.toLowerCase().includes(key)) {
        return response;
      }
    }

    return "That's an interesting question! Based on your project, I can help with design feedback, color analysis, accessibility improvements, and creative suggestions. What specific aspect would you like to explore?";
  };

  const handleMouseMove = (e) => {
    if (selectedProject && websocketRef.current) {
      const rect = e.currentTarget.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;

      sendWebSocketMessage({
        type: 'cursor_move',
        position: { x, y }
      });
    }
  };

  const addComment = (x, y) => {
    const content = prompt('Add a comment:');
    if (!content) return;

    const newComment = {
      id: Date.now(),
      author: { name: 'You', avatar: '👤' },
      content,
      timestamp: new Date(),
      type: 'general',
      resolved: false,
      coordinates: { x, y }
    };

    setComments(prev => [newComment, ...prev]);

    if (websocketRef.current) {
      sendWebSocketMessage({
        type: 'add_comment',
        comment_data: {
          content,
          comment_type: 'general',
          metadata: { coordinates: { x, y } }
        }
      });
    }
  };

  const getProjectIcon = (type) => {
    const icons = {
      website_mockup: Eye,
      social_media: MessageCircle,
      print_graphic: FileText,
      video: Video,
      branding: Palette,
      other: Image
    };
    return icons[type] || Image;
  };

  const getStatusColor = (status) => {
    const colors = {
      uploaded: 'bg-blue-100 text-blue-800',
      analyzing: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-purple-100 text-purple-800',
      review: 'bg-indigo-100 text-indigo-800',
      completed: 'bg-green-100 text-green-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept="image/*,.pdf,.ai,.psd,.sketch"
        onChange={handleFileUpload}
      />

      {/* Sidebar */}
      <div className={`bg-white border-r transition-all duration-300 ${sidebarCollapsed ? 'w-16' : 'w-80'}`}>
        {/* Header */}
        <div className="p-4 border-b flex items-center justify-between">
          {!sidebarCollapsed && (
            <h1 className="text-xl font-bold text-gray-800">MindForge</h1>
          )}
          <button 
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            {sidebarCollapsed ? <Maximize2 className="w-5 h-5" /> : <Minimize2 className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation */}
        {!sidebarCollapsed && (
          <div className="p-4 border-b">
            <button 
              onClick={() => fileInputRef.current?.click()}
              className="w-full bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center space-x-2"
            >
              <Upload className="w-4 h-4" />
              <span>Upload Project</span>
            </button>
          </div>
        )}

        {/* Projects List */}
        {!sidebarCollapsed && (
          <div className="flex-1 overflow-y-auto p-4">
            <h3 className="font-semibold text-gray-700 mb-3">Projects</h3>
            <div className="space-y-2">
              {projects.map(project => {
                const IconComponent = getProjectIcon(project.type);
                return (
                  <div
                    key={project.id}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      selectedProject?.id === project.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                    onClick={() => setSelectedProject(project)}
                  >
                    <div className="flex items-center space-x-3">
                      <img 
                        src={project.thumbnail} 
                        alt={project.name}
                        className="w-12 h-8 object-cover rounded"
                      />
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 truncate">{project.name}</h4>
                        <div className="flex items-center space-x-2 mt-1">
                          <IconComponent className="w-3 h-3 text-gray-500" />
                          <span className={`px-2 py-1 rounded text-xs ${getStatusColor(project.status)}`}>
                            {project.status.replace('_', ' ')}
                          </span>
                        </div>
                        <div className="mt-2">
                          <div className="w-full bg-gray-200 rounded-full h-1">
                            <div 
                              className="bg-blue-500 h-1 rounded-full transition-all"
                              style={{ width: `${project.progress}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Team Members */}
            <div className="mt-6">
              <h3 className="font-semibold text-gray-700 mb-3">Team</h3>
              <div className="space-y-2">
                {teamMembers.map(member => (
                  <div key={member.id} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50">
                    <div className="relative">
                      <span className="text-2xl">{member.avatar}</span>
                      {member.online && (
                        <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">{member.name}</p>
                      <p className="text-sm text-gray-500 truncate">{member.role}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="bg-white border-b px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {selectedProject && (
                <>
                  <h2 className="text-xl font-semibold text-gray-900">{selectedProject.name}</h2>
                  <span className={`px-3 py-1 rounded-full text-sm ${getStatusColor(selectedProject.status)}`}>
                    {selectedProject.status.replace('_', ' ')}
                  </span>
                  {isAnalyzing && (
                    <div className="flex items-center space-x-2 text-yellow-600">
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span className="text-sm">Analyzing...</span>
                    </div>
                  )}
                </>
              )}
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Connected Users */}
              {connectedUsers.length > 0 && (
                <div className="flex items-center space-x-2">
                  <div className="flex -space-x-2">
                    {connectedUsers.slice(0, 3).map((userId, index) => (
                      <div
                        key={userId}
                        className="w-8 h-8 bg-blue-500 rounded-full border-2 border-white flex items-center justify-center text-white text-xs font-medium"
                        title={`User ${userId}`}
                      >
                        {userId}
                      </div>
                    ))}
                  </div>
                  {connectedUsers.length > 3 && (
                    <span className="text-sm text-gray-500">+{connectedUsers.length - 3}</span>
                  )}
                </div>
              )}

              {/* Notifications */}
              <div className="relative">
                <button 
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="p-2 hover:bg-gray-100 rounded-lg relative"
                >
                  <Bell className="w-5 h-5" />
                  {notifications.length > 0 && (
                    <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white">{notifications.length}</span>
                    </div>
                  )}
                </button>
                
                {showNotifications && (
                  <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-lg border z-50">
                    <div className="p-4 border-b">
                      <h3 className="font-semibold">Notifications</h3>
                    </div>
                    <div className="max-h-64 overflow-y-auto">
                      {notifications.map(notification => (
                        <div key={notification.id} className="p-3 border-b hover:bg-gray-50">
                          <div className="flex items-start space-x-3">
                            <div className={`w-2 h-2 rounded-full mt-2 ${
                              notification.type === 'success' ? 'bg-green-500' :
                              notification.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
                            }`} />
                            <div className="flex-1">
                              <p className="text-sm text-gray-900">{notification.message}</p>
                              <p className="text-xs text-gray-500 mt-1">
                                {notification.timestamp.toLocaleTimeString()}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <button className="p-2 hover:bg-gray-100 rounded-lg">
                <Share2 className="w-5 h-5" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg">
                <Download className="w-5 h-5" />
              </button>
              <button className="p-2 hover:bg-gray-100 rounded-lg">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex space-x-1 mt-4">
            {['overview', 'analysis', 'comments', 'activity'].map(tab => (
              <button 
                key={tab} 
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeTab === tab 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden">
          {selectedProject ? (
            <>
              {/* User Cursors */}
              {Object.entries(userCursors).map(([userId, position]) => (
                <div
                  key={userId}
                  className="absolute pointer-events-none z-40"
                  style={{ 
                    left: `${position.x}%`, 
                    top: `${position.y}%`,
                    transform: 'translate(-50%, -50%)'
                  }}
                >
                  <MousePointer2 className="w-4 h-4 text-blue-500" />
                  <span className="ml-2 text-xs bg-blue-500 text-white px-2 py-1 rounded">
                    User {userId}
                  </span>
                </div>
              ))}

              {activeTab === 'overview' && (
                <div 
                  className="relative h-full bg-white"
                  onMouseMove={handleMouseMove}
                  onDoubleClick={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect();
                    const x = ((e.clientX - rect.left) / rect.width) * 100;
                    const y = ((e.clientY - rect.top) / rect.height) * 100;
                    addComment(x, y);
                  }}
                >
                  <img 
                    src={selectedProject.thumbnail} 
                    alt={selectedProject.name}
                    className="w-full h-full object-contain"
                  />
                  
                  {/* Comment pins */}
                  {comments.map(comment => (
                    <div
                      key={comment.id}
                      className="absolute w-4 h-4 bg-blue-500 rounded-full cursor-pointer hover:bg-blue-600 transition-colors"
                      style={{ 
                        left: `${comment.coordinates.x}%`, 
                        top: `${comment.coordinates.y}%`,
                        transform: 'translate(-50%, -50%)'
                      }}
                      title={comment.content}
                    />
                  ))}
                </div>
              )}

              {activeTab === 'analysis' && (
                <div className="p-6 space-y-6 overflow-y-auto">
                  <div className="bg-white rounded-lg p-6 border">
                    <h3 className="text-lg font-semibold mb-4">AI Insights</h3>
                    <div className="grid gap-4">
                      {insights.map(insight => (
                        <div key={insight.id} className="border rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium">{insight.title}</h4>
                            <span className={`px-2 py-1 rounded text-xs ${
                              insight.score > 0.8 ? 'bg-green-100 text-green-800' :
                              insight.score > 0.6 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {Math.round(insight.score * 100)}%
                            </span>
                          </div>
                          <p className="text-gray-600">{insight.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'comments' && (
                <div className="p-6 space-y-4 overflow-y-auto">
                  <div className="bg-white rounded-lg p-6 border">
                    <h3 className="text-lg font-semibold mb-4">Comments</h3>
                    <div className="space-y-4">
                      {comments.map(comment => (
                        <div key={comment.id} className="border-b pb-4">
                          <div className="flex items-start space-x-3">
                            <span className="text-2xl">{comment.author.avatar}</span>
                            <div className="flex-1">
                              <div className="flex items-center space-x-2">
                                <span className="font-medium">{comment.author.name}</span>
                                <span className="text-sm text-gray-500">
                                  {comment.timestamp.toLocaleTimeString()}
                                </span>
                              </div>
                              <p className="text-gray-700 mt-1">{comment.content}</p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'activity' && (
                <div className="p-6 space-y-6 overflow-y-auto">
                  <div className="bg-white rounded-lg p-6 border">
                    <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                    <div className="space-y-4">
                      <div className="flex space-x-4 p-4 border-l-4 border-blue-500 bg-blue-50">
                        <Clock className="w-5 h-5 text-blue-500 mt-1" />
                        <div>
                          <p className="font-medium">Project uploaded</p>
                          <p className="text-sm text-gray-600">Casey started analyzing your design</p>
                          <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-xl font-semibold text-gray-600 mb-2">Welcome to MindForge Casey</h3>
                <p className="text-gray-500 mb-4">Upload your first creative project to get started</p>
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Upload Project
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Casey Chat Sidebar */}
      <div className="w-96 bg-white border-l flex flex-col">
        <div className="p-4 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold">Casey AI</h3>
              <p className="text-sm text-gray-500">Your Creative Assistant</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {caseyMessages.map(message => (
            <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-900'
              }`}>
                <p className="text-sm">{message.content}</p>
                <p className={`text-xs mt-1 ${
                  message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="p-4 border-t">
          <div className="flex space-x-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask Casey anything..."
              className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button 
              onClick={sendMessage}
              className="p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreativeWorkspace;