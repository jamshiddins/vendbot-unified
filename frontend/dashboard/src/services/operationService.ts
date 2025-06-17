import { api } from '../config/api';

export interface HopperOperation {
  id: number;
  hopper_id: number;
  operation_type: string;
  ingredient_id: number;
  quantity_before: number;
  quantity_after: number;
  quantity_added: number;
  operator_id: number;
  machine_id?: number;
  photos: string[];
  notes?: string;
  created_at: string;
  sync_status: {
    telegram: boolean;
    web: boolean;
    mobile: boolean;
  };
}

export interface OperationFilters {
  hopper_id?: number;
  operator_id?: number;
  operation_type?: string;
  date_from?: string;
  date_to?: string;
}

export const operationService = {
  async getOperations(filters: OperationFilters = {}): Promise<HopperOperation[]> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value));
      }
    });
    
    const response = await api.get('/operations/hopper', { params });
    return response.data;
  },

  async getOperation(id: number): Promise<HopperOperation> {
    const response = await api.get(`/operations/hopper/${id}`);
    return response.data;
  },

  async createOperation(data: any): Promise<HopperOperation> {
    const response = await api.post('/operations/hopper', data);
    return response.data;
  },

  async getConsumptionAnalysis(machineId: number, periodDays: number = 7) {
    const response = await api.get(`/operations/consumption/${machineId}`, {
      params: { period_days: periodDays }
    });
    return response.data;
  }
};