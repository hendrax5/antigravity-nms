<template>
  <div class="h-full flex flex-col space-y-4">
    <!-- Command Configurator -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex-shrink-0">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Execute Remote Command</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div class="col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Target Device</label>
          <select v-model="selectedDevice" class="w-full border-gray-300 rounded-lg shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 bg-gray-50 border">
            <option value="" disabled>Select a device</option>
            <option v-for="device in devices" :key="device.id" :value="device.id">
              {{ device.hostname }} ({{ device.vendor }})
            </option>
          </select>
        </div>
        
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Command String</label>
          <input 
            v-model="command"
            type="text" 
            placeholder="e.g., show ip interface brief" 
            class="w-full border-gray-300 rounded-lg shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 bg-gray-50 border font-mono"
            @keyup.enter="executeCommand"
          />
        </div>

        <div class="col-span-1">
          <button 
            @click="executeCommand"
            :disabled="!selectedDevice || !command || isExecuting"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white transition-colors"
            :class="(!selectedDevice || !command || isExecuting) ? 'bg-gray-400 cursor-not-allowed' : 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'"
          >
            {{ isExecuting ? 'Executing...' : 'Run Command' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Terminal Output Window -->
    <div class="flex-1 bg-dark-900 rounded-xl shadow-lg border border-gray-800 flex flex-col overflow-hidden relative">
      <div class="bg-dark-800 px-4 py-2 border-b border-gray-700 flex items-center justify-between">
        <div class="flex space-x-2">
          <div class="w-3 h-3 rounded-full bg-red-500"></div>
          <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div class="w-3 h-3 rounded-full bg-green-500"></div>
        </div>
        <div class="text-xs text-gray-400 font-mono">SSH session</div>
      </div>
      
      <div class="flex-1 p-4 overflow-y-auto font-mono text-sm text-gray-300 whitespace-pre-wrap">
        <template v-if="output">
          <div class="text-green-400 mb-2">$ {{ executedCommand }}</div>
          <div>{{ output }}</div>
        </template>
        <div v-else class="text-gray-500 italic flex items-center justify-center h-full">
          Select a device and run a command to see output here.
        </div>

        <!-- Loading overlay -->
        <div v-if="isExecuting" class="absolute inset-0 bg-dark-900/50 backdrop-blur-[1px] flex flex-col items-center justify-center z-10 transition-opacity">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mb-4"></div>
          <p class="text-primary-400 text-sm font-mono animate-pulse">Connecting to {{ getDeviceName(selectedDevice) }}...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const devices = ref([
  { id: 1, hostname: 'CORE-RT-01', vendor: 'Cisco IOS' },
  { id: 2, hostname: 'ACC-SW-04', vendor: 'Juniper Junos' },
  { id: 3, hostname: 'EDGE-RT-02', vendor: 'Huawei VRP' },
])

const selectedDevice = ref('')
const command = ref('')
const executedCommand = ref('')
const output = ref('')
const isExecuting = ref(false)

const getDeviceName = (id) => {
  const device = devices.value.find(d => d.id === id)
  return device ? device.hostname : 'Device'
}

const executeCommand = async () => {
  if (!selectedDevice.value || !command.value) return
  
  isExecuting.value = true
  executedCommand.value = command.value
  output.value = ''

  // MOCK API CALL Delay
  setTimeout(() => {
    isExecuting.value = false
    output.value = `Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.0.1        YES NVRAM  up                    up      
GigabitEthernet0/1         unassigned      YES NVRAM  administratively down down    
GigabitEthernet0/2         unassigned      YES NVRAM  administratively down down    
Loopback0                  192.168.1.1     YES NVRAM  up                    up`
    command.value = ''
  }, 2500)
}
</script>
