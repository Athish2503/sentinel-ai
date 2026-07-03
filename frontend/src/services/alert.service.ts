import { apiClient } from '../lib/api-client';
import { Alert } from '../types';
import { mockAlerts } from '../mock/data';

export const alertService = {
  getAlerts: async (skip = 0, limit = 100): Promise<Alert[]> => {
    try {
      const response = await apiClient.get<Alert[]>('/alerts/', {
        params: { skip, limit }
      });
      return response.data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    } catch (error) {
      console.warn('FastAPI backend not reachable for getAlerts, falling back to mock data.', error);
      return mockAlerts.slice(skip, skip + limit);
    }
  },

  getAlert: async (alertId: string): Promise<Alert> => {
    try {
      const response = await apiClient.get<Alert>(`/alerts/${alertId}`);
      return response.data;
    } catch (error) {
      console.warn(`FastAPI backend not reachable for getAlert (${alertId}), falling back to mock data.`, error);
      const found = mockAlerts.find(a => a.id === alertId);
      if (!found) {
        throw new Error(`Alert ${alertId} not found.`);
      }
      return found;
    }
  },

  getAlertsForSession: async (sessionId: string): Promise<Alert[]> => {
    try {
      const response = await apiClient.get<Alert[]>(`/alerts/session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.warn(`FastAPI backend not reachable for getAlertsForSession (${sessionId}), falling back to mock data.`, error);
      return mockAlerts.filter(a => a.session_id === sessionId);
    }
  }
};
