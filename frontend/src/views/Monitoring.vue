<template>
  <div class="h-full flex flex-col space-y-6">
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex-shrink-0 flex justify-between items-center">
      <div>
        <h2 class="text-lg font-semibold text-gray-800">Advanced Network Telemetry</h2>
        <p class="text-sm text-gray-500 mt-1">Real-time bandwidth, CPU, and Memory utilization powered by Grafana</p>
      </div>
      <div>
         <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
           <span class="flex w-2 h-2 bg-green-500 rounded-full mr-1.5 animate-pulse"></span>
           Telegraf Agent Active
         </span>
      </div>
    </div>

    <!-- Embedded Grafana Dashboard -->
    <div class="bg-gray-900 rounded-xl shadow-sm border border-gray-700 flex-1 overflow-hidden relative">
       <!-- 
          In production, this URL would be dynamically constructed based on the Tenant ID and Grafana embedding specs. 
          Assuming Grafana is exposed on port 3000 mapping to coolify/localhost 
       -->
       <div v-if="iframeLoading" class="absolute inset-0 flex items-center justify-center bg-gray-900 z-10">
          <div class="text-center">
             <div class="inline-block animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full mb-4"></div>
             <p class="text-gray-400 text-sm">Loading Live Telemetry...</p>
          </div>
       </div>

       <iframe 
         @load="iframeLoading = false"
         title="Grafana Dashboard" 
         src="http://localhost:3000/d-solo/rYdddlPWk/node-exporter-full?orgId=1&theme=dark&panelId=77&autofresh=10s" 
         width="100%" 
         height="100%" 
         frameborder="0"
         class="w-full h-full border-0">
       </iframe>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const iframeLoading = ref(true)
</script>
