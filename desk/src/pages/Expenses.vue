<template>
  <div class="flex h-full flex-col overflow-auto bg-surface-gray-1">
    <div class="flex-1 px-5 py-5 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-6xl">
        <!-- Header -->
        <div class="mb-6 flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold text-ink-gray-9">Expenses & Budget</h1>
            <p class="mt-1 text-sm text-ink-gray-6">Track marketing spend and budget utilization</p>
          </div>
          <Button variant="solid" @click="showAddExpense = true">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4 w-4" />
            </template>
            Add Expense
          </Button>
        </div>

        <!-- KPIs -->
        <div class="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4" v-if="budgetOverview.data">
          <StatCard
            label="Total Budget"
            :value="formatCurrency(budgetOverview.data.total_budget)"
            icon="briefcase"
          />
          <StatCard
            label="Total Spend"
            :value="formatCurrency(budgetOverview.data.total_spend)"
            icon="credit-card"
            :subtext="`${budgetOverview.data.utilization || 0}% Utilization`"
          />
          <StatCard
            label="Remaining"
            :value="formatCurrency(budgetOverview.data.remaining_budget)"
            icon="pocket"
          />
          <StatCard
            label="Avg. Monthly Spend"
            :value="formatCurrency(budgetOverview.data.avg_monthly_spend || 0)"
            icon="trending-up"
          />
        </div>

        <!-- Budget Trend Chart -->
        <div
          v-if="budgetOverview.data?.chart"
          class="mb-6 rounded-lg border border-outline-gray-1 bg-surface-cards p-6 shadow-sm"
        >
          <h3 class="mb-4 font-semibold text-ink-gray-9">Budget Trend (Last 6 Months)</h3>
          <AxisChart
            :data="budgetChartData"
            :colors="['var(--blue-500)', 'var(--gray-400)']"
            :axisOptions="{
              xAxisMode: 'tick',
              xIsSeries: true,
            }"
            :tooltipOptions="{
              formatTooltipY: (d) => formatCurrency(d),
            }"
            type="bar"
          />
        </div>

        <!-- Recent Expenses Table -->
        <div class="rounded-lg border border-outline-gray-1 bg-surface-cards shadow-sm">
          <div class="flex items-center justify-between border-b border-outline-gray-1 px-6 py-4">
            <h3 class="font-semibold text-ink-gray-9">Recent Expenses</h3>
            <Button size="sm" variant="ghost" @click="expensesResource.fetch()">
              <template #prefix>
                <FeatherIcon name="refresh-cw" class="h-4 w-4" />
              </template>
              Refresh
            </Button>
          </div>

          <!-- Loading -->
          <div v-if="expensesResource.loading" class="flex items-center justify-center py-12">
            <LoadingIndicator class="h-8 w-8" />
          </div>

          <!-- Table -->
          <div v-else-if="expenses.length" class="overflow-x-auto">
            <table class="min-w-full divide-y divide-outline-gray-1">
              <thead class="bg-surface-gray-1">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    Date
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    Title
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    Amount
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    Type
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    Campaign
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-ink-gray-5">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-gray-1 bg-surface-cards">
                <tr
                  v-for="expense in expenses"
                  :key="expense.name"
                  class="transition-colors hover:bg-surface-gray-1"
                >
                  <td class="whitespace-nowrap px-6 py-4 text-sm text-ink-gray-6">
                    {{ formatDate(expense.expense_date) }}
                  </td>
                  <td class="px-6 py-4 text-sm font-medium text-ink-gray-9">
                    {{ expense.expense_title }}
                  </td>
                  <td class="whitespace-nowrap px-6 py-4 text-right text-sm font-semibold text-ink-gray-9">
                    {{ formatCurrency(expense.amount) }}
                  </td>
                  <td class="whitespace-nowrap px-6 py-4 text-sm text-ink-gray-6">
                    {{ expense.expense_type }}
                  </td>
                  <td class="whitespace-nowrap px-6 py-4 text-sm text-ink-gray-6">
                    {{ expense.campaign_name || '—' }}
                  </td>
                  <td class="whitespace-nowrap px-6 py-4">
                    <Badge
                      :label="expense.status || 'Pending'"
                      :theme="getStatusTheme(expense.status)"
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Empty State -->
          <div v-else class="p-12 text-center">
            <FeatherIcon name="dollar-sign" class="mx-auto h-12 w-12 text-ink-gray-4" />
            <h3 class="mt-2 text-sm font-medium text-ink-gray-9">No expenses recorded</h3>
            <p class="mt-1 text-sm text-ink-gray-5">
              Start tracking your marketing spend by adding an expense.
            </p>
            <Button class="mt-4" @click="showAddExpense = true">
              <template #prefix>
                <FeatherIcon name="plus" class="h-4 w-4" />
              </template>
              Add Expense
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Expense Dialog -->
    <Dialog
      v-model="showAddExpense"
      :options="{ title: 'Log New Expense', size: 'md' }"
    >
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            label="Title"
            v-model="newExpense.title"
            :required="true"
            placeholder="e.g. Facebook Ads Invoice #1024"
          />
          <div class="grid grid-cols-2 gap-4">
            <FormControl
              label="Amount"
              type="number"
              v-model="newExpense.amount"
              :required="true"
              placeholder="0.00"
            />
            <FormControl
              label="Date"
              type="date"
              v-model="newExpense.date"
              :required="true"
            />
          </div>
          <FormControl
            label="Type"
            type="select"
            v-model="newExpense.type"
            :options="[
              { label: 'Ad Spend', value: 'Ad Spend' },
              { label: 'Software', value: 'Software' },
              { label: 'Creative', value: 'Creative' },
              { label: 'Agency Fee', value: 'Agency Fee' },
              { label: 'Other', value: 'Other' },
            ]"
          />
          <FormControl
            label="Campaign (Optional)"
            v-model="newExpense.campaign"
            placeholder="Link to a campaign"
          />
        </div>
      </template>
      <template #actions>
        <Button variant="ghost" @click="showAddExpense = false">Cancel</Button>
        <Button variant="solid" :loading="creatingExpense" @click="saveExpense">
          Save Expense
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  createResource,
  Button,
  FormControl,
  Badge,
  Dialog,
  FeatherIcon,
  LoadingIndicator,
  AxisChart,
  toast,
} from 'frappe-ui'
import StatCard from '@/components/StatCard.vue'

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
  url: 'marketing_hub.www.marketing.api.get_budget_overview',
  auto: true,
})

const expensesResource = createResource({
  url: 'marketing_hub.www.marketing.api.get_expense_list',
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
      method: 'marketing_hub.www.marketing.api.create_expense',
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
