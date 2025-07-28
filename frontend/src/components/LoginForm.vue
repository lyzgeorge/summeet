<template>
  <div class="flex items-center justify-center min-h-[calc(100vh-200px)]">
    <div class="card max-w-md w-full mx-4">
      <div class="card-header-primary">
        <div class="flex items-center justify-center">
          <div class="logo flex items-center gap-2">
            <div class="logo-icon">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <h1 class="text-heading">Summeet</h1>
          </div>
        </div>
        <p class="text-center text-subtitle mt-3">
          Sign in to your account
        </p>
      </div>
      
      <div class="card-body">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label for="email" class="form-label">
              Email address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              v-model="form.email"
              class="form-field"
              placeholder="Enter your email"
              :disabled="isLoading"
            />
          </div>
          
          <div>
            <label for="password" class="form-label">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autocomplete="current-password"
              required
              v-model="form.password"
              class="form-field"
              placeholder="Enter your password"
              :disabled="isLoading"
            />
          </div>

          <div v-if="error" class="alert alert-error">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="btn btn-primary w-full py-3"
          >
            <span v-if="isLoading" class="inline-flex items-center gap-2">
              <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Signing in...
            </span>
            <span v-else>Sign in</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { authAPI } from '../api.js'

export default {
  name: 'LoginForm',
  emits: ['login-success'],
  setup(props, { emit }) {
    const form = ref({
      email: '',
      password: ''
    })
    
    const isLoading = ref(false)
    const error = ref('')

    const handleLogin = async () => {
      if (!form.value.email || !form.value.password) {
        error.value = 'Please fill in all fields'
        return
      }

      isLoading.value = true
      error.value = ''

      try {
        await authAPI.login(form.value.email, form.value.password)
        emit('login-success')
      } catch (err) {
        console.error('Login error:', err)
        error.value = err.response?.data?.detail || 'Login failed. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    return {
      form,
      isLoading,
      error,
      handleLogin
    }
  }
}
</script>