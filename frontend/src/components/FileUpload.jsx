import React, { useState, useCallback } from 'react';
import { FiUpload, FiFile, FiCheck, FiX } from 'react-icons/fi';
import api from '../utils/api';

function FileUpload() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [analysisPrompt, setAnalysisPrompt] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  }, []);

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = async (files) => {
    setUploading(true);
    const fileArray = Array.from(files);
    
    for (const file of fileArray) {
      try {
        const response = await api.uploadFile(file);
        setUploadedFiles((prev) => [
          ...prev,
          {
            id: response.file_id,
            name: file.name,
            size: file.size,
            status: 'uploaded',
          },
        ]);
      } catch (error) {
        console.error('Error uploading file:', error);
        setUploadedFiles((prev) => [
          ...prev,
          {
            name: file.name,
            size: file.size,
            status: 'error',
          },
        ]);
      }
    }
    
    setUploading(false);
  };

  const removeFile = (index) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const analyzeFiles = async () => {
    if (!analysisPrompt.trim() || uploadedFiles.length === 0) return;

    setAnalyzing(true);
    setAnalysisResult(null);

    try {
      const fileIds = uploadedFiles
        .filter((f) => f.status === 'uploaded')
        .map((f) => f.id);
      
      const response = await api.analyzeData(analysisPrompt, fileIds);
      setAnalysisResult(response);
    } catch (error) {
      console.error('Error analyzing files:', error);
      setAnalysisResult({
        message: 'Error analyzing files. Please try again.',
        files: [],
      });
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          File Upload & Analysis
        </h2>
        <p className="text-gray-600">
          Upload CSV, Excel, JSON, or text files to analyze them with the Code Interpreter.
          The AI can read, process, and visualize your data.
        </p>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Upload Files
        </h3>
        
        <div
          className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="file-upload"
            multiple
            onChange={handleChange}
            className="hidden"
            accept=".csv,.xlsx,.xls,.json,.txt,.pdf"
          />
          
          <div className="flex flex-col items-center">
            <div className="bg-blue-100 p-4 rounded-full mb-4">
              <FiUpload className="text-4xl text-blue-600" />
            </div>
            <label
              htmlFor="file-upload"
              className="cursor-pointer text-blue-600 hover:text-blue-700 font-semibold"
            >
              Click to upload
            </label>
            <p className="text-gray-600 mt-1">or drag and drop files here</p>
            <p className="text-sm text-gray-500 mt-2">
              Supported: CSV, Excel, JSON, TXT, PDF
            </p>
          </div>
        </div>

        {/* Uploaded Files List */}
        {uploadedFiles.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold text-gray-800 mb-3">
              Uploaded Files ({uploadedFiles.length})
            </h4>
            <div className="space-y-2">
              {uploadedFiles.map((file, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between bg-gray-50 p-4 rounded-lg border border-gray-200"
                >
                  <div className="flex items-center space-x-3 flex-1">
                    <div
                      className={`p-2 rounded ${
                        file.status === 'uploaded'
                          ? 'bg-green-100'
                          : 'bg-red-100'
                      }`}
                    >
                      {file.status === 'uploaded' ? (
                        <FiCheck className="text-green-600" />
                      ) : (
                        <FiFile className="text-red-600" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-800">{file.name}</p>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(file.size)}
                        {file.status === 'uploaded' && (
                          <span className="ml-2 text-green-600">✓ Uploaded</span>
                        )}
                        {file.status === 'error' && (
                          <span className="ml-2 text-red-600">✗ Error</span>
                        )}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                  >
                    <FiX />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Analysis Section */}
      {uploadedFiles.some((f) => f.status === 'uploaded') && (
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Analyze Data
          </h3>
          
          <div className="space-y-4">
            <textarea
              value={analysisPrompt}
              onChange={(e) => setAnalysisPrompt(e.target.value)}
              placeholder="What would you like to know about your data? (e.g., 'Show me the summary statistics and create a visualization of the trends')"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 h-32 resize-none"
            />
            
            <button
              onClick={analyzeFiles}
              disabled={analyzing || !analysisPrompt.trim()}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 transition-all duration-200"
            >
              {analyzing ? 'Analyzing...' : 'Analyze Data'}
            </button>
          </div>

          {/* Analysis Results */}
          {analysisResult && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="font-semibold text-gray-800 mb-3">Results</h4>
              <div className="prose prose-sm max-w-none bg-gray-50 p-4 rounded-lg">
                <pre className="whitespace-pre-wrap text-sm">
                  {analysisResult.message}
                </pre>
              </div>
              
              {analysisResult.files && analysisResult.files.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Generated Files:
                  </p>
                  <div className="space-y-2">
                    {analysisResult.files.map((file, index) => (
                      <button
                        key={index}
                        onClick={() => api.downloadFile(file.file_id)}
                        className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                      >
                        <FiFile />
                        <span>Download File {index + 1}</span>
                      </button>
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

export default FileUpload;

