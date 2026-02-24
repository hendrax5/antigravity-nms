<template>
  <div class="h-screen bg-gray-50 flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-dark-900 text-white flex flex-col">
      <div class="h-16 flex items-center justify-center border-b border-dark-700 font-bold text-lg tracking-wider">
        <span class="text-primary-400 mr-2">Net</span>Dash
      </div>
      <nav class="flex-1 p-4 space-y-2">
        <router-link to="/" class="flex items-center px-4 py-3 rounded-lg hover:bg-dark-700 transition" :class="{ 'bg-primary-600': $route.path === '/' }">
          Dashboard
        </router-link>
        <router-link to="/inventory" class="flex items-center px-4 py-3 rounded-lg hover:bg-dark-700 transition" :class="{ 'bg-primary-600': $route.path.startsWith('/inventory') }">
          Inventory
        </router-link>
        <router-link to="/configurator" class="flex items-center px-4 py-3 rounded-lg hover:bg-gray-700 transition" :class="{ 'bg-primary-600': $route.path.startsWith('/configurator') }">
          Device Configurator
        </router-link>
        <router-link to="/history" class="flex items-center px-4 py-3 rounded-lg hover:bg-gray-700 transition" :class="{ 'bg-primary-600': $route.path.startsWith('/history') }">
          Config Diff Viewer
        </router-link>
        <router-link to="/monitoring" class="flex items-center px-4 py-3 rounded-lg hover:bg-gray-700 transition" :class="{ 'bg-primary-600': $route.path.startsWith('/monitoring') }">
          Telemetry & Monitoring
        </router-link>
      </nav>
      <div class="p-4 border-t border-dark-700 text-sm text-gray-400 text-center">
        Multivendor Dashboard v1.0
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Navbar -->
      <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shadow-sm">
        <h1 class="text-xl font-semibold text-gray-700">{{ $route.name || 'Dashboard' }}</h1>
        <div class="flex items-center space-x-4">
          <!-- Tenant Context Switcher (Placeholder) -->
          <select class="bg-gray-100 border border-gray-300 text-gray-700 text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block p-2">
            <option>Global View</option>
            <option>Company A</option>
            <option>Company B</option>
          </select>
          <div class="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white font-bold cursor-pointer">
            H
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
</script>
