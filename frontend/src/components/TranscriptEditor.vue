<template>
  <div class="card max-w-6xl mx-auto">
    <div class="card-header-primary">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="logo-icon">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </div>
          <div>
            <h2 class="text-title">Edit Transcript & Speakers</h2>
            <p class="text-caption text-accent-primary">Review and modify the transcription</p>
          </div>
        </div>
        <button
          @click="$emit('back-to-input')"
          class="btn btn-ghost"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
          </svg>
          Back to Input
        </button>
      </div>
    </div>
    
    <div class="card-body space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Transcript Editor -->
        <div>
          <div class="flex justify-between items-center mb-3">
            <h3 class="text-title">Transcript</h3>
            <span>{{ transcriptWordCount }} words</span>
          </div>
          
          <textarea
            v-model="editableTranscript"
            class="form-field h-64 font-mono text-sm"
            placeholder="Transcript will appear here after transcription..."
            :readonly="!transcriptionData"
          ></textarea>
          
          <div class="mt-2 flex justify-between">
            <span>Editable transcript</span>
            <span v-if="isTranscriptModified" class="text-caption text-accent-warning">Modified</span>
          </div>
        </div>

        <!-- Speaker Information -->
        <div>
          <h3 class="text-title mb-3">Speaker Information</h3>
          
          <div v-if="speakers.length === 0" class="text-center py-8">
            <p class="text-body">No speakers detected yet. Upload audio file first.</p>
          </div>
          
          <div v-else class="space-y-3">
            <div 
              v-for="(speaker, index) in speakers" 
              :key="speaker.speaker"
              class="border rounded-lg p-4"
            >
              <div class="flex items-center mb-2">
                <label class="w-20 flex-shrink-0">
                  {{ speaker.speaker }}:
                </label>
                <input
                  v-model="speaker.description"
                  type="text"
                  :placeholder="`Name or role for ${speaker.speaker}`"
                  class="form-field flex-1"
                />
                <button
                  @click="deleteSpeaker(index)"
                  class="ml-2 p-2 text-red-500 hover:bg-red-50 rounded-md"
                  title="Delete speaker"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
              </div>
              <p class="text-caption">
                Add speaker details to improve summary quality
              </p>
            </div>
          </div>

          <!-- Speaker Management -->
          <div class="mt-4">
            <button
              @click="addSpeaker"
              class="w-full btn btn-secondary"
            >
              + Add Speaker
            </button>
          </div>

          <!-- Summary Options -->
          <div class="mt-6">
            <h3 class="text-title mb-3">Summary Options</h3>
            <div class="flex justify-center">
              <!-- Language Selection -->
              <div>
                <label class="form-label text-center mb-3">
                  Summary Language
                </label>
                <div class="radio-button-group">
                  <label class="radio-button" :class="{ 'selected': summaryLanguage === 'cn' }">
                    <input
                      v-model="summaryLanguage"
                      type="radio"
                      value="cn"
                      class="sr-only"
                    />
                    <span>中文</span>
                  </label>
                  <label class="radio-button" :class="{ 'selected': summaryLanguage === 'en' }">
                    <input
                      v-model="summaryLanguage"
                      type="radio"
                      value="en"
                      class="sr-only"
                    />
                    <span>English</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <button
          @click="generateSummary"
          :disabled="!canGenerateSummary || isGeneratingSummary"
          class="btn btn-primary"
        >
        <span v-if="isGeneratingSummary" class="flex items-center">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Generating Summary...
        </span>
        <span v-else>
          Generate Summary
        </span>
        </button>

        <button
          @click="exportMarkdown"
          :disabled="!transcriptionData"
          class="btn btn-success"
        >
          Export Markdown
        </button>
      </div>

      <!-- Status Messages -->
      <div v-if="statusMessage" class="alert" :class="statusClass">
        {{ statusMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { transcriptionAPI } from '../api.js'

export default {
  name: 'TranscriptEditor',
  props: {
    transcriptionData: {
      type: Object,
      default: null
    }
  },
  emits: ['summary-generated', 'back-to-input'],
  setup(props, { emit }) {
    const editableTranscript = ref('')
    const speakers = ref([])
    const originalTranscript = ref('')
    const isGeneratingSummary = ref(false)
    const statusMessage = ref('')
    const statusClass = ref('')
    const summaryLanguage = ref('cn')
    const summaryTemperature = ref(0.8)


    // Computed properties
    const transcriptWordCount = computed(() => {
      return editableTranscript.value.split(/\s+/).filter(word => word.length > 0).length
    })

    const isTranscriptModified = computed(() => {
      return editableTranscript.value !== originalTranscript.value
    })

    const canGenerateSummary = computed(() => {
      return props.transcriptionData && editableTranscript.value.trim().length > 0
    })

    // Watch for transcription data changes
    watch(() => props.transcriptionData, (newData) => {
      if (newData) {
        editableTranscript.value = newData.transcript || ''
        originalTranscript.value = newData.transcript || ''
        
        // Parse speakers
        try {
          const speakersData = JSON.parse(newData.speakers || '[]')
          speakers.value = speakersData.map(speaker => ({
            speaker: speaker.speaker || 'Unknown',
            description: speaker.description || ''
          }))
        } catch (e) {
          console.error('Error parsing speakers:', e)
          speakers.value = []
        }
      }
    }, { immediate: true })

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

    const addSpeaker = () => {
      const nextSpeakerLabel = `Speaker ${String.fromCharCode(65 + speakers.value.length)}`
      speakers.value.push({
        speaker: nextSpeakerLabel,
        description: ''
      })
    }

    const deleteSpeaker = (index) => {
      speakers.value.splice(index, 1)
    }

    const generateSummary = async () => {
      if (!props.transcriptionData) return

      isGeneratingSummary.value = true
      statusMessage.value = ''

      try {
        const result = await transcriptionAPI.summarize(
          props.transcriptionData.id, 
          summaryLanguage.value, 
          summaryTemperature.value
        )
        
        showStatus('✅ Summary generated successfully!', 'success')
        emit('summary-generated', {
          ...props.transcriptionData,
          summary: result.summary,
          transcript: editableTranscript.value,
          speakers: JSON.stringify(speakers.value)
        })
        
      } catch (error) {
        console.error('Summary generation error:', error)
        showStatus(
          `❌ Summary generation failed: ${error.response?.data?.detail || error.message}`,
          'error'
        )
      } finally {
        isGeneratingSummary.value = false
      }
    }

    const exportMarkdown = async () => {
      if (!props.transcriptionData) return

      try {
        const blob = await transcriptionAPI.export(props.transcriptionData.id)
        
        // Create download link
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${props.transcriptionData.filename || 'meeting'}_summary.md`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        showStatus('✅ Markdown file downloaded!', 'success')
        
      } catch (error) {
        console.error('Export error:', error)
        showStatus(
          `❌ Export failed: ${error.response?.data?.detail || error.message}`,
          'error'
        )
      }
    }

    return {
      editableTranscript,
      speakers,
      isGeneratingSummary,
      statusMessage,
      statusClass,
      summaryLanguage,
      summaryTemperature,
      transcriptWordCount,
      isTranscriptModified,
      canGenerateSummary,
      addSpeaker,
      deleteSpeaker,
      generateSummary,
      exportMarkdown
    }
  }
}
</script>