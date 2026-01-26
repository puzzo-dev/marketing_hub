<template>
  <div class="flex h-full flex-col overflow-hidden bg-gray-50">
    <!-- Header -->
    <div class="h-16 border-b flex items-center justify-between px-5 bg-white shrink-0">
      <h1 class="text-2xl font-bold text-gray-900">Expenses & Budget</h1>
      <div class="flex gap-2">
        <Button variant="solid" icon-left="plus" @click="showAddExpense = true">
          Add Expense
        </Button>
      </div>
    </div>

    <div class="flex-1 overflow-y-auto p-5">
      <div class="mx-auto max-w-6xl space-y-6">
        
        <!-- KPIs -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4" v-if="budgetOverview.data">
          <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <div class="text-sm text-gray-500">Total Budget</div>
            <div class="text-2xl font-semibold mt-1">
              {{ formatCurrency(budgetOverview.data.total_budget) }}
            </div>
          </div>
          <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <div class="text-sm text-gray-500">Total Spend</div>
            <div class="text-2xl font-semibold mt-1">
              {{ formatCurrency(budgetOverview.data.total_spend) }}
            </div>
            <div class="text-xs mt-2 text-green-600">
              {{ budgetOverview.data.utilization }}% Utilization
            </div>
          </div>
          <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
            <div class="text-sm text-gray-500">Remaining</div>
            <div class="text-2xl font-semibold mt-1">
              {{ formatCurrency(budgetOverview.data.remaining_budget) }}
            </div>
          </div>
           <!-- Placeholder for additional KPI or ROI -->
          <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex items-center justify-center text-gray-400 text-sm">
             ROI Metric Coming Soon
          </div>
        </div>

        <!-- Charts Section -->
        <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
           <h3 class="font-semibold text-gray-900 mb-4">Budget Trend (Last 6 Months)</h3>
           <!-- Simple CSS Bar Chart Fallback if no chart lib provided -->
           <div v-if="budgetOverview.data?.chart" class="h-64 flex items-end justify-between gap-2 px-4 pb-2 border-b">
              <div v-for="(label, index) in budgetOverview.data.chart.labels" :key="index" class="flex-1 flex flex-col items-center gap-2 group relative">
                 <div class="w-full flex gap-1 items-end justify-center h-full">
                    <!-- Actual Bar -->
                    <div 
                      class="w-4 bg-blue-500 rounded-t transition-all hover:bg-blue-600" 
                      :style="{ height: getBarHeight(budgetOverview.data.chart.actual[index]) }"
                      :title="'Spend: ' + formatCurrency(budgetOverview.data.chart.actual[index])"
                    ></div>
                    <!-- Budget Line Marker (Simulated) -->
                    <div 
                      class="w-4 bg-gray-300 rounded-t opacity-50"
                      :style="{ height: getBarHeight(budgetOverview.data.chart.budget[index]) }"
                      :title="'Budget: ' + formatCurrency(budgetOverview.data.chart.budget[index])"
                    ></div>
                 </div>
                 <span class="text-xs text-gray-500">{{ label }}</span>
              </div>
           </div>
           <div class="flex justify-center gap-4 mt-4 text-xs text-gray-600">
              <div class="flex items-center gap-1"><div class="w-3 h-3 bg-blue-500 rounded-sm"></div> Actual Spend</div>
              <div class="flex items-center gap-1"><div class="w-3 h-3 bg-gray-300 rounded-sm"></div> Budget</div>
           </div>
        </div>

        <!-- Recent Expenses List -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-100">
          <div class="p-4 border-b flex justify-between items-center">
             <h3 class="font-semibold text-gray-900">Recent Expenses</h3>
             <Button size="sm" variant="ghost" @click="expensesResource.fetch()">Refresh</Button>
          </div>
          <ListView
             class="min-h-[300px]"
             :columns="columns"
             :rows="expensesResource.data?.expenses || []"
             row-key="name"
          >
            <template #cell-amount="{ row }">
               <span class="font-medium">{{ formatCurrency(row.amount) }}</span>
            </template>
            <template #cell-status="{ row }">
              <Badge :theme="getStatusTheme(row.status)">{{ row.status }}</Badge>
            </template>
          </ListView>
        </div>

      </div>
    </div>

    <!-- Quick Expense Dialog -->
    <Dialog v-model="showAddExpense">
      <template #body-title>
        <h3 class="text-lg font-bold">Log New Expense</h3>
      </template>
      <template #body-content>
        <div class="space-y-4 mt-4">
           <FormControl
             label="Title"
             v-model="newExpense.title"
             :required="true"
             placeholder="e.g. Facebook Ads Invoice #1024"
           />
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
           <FormControl
             label="Type"
             type="select"
             v-model="newExpense.type"
             :options="[
               {label: 'Ad Spend', value: 'Ad Spend'},
               {label: 'Software', value: 'Software'},
               {label: 'Creative', value: 'Creative'},
               {label: 'Agency Fee', value: 'Agency Fee'},
               {label: 'Other', value: 'Other'},
             ]"
           />
           <FormControl
             label="Campaign (Optional)"
             type="link"
             doctype="Campaign"
             v-model="newExpense.campaign"
           />
        </div>
      </template>
      <template #actions>
        <Button variant="solid" :loading="creatingExpense" @click="saveExpense">
          Save Expense
        </Button>
      </template>
    </Dialog>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { createResource, Button, FormControl, ListView, Badge, Dialog, toast } from 'frappe-ui'

