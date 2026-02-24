<template>
  <div class="space-y-6">
    <!-- Stats Row -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div v-for="stat in stats" :key="stat.name" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center space-x-4">
        <div :class="`p-3 rounded-lg ${stat.colorClass}`">
          <component :is="stat.icon" class="w-6 h-6 text-white" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-500">{{ stat.name }}</p>
          <p class="text-2xl font-bold text-gray-900">{{ stat.value }}</p>
        </div>
      </div>
    </div>

    <!-- Recent Activity & Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Device Status by Vendor</h2>
        <div class="space-y-4">
          <div v-for="vendor in vendors" :key="vendor.name" class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition">
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 rounded-full" :class="vendor.status === 'operational' ? 'bg-green-500' : 'bg-red-500'"></div>
              <span class="font-medium text-gray-700">{{ vendor.name }}</span>
            </div>
            <div class="text-sm text-gray-500">{{ vendor.count }} devices</div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h2>
        <div class="space-y-3">
          <button class="w-full flex items-center justify-center space-x-2 bg-primary-50 text-primary-700 py-2.5 rounded-lg hover:bg-primary-100 transition font-medium">
            <PlusIcon class="w-4 h-4" />
            <span>Add New Device</span>
          </button>
          <button class="w-full flex items-center justify-center space-x-2 bg-gray-50 text-gray-700 py-2.5 rounded-lg hover:bg-gray-100 transition font-medium">
            <TerminalIcon class="w-4 h-4" />
            <span>Run Network Command</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  ServerIcon, 
  ActivityIcon, 
  AlertTriangleIcon, 
  UsersIcon,
  PlusIcon,
  TerminalIcon
} from 'lucide-vue-next'

const stats = [
  { name: 'Total Devices', value: '124', icon: ServerIcon, colorClass: 'bg-blue-500' },
  { name: 'Active Connections', value: '118', icon: ActivityIcon, colorClass: 'bg-green-500' },
  { name: 'Alerts', value: '3', icon: AlertTriangleIcon, colorClass: 'bg-red-500' },
  { name: 'Sites Managed', value: '15', icon: UsersIcon, colorClass: 'bg-purple-500' },
]

const vendors = [
  { name: 'Cisco IOS', count: 45, status: 'operational' },
  { name: 'Juniper Junos', count: 32, status: 'operational' },
  { name: 'MikroTik RouterOS', count: 28, status: 'operational' },
  { name: 'Huawei VRP', count: 15, status: 'operational' },
  { name: 'VyOS', count: 4, status: 'issues' },
]
</script>
