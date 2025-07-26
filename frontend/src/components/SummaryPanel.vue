<template>
  <div class="card max-w-6xl mx-auto">
    <div class="card-header-primary">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="logo-icon bg-accent-purple">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <h2 class="text-title">Meeting Summary</h2>
            <p class="text-caption text-accent-purple">AI-generated insights and key points</p>
          </div>
        </div>
        <button
          @click="$emit('new-session')"
          class="btn btn-primary"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          New Session
        </button>
      </div>
    </div>
    
    <div class="card-body space-y-6">
      <!-- Summary Display -->
      <div v-if="summaryData?.summary">
        <div class="bg-secondary rounded-lg p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-title">Generated Summary</h3>
            <div class="flex gap-2">
              <button
                @click="copySummary"
                class="btn btn-secondary"
              >
                Copy
              </button>
              <button
                @click="editSummary"
                class="btn btn-secondary"
              >
                Edit
              </button>
            </div>
          </div>
        
          <!-- Summary Content -->
          <div v-if="!isEditingMode" class="markdown-content">
            <div v-html="formattedSummary"></div>
          </div>
        
          <!-- Edit Mode -->
          <div v-else class="magic-down-container">
            <!-- Editor Toolbar -->
            <div class="bg-secondary border rounded-t-lg px-4 py-2 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-subtitle">Markdown Editor</span>
                <span class="text-caption">Live preview available</span>
              </div>
              <button
                @click="togglePreview"
                class="btn btn-ghost text-xs"
              >
                {{ showPreview ? 'Editor Only' : 'Show Preview' }}
              </button>
            </div>

          <!-- Editor Container -->
          <div class="editor-content border rounded-b-md overflow-hidden">
            <div class="editor-wrapper" :class="{ 'split-view': showPreview }">
              <!-- Editor Section -->
              <div 
                ref="editorContainer" 
                class="editor-section"
                :class="{ 'half-width': showPreview }"
              ></div>
              
              <!-- Preview Section -->
              <div 
                v-if="showPreview" 
                class="preview-section half-width border-l bg-secondary"
              >
                <div class="preview-header px-4 py-2 bg-tertiary border-b">
                  <span class="text-subtitle">Preview</span>
                </div>
                <div class="preview-content p-4 markdown-content" v-html="formattedPreview"></div>
              </div>
            </div>
          </div>

            <!-- Action Buttons -->
            <div class="mt-4 flex gap-3">
              <button
                @click="saveSummaryEdit"
                class="btn btn-success"
              >
                Save Changes
              </button>
              <button
                @click="cancelSummaryEdit"
                class="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- No Summary State -->
      <div v-else class="text-center py-12">
        <div class="mb-6">
          <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-heading mb-3">No Summary Generated</h3>
        <p class="text-body">
          Upload audio and generate a summary to view it here.
        </p>
      </div>

      <!-- Meeting Details -->
      <div v-if="summaryData" class="border-t pt-6">
        <h3 class="text-title mb-4">Meeting Details</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-secondary p-4 rounded-lg">
            <span class="text-subtitle">File Name:</span>
            <p class="mt-1 text-body">{{ summaryData.filename || 'Unknown' }}</p>
          </div>
          
          <div class="bg-secondary p-4 rounded-lg">
            <span class="text-subtitle">Created:</span>
            <p class="mt-1 text-body">{{ formatDate(summaryData.created_at) }}</p>
          </div>
          
          <div class="bg-secondary p-4 rounded-lg">
            <span class="text-subtitle">Transcript Length:</span>
            <p class="mt-1 text-body">{{ transcriptWordCount }} words</p>
          </div>
          
          <div class="bg-secondary p-4 rounded-lg">
            <span class="text-subtitle">Speakers:</span>
            <p class="mt-1 text-body">{{ speakerCount }} detected</p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div v-if="summaryData?.summary" class="flex flex-col sm:flex-row gap-3 justify-center">
        <button
          @click="exportMarkdown"
          :disabled="isExporting"
          class="btn btn-success"
        >
          <span v-if="isExporting">Exporting...</span>
          <span v-else>Export Markdown</span>
        </button>
        
        <button
          @click="shareableLink"
          class="btn btn-primary"
        >
          Copy Link
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
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { transcriptionAPI } from '../api.js'
import { MagicdownEditor } from '@xiangfa/mdeditor'

