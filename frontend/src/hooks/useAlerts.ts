import { useState, useEffect, useCallback } from 'react';
import api from '@/lib/api';
import toast from 'react-hot-toast';

interface Alert {
  id: number;
  origin: string;
  destination?: string;
  max_price?: number;
  is_active: boolean;
  deal_quality_minimum: string;
  created_at?: string;
}

interface AlertCreateParams {
  origin: string;
  destination?: string;
  max_price?: number;
  date_range_start?: string;
  date_range_end?: string;
  max_stops?: number;
  deal_quality_minimum?: string;
}

export function useAlerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchAlerts = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.get<Alert[]>('/alerts/');
      setAlerts(response.data);
    } catch (err) {
      toast.error('Failed to load alerts');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createAlert = useCallback(async (params: AlertCreateParams) => {
    try {
      const response = await api.post<Alert>('/alerts/', params);
      setAlerts((prev) => [response.data, ...prev]);
      toast.success('Alert created successfully');
      return response.data;
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to create alert');
      throw err;
    }
  }, []);

  const deleteAlert = useCallback(async (id: number) => {
    try {
      await api.delete(`/alerts/${id}`);
      setAlerts((prev) => prev.filter((a) => a.id !== id));
      toast.success('Alert deleted');
    } catch (err) {
      toast.error('Failed to delete alert');
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  return { alerts, isLoading, createAlert, deleteAlert, refreshAlerts: fetchAlerts };
}
