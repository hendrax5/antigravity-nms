<template>
  <div class="h-full flex flex-col space-y-6">
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex-shrink-0">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Configuration Diff Viewer</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Target Device</label>
          <select v-model="selectedDevice" @change="fetchHistory" class="w-full border-gray-300 rounded-lg shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm p-2 bg-gray-50 border">
            <option value="" disabled>Select a device</option>
            <option v-for="device in devices" :key="device.id" :value="device.id">
              {{ device.hostname }} - {{ device.ip_address }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- History Panel -->
    <div v-if="selectedDevice" class="grid grid-cols-1 md:grid-cols-3 gap-6 flex-1 min-h-0">
      
      <!-- Commits List -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 overflow-y-auto">
        <h3 class="text-md font-bold text-gray-800 mb-3 flex items-center">
          <GitCommitIcon class="w-5 h-5 mr-2 text-primary-500" />
          Backup History (Git)
        </h3>
        
        <div v-if="isFetchingHistory" class="text-center py-4 text-gray-500">Loading history...</div>
        
        <div v-else-if="history.length > 0" class="space-y-3">
          <div v-for="(commit, idx) in history" :key="commit.commit_hash" 
               @click="fetchContent(commit.commit_hash)"
               class="p-3 border rounded-lg cursor-pointer transition"
               :class="selectedCommit === commit.commit_hash ? 'bg-primary-50 border-primary-500 ring-1 ring-primary-500' : 'bg-gray-50 border-gray-100 hover:bg-gray-100'">
            <div class="font-medium text-sm text-gray-800">{{ commit.message }}</div>
            <div class="text-xs text-gray-500 mt-1 mt-1 flex justify-between">
              <span>{{ formatDate(commit.date) }}</span>
              <span class="font-mono text-[10px] text-gray-400">{{ commit.commit_hash.substring(0, 7) }}</span>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center py-8 text-gray-400 text-sm">
          No backup history found for this device.
        </div>
      </div>

      <!-- Content Viewer -->
      <div class="bg-gray-900 rounded-xl shadow-sm border border-gray-700 p-0 md:col-span-2 overflow-hidden flex flex-col">
        <div class="bg-gray-800 px-4 py-3 border-b border-gray-700 flex justify-between items-center text-gray-300">
           <span class="text-sm font-medium flex items-center">
             <FileTextIcon class="w-4 h-4 mr-2" />
             <span v-if="selectedCommit">Viewing File @ {{ selectedCommit.substring(0, 7) }}</span>
             <span v-else>Select a commit to view configuration</span>
           </span>
        </div>
        
        <div class="p-4 overflow-auto flex-1 h-full">
           <div v-if="isFetchingContent" class="text-center py-12 text-gray-500">Loading file content...</div>
           <pre v-else-if="configContent" class="text-xs text-green-400 font-mono whitespace-pre-wrap leading-relaxed">{{ configContent }}</pre>
           <div v-else class="h-full flex items-center justify-center text-gray-600 text-sm">
              <span v-if="selectedDevice && !selectedCommit">Click a commit on the left to see the configuration file content.</span>
           </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { GitCommitIcon, FileTextIcon } from 'lucide-vue-next'

const devices = ref([
  { id: 1, hostname: 'CORE-RT-01', vendor: 'Cisco IOS', ip_address: '10.0.0.1' },
  { id: 2, hostname: 'ACC-SW-04', vendor: 'Juniper Junos', ip_address: '10.0.4.15' },
])

const selectedDevice = ref('')
const selectedCommit = ref('')
const history = ref([])
const configContent = ref('')

const isFetchingHistory = ref(false)
const isFetchingContent = ref(false)

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString(undefined, options);
}

const fetchHistory = () => {
  if (!selectedDevice.value) return
  isFetchingHistory.value = true
  selectedCommit.value = ''
  configContent.value = ''
  
  // MOCK API CALL Delay
  setTimeout(() => {
    isFetchingHistory.value = false
    history.value = [
      { commit_hash: 'a1b2c3d4e5f6', date: new Date().toISOString(), message: 'Automated config backup for CORE-RT-01', author: 'NMS Bot' },
      { commit_hash: 'f6e5d4c3b2a1', date: new Date(Date.now() - 86400000).toISOString(), message: 'Added new VLAN 100 via Dashboard', author: 'Hendra' },
      { commit_hash: '9081726354ab', date: new Date(Date.now() - 172800000).toISOString(), message: 'Initial configuration snapshot', author: 'NMS Bot' },
    ]
  }, 800)
}

const fetchContent = (hash) => {
  selectedCommit.value = hash
  isFetchingContent.value = true
  
  // MOCK API CALL Delay
  setTimeout(() => {
    isFetchingContent.value = false
    configContent.value = `!
! Last configuration change by NMS Framework
!
hostname CORE-RT-01
!
interface GigabitEthernet0/0
 ip address 10.0.0.1 255.255.255.0
 no shutdown
!
interface Vlan100
 description SERVER_MGMT
 ip address 192.168.100.1 255.255.255.0
!
router bgp 65000
 neighbor 10.0.0.2 remote-as 65001
!
end`
  }, 500)
}
</script>
