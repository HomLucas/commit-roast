'use client';

import { Plane, MapPin, Clock, DollarSign, Award } from 'lucide-react';

interface DealCardProps {
  flight: {
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
    points_program?: string;
    points_required?: number;
    cabin_class?: string;
  };
}

const qualityColors: Record<string, string> = {
  exceptional: 'bg-purple-100 text-purple-800 border-purple-300',
  great: 'bg-green-100 text-green-800 border-green-300',
  good: 'bg-blue-100 text-blue-800 border-blue-300',
};

export function DealCard({ flight }: DealCardProps) {
  const qualityClass = qualityColors[flight.deal_quality || ''] || 'bg-gray-100 text-gray-800';

  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 border border-gray-100 overflow-hidden">
      <div className="p-5">
        <div className="flex justify-between items-start mb-3">
          <div>
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-gray-400" />
              <span className="text-lg font-semibold">{flight.origin}</span>
              <span className="text-gray-400">→</span>
              <span className="text-lg font-semibold">{flight.destination}</span>
            </div>
            {flight.airline && (
              <p className="text-sm text-gray-500 mt-1">{flight.airline}</p>
            )}
          </div>
          {flight.deal_quality && (
            <span className={`px-2 py-1 rounded-full text-xs font-medium border ${qualityClass}`}>
              {flight.deal_quality}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
          <Clock className="w-3.5 h-3.5" />
          <span>{new Date(flight.departure_date).toLocaleDateString()}</span>
          {flight.stops > 0 ? (
            <span className="ml-2">{flight.stops} stop{flight.stops > 1 ? 's' : ''}</span>
          ) : (
            <span className="ml-2 text-green-600">Nonstop</span>
          )}
        </div>

        <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
          <div className="flex items-center gap-1">
            <DollarSign className="w-5 h-5 text-gray-400" />
            <span className="text-2xl font-bold text-gray-900">
              {flight.price_currency === 'USD' ? '$' : flight.price_currency}{' '}
              {flight.price_amount.toLocaleString()}
            </span>
          </div>
          {flight.savings && flight.savings > 0 && (
            <span className="text-sm font-medium text-green-600">
              Save ${flight.savings.toFixed(0)}
            </span>
          )}
        </div>

        {flight.points_program && flight.points_required && (
          <div className="flex items-center gap-1 mt-2 text-sm text-amber-600">
            <Award className="w-4 h-4" />
            <span>
              {flight.points_required.toLocaleString()} {flight.points_program} points
            </span>
          </div>
        )}

        {flight.cabin_class && flight.cabin_class !== 'economy' && (
          <div className="mt-2">
            <span className="text-xs font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded">
              {flight.cabin_class}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
