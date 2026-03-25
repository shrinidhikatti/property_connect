import api from './client'

export const propertiesApi = {
  list: (params) => api.get('/properties/', { params }),
  get: (id) => api.get(`/properties/${id}/`),
  create: (data) => api.post('/properties/', data),
  update: (id, data) => api.patch(`/properties/${id}/`, data),
  delete: (id) => api.delete(`/properties/${id}/`),
  submit: (id) => api.post(`/properties/${id}/submit/`),
  myListings: () => api.get('/properties/my_listings/'),
  nearby: (params) => api.get('/properties/nearby/', { params }),
  favorites: () => api.get('/properties/favorites/'),
  addFavorite: (id) => api.post(`/properties/${id}/favorite/`),
  removeFavorite: (id) => api.delete(`/properties/${id}/favorite/`),
  // Documents (nested)
  getDocuments: (propertyId) => api.get(`/properties/${propertyId}/documents/`),
  uploadDocument: (propertyId, formData) =>
    api.post(`/properties/${propertyId}/documents/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  deleteDocument: (propertyId, docId) =>
    api.delete(`/properties/${propertyId}/documents/${docId}/`),
  getDownloadUrl: (propertyId, docId) =>
    api.get(`/properties/${propertyId}/documents/${docId}/download_url/`),
}

export const verificationsApi = {
  queue: () => api.get('/verifications/queue/'),
  list: () => api.get('/verifications/'),
  get: (id) => api.get(`/verifications/${id}/`),
  approve: (id) => api.post(`/verifications/${id}/approve/`),
  reject: (id, data) => api.post(`/verifications/${id}/reject/`, data),
  requestChanges: (id, data) => api.post(`/verifications/${id}/request_changes/`, data),
}
