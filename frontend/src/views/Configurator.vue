<template>
  <div class="h-full flex flex-col space-y-6">
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex-shrink-0">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Device Configurator</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Target Device</label>
          <select v-model="selectedDevice" class="w-full border-gray-300 rounded-lg shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 bg-gray-50 border">
            <option value="" disabled>Select a device to configure</option>
            <option v-for="device in devices" :key="device.id" :value="device.id">
              {{ device.hostname }} ({{ device.vendor }}) - {{ device.ip_address }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Configuration Modules (Visible only when device selected) -->
    <div v-if="selectedDevice" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <!-- IP Interface Module -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-md font-bold text-gray-800 flex items-center">
            <NetworkIcon class="w-5 h-5 mr-2 text-primary-500" />
            IP Interfaces
          </h3>
          <button @click="fetchInterfaces" class="text-sm bg-primary-50 text-primary-700 px-3 py-1.5 rounded-lg hover:bg-primary-100 font-medium flex items-center transition">
            <RefreshCwIcon class="w-4 h-4 mr-1" :class="{'animate-spin': isFetchingInterfaces}" />
            {{ isFetchingInterfaces ? 'Syncing...' : 'Sync from Device' }}
          </button>
        </div>
        
        <div v-if="interfaces.length > 0" class="space-y-3">
          <div v-for="(intf, idx) in interfaces" :key="idx" class="flex items-center justify-between p-3 border border-gray-100 rounded-lg bg-gray-50">
            <div>
              <div class="font-medium text-gray-800">{{ intf.intf }}</div>
              <div class="text-xs text-gray-500 mt-1">{{ intf.ipaddr }}</div>
            </div>
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded text-xs font-semibold" :class="intf.status === 'up' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                {{ intf.status }}
              </span>
              <button class="text-gray-400 hover:text-primary-600 transition" title="Edit Interface">
                <SettingsIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center py-8 text-gray-400 text-sm">
          Click "Sync from Device" to load interfaces.
        </div>
      </div>

      <!-- Add VLAN Module -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 class="text-md font-bold text-gray-800 flex items-center mb-4">
          <LayersIcon class="w-5 h-5 mr-2 text-primary-500" />
          Provision VLAN
        </h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">VLAN ID (1-4094)</label>
            <input type="number" v-model="newVlan.id" class="w-full border-gray-300 rounded-lg shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 bg-gray-50 border" placeholder="e.g. 100" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">VLAN Name</label>
            <input type="text" v-model="newVlan.name" class="w-full border-gray-300 rounded-lg shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 bg-gray-50 border" placeholder="e.g. SERVER-MGMT" />
          </div>
          <button @click="pushVlan" :disabled="isPushingVlan" class="w-full bg-primary-600 text-white font-medium py-2 rounded-lg hover:bg-primary-700 transition disabled:bg-gray-400 flex justify-center items-center">
             <SaveIcon v-if="!isPushingVlan" class="w-4 h-4 mr-2" />
             <div v-else class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
             {{ isPushingVlan ? 'Pushing Config...' : 'Push VLAN to Router' }}
          </button>
        </div>
      </div>
      
      <!-- Backup Config Module -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 md:col-span-2">
        <h3 class="text-md font-bold text-gray-800 flex items-center mb-4">
          <DownloadIcon class="w-5 h-5 mr-2 text-primary-500" />
          Device Configuration Backup
        </h3>
        <p class="text-sm text-gray-600 mb-4">Generate and view a full backup of the device's running configuration.</p>
        
        <button @click="triggerBackup" :disabled="isBackingUp" class="bg-gray-800 text-white font-medium py-2 px-4 rounded-lg hover:bg-gray-900 transition disabled:bg-gray-400 flex items-center">
           <DownloadIcon v-if="!isBackingUp" class="w-4 h-4 mr-2" />
           <div v-else class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
           {{ isBackingUp ? 'Generating Backup...' : 'Generate Backup Now' }}
        </button>
        
        <div v-if="backupResult" class="mt-4 p-4 bg-gray-900 rounded-lg overflow-x-auto shadow-inner border border-gray-700">
           <pre class="text-xs text-green-400 font-mono whitespace-pre-wrap">{{ backupResult }}</pre>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { NetworkIcon, LayersIcon, RefreshCwIcon, SettingsIcon, SaveIcon, DownloadIcon } from 'lucide-vue-next'

const devices = ref([
  { id: 1, hostname: 'CORE-RT-01', vendor: 'Cisco IOS', ip_address: '10.0.0.1' },
  { id: 2, hostname: 'ACC-SW-04', vendor: 'Juniper Junos', ip_address: '10.0.4.15' },
  { id: 3, hostname: 'EDGE-RT-02', vendor: 'Huawei VRP', ip_address: '10.1.0.1' },
])

const selectedDevice = ref('')
const interfaces = ref([])
const isFetchingInterfaces = ref(false)

const newVlan = ref({ id: '', name: '' })
const isPushingVlan = ref(false)

const isBackingUp = ref(false)
const backupResult = ref('')

const fetchInterfaces = () => {
  if (!selectedDevice.value) return
  isFetchingInterfaces.value = true
  
  // MOCK API CALL Delay
  setTimeout(() => {
    isFetchingInterfaces.value = false
    interfaces.value = [
      {"intf": "GigabitEthernet0/0", "ipaddr": "10.0.0.1", "status": "up", "proto": "up"},
      {"intf": "GigabitEthernet0/1", "ipaddr": "unassigned", "status": "down"},
      {"intf": "Loopback0", "ipaddr": "192.168.1.1", "status": "up"}
    ]
  }, 1500)
}

const pushVlan = () => {
  if (!selectedDevice.value || !newVlan.value.id) return
  isPushingVlan.value = true
  
  // MOCK API CALL Delay
  setTimeout(() => {
    isPushingVlan.value = false
    alert(`Successfully provisioning VLAN ${newVlan.value.id} on router.`)
    newVlan.value = { id: '', name: '' }
  }, 2000)
}

const triggerBackup = () => {
  if (!selectedDevice.value) return
  isBackingUp.value = true
  backupResult.value = ''
  
  // MOCK API CALL Delay
  setTimeout(() => {
    isBackingUp.value = false
    backupResult.value = `!
! Last configuration change at 10:15:22 UTC
!
hostname ${devices.value.find(d => d.id === selectedDevice.value).hostname}
!
interface GigabitEthernet0/0
 ip address 10.0.0.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 no ip address
 shutdown
!
line vty 0 4
 login local
 transport input ssh
!
end`
  }, 3000)
}
</script>
