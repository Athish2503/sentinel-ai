import { apiClient } from '../lib/api-client';
import { SimulateResponse } from '../types';
import { mockSimulatorResponses } from '../mock/data';

export const simulationService = {
  runSimulation: async (attackNumber: number): Promise<SimulateResponse> => {
    try {
      const response = await apiClient.post<SimulateResponse>(`/simulate/${attackNumber}`);
      return response.data;
    } catch (error) {
      console.warn(`FastAPI backend not reachable for runSimulation (${attackNumber}), falling back to mock response.`, error);
      
      // Simulate backend latency
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const response = mockSimulatorResponses[attackNumber];
      if (!response) {
        throw new Error(`Simulation scenario ${attackNumber} not supported.`);
      }
      return response;
    }
  }
};
