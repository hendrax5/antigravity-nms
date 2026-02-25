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
      <button @click="showAddModal = true" class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg text-sm font-medium shadow-sm transition flex items-center space-x-2">
        <PlusIcon class="w-4 h-4" />
        <span>Add Device</span>
      </button>
    </div>

    <!-- Add Device Modal -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-800">Add New Device</h3>
          <button @click="showAddModal = false" class="text-gray-400 hover:text-gray-600">
            <XIcon class="w-5 h-5" />
          </button>
        </div>
        <form @submit.prevent="submitDevice" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Hostname</label>
              <input v-model="form.hostname" type="text" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm p-2 bg-gray-50 border" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Site ID</label>
              <input v-model.number="form.site_id" type="number" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm p-2 bg-gray-50 border" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">IP Address</label>
            <input v-model="form.ip_address" type="text" required placeholder="e.g. 192.168.1.1" class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm p-2 bg-gray-50 border" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Vendor</label>
            <select v-model="form.vendor" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm p-2 bg-gray-50 border">
              <option value="" disabled>Select Vendor</option>
              <option value="cisco_ios">Cisco IOS</option>
              <option value="juniper_junos">Juniper Junos</option>
              <option value="mikrotik_routeros">MikroTik RouterOS</option>
              <option value="vyos">VyOS</option>
            </select>
          </div>

          <div class="border-t pt-4 mt-2">
            <label class="block text-sm font-medium text-gray-700 mb-2">Connection Settings</label>
            <div class="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Method</label>
                <select v-model="form.connection_method" @change="handleMethodChange" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm p-1.5 bg-gray-50 border">
                  <option value="ssh">SSH (CLI)</option>
                  <option value="snmp">SNMP</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Port</label>
                <input v-model.number="form.port" type="number" required class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm p-1.5 bg-gray-50 border" />
              </div>
            </div>

            <!-- SSH Credentials -->
            <div v-if="form.connection_method === 'ssh'" class="grid grid-cols-2 gap-4 bg-blue-50 p-3 rounded-lg border border-blue-100">
              <div>
                <label class="block text-xs text-gray-700 mb-1">SSH Username</label>
                <input v-model="form.ssh_username" type="text" required class="w-full border-gray-300 rounded shadow-sm sm:text-sm p-1.5" />
              </div>
              <div>
                <label class="block text-xs text-gray-700 mb-1">SSH Password</label>
                <input v-model="form.ssh_password" type="password" required class="w-full border-gray-300 rounded shadow-sm sm:text-sm p-1.5" />
              </div>
            </div>

            <!-- SNMP Protocol -->
            <div v-if="form.connection_method === 'snmp'" class="bg-indigo-50 p-3 rounded-lg border border-indigo-100">
              <label class="block text-xs text-gray-700 mb-1">SNMP Community String</label>
              <input v-model="form.snmp_community" type="password" required placeholder="public" class="w-full border-gray-300 rounded shadow-sm sm:text-sm p-1.5" />
            </div>
          </div>

          <div class="mt-6 flex justify-end space-x-3">
            <button type="button" @click="showAddModal = false" class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">Cancel</button>
            <button type="submit" :disabled="isSubmitting" class="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 flex items-center">
              <span v-if="isSubmitting">Saving...</span>
              <span v-else>Save Device</span>
            </button>
          </div>
        </form>
      </div>
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
              <div class="text-xs text-gray-500">{{ device.connection_method.toUpperCase() }} : {{ device.port }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ device.ip_address }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 py-1 text-xs font-medium rounded-md bg-blue-100 text-blue-800">
                {{ device.vendor }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ device.site_id }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 flex items-center space-x-1 text-xs font-semibold rounded-full"
                    :class="device.status === 'online' ? 'text-green-600' : 'text-gray-600'">
                <div class="w-1.5 h-1.5 rounded-full" :class="device.status === 'online' ? 'bg-green-500' : 'bg-gray-500'"></div>
                <span>{{ device.status === 'online' ? 'Online' : 'Unknown' }}</span>
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
import { SearchIcon, PlusIcon, XIcon } from 'lucide-vue-next'
import { ref, onMounted } from 'vue'

const devices = ref([])
const showAddModal = ref(false)
const isSubmitting = ref(false)

const getDefaultForm = () => ({
  hostname: '',
  ip_address: '',
  vendor: '',
  site_id: 1,
  connection_method: 'ssh',
  port: 22,
  ssh_username: '',
  ssh_password: '',
  snmp_community: 'public'
})

const form = ref(getDefaultForm())

const handleMethodChange = () => {
  if (form.value.connection_method === 'ssh') {
    form.value.port = 22
  } else if (form.value.connection_method === 'snmp') {
    form.value.port = 161
  }
}

const getApiPath = (path) => {
  // If running via npm run dev locally without Nginx proxy, 
  // point directly to the backend URL on port 8000.
  // We use relative path for production where Nginx routes /api/v1 to backend.
  const isDev = window.location.hostname === 'localhost' && window.location.port !== '80';
  return isDev ? `http://localhost:8000${path}` : path;
}

const fetchDevices = async () => {
  try {
    const res = await fetch(getApiPath('/api/v1/devices/'))
    if (res.ok) {
      devices.value = await res.json()
    } else {
      console.error('Failed to load devices', await res.text())
    }
  } catch (err) {
    console.error('Network error fetching devices:', err)
  }
}

const submitDevice = async () => {
  try {
    isSubmitting.value = true
    const res = await fetch(getApiPath('/api/v1/devices/'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })
    
    if (res.ok) {
      showAddModal.value = false
      form.value = getDefaultForm()
      await fetchDevices()
      alert('Device added successfully!')
    } else {
      const errorData = await res.json()
      alert(`Error creating device: ${JSON.stringify(errorData)}`)
    }
  } catch (err) {
    console.error('Error submitting device:', err)
    alert('Network error. Check console.')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchDevices()
})
</script>
