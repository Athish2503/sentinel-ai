import { apiClient } from '../lib/api-client';
import { Baseline, BaselineTrainResponse } from '../types';
import { mockActiveBaseline, mockBaselineStats, mockBaselineFeatureVectors } from '../mock/data';

export const baselineService = {
  getBaselines: async (): Promise<Baseline[]> => {
    try {
      const response = await apiClient.get<Baseline[]>('/baselines/');
      return response.data;
    } catch (error) {
      console.warn('FastAPI backend not reachable for getBaselines, falling back to mock data.', error);
      return [mockActiveBaseline];
    }
  },

  getActiveBaseline: async (): Promise<Baseline> => {
    try {
      const response = await apiClient.get<Baseline>('/baselines/active');
      return response.data;
    } catch (error) {
      console.warn('FastAPI backend not reachable for getActiveBaseline, falling back to mock data.', error);
      return mockActiveBaseline;
    }
  },

  trainBaseline: async (numRuns = 25, useRealAgent = false): Promise<BaselineTrainResponse> => {
    try {
      const response = await apiClient.post<BaselineTrainResponse>('/baseline/train', {
        num_runs: numRuns,
        use_real_agent: useRealAgent
      });
      return response.data;
    } catch (error) {
      console.warn('FastAPI backend not reachable for trainBaseline, executing mock training delay.', error);
      
      // Simulate training delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const newBaselineId = `bl-train-${Date.now()}`;
      return {
        baseline_id: newBaselineId,
        model_version: `v${new Date().toISOString().replace(/[-:T.]/g, '').slice(0, 14)}`,
        training_runs: numRuns,
        threshold: 0.65,
        created_at: new Date().toISOString(),
        statistics: {
          ...mockBaselineStats,
          total_runs: numRuns
        },
        feature_vectors: mockBaselineFeatureVectors.map(fv => ({
          ...fv,
          baseline_id: newBaselineId
        }))
      };
    }
  }
};
