'use client';

import { useState } from 'react';
import { Bell, Plus, Trash2 } from 'lucide-react';
import { useAlerts } from '@/hooks/useAlerts';

export function AlertManager() {
  const { alerts, isLoading, createAlert, deleteAlert } = useAlerts();
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    max_price: '',
    deal_quality_minimum: 'good',
  });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await createAlert({
      origin: formData.origin.toUpperCase(),
      destination: formData.destination.toUpperCase() || undefined,
      max_price: formData.max_price ? Number(formData.max_price) : undefined,
      deal_quality_minimum: formData.deal_quality_minimum,
    });
    setIsCreating(false);
    setFormData({ origin: '', destination: '', max_price: '', deal_quality_minimum: 'good' });
  };

  return (
    <div className="bg-white shadow-xl rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-blue-600" />
          <h2 className="text-xl font-bold text-gray-900">Price Alerts</h2>
        </div>
        <button
          onClick={() => setIsCreating(!isCreating)}
          className="flex items-center gap-1 text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Alert
        </button>
      </div>

      {isCreating && (
        <form onSubmit={handleCreate} className="mb-6 p-4 bg-gray-50 rounded-lg space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input
              placeholder="From (LAX)"
              value={formData.origin}
              onChange={(e) => setFormData({ ...formData, origin: e.target.value })}
              className="rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
              required
              maxLength={3}
            />
            <input
              placeholder="To (JFK)"
              value={formData.destination}
              onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
              className="rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
              maxLength={3}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <input
              type="number"
              placeholder="Max price ($)"
              value={formData.max_price}
              onChange={(e) => setFormData({ ...formData, max_price: e.target.value })}
              className="rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
            />
            <select
              value={formData.deal_quality_minimum}
              onChange={(e) => setFormData({ ...formData, deal_quality_minimum: e.target.value })}
              className="rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
            >
              <option value="good">Good deals</option>
              <option value="great">Great deals</option>
              <option value="exceptional">Exceptional deals</option>
            </select>
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 text-sm font-medium"
          >
            Create Alert
          </button>
        </form>
      )}

      <div className="space-y-2">
        {isLoading ? (
          <p className="text-gray-500 text-sm">Loading alerts...</p>
        ) : alerts.length === 0 ? (
          <p className="text-gray-500 text-sm">No alerts yet. Create one to get notified about deals!</p>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div>
                <span className="font-medium text-sm">
                  {alert.origin}{alert.destination ? ` → ${alert.destination}` : ' (any destination)'}
                </span>
                {alert.max_price && (
                  <span className="ml-2 text-sm text-gray-500">max ${alert.max_price}</span>
                )}
                <span className={`ml-2 text-xs px-1.5 py-0.5 rounded ${
                  alert.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-500'
                }`}>
                  {alert.is_active ? 'Active' : 'Paused'}
                </span>
              </div>
              <button
                onClick={() => deleteAlert(alert.id)}
                className="text-red-400 hover:text-red-600 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
