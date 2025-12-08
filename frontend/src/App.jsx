import React, { useState, useEffect } from 'react';
import { FiCode, FiFileText, FiBarChart2, FiUpload } from 'react-icons/fi';
import ChatInterface from './components/ChatInterface';
import Examples from './components/Examples';
import FileUpload from './components/FileUpload';
import About from './components/About';

function App() {
  // Load active tab from sessionStorage or default to 'chat'
  const [activeTab, setActiveTab] = useState(() => {
    return sessionStorage.getItem('activeTab') || 'chat';
  });

  // Save active tab to sessionStorage whenever it changes
  useEffect(() => {
    sessionStorage.setItem('activeTab', activeTab);
  }, [activeTab]);

  const tabs = [
    { id: 'chat', name: 'Chat', icon: FiCode },
    { id: 'examples', name: 'Examples', icon: FiBarChart2 },
    { id: 'upload', name: 'File Upload', icon: FiUpload },
    { id: 'about', name: 'About', icon: FiFileText },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-lg">
                <FiCode className="text-white text-2xl" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  OpenAI Code Interpreter
                </h1>
                <p className="text-sm text-gray-600">
                  Explore the power of AI-powered code execution
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm
                    transition-colors duration-200
                    ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }
                  `}
                >
                  <Icon className="text-lg" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'chat' && <ChatInterface />}
        {activeTab === 'examples' && <Examples />}
        {activeTab === 'upload' && <FileUpload />}
        {activeTab === 'about' && <About />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-600 text-sm">
            Built with React, FastAPI, and OpenAI's Code Interpreter
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;


