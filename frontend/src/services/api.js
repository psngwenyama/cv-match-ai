import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  register: (userData) => api.post('/auth/register/', userData),
  login: (credentials) => api.post('/auth/login/', credentials),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh: refreshToken }),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => api.patch('/auth/profile/', data),
  changePassword: (data) => api.post('/auth/change-password/', data),
  refreshToken: (refresh) => api.post('/auth/token/refresh/', { refresh }),
};

// Profile endpoints
export const profileAPI = {
  // Profile
  getProfile: () => api.get('/profiles/profile/me/'),
  updateProfile: (data) => api.patch('/profiles/profile/me/', data),
  
  // Work Experience
  getWorkExperiences: () => api.get('/profiles/work-experiences/'),
  createWorkExperience: (data) => api.post('/profiles/work-experiences/', data),
  updateWorkExperience: (id, data) => api.put(`/profiles/work-experiences/${id}/`, data),
  deleteWorkExperience: (id) => api.delete(`/profiles/work-experiences/${id}/`),
  
  // Education
  getEducation: () => api.get('/profiles/education/'),
  createEducation: (data) => api.post('/profiles/education/', data),
  updateEducation: (id, data) => api.put(`/profiles/education/${id}/`, data),
  deleteEducation: (id) => api.delete(`/profiles/education/${id}/`),
  
  // Skills
  getSkills: () => api.get('/profiles/skills/'),
  createSkill: (data) => api.post('/profiles/skills/', data),
  updateSkill: (id, data) => api.put(`/profiles/skills/${id}/`, data),
  deleteSkill: (id) => api.delete(`/profiles/skills/${id}/`),
  
  // Projects
  getProjects: () => api.get('/profiles/projects/'),
  createProject: (data) => api.post('/profiles/projects/', data),
  updateProject: (id, data) => api.put(`/profiles/projects/${id}/`, data),
  deleteProject: (id) => api.delete(`/profiles/projects/${id}/`),
  
  // Certifications
  getCertifications: () => api.get('/profiles/certifications/'),
  createCertification: (data) => api.post('/profiles/certifications/', data),
  updateCertification: (id, data) => api.put(`/profiles/certifications/${id}/`, data),
  deleteCertification: (id) => api.delete(`/profiles/certifications/${id}/`),
  
  // Languages
  getLanguages: () => api.get('/profiles/languages/'),
  createLanguage: (data) => api.post('/profiles/languages/', data),
  updateLanguage: (id, data) => api.put(`/profiles/languages/${id}/`, data),
  deleteLanguage: (id) => api.delete(`/profiles/languages/${id}/`),
};

// CV endpoints
export const cvAPI = {
  getAll: () => api.get('/cvs/'),
  getById: (id) => api.get(`/cvs/${id}/`),
  analyze: (jobDescription, provider = 'gemini') => 
    api.post('/cvs/analyze/', { job_description: jobDescription, provider }),
  generate: (data) => api.post('/cvs/generate/', data),
  update: (id, data) => api.patch(`/cvs/${id}/`, data),
  delete: (id) => api.delete(`/cvs/${id}/`),
  duplicate: (id) => api.post(`/cvs/${id}/duplicate/`),
  download: async (id) => {
    try {
      const response = await api.get(`/cvs/${id}/download/`, {
        responseType: 'blob',
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'cv.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return { success: true };
    } catch (error) {
      console.error('Download error:', error);
      // If error response is blob, try to parse it
      if (error.response?.data instanceof Blob) {
        const text = await error.response.data.text();
        try {
          const json = JSON.parse(text);
          throw new Error(json.error || 'Download failed');
        } catch {
          throw new Error('Download failed');
        }
      }
      throw error;
    }
  },
  markApplied: (id, data) => api.post(`/cvs/${id}/mark_applied/`, data),
  getVersions: (id) => api.get(`/cvs/${id}/versions/`),
  createVersion: (id, data) => api.post(`/cvs/${id}/create_version/`, data),
  
  // Applications
  getApplications: (cvId) => api.get(`/cvs/${cvId}/applications/`),
  createApplication: (cvId, data) => api.post(`/cvs/${cvId}/applications/`, data),
  updateApplication: (cvId, appId, data) => api.patch(`/cvs/${cvId}/applications/${appId}/`, data),
  deleteApplication: (cvId, appId) => api.delete(`/cvs/${cvId}/applications/${appId}/`),
};

// Template endpoints
export const templateAPI = {
  // Get all templates (with optional filters)
  getAll: async (params = {}) => {
    const response = await api.get('/templates/', { params });
    return response;
  },
  
  // Get default templates
  getDefaults: () => api.get('/templates/defaults/'),
  
  // Get single template
  getById: (id) => api.get(`/templates/${id}/`),
  
  // Upload new template
  upload: (formData) => api.post('/templates/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  // Update template
  update: (id, data) => api.patch(`/templates/${id}/`, data),
  
  // Delete template
  delete: (id) => api.delete(`/templates/${id}/`),
  
  // Favorite/unfavorite
  favorite: (id) => api.post(`/templates/${id}/favorite/`),
  unfavorite: (id) => api.post(`/templates/${id}/unfavorite/`),
  
  // Download template files
  download: (id) => api.get(`/templates/${id}/download/`, {
    responseType: 'blob'
  }),
};

export default api;