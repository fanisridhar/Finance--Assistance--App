'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { isAuthenticated, logout } from '@/lib/auth';
import { transactionsAPI, budgetAPI, plaidAPI } from '@/lib/api';
import Link from 'next/link';
import { createPlaidLink } from '@/lib/plaid';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  CreditCard,
  MessageSquare,
  Settings,
  LogOut
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [linkToken, setLinkToken] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  // Fetch link token
  const { data: linkTokenData } = useQuery({
    queryKey: ['plaid-link-token'],
    queryFn: async () => {
      const response = await plaidAPI.createLinkToken();
      return response.data;
    },
    enabled: isAuthenticated(),
  });

  useEffect(() => {
    if (linkTokenData) {
      setLinkToken(linkTokenData.link_token);
    }
  }, [linkTokenData]);

  // Fetch transaction summary
  const { data: summary } = useQuery({
    queryKey: ['transaction-summary'],
    queryFn: async () => {
      const response = await transactionsAPI.getSummary(30);
      return response.data;
    },
    enabled: isAuthenticated(),
  });

  // Fetch budgets
  const { data: budgets } = useQuery({
    queryKey: ['budgets'],
    queryFn: async () => {
      const response = await budgetAPI.getBudgets();
      return response.data;
    },
    enabled: isAuthenticated(),
  });

  const [plaidReady, setPlaidReady] = useState(false);
  const [plaidHandler, setPlaidHandler] = useState<any>(null);

  useEffect(() => {
    if (linkToken) {
      createPlaidLink({
        token: linkToken,
        onSuccess: async (publicToken: string, metadata: any) => {
          try {
            await plaidAPI.exchangeToken(
              publicToken,
              metadata.institution?.institution_id,
              metadata.institution?.name
            );
            // Refresh data
            window.location.reload();
          } catch (error) {
            console.error('Error exchanging token:', error);
          }
        },
      }).then((handler) => {
        setPlaidHandler(handler);
        setPlaidReady(true);
      }).catch((error) => {
        console.error('Error creating Plaid link:', error);
      });
    }
  }, [linkToken]);

  const openPlaidLink = () => {
    if (plaidHandler) {
      plaidHandler.open();
    }
  };

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Finance Planner</h1>
            <div className="flex gap-4">
              <Link
                href="/chat"
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-indigo-600"
              >
                <MessageSquare className="w-5 h-5" />
                Chat
              </Link>
              <button
                onClick={logout}
                className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-red-600"
              >
                <LogOut className="w-5 h-5" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Connect Bank Button */}
        <div className="mb-8">
          <button
            onClick={openPlaidLink}
            disabled={!plaidReady}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <CreditCard className="w-5 h-5" />
            {plaidReady ? 'Connect Bank Account' : 'Loading...'}
          </button>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Income</p>
                  <p className="text-2xl font-bold text-green-600">
                    ${summary.total_income.toFixed(2)}
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Expenses</p>
                  <p className="text-2xl font-bold text-red-600">
                    ${summary.total_expenses.toFixed(2)}
                  </p>
                </div>
                <TrendingDown className="w-8 h-8 text-red-600" />
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Net</p>
                  <p className={`text-2xl font-bold ${summary.net >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ${summary.net.toFixed(2)}
                  </p>
                </div>
                <DollarSign className="w-8 h-8 text-indigo-600" />
              </div>
            </div>
          </div>
        )}

        {/* Budgets Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">Budgets</h2>
            <Link
              href="/budgets"
              className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
            >
              Manage Budgets
            </Link>
          </div>
          
          {budgets && budgets.length > 0 ? (
            <div className="space-y-4">
              {budgets.map((budget: any) => {
                const percentage = (budget.current_spending / budget.monthly_limit) * 100;
                const isOverBudget = percentage > 100;
                
                return (
                  <div key={budget.id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-gray-900">{budget.category}</span>
                      <span className="text-sm text-gray-600">
                        ${budget.current_spending.toFixed(2)} / ${budget.monthly_limit.toFixed(2)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          isOverBudget ? 'bg-red-600' : 'bg-indigo-600'
                        }`}
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {percentage.toFixed(1)}% used
                    </p>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-gray-500">No budgets set. Create one to get started!</p>
          )}
        </div>

        {/* Category Breakdown */}
        {summary && summary.category_breakdown && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Spending by Category</h2>
            <div className="space-y-2">
              {Object.entries(summary.category_breakdown)
                .sort(([, a]: any, [, b]: any) => b - a)
                .map(([category, amount]: [string, any]) => (
                  <div key={category} className="flex justify-between items-center">
                    <span className="text-gray-700">{category}</span>
                    <span className="font-medium text-gray-900">${amount.toFixed(2)}</span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

