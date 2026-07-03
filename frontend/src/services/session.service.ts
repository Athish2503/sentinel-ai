import { apiClient } from '../lib/api-client';
import { Session } from '../types';
import { mockSessions } from '../mock/data';

export const sessionService = {
  getSessions: async (skip = 0, limit = 100): Promise<Session[]> => {
    try {
      const response = await apiClient.get<Session[]>('/sessions/', {
        params: { skip, limit }
      });
      // Sort sessions newest first just in case
      return response.data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    } catch (error) {
      console.warn('FastAPI backend not reachable for getSessions, falling back to mock data.', error);
      return mockSessions.slice(skip, skip + limit);
    }
  },

  getSession: async (sessionId: string): Promise<Session> => {
    try {
      const response = await apiClient.get<Session>(`/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      console.warn(`FastAPI backend not reachable for getSession (${sessionId}), falling back to mock data.`, error);
      const found = mockSessions.find(s => s.id === sessionId);
      if (!found) {
        throw new Error(`Session ${sessionId} not found.`);
      }
      return found;
    }
  },

  updateSession: async (sessionId: string, data: Partial<Session>): Promise<Session> => {
    try {
      const response = await apiClient.patch<Session>(`/sessions/${sessionId}`, data);
      return response.data;
    } catch (error) {
      console.warn(`FastAPI backend not reachable for updateSession (${sessionId}), updating mock data.`, error);
      const index = mockSessions.findIndex(s => s.id === sessionId);
      if (index !== -1) {
        mockSessions[index] = { ...mockSessions[index], ...data };
        return mockSessions[index];
      }
      throw new Error(`Session ${sessionId} not found in mock data.`);
    }
  }
};
