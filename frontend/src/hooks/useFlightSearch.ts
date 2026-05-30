import { useState, useCallback } from 'react';
import api from '@/lib/api';
import toast from 'react-hot-toast';

interface SearchParams {
  origin: string;
  destination: string;
  departureDate: string;
  returnDate?: string;
  passengers: number;
  maxPrice?: number;
}

interface FlightResult {
  source_api: string;
  origin: string;
  destination: string;
  departure_date: string;
  return_date?: string;
  airline?: string;
  price_amount: number;
  price_currency: string;
  stops: number;
  is_deal?: boolean;
  deal_quality?: string;
  deal_type?: string;
  discount_percentage?: number;
  savings?: number;
}

interface SearchResponse {
  total_results: number;
  deals_found: number;
  error_fares: number;
  results: FlightResult[];
}

export function useFlightSearch() {
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchFlights = useCallback(async (params: SearchParams) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post<SearchResponse>('/flights/search', {
        origin: params.origin.toUpperCase(),
        destination: params.destination.toUpperCase(),
        departure_date: params.departureDate,
        return_date: params.returnDate || null,
        passengers: params.passengers,
        max_price: params.maxPrice || null,
      });

      setResults(response.data);
      return response.data;
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Search failed. Please try again.';
      setError(message);
      toast.error(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { results, isLoading, error, searchFlights };
}
