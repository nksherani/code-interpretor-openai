import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiDownload, FiImage, FiFile } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import api from '../utils/api';

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [threadId, setThreadId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await api.sendMessage(userMessage, threadId);
      setThreadId(response.thread_id);
      
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.message,
          files: response.files || [],
          annotations: response.annotations || [],
        },
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'error',
          content: 'Sorry, there was an error processing your request. Please try again.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadFile = async (fileId) => {
    try {
      await api.downloadFile(fileId);
    } catch (error) {
      console.error('Error downloading file:', error);
      alert('Failed to download file');
    }
  };

  const examplePrompts = [
    'Calculate the first 15 Fibonacci numbers',
    'Create a bar chart showing sales data for 5 products',
    'Analyze this dataset and show me the correlation matrix',
    'Solve the quadratic equation: 2x² - 5x + 3 = 0',
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-280px)]">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto bg-white rounded-lg shadow-lg border border-gray-200 p-6 mb-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="bg-gradient-to-br from-blue-100 to-purple-100 p-8 rounded-full mb-6">
              <FiFile className="text-6xl text-blue-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-3">
              Start a Conversation
            </h2>
            <p className="text-gray-600 mb-6 max-w-md">
              Ask me to perform data analysis, create visualizations, solve mathematical
              problems, or execute Python code!
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
              {examplePrompts.map((prompt, index) => (
                <button
                  key={index}
                  onClick={() => setInput(prompt)}
                  className="text-left p-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors duration-200 text-sm text-gray-700"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-3xl rounded-lg px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.role === 'error'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {message.role === 'assistant' ? (
                    <div>
                      <div className="markdown-content prose prose-sm max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {message.content}
                        </ReactMarkdown>
                      </div>
                      {message.files && message.files.length > 0 && (
                        <div className="mt-4 space-y-2">
                          {message.files.map((file, fileIndex) => (
                            <div
                              key={fileIndex}
                              className="flex items-center justify-between bg-white p-3 rounded border border-gray-200"
                            >
                              <div className="flex items-center space-x-2">
                                {file.type === 'image_file' ? (
                                  <FiImage className="text-blue-600" />
                                ) : (
                                  <FiFile className="text-blue-600" />
                                )}
                                <span className="text-sm text-gray-700">
                                  Generated File
                                </span>
                              </div>
                              <button
                                onClick={() => handleDownloadFile(file.file_id)}
                                className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm"
                              >
                                <FiDownload />
                                <span>Download</span>
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg px-4 py-3">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div
                      className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                      style={{ animationDelay: '0.1s' }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                      style={{ animationDelay: '0.2s' }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg border border-gray-200 p-4">
        <div className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything... (e.g., 'Create a graph showing exponential growth')"
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2"
          >
            <FiSend />
            <span>Send</span>
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatInterface;