const showAddExpense = ref(false)
const creatingExpense = ref(false)

const newExpense = ref({
  title: '',
  amount: '',
  date: new Date().toISOString().split('T')[0],
  type: 'Ad Spend',
  campaign: '',
  vendor: '',
  description: ''
})

const columns = [
  { label: 'Date', key: 'expense_date', width: 120, type: 'date' },
  { label: 'Title', key: 'expense_title', width: 250 },
  { label: 'Amount', key: 'amount', width: 120, align: 'right' },
  { label: 'Type', key: 'expense_type', width: 120 },
  { label: 'Campaign', key: 'campaign_name', width: 200 },
  { label: 'Status', key: 'status', width: 100 },
]

// Data Fetching
const budgetOverview = createResource({
  url: 'marketing_hub.www.marketing.api.get_budget_overview',
  auto: true
})

const expensesResource = createResource({
  url: 'marketing_hub.www.marketing.api.get_expense_list',
  params: { limit: 20 },
  auto: true
})

// Actions
async function saveExpense() {
    if(!newExpense.value.title || !newExpense.value.amount) {
        toast({ title: 'Error', text: 'Title and Amount are required', icon: 'x', iconClasses: 'text-red-600' })
        return
    }

    creatingExpense.value = true
    try {
        await window.frappe.call({
            method: 'marketing_hub.www.marketing.api.create_expense',
            args: { data: JSON.stringify(newExpense.value) }
        })
        
        toast({ title: 'Success', text: 'Expense logged', icon: 'check', iconClasses: 'text-green-600' })
        showAddExpense.value = false
        // Reset form
        newExpense.value = {
            title: '',
            amount: '',
            date: new Date().toISOString().split('T')[0],
            type: 'Ad Spend',
            campaign: ''
        }
        // Refresh data
        expensesResource.fetch()
        budgetOverview.fetch()

    } catch (e) {
        toast({ title: 'Error', text: e.message, icon: 'x', iconClasses: 'text-red-600' })
    } finally {
        creatingExpense.value = false
    }
}

// Helpers
function formatCurrency(val) {
   if(val === undefined || val === null) return '$0.00'
   return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val)
}

function getStatusTheme(status) {
   return {
      'Pending': 'orange',
      'Approved': 'green',
      'Rejected': 'red'
   }[status] || 'gray'
}

function getBarHeight(value) {
   if(!value) return '0%'
   const max = Math.max(...(budgetOverview.data?.chart?.budget || []), ...(budgetOverview.data?.chart?.actual || []))
   if(max === 0) return '0%'
   return (value / max * 100) + '%'
}

</script>
