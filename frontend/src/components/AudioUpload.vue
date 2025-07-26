<template>
  <div class="space-y-6">
    <!-- File Upload Area -->
    <div 
      class="upload-zone"
      :class="{ 'active': isDragOver }"
      @dragover.prevent="isDragOver = true"
      @dragleave.prevent="isDragOver = false"
      @drop.prevent="handleDrop"
      @click="fileInput.click()"
    >
      <div class="flex flex-col items-center">
        <div class="w-16 h-16 bg-elevated rounded-2xl flex items-center justify-center mb-6 border border-primary">
          <svg class="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <div class="text-title mb-2">
          {{ selectedFile ? selectedFile.name : 'Drop your audio file here' }}
        </div>
        <div class="text-body mb-4">or click to browse files</div>
        <div class="flex flex-wrap gap-2 justify-center">
          <span class="badge badge-primary">MP3</span>
          <span class="badge badge-primary">WAV</span>
          <span class="badge badge-primary">M4A</span>
          <span class="badge badge-primary">FLAC</span>
        </div>
      </div>
      <input
        ref="fileInput"
        type="file"
        accept="audio/*"
        class="hidden"
        @change="handleFileSelect"
      />
    </div>

    <!-- Options -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label class="form-label">Language</label>
        <select v-model="language" class="form-field">
          <option value="auto">Auto-Detect</option>
          <option value="en">English</option>
          <option value="zh">Chinese</option>
        </select>
      </div>
      
      <div>
        <label class="form-label">Word Boost (Optional)</label>
        <input
          v-model="wordBoost"
          type="text"
          placeholder="e.g., project names, technical terms"
          class="form-field"
        />
        <p class="mt-1 text-caption">Comma-separated words to improve recognition</p>
      </div>
    </div>

    <!-- Action Button -->
    <button
      @click="uploadAndTranscribe"
      :disabled="!selectedFile || isProcessing"
      class="w-full btn btn-primary relative overflow-hidden"
    >
      <span v-if="isProcessing" class="flex items-center justify-center">
        <div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-3"></div>
        {{ processingMessage }}
      </span>
      <span v-else class="flex items-center justify-center">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Transcribe Audio
      </span>
    </button>

    <!-- Status Messages -->
    <div v-if="statusMessage" class="alert" :class="statusClass">
      {{ statusMessage }}
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { transcriptionAPI } from '../api.js'

export default {
  name: 'AudioUpload',
  emits: ['transcription-complete'],
  setup(props, { emit }) {
    const selectedFile = ref(null)
    const language = ref('auto')
    const wordBoost = ref('')
    const isProcessing = ref(false)
    const processingMessage = ref('Processing...')
    const statusMessage = ref('')
    const statusClass = ref('')
    const isDragOver = ref(false)
    const fileInput = ref(null)

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        selectedFile.value = file
        clearStatus()
      }
    }

    const handleDrop = (event) => {
      isDragOver.value = false
      const files = event.dataTransfer.files
      if (files.length > 0) {
        selectedFile.value = files[0]
        clearStatus()
      }
    }

    const clearStatus = () => {
      statusMessage.value = ''
      statusClass.value = ''
    }

    const showStatus = (message, type = 'info') => {
      statusMessage.value = message
      statusClass.value = {
        'success': 'alert-success',
        'error': 'alert-error', 
        'info': 'alert-info'
      }[type]
    }

    const uploadAndTranscribe = async () => {
      if (!selectedFile.value) return

      isProcessing.value = true
      processingMessage.value = 'Uploading and transcribing...'
      clearStatus()

      try {
        const result = await transcriptionAPI.upload(selectedFile.value)
        
        showStatus('✅ Transcription completed successfully!', 'success')
        emit('transcription-complete', result)
        
        // Reset form
        selectedFile.value = null
        if (fileInput.value) {
          fileInput.value.value = ''
        }
        
      } catch (error) {
        console.error('Transcription error:', error)
        showStatus(
          `❌ Transcription failed: ${error.response?.data?.detail || error.message}`,
          'error'
        )
      } finally {
        isProcessing.value = false
        processingMessage.value = 'Processing...'
      }
    }

    return {
      selectedFile,
      language,
      wordBoost,
      isProcessing,
      processingMessage,
      statusMessage,
      statusClass,
      isDragOver,
      fileInput,
      handleFileSelect,
      handleDrop,
      uploadAndTranscribe
    }
  }
}
</script>