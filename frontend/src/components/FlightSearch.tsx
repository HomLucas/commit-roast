'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Search } from 'lucide-react';
import { useFlightSearch } from '@/hooks/useFlightSearch';
import { DealCard } from './DealCard';
import toast from 'react-hot-toast';

interface SearchFormData {
  origin: string;
  destination: string;
  departureDate: string;
  returnDate?: string;
  passengers: number;
  maxPrice?: number;
}

export default function FlightSearch() {
  const [results, setResults] = useState<any>(null);
  const { searchFlights, isLoading } = useFlightSearch();

  const { register, handleSubmit, formState: { errors } } = useForm<SearchFormData>();

  const onSubmit = async (data: SearchFormData) => {
    try {
      const searchResults = await searchFlights(data);
      setResults(searchResults);

      if (searchResults.deals_found > 0) {
        toast.success(`Found ${searchResults.deals_found} potential deals!`);
      }
    } catch (error) {
      toast.error('Search failed. Please try again.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <form onSubmit={handleSubmit(onSubmit)} className="bg-white shadow-xl rounded-2xl p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              From (Airport Code)
            </label>
            <input
              {...register('origin', { required: true, minLength: 3, maxLength: 3 })}
              className="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="LAX"
              maxLength={3}
            />
            {errors.origin && (
              <span className="text-red-500 text-sm">Required (3-letter IATA code)</span>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              To (Airport Code)
            </label>
            <input
              {...register('destination', { required: true, minLength: 3, maxLength: 3 })}
              className="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="JFK"
              maxLength={3}
            />
            {errors.destination && (
              <span className="text-red-500 text-sm">Required (3-letter IATA code)</span>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Departure Date
            </label>
            <input
              type="date"
              {...register('departureDate', { required: true })}
              className="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Return Date (Optional)
            </label>
            <input
              type="date"
              {...register('returnDate')}
              className="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Passengers
            </label>
            <input
              type="number"
              {...register('passengers', { required: true, min: 1, max: 9 })}
              defaultValue={1}
              className="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Price (Optional)
            </label>
            <input
              type="number"
              {...register('maxPrice')}
              className="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="500"
            />
          </div>
        </div>

        <div className="mt-6">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {isLoading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Searching...
              </span>
            ) : (
              <span className="flex items-center justify-center">
                <Search className="mr-2 h-5 w-5" />
                Search Flights
              </span>
            )}
          </button>
        </div>
      </form>

      {results && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">
              Results ({results.total_results})
            </h2>
            {results.deals_found > 0 && (
              <span className="bg-green-100 text-green-800 text-sm font-medium px-3 py-1 rounded-full">
                {results.deals_found} Deals Found
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.results?.map((flight: any, index: number) => (
              <DealCard key={index} flight={flight} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
