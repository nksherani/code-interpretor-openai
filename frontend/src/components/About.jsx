import React from 'react';
import { FiCode, FiCpu, FiDatabase, FiZap } from 'react-icons/fi';

function About() {
  const features = [
    {
      icon: FiCode,
      title: 'Code Execution',
      description: 'Run Python code in a secure sandboxed environment with access to popular data science libraries.',
    },
    {
      icon: FiDatabase,
      title: 'Data Analysis',
      description: 'Upload and analyze CSV, Excel, JSON files. Get insights, statistics, and visualizations.',
    },
    {
      icon: FiCpu,
      title: 'Mathematical Computing',
      description: 'Perform complex calculations, solve equations, and work with numerical data.',
    },
    {
      icon: FiZap,
      title: 'Visualization',
      description: 'Create charts, graphs, and plots. Export as downloadable image files.',
    },
  ];

  const examples = [
    {
      category: 'Data Analysis',
      items: [
        'Load and explore datasets',
        'Calculate summary statistics',
        'Find correlations and patterns',
        'Clean and transform data',
      ],
    },
    {
      category: 'Visualizations',
      items: [
        'Line and bar charts',
        'Scatter plots and heatmaps',
        '3D surface plots',
        'Pie charts and histograms',
      ],
    },
    {
      category: 'Mathematics',
      items: [
        'Solve equations and systems',
        'Calculate sequences (Fibonacci, primes)',
        'Linear algebra operations',
        'Statistical analysis',
      ],
    },
    {
      category: 'File Operations',
      items: [
        'Read CSV and Excel files',
        'Parse JSON data',
        'Generate output files',
        'Export visualizations',
      ],
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-8 text-white">
        <h1 className="text-3xl font-bold mb-3">
          OpenAI Code Interpreter Explorer
        </h1>
        <p className="text-lg opacity-90">
          A powerful web interface to explore and interact with OpenAI's Code Interpreter
          capabilities. Analyze data, create visualizations, and execute Python code with
          natural language.
        </p>
      </div>

      {/* Features */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="flex space-x-4">
                <div className="bg-blue-100 p-3 rounded-lg h-fit">
                  <Icon className="text-2xl text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800 mb-1">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 text-sm">{feature.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* What You Can Do */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">
          What You Can Do
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {examples.map((example, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-800 mb-3">
                {example.category}
              </h3>
              <ul className="space-y-2">
                {example.items.map((item, itemIndex) => (
                  <li key={itemIndex} className="flex items-start text-sm text-gray-700">
                    <span className="text-green-500 mr-2">✓</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Technology Stack */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Technology Stack
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">Frontend</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• React 18</li>
              <li>• Vite</li>
              <li>• Tailwind CSS</li>
              <li>• React Icons</li>
            </ul>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
            <h3 className="font-semibold text-purple-900 mb-2">Backend</h3>
            <ul className="text-sm text-purple-800 space-y-1">
              <li>• FastAPI</li>
              <li>• Python 3.11+</li>
              <li>• Uvicorn</li>
              <li>• Pydantic</li>
            </ul>
          </div>
          <div className="bg-gradient-to-br from-pink-50 to-pink-100 p-4 rounded-lg">
            <h3 className="font-semibold text-pink-900 mb-2">AI</h3>
            <ul className="text-sm text-pink-800 space-y-1">
              <li>• OpenAI API</li>
              <li>• GPT-4 Turbo</li>
              <li>• Code Interpreter</li>
              <li>• Assistants API</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Getting Started */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Getting Started
        </h2>
        <div className="space-y-4 text-gray-700">
          <div>
            <h3 className="font-semibold mb-2">1. Set up your OpenAI API Key</h3>
            <p className="text-sm">
              Create a <code className="bg-gray-100 px-2 py-1 rounded">.env</code> file
              in the backend directory with your OpenAI API key.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">2. Create an Assistant</h3>
            <p className="text-sm">
              Run the <code className="bg-gray-100 px-2 py-1 rounded">create_assistant.py</code>
              script to create an OpenAI Assistant with Code Interpreter enabled.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">3. Start the Backend</h3>
            <p className="text-sm">
              Install dependencies and run the FastAPI server with uvicorn.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">4. Start the Frontend</h3>
            <p className="text-sm">
              Install npm packages and run the Vite development server.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default About;


