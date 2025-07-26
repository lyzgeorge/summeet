<template>
  <div class="space-y-6">
    <!-- Transcript Input -->
    <div>
      <label class="form-label">Meeting Transcript</label>
      <textarea
        v-model="transcript"
        placeholder="Speaker A: Welcome to the meeting. Let's start with updates.
Speaker B: Thanks, development is progressing well.
Speaker A: Great! What about the budget?"
        class="form-field h-40 font-mono text-sm"
        :class="{ 'border-red-300 focus:border-red-300 focus:ring-red-500': hasError }"
      ></textarea>
      
      <div class="flex justify-between items-center mt-2">
        <span>{{ wordCount }} words</span>
        <span v-if="hasError" class="text-caption text-accent-error">Please enter a transcript</span>
      </div>
    </div>


    <!-- Speaker Detection Info -->
    <div class="alert alert-info">
      <div class="flex items-start">
        <svg class="w-5 h-5 mt-0.5 mr-3 flex-shrink-0 text-primary" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
        </svg>
        <div>
          <h4 class="text-title">Speaker Detection</h4>
          <p class="mt-1 text-body">
            We'll automatically detect speakers from your transcript. You can edit speaker information in the next step.
          </p>
        </div>
      </div>
    </div>

    <!-- Action Button -->
    <button
      @click="processTranscript"
      :disabled="!canProcess || isProcessing"
      class="w-full btn btn-primary"
    >
      <span v-if="isProcessing" class="flex items-center">
        <svg class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Processing...
      </span>
      <span v-else>
        Process Transcript
      </span>
    </button>

    <!-- Status Messages -->
    <div v-if="statusMessage" class="alert" :class="statusClass">
      {{ statusMessage }}
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { transcriptionAPI } from '../api.js'

export default {
  name: 'DirectTranscriptInput',
  emits: ['transcript-entered'],
  setup(props, { emit }) {
    const transcript = ref('')
    const isProcessing = ref(false)
    const hasError = ref(false)
    const statusMessage = ref('')
    const statusClass = ref('')

    // Computed properties
    const wordCount = computed(() => {
      return transcript.value.split(/\s+/).filter(word => word.length > 0).length
    })

    const canProcess = computed(() => {
      return transcript.value.trim().length > 10 && wordCount.value > 5
    })

    const showStatus = (message, type = 'info') => {
      statusMessage.value = message
      statusClass.value = {
        'success': 'alert-success',
        'error': 'alert-error',
        'info': 'alert-info'
      }[type]
      
      // Auto-clear after 5 seconds
      setTimeout(() => {
        statusMessage.value = ''
      }, 5000)
    }

    const detectSpeakers = (text) => {
      // Simple speaker detection - look for patterns like "Speaker A:", "John:", etc.
      const speakerPatterns = [
        /^(Speaker [A-Z]|Speaker \d+):/gm,
        /^([A-Z][a-zA-Z\s]*[A-Z]):/gm,
        /^([A-Z][a-z]+):/gm
      ]
      
      const speakers = new Set()
      
      speakerPatterns.forEach(pattern => {
        const matches = text.match(pattern)
        if (matches) {
          matches.forEach(match => {
            const speaker = match.replace(':', '').trim()
            speakers.add(speaker)
          })
        }
      })
      
      // If no speakers detected, create default speakers
      if (speakers.size === 0) {
        speakers.add('Speaker A')
        speakers.add('Speaker B')
      }
      
      return Array.from(speakers).map(speaker => ({
        speaker,
        description: ''
      }))
    }

    const processTranscript = async () => {
      hasError.value = false
      
      if (!canProcess.value) {
        hasError.value = true
        showStatus('Please enter a meaningful transcript (at least 10 characters and 5 words)', 'error')
        return
      }

      isProcessing.value = true
      statusMessage.value = ''

      try {
        const speakers = detectSpeakers(transcript.value)
        const filename = `Meeting ${new Date().toLocaleDateString()}`
        
        // Save transcript to database
        const savedTranscript = await transcriptionAPI.saveDirectTranscript(
          filename,
          transcript.value,
          JSON.stringify(speakers)
        )
        
        showStatus('✅ Transcript processed successfully!', 'success')
        emit('transcript-entered', savedTranscript)
        
      } catch (error) {
        console.error('Processing error:', error)
        showStatus(`❌ Error processing transcript: ${error.response?.data?.detail || error.message}`, 'error')
      } finally {
        isProcessing.value = false
      }
    }

    return {
      transcript,
      isProcessing,
      hasError,
      statusMessage,
      statusClass,
      wordCount,
      canProcess,
      processTranscript
    }
  }
}
</script>