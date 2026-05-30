import type { Metadata } from 'next';
import { Toaster } from 'react-hot-toast';
import './globals.css';

export const metadata: Metadata = {
  title: 'Flight Scanner',
  description: 'Privacy-focused flight deal scanner with points tracking',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold text-blue-600">FlightScanner</span>
              </div>
              <div className="flex items-center gap-4">
                <a href="/" className="text-sm text-gray-700 hover:text-blue-600">Search</a>
                <a href="/login" className="text-sm text-gray-700 hover:text-blue-600">Sign In</a>
              </div>
            </div>
          </div>
        </nav>
        <main className="py-8">
          {children}
        </main>
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
