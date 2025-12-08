import React, { useState } from 'react';
import { FiBarChart2, FiTrendingUp, FiImage, FiPlay, FiDownload } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import api from '../utils/api';

function Examples() {
  // Load state from sessionStorage
  const [activeExample, setActiveExample] = useState(() => {
    return sessionStorage.getItem('activeExample') || null;
  });
  const [result, setResult] = useState(() => {
    const saved = sessionStorage.getItem('exampleResult');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(false);

  // Save state to sessionStorage
  React.useEffect(() => {
    if (activeExample) {
      sessionStorage.setItem('activeExample', activeExample);
    }
  }, [activeExample]);

  React.useEffect(() => {
    if (result) {
      sessionStorage.setItem('exampleResult', JSON.stringify(result));
    }
  }, [result]);

  const examples = [
    {
      id: 'data-analysis',
      title: 'Data Analysis',
      description: 'Generate sample sales data and perform comprehensive analysis',
      icon: FiBarChart2,
      color: 'blue',
      details: [
        'Generate 100 sales records',
        'Calculate revenue by product',
        'Find best performing region',
        'Create time-series visualization',
      ],
    },
    {
      id: 'math-computation',
      title: 'Mathematical Computing',
      description: 'Perform complex mathematical computations and solve equations',
      icon: FiTrendingUp,
      color: 'purple',
      details: [
        'Calculate Fibonacci sequence',
        'Find prime numbers',
        'Solve polynomial equations',
        'Create mathematical plots',
      ],
    },
    {
      id: 'image-generation',
      title: 'Data Visualization',
      description: 'Generate various types of charts and visualizations',
      icon: FiImage,
      color: 'pink',
      details: [
        'Create correlation heatmaps',
        'Generate 3D surface plots',
        'Build pie charts',
        'Export as image files',
      ],
    },
  ];

  const runExample = async (exampleId) => {
    console.log('🎯 Running example:', exampleId);
    
    setActiveExample(exampleId);
    setLoading(true);
    setResult(null);

    try {
      const response = await api.runExample(exampleId);
      
      console.log('✓ Example completed:', {
        exampleId,
        messageLength: response.message?.length,
        filesCount: response.files?.length || 0,
      });
      
      setResult(response);
    } catch (error) {
      console.error('✗ Error running example:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
      
      setResult({
        message: error.response?.data?.detail || error.message || 'Error running example. Please check your API configuration.',
        files: [],
        error: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = async (fileId) => {
    try {
      console.log('📥 Downloading file:', fileId);
      await api.downloadFile(fileId);
      console.log('✓ File downloaded successfully');
    } catch (error) {
      console.error('✗ Error downloading file:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
      alert(`Failed to download file: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Pre-built Examples
        </h2>
        <p className="text-gray-600">
          Try these examples to see what the Code Interpreter can do. Each example
          demonstrates different capabilities including data analysis, mathematical
          computation, and visualization.
        </p>
      </div>

      {/* Example Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {examples.map((example) => {
          const Icon = example.icon;
          const isActive = activeExample === example.id;
          
          return (
            <div
              key={example.id}
              className={`bg-white rounded-lg shadow-lg border-2 transition-all duration-200 ${
                isActive
                  ? 'border-blue-500 shadow-xl'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="p-6">
                <div
                  className={`bg-gradient-to-br from-${example.color}-100 to-${example.color}-200 p-4 rounded-lg inline-block mb-4`}
                >
                  <Icon className={`text-3xl text-${example.color}-600`} />
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">
                  {example.title}
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  {example.description}
                </p>
                <ul className="space-y-2 mb-6">
                  {example.details.map((detail, index) => (
                    <li key={index} className="flex items-start text-sm text-gray-700">
                      <span className="text-green-500 mr-2">✓</span>
                      <span>{detail}</span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => runExample(example.id)}
                  disabled={loading && isActive}
                  className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition-all duration-200 flex items-center justify-center space-x-2"
                >
                  <FiPlay />
                  <span>{loading && isActive ? 'Running...' : 'Run Example'}</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Results</h3>
          
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div>
              <div className={`prose prose-sm max-w-none mb-6 markdown-content ${
                result.error ? 'text-red-800 bg-red-50 p-4 rounded-lg' : ''
              }`}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {result.message}
                </ReactMarkdown>
              </div>

              {result.files && result.files.length > 0 && (
                <div className="border-t border-gray-200 pt-6">
                  <h4 className="font-semibold text-gray-800 mb-3">
                    Generated Files ({result.files.length})
                  </h4>
                  <div className="grid grid-cols-1 gap-4">
                    {result.files.map((file, index) => (
                      <div
                        key={index}
                        className="bg-gray-50 p-4 rounded-lg border border-gray-200"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div className="bg-blue-100 p-2 rounded">
                              <FiImage className="text-blue-600 text-xl" />
                            </div>
                            <div>
                              <p className="font-medium text-gray-800">
                                {file.type === 'image_file' ? 'Generated Image' : 'Generated File'}
                              </p>
                              <p className="text-xs text-gray-500">
                                ID: {file.file_id.substring(0, 20)}...
                              </p>
                            </div>
                          </div>
                          <button
                            onClick={() => downloadFile(file.file_id)}
                            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm flex items-center space-x-1"
                          >
                            <FiDownload />
                            <span>Download</span>
                          </button>
                        </div>
                        
                        {/* Render image preview */}
                        {file.type === 'image_file' && (
                          <div className="mt-2 rounded overflow-hidden border border-gray-300 bg-white">
                            <img
                              src={`/api/file/${file.file_id}`}
                              alt={`Generated visualization ${index + 1}`}
                              className="w-full h-auto"
                              onError={(e) => {
                                console.error('Error loading image:', file.file_id);
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'block';
                              }}
                            />
                            <div className="hidden p-4 text-center text-gray-500">
                              Unable to load image preview. Use download button above.
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Examples;


