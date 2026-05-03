import api from './api';

export const templateAPI = {
  // Get all templates (with optional filters)
  getAll: (params = {}) => api.get('/templates/', { params }),
  
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