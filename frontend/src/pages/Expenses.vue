<template>
  <div class="flex h-full flex-col overflow-hidden">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="[{ label: 'Marketing Hub' }, { label: 'Expenses & Budget' }]" />
      </template>
      <template #right-header>
        <Button variant="ghost" @click="expensesResource.fetch(); budgetOverview.fetch()">
          <template #icon>
            <IconRefreshCw class="h-4 w-4" />
          </template>
        </Button>
        <Button variant="solid" label="Add Expense" @click="showAddExpense = true">
          <template #prefix>
            <IconPlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </LayoutHeader>

    <!-- Content Area -->
    <div class="flex-1 overflow-auto p-5">
      <!-- KPIs -->
      <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4" v-if="budgetOverview.data">
        <StatCard label="Total Budget" :value="formatCurrency(budgetOverview.data.total_budget)" />
        <StatCard label="Total Spend" :value="formatCurrency(budgetOverview.data.total_spend)"
          :subtext="`${budgetOverview.data.utilization || 0}% Utilization`" />
        <StatCard label="Remaining" :value="formatCurrency(budgetOverview.data.remaining_budget)" />
        <StatCard label="Avg. Monthly Spend" :value="formatCurrency(budgetOverview.data.avg_monthly_spend || 0)" />
      </div>

      <!-- Budget Trend Chart -->
      <div v-if="budgetOverview.data?.chart" class="mb-6 rounded-lg border border-outline-gray-1 bg-surface-white p-5 shadow-sm">
        <h4 class="mb-4 text-base font-medium text-ink-gray-9">Budget Trend (Last 6 Months)</h4>
        <AxisChart
          :data="budgetChartData"
          :colors="['var(--blue-500)', 'var(--gray-400)']"
          :axisOptions="{ xAxisMode: 'tick', xIsSeries: true }"
          :tooltipOptions="{ formatTooltipY: (d) => formatCurrency(d) }"
          type="bar"
        />
      </div>

      <!-- Recent Expenses Table -->
      <div class="rounded-lg border border-outline-gray-1 bg-surface-white shadow-sm">
        <div class="border-b border-outline-gray-1 px-5 py-3">
          <h4 class="text-base font-medium text-ink-gray-9">Recent Expenses</h4>
        </div>

        <div v-if="expensesResource.loading" class="flex items-center justify-center py-12">
          <LoadingIndicator class="h-6 w-6" />
        </div>

        <div v-else-if="expenses.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-outline-gray-1">
            <thead>
              <tr>
                <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Date</th>
                <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Title</th>
                <th class="px-5 py-2.5 text-right text-xs font-medium uppercase text-ink-gray-5">Amount</th>
                <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Type</th>
                <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Campaign</th>
                <th class="px-5 py-2.5 text-left text-xs font-medium uppercase text-ink-gray-5">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-gray-1">
              <tr v-for="expense in expenses" :key="expense.name" class="transition-colors hover:bg-surface-gray-2">
                <td class="whitespace-nowrap px-5 py-3 text-sm text-ink-gray-6">{{ formatDate(expense.expense_date) }}</td>
                <td class="px-5 py-3 text-sm font-medium text-ink-gray-9">{{ expense.expense_title }}</td>
                <td class="whitespace-nowrap px-5 py-3 text-right text-sm font-medium text-ink-gray-9">{{ formatCurrency(expense.amount) }}</td>
                <td class="whitespace-nowrap px-5 py-3 text-sm text-ink-gray-6">{{ expense.expense_type }}</td>
                <td class="whitespace-nowrap px-5 py-3 text-sm text-ink-gray-6">{{ expense.campaign_name || '—' }}</td>
                <td class="whitespace-nowrap px-5 py-3">
                  <Badge :label="expense.status || 'Pending'" variant="subtle" :theme="getStatusTheme(expense.status)" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="relative flex h-40 w-full justify-center">
          <div class="absolute left-1/2 flex -translate-x-1/2 flex-col items-center gap-3" style="top: 25%">
            <IconWallet class="h-7 w-7 text-ink-gray-5" />
            <span class="text-base font-medium text-ink-gray-8">No expenses recorded</span>
            <span class="text-center text-sm text-ink-gray-6">Start tracking your marketing spend</span>
            <Button @click="showAddExpense = true" variant="solid" label="Add Expense">
              <template #prefix>
                <IconPlus class="h-4 w-4" />
              </template>
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Expense Dialog -->
    <Dialog v-model="showAddExpense" :options="{ title: 'Log New Expense', size: 'md' }">
      <template #body-content>
        <div class="space-y-4">
          <FormControl label="Title" v-model="newExpense.title" :required="true" placeholder="e.g. Facebook Ads Invoice #1024" />
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Amount" type="number" v-model="newExpense.amount" :required="true" placeholder="0.00" />
            <FormControl label="Date" type="date" v-model="newExpense.date" :required="true" />
          </div>
          <FormControl label="Type" type="select" v-model="newExpense.type"
            :options="[
              { label: 'Ad Spend', value: 'Ad Spend' },
              { label: 'Software', value: 'Software' },
              { label: 'Creative', value: 'Creative' },
              { label: 'Agency Fee', value: 'Agency Fee' },
              { label: 'Other', value: 'Other' },
            ]" />
          <FormControl label="Campaign (Optional)" v-model="newExpense.campaign" placeholder="Link to a campaign" />
        </div>
      </template>
      <template #actions>
        <Button variant="ghost" label="Cancel" @click="showAddExpense = false" />
        <Button variant="solid" label="Save Expense" :loading="creatingExpense" @click="saveExpense" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Breadcrumbs,
  createResource,
  Button,
  FormControl,
  Badge,
  Dialog,
  LoadingIndicator,
  AxisChart,
  toast,
} from 'frappe-ui'
import LayoutHeader from '@/components/LayoutHeader.vue'
import StatCard from '@/components/StatCard.vue'

