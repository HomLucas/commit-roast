'use client';

import FlightSearch from '@/components/FlightSearch';
import { AlertManager } from '@/components/AlertManager';

export default function Home() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Find Your Next Flight Deal
        </h1>
        <p className="text-lg text-gray-600">
          Search flights, track prices, and discover error fares
        </p>
      </div>
      <FlightSearch />
      <div className="mt-12">
        <AlertManager />
      </div>
    </div>
  );
}
