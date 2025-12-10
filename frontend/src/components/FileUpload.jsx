import React, { useState, useCallback } from 'react';
import { FiUpload, FiFile, FiCheck, FiX } from 'react-icons/fi';
import api from '../utils/api';

function FileUpload() {
  // Load state from sessionStorage
  const [uploadedFiles, setUploadedFiles] = useState(() => {
    const saved = sessionStorage.getItem('uploadedFiles');
    return saved ? JSON.parse(saved) : [];
  });
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [analysisPrompt, setAnalysisPrompt] = useState(() => {
    return sessionStorage.getItem('analysisPrompt') || '';
  });
  const [analysisResult, setAnalysisResult] = useState(() => {
    const saved = sessionStorage.getItem('analysisResult');
    return saved ? JSON.parse(saved) : null;
  });
  const [analyzing, setAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});

  // Save state to sessionStorage
  React.useEffect(() => {
    sessionStorage.setItem('uploadedFiles', JSON.stringify(uploadedFiles));
  }, [uploadedFiles]);

  React.useEffect(() => {
    sessionStorage.setItem('analysisPrompt', analysisPrompt);
  }, [analysisPrompt]);

  React.useEffect(() => {
    if (analysisResult) {
      sessionStorage.setItem('analysisResult', JSON.stringify(analysisResult));
    }
  }, [analysisResult]);

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
      const fileName = file.name;
      
      // Set initial progress
      setUploadProgress((prev) => ({ ...prev, [fileName]: 0 }));
      
      try {
        // Simulate progress for better UX
        const progressInterval = setInterval(() => {
          setUploadProgress((prev) => ({
            ...prev,
            [fileName]: Math.min((prev[fileName] || 0) + 10, 90),
          }));
        }, 200);

        const response = await api.uploadFile(file);
        
        clearInterval(progressInterval);
        setUploadProgress((prev) => ({ ...prev, [fileName]: 100 }));
        
        console.log(`✓ File uploaded successfully: ${fileName}`, response);
        
        setUploadedFiles((prev) => [
          ...prev,
          {
            id: response.file_id,
            name: file.name,
            size: file.size,
            status: 'uploaded',
            tokenEstimate: response.token_estimate || 0,
            sizeKb: response.size_kb || 0,
          },
        ]);

        // Clear progress after a delay
        setTimeout(() => {
          setUploadProgress((prev) => {
            const newProgress = { ...prev };
            delete newProgress[fileName];
            return newProgress;
          });
        }, 1000);
      } catch (error) {
        console.error(`✗ Error uploading file: ${fileName}`, error);
        console.error('Error details:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status,
        });
        
        setUploadProgress((prev) => {
          const newProgress = { ...prev };
          delete newProgress[fileName];
          return newProgress;
        });
        
        setUploadedFiles((prev) => [
          ...prev,
          {
            name: file.name,
            size: file.size,
            status: 'error',
            error: error.response?.data?.detail || error.message || 'Upload failed',
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

    // Calculate total tokens
    const uploadedFilesOnly = uploadedFiles.filter((f) => f.status === 'uploaded');
    const totalTokens = uploadedFilesOnly.reduce((sum, f) => sum + (f.tokenEstimate || 0), 0);
    
    console.log('📊 Starting analysis...', {
      prompt: analysisPrompt,
      fileCount: uploadedFilesOnly.length,
      estimatedTokens: totalTokens,
    });

    // Show warning if tokens are high
    if (totalTokens > 150000) {
      const proceed = window.confirm(
        `⚠️ High token count detected!\n\n` +
        `Estimated tokens: ${totalTokens.toLocaleString()}\n` +
        `This may take longer and consume more credits.\n\n` +
        `Do you want to proceed?`
      );
      if (!proceed) return;
    }

    setAnalyzing(true);
    setAnalysisResult(null);

    try {
      const fileIds = uploadedFiles
        .filter((f) => f.status === 'uploaded')
        .map((f) => f.id);
      
      console.log('📤 Sending analysis request with file IDs:', fileIds);
      
      const response = await api.analyzeData(analysisPrompt, fileIds);
      
      console.log('✓ Analysis completed successfully', {
        messageLength: response.message?.length,
        filesGenerated: response.files?.length || 0,
      });
      
      setAnalysisResult(response);
    } catch (error) {
      console.error('✗ Error analyzing files:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
      
      const errorDetail = error.response?.data?.detail || error.message || 'Error analyzing files. Please try again.';
      const isRateLimit = error.response?.status === 429 || errorDetail.toLowerCase().includes('rate limit');
      
      setAnalysisResult({
        message: isRateLimit 
          ? '⏱️ Rate limit reached. The request will automatically retry. Please wait a moment...'
          : errorDetail,
        files: [],
        error: true,
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
                  className="bg-gray-50 p-4 rounded-lg border border-gray-200"
                >
                  <div className="flex items-center justify-between">
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
                          <span className="ml-2 text-red-600">✗ Failed</span>
                        )}
                      </p>
                      {file.status === 'uploaded' && file.tokenEstimate > 0 && (
                        <p className="text-xs text-blue-600 mt-1">
                          📊 Estimated tokens: {file.tokenEstimate.toLocaleString()} 
                          {' '}({file.sizeKb.toFixed(2)} KB)
                        </p>
                      )}
                      {file.error && (
                        <p className="text-xs text-red-600 mt-1">{file.error}</p>
                      )}
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="ml-4 p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                    >
                      <FiX />
                    </button>
                  </div>
                  
                  {/* Upload Progress */}
                  {uploadProgress[file.name] !== undefined && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                        <span>Uploading...</span>
                        <span>{uploadProgress[file.name]}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${uploadProgress[file.name]}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Analysis Section */}
          {uploadedFiles.some((f) => f.status === 'uploaded') && (
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-800">
              Analyze Data
            </h3>
            {(() => {
              const totalTokens = uploadedFiles
                .filter((f) => f.status === 'uploaded')
                .reduce((sum, f) => sum + (f.tokenEstimate || 0), 0);
              return totalTokens > 0 ? (
                <div className="text-sm">
                  <span className="text-gray-600">Total tokens: </span>
                  <span className={`font-semibold ${
                    totalTokens > 150000 ? 'text-orange-600' : 'text-blue-600'
                  }`}>
                    {totalTokens.toLocaleString()}
                  </span>
                  {totalTokens > 150000 && (
                    <span className="ml-2 text-orange-600 text-xs">⚠️ High</span>
                  )}
                </div>
              ) : null;
            })()}
          </div>
          
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
              <div className={`prose prose-sm max-w-none p-4 rounded-lg ${
                analysisResult.error ? 'bg-red-50 border border-red-200' : 'bg-gray-50'
              }`}>
                <pre className={`whitespace-pre-wrap text-sm ${
                  analysisResult.error ? 'text-red-800' : ''
                }`}>
                  {analysisResult.message}
                </pre>
              </div>
              
              {analysisResult.files && analysisResult.files.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700 mb-3">
                    Generated Files ({analysisResult.files.length}):
                  </p>
                  <div className="space-y-3">
                    {analysisResult.files.map((file, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-3 bg-white">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">
                            File {index + 1}
                          </span>
                          <button
                            onClick={() => api.downloadFile(file.file_id, file.container_id)}
                            className="flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-sm"
                          >
                            <FiFile />
                            <span>Download</span>
                          </button>
                        </div>
                        {/* Render image preview if it's an image */}
                        <div className="rounded overflow-hidden border border-gray-200">
                          <img
                            src={`/api/file/${file.file_id}`}
                            alt={`Generated file ${index + 1}`}
                            className="w-full h-auto"
                            onError={(e) => {
                              console.error('Error loading image:', file.file_id);
                              e.target.style.display = 'none';
                              e.target.nextSibling.style.display = 'block';
                            }}
                          />
                          <div className="hidden p-3 text-center text-gray-500 bg-gray-50 text-sm">
                            Preview not available. Use download button above.
                          </div>
                        </div>
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

export default FileUpload;


