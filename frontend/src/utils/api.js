import axios from 'axios';

const API_BASE_URL = '/api';

// Add request/response interceptors for logging
axios.interceptors.request.use(
  (config) => {
    console.log(`📤 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('📤 API Request Error:', error);
    return Promise.reject(error);
  }
);

axios.interceptors.response.use(
  (response) => {
    console.log(`📥 API Response: ${response.config.url} - Status: ${response.status}`);
    return response;
  },
  (error) => {
    console.error(`📥 API Response Error: ${error.config?.url}`, {
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
    });
    return Promise.reject(error);
  }
);

const api = {
  // Send a chat message
  sendMessage: async (message, threadId = null) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message,
        thread_id: threadId,
        use_code_interpreter: true,
      });
      return response.data;
    } catch (error) {
      console.error('Error in sendMessage:', error);
      throw error;
    }
  },

  // Upload a file
  uploadFile: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error in uploadFile:', error);
      throw error;
    }
  },

  // Download a file (optionally with containerId for container-files API)
  downloadFile: async (fileId, containerId = null) => {
    try {
      const downloadUrl =
        containerId == null
          ? `${API_BASE_URL}/file/${fileId}`
          : `${API_BASE_URL}/file/${fileId}?container_id=${encodeURIComponent(containerId)}`;

      const response = await axios.get(downloadUrl, {
        responseType: 'blob',
      });
      
      // Get filename from Content-Disposition header if available
      const contentDisposition = response.headers['content-disposition'];
      let filename = `output_${fileId}.png`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      // Create download link
      const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = blobUrl;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      console.error('Error in downloadFile:', error);
      throw error;
    }
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