import IconPlus from '~icons/lucide/plus'
import IconRefreshCw from '~icons/lucide/refresh-cw'
import IconWallet from '~icons/lucide/wallet'

const showAddExpense = ref(false)
const creatingExpense = ref(false)

const newExpense = ref({
  title: '',
  amount: '',
  date: new Date().toISOString().split('T')[0],
  type: 'Ad Spend',
  campaign: '',
})

// Data Fetching
const budgetOverview = createResource({
  url: 'marketing_hub.api.expenses.get_budget_overview',
  auto: true,
})

const expensesResource = createResource({
  url: 'marketing_hub.api.expenses.get_expense_list',
  params: { limit: 20 },
  auto: true,
})

// Computed
const expenses = computed(() => expensesResource.data?.expenses || [])

const budgetChartData = computed(() => {
  const chart = budgetOverview.data?.chart
  if (!chart) return { labels: [], datasets: [] }

  return {
    labels: chart.labels || [],
    datasets: [
      {
        name: 'Actual Spend',
        values: chart.actual || [],
      },
      {
        name: 'Budget',
        values: chart.budget || [],
      },
    ],
  }
})

// Actions
async function saveExpense() {
  if (!newExpense.value.title || !newExpense.value.amount) {
    toast({
      title: 'Validation Error',
      text: 'Title and Amount are required',
      icon: 'alert-circle',
      iconClasses: 'text-ink-amber-2',
    })
    return
  }

  creatingExpense.value = true
  try {
    await window.frappe.call({
      method: 'marketing_hub.api.expenses.create_expense',
      args: { data: JSON.stringify(newExpense.value) },
    })

    toast({
      title: 'Success',
      text: 'Expense logged successfully',
      icon: 'check',
      iconClasses: 'text-ink-green-2',
    })
    showAddExpense.value = false
    newExpense.value = {
      title: '',
      amount: '',
      date: new Date().toISOString().split('T')[0],
      type: 'Ad Spend',
      campaign: '',
    }
    expensesResource.fetch()
    budgetOverview.fetch()
  } catch (e) {
    toast({
      title: 'Error',
      text: e.message || 'Failed to create expense',
      icon: 'x',
      iconClasses: 'text-ink-red-2',
    })
  } finally {
    creatingExpense.value = false
  }
}

// Helpers
function formatCurrency(val) {
  if (val === undefined || val === null) return '$0.00'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}

function formatDate(date) {
  if (!date) return '—'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function getStatusTheme(status) {
  return (
    {
      Pending: 'orange',
      Approved: 'green',
      Rejected: 'red',
    }[status] || 'gray'
  )
}
</script>
