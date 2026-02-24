<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div class="relative w-64">
        <input 
          type="text" 
          placeholder="Search devices..." 
          class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500 text-sm shadow-sm"
        />
        <SearchIcon class="w-4 h-4 text-gray-400 absolute left-3 top-3" />
      </div>
      <button class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium shadow-sm transition flex items-center space-x-2">
        <PlusIcon class="w-4 h-4" />
        <span>Add Device</span>
      </button>
    </div>

    <!-- Inventory Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hostname</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IP Address</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vendor</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Site</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="device in devices" :key="device.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="font-medium text-gray-900">{{ device.hostname }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ device.ip_address }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 py-1 text-xs font-medium rounded-md bg-blue-100 text-blue-800">
                {{ device.vendor }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ device.site }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 flex items-center space-x-1 text-xs font-semibold rounded-full"
                    :class="device.status === 'active' ? 'text-green-600' : 'text-red-600'">
                <div class="w-1.5 h-1.5 rounded-full" :class="device.status === 'active' ? 'bg-green-500' : 'bg-red-500'"></div>
                <span>{{ device.status === 'active' ? 'Online' : 'Offline' }}</span>
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button class="text-primary-600 hover:text-primary-900 mr-3">Edit</button>
              <button class="text-red-600 hover:text-red-900">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { SearchIcon, PlusIcon } from 'lucide-vue-next'
import { ref } from 'vue'

const devices = ref([
  { id: 1, hostname: 'CORE-RT-01', ip_address: '10.0.0.1', vendor: 'Cisco IOS', site: 'HQ-Jakarta', status: 'active' },
  { id: 2, hostname: 'ACC-SW-04', ip_address: '10.0.4.15', vendor: 'Juniper Junos', site: 'Branch-Bandung', status: 'active' },
  { id: 3, hostname: 'FW-MAIN-01', ip_address: '10.0.0.254', vendor: 'VyOS', site: 'HQ-Jakarta', status: 'offline' },
  { id: 4, hostname: 'EDGE-RT-02', ip_address: '10.1.0.1', vendor: 'Huawei VRP', site: 'DC-Singapore', status: 'active' },
])
</script>
