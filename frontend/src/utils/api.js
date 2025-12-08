import axios from 'axios';

const API_BASE_URL = '/api';

const api = {
  // Send a chat message
  sendMessage: async (message, threadId = null) => {
    const response = await axios.post(`${API_BASE_URL}/chat`, {
      message,
      thread_id: threadId,
      use_code_interpreter: true,
    });
    return response.data;
  },

  // Upload a file
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Download a file
  downloadFile: async (fileId) => {
    const response = await axios.get(`${API_BASE_URL}/file/${fileId}`, {
      responseType: 'blob',
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `output_${fileId}.png`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  // Analyze data with files
  analyzeData: async (prompt, fileIds = []) => {
    const response = await axios.post(`${API_BASE_URL}/analyze`, {
      prompt,
      file_ids: fileIds,
    });
    return response.data;
  },

  // Run example
  runExample: async (exampleId) => {
    const response = await axios.post(`${API_BASE_URL}/examples/${exampleId}`);
    return response.data;
  },

  // Get thread messages
  getThreadMessages: async (threadId) => {
    const response = await axios.get(`${API_BASE_URL}/thread/${threadId}/messages`);
    return response.data;
  },

  // Create a new thread
  createThread: async () => {
    const response = await axios.post(`${API_BASE_URL}/thread/create`);
    return response.data;
  },
};

export default api;

