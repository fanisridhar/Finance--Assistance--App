'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { isAuthenticated, logout } from '@/lib/auth';
import { budgetAPI, transactionsAPI } from '@/lib/api';
import Link from 'next/link';
import { ArrowLeft, Plus, Trash2, Edit } from 'lucide-react';

export default function BudgetsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editingBudget, setEditingBudget] = useState<any>(null);
  const [formData, setFormData] = useState({
    category: '',
    monthly_limit: '',
    period_start: '',
    period_end: '',
  });

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  const { data: budgets } = useQuery({
    queryKey: ['budgets'],
    queryFn: async () => {
      const response = await budgetAPI.getBudgets(false);
      return response.data;
    },
    enabled: isAuthenticated(),
  });

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await transactionsAPI.getCategories();
      return response.data;
    },
    enabled: isAuthenticated(),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => budgetAPI.createBudget(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets'] });
      setShowForm(false);
      resetForm();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) =>
      budgetAPI.updateBudget(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets'] });
      setEditingBudget(null);
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => budgetAPI.deleteBudget(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['budgets'] });
    },
  });

  const resetForm = () => {
    setFormData({
      category: '',
      monthly_limit: '',
      period_start: '',
      period_end: '',
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      category: formData.category,
      monthly_limit: parseFloat(formData.monthly_limit),
      period_start: new Date(formData.period_start).toISOString(),
      period_end: new Date(formData.period_end).toISOString(),
    };

    if (editingBudget) {
      updateMutation.mutate({ id: editingBudget.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (budget: any) => {
    setEditingBudget(budget);
    setFormData({
      category: budget.category,
      monthly_limit: budget.monthly_limit.toString(),
      period_start: new Date(budget.period_start).toISOString().split('T')[0],
      period_end: new Date(budget.period_end).toISOString().split('T')[0],
    });
    setShowForm(true);
  };

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this budget?')) {
      deleteMutation.mutate(id);
    }
  };

  if (!isAuthenticated()) {
    return null;
  }

  // Get start and end of current month for default dates
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    .toISOString()
    .split('T')[0];
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0)
    .toISOString()
    .split('T')[0];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Link
                href="/dashboard"
                className="text-gray-600 hover:text-indigo-600"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Manage Budgets</h1>
            </div>
            <button
              onClick={logout}
              className="px-4 py-2 text-gray-700 hover:text-red-600"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <button
            onClick={() => {
              setShowForm(!showForm);
              setEditingBudget(null);
              resetForm();
            }}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            {showForm ? 'Cancel' : 'Create Budget'}
          </button>
        </div>

        {showForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-bold mb-4">
              {editingBudget ? 'Edit Budget' : 'Create New Budget'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={formData.category}
                  onChange={(e) =>
                    setFormData({ ...formData, category: e.target.value })
                  }
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Select a category</option>
                  {categories?.map((cat: string) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Monthly Limit ($)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.monthly_limit}
                  onChange={(e) =>
                    setFormData({ ...formData, monthly_limit: e.target.value })
                  }
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Period Start
                  </label>
                  <input
                    type="date"
                    value={formData.period_start || startOfMonth}
                    onChange={(e) =>
                      setFormData({ ...formData, period_start: e.target.value })
                    }
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Period End
                  </label>
                  <input
                    type="date"
                    value={formData.period_end || endOfMonth}
                    onChange={(e) =>
                      setFormData({ ...formData, period_end: e.target.value })
                    }
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={createMutation.isPending || updateMutation.isPending}
                className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
              >
                {editingBudget ? 'Update' : 'Create'} Budget
              </button>
            </form>
          </div>
        )}

        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            <h2 className="text-xl font-bold mb-4">Your Budgets</h2>
            {budgets && budgets.length > 0 ? (
              <div className="space-y-4">
                {budgets.map((budget: any) => {
                  const percentage =
                    (budget.current_spending / budget.monthly_limit) * 100;
                  const isOverBudget = percentage > 100;

                  return (
                    <div
                      key={budget.id}
                      className="border rounded-lg p-4 hover:bg-gray-50"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-medium text-gray-900">
                            {budget.category}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {new Date(budget.period_start).toLocaleDateString()} -{' '}
                            {new Date(budget.period_end).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEdit(budget)}
                            className="text-indigo-600 hover:text-indigo-800"
                          >
                            <Edit className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleDelete(budget.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                      <div className="mb-2">
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-600">
                            ${budget.current_spending.toFixed(2)} / $
                            {budget.monthly_limit.toFixed(2)}
                          </span>
                          <span
                            className={
                              isOverBudget ? 'text-red-600' : 'text-gray-600'
                            }
                          >
                            {percentage.toFixed(1)}%
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
                      </div>
                      <p
                        className={`text-xs ${
                          budget.is_active ? 'text-green-600' : 'text-gray-500'
                        }`}
                      >
                        {budget.is_active ? 'Active' : 'Inactive'}
                      </p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-gray-500">No budgets created yet.</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