export default {
  name: 'SummaryPanel',
  props: {
    summaryData: {
      type: Object,
      default: null
    }
  },
  emits: ['new-session'],
  setup(props) {
    const isEditingMode = ref(false)
    const editableSummary = ref('')
    const originalSummary = ref('')
    const isExporting = ref(false)
    const statusMessage = ref('')
    const statusClass = ref('')
    const editorContainer = ref(null)
    const showPreview = ref(false)
    let mdEditor = null

    // Computed properties
    const formattedSummary = computed(() => {
      if (!props.summaryData?.summary) return ''
      
      // Convert markdown-like formatting to clean HTML for prose styling
      return props.summaryData.summary
        .replace(/### (.*)/g, '<h3>$1</h3>')
        .replace(/## (.*)/g, '<h2>$1</h2>')
        .replace(/# (.*)/g, '<h1>$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        // Convert markdown list items to <li> tags
        .replace(/^(?:-|\d+\.) (.*)/gm, '<li>$1</li>')
        // Wrap blocks of <li> tags with <ul> tags
        .replace(/((?:<li>.*?<\/li>\s*)+)/gs, '<ul>$1</ul>')
        .replace(/<\/ul>\s*<ul>/g, '<ul>') // Merge consecutive <ul> tags
        .replace(/\n\n/g, '<\/p><p>')
        .replace(/^(.*)$/gm, (match, p1) => {
          if (p1 && !p1.startsWith('<') && p1.trim()) {
            return `<p>${p1}<\/p>`
          }
          return p1
        })
        .replace(/<p><\/p>/g, '')
        .replace(/<p>(<[hul])/g, '$1')
        .replace(/(<\/[hul][^>]*>)<\/p>/g, '$1')
    })

    const transcriptWordCount = computed(() => {
      if (!props.summaryData?.transcript) return 0
      return props.summaryData.transcript.split(/\s+/).filter(word => word.length > 0).length
    })

    const speakerCount = computed(() => {
      if (!props.summaryData?.speakers) return 0
      try {
        const speakers = JSON.parse(props.summaryData.speakers)
        return speakers.length
      } catch (e) {
        return 0
      }
    })

    const formattedPreview = computed(() => {
      if (!editableSummary.value) return ''
      
      // Convert markdown-like formatting to HTML for preview
      return editableSummary.value
        .replace(/### (.*)/g, '<h3 class="text-lg font-semibold text-gray-800 mt-4 mb-2">$1</h3>')
        .replace(/## (.*)/g, '<h2 class="text-xl font-bold text-gray-900 mt-6 mb-3">$1</h2>')
        .replace(/# (.*)/g, '<h1 class="text-2xl font-bold text-gray-900 mt-8 mb-4">$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
        .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
        .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono">$1</code>')
        .replace(/^- (.*)/gm, '<li class="ml-4 mb-1">$1</li>')
        .replace(/^\d+\. (.*)/gm, '<li class="ml-4 mb-1">$1</li>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>')
    })

    // Watch for summary data changes
    watch(() => props.summaryData, (newData) => {
      if (newData?.summary) {
        originalSummary.value = newData.summary
        editableSummary.value = newData.summary
      }
    }, { immediate: true })

    const showStatus = (message, type = 'info') => {
      statusMessage.value = message
      statusClass.value = {
        'success': 'alert-success',
        'error': 'alert-error',
        'info': 'alert-info'
      }[type]
      
      // Auto-clear after 3 seconds
      setTimeout(() => {
        statusMessage.value = ''
      }, 3000)
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown'
      try {
        return new Date(dateString).toLocaleString()
      } catch (e) {
        return 'Unknown'
      }
    }

    const copySummary = async () => {
      if (!props.summaryData?.summary) return
      
      try {
        await navigator.clipboard.writeText(props.summaryData.summary)
        showStatus('📋 Summary copied to clipboard!', 'success')
      } catch (error) {
        console.error('Copy failed:', error)
        showStatus('❌ Failed to copy summary', 'error')
      }
    }

    const editSummary = async () => {
      isEditingMode.value = true
      editableSummary.value = originalSummary.value
      
      // Wait for the DOM to update
      await nextTick()
      
      // Initialize the markdown editor
      if (editorContainer.value && !mdEditor) {
        mdEditor = new MagicdownEditor({
          root: editorContainer.value,
          defaultValue: editableSummary.value,
          placeholder: "Edit your summary...",
          onChange: (value) => {
            editableSummary.value = value
            // Auto-adjust container height based on content
            adjustEditorHeight()
          }
        })
        await mdEditor.create()
        adjustEditorHeight()
      } else if (mdEditor) {
        mdEditor.update(editableSummary.value)
        adjustEditorHeight()
      }
    }

    const adjustEditorHeight = () => {
      if (editorContainer.value && mdEditor) {
        // Set a minimum height for the editor
        const minHeight = showPreview.value ? 300 : 400
        editorContainer.value.style.minHeight = `${minHeight}px`
        editorContainer.value.style.height = 'auto'
      }
    }

    const togglePreview = () => {
      showPreview.value = !showPreview.value
      // Adjust editor size when toggling preview
      nextTick(() => {
        adjustEditorHeight()
      })
    }

    const saveSummaryEdit = () => {
      // In a real app, you might want to save this to the backend
      originalSummary.value = editableSummary.value
      isEditingMode.value = false
      if (mdEditor) {
        mdEditor.destroy()
        mdEditor = null
      }
      showStatus('✅ Summary updated!', 'success')
    }

    const cancelSummaryEdit = () => {
      editableSummary.value = originalSummary.value
      isEditingMode.value = false
      if (mdEditor) {
        mdEditor.destroy()
        mdEditor = null
      }
    }

    const exportMarkdown = async () => {
      if (!props.summaryData) return

      isExporting.value = true
      
      try {
        const blob = await transcriptionAPI.export(props.summaryData.id)
        
        // Create download link
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${props.summaryData.filename || 'meeting'}_summary.md`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        showStatus('📁 Markdown file downloaded!', 'success')
        
      } catch (error) {
        console.error('Export error:', error)
        showStatus(
          `❌ Export failed: ${error.response?.data?.detail || error.message}`,
          'error'
        )
      } finally {
        isExporting.value = false
      }
    }

    const shareableLink = async () => {
      if (!props.summaryData) return
      
      try {
        const url = `${window.location.origin}?transcription=${props.summaryData.id}`
        await navigator.clipboard.writeText(url)
        showStatus('🔗 Shareable link copied to clipboard!', 'success')
      } catch (error) {
        console.error('Copy link failed:', error)
        showStatus('❌ Failed to copy link', 'error')
      }
    }

    return {
      isEditingMode,
      editableSummary,
      isExporting,
      statusMessage,
      statusClass,
      editorContainer,
      showPreview,
      formattedSummary,
      formattedPreview,
      transcriptWordCount,
      speakerCount,
      formatDate,
      copySummary,
      editSummary,
      saveSummaryEdit,
      cancelSummaryEdit,
      exportMarkdown,
      shareableLink,
      togglePreview,
      adjustEditorHeight
    }
  }
}
</script>
