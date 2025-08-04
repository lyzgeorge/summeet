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
      
      let content = props.summaryData.summary.trim()
      
      // Convert markdown-like formatting to semantic HTML
      content = content
        // Headers with proper hierarchy
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        
        // Text formatting
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        
        // Blockquotes
        .replace(/^> (.*$)/gm, '<blockquote><p>$1</p></blockquote>')
        
        // Horizontal rules
        .replace(/^---$/gm, '<hr>')
        
        // Lists - handle both unordered and ordered
        .replace(/^- (.*$)/gm, '<li>$1</li>')
        .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
      
      // Wrap consecutive list items in proper list containers
      content = content.replace(/((?:<li>.*?<\/li>\s*)+)/gs, (match) => {
        // Check if this is part of an ordered list by looking at the original content
        const originalLines = match.match(/<li>.*?<\/li>/g)
        if (originalLines) {
          const firstLine = originalLines[0]
          const originalText = props.summaryData.summary
          const liContent = firstLine.replace(/<\/?li>/g, '')
          const isOrdered = originalText.includes(`1. ${liContent}`) || 
                           originalText.includes(`2. ${liContent}`) ||
                           /^\d+\. /.test(originalText.split('\n').find(line => line.includes(liContent)) || '')
          
          return isOrdered ? `<ol>${match}</ol>` : `<ul>${match}</ul>`
        }
        return `<ul>${match}</ul>`
      })
      
      // Clean up consecutive list containers
      content = content.replace(/<\/(ul|ol)>\s*<\1>/g, '')
      
      // Convert double line breaks to paragraph breaks
      content = content.replace(/\n\n+/g, '</p><p>')
      
      // Wrap remaining text in paragraphs
      const lines = content.split('\n')
      const processedLines = lines.map(line => {
        line = line.trim()
        if (!line) return ''
        
        // Skip if already wrapped in HTML tags
        if (line.match(/^<(h[1-6]|ul|ol|li|blockquote|hr|\/)/)) {
          return line
        }
        
        // Skip if it's part of a list or other structure
        if (line.includes('</p><p>')) {
          return `<p>${line}</p>`
        }
        
        // Wrap standalone text in paragraphs
        return `<p>${line}</p>`
      }).filter(line => line)
      
      content = processedLines.join('\n')
      
      // Clean up malformed paragraphs
      content = content
        .replace(/<p><\/p>/g, '')
        .replace(/<p>(<h[1-6]>)/g, '$1')
        .replace(/(<\/h[1-6]>)<\/p>/g, '$1')
        .replace(/<p>(<ul>|<ol>|<blockquote>|<hr>)/g, '$1')
        .replace(/(<\/ul>|<\/ol>|<\/blockquote>|<hr>)<\/p>/g, '$1')
        .replace(/<p><p>/g, '<p>')
        .replace(/<\/p><\/p>/g, '</p>')
      
      return content
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
      
      let content = editableSummary.value.trim()
      
      // Convert markdown-like formatting to HTML for preview (matches main formatting)
      content = content
        // Headers
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        
        // Text formatting
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        
        // Blockquotes
        .replace(/^> (.*$)/gm, '<blockquote><p>$1</p></blockquote>')
        
        // Horizontal rules
        .replace(/^---$/gm, '<hr>')
        
        // Lists
        .replace(/^- (.*$)/gm, '<li>$1</li>')
        .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
      
      // Wrap consecutive list items
      content = content.replace(/((?:<li>.*?<\/li>\s*)+)/gs, (match) => {
        const originalLines = match.match(/<li>.*?<\/li>/g)
        if (originalLines) {
          const firstLine = originalLines[0]
          const liContent = firstLine.replace(/<\/?li>/g, '')
          const isOrdered = editableSummary.value.includes(`1. ${liContent}`) || 
                           editableSummary.value.includes(`2. ${liContent}`) ||
                           /^\d+\. /.test(editableSummary.value.split('\n').find(line => line.includes(liContent)) || '')
          
          return isOrdered ? `<ol>${match}</ol>` : `<ul>${match}</ul>`
        }
        return `<ul>${match}</ul>`
      })
      
      // Clean up and wrap in paragraphs
      content = content.replace(/<\/(ul|ol)>\s*<\1>/g, '')
      content = content.replace(/\n\n+/g, '</p><p>')
      
      const lines = content.split('\n')
      const processedLines = lines.map(line => {
        line = line.trim()
        if (!line) return ''
        
        if (line.match(/^<(h[1-6]|ul|ol|li|blockquote|hr|\/)/)) {
          return line
        }
        
        if (line.includes('</p><p>')) {
          return `<p>${line}</p>`
        }
        
        return `<p>${line}</p>`
      }).filter(line => line)
      
      content = processedLines.join('\n')
      
      // Clean up
      content = content
        .replace(/<p><\/p>/g, '')
        .replace(/<p>(<h[1-6]>)/g, '$1')
        .replace(/(<\/h[1-6]>)<\/p>/g, '$1')
        .replace(/<p>(<ul>|<ol>|<blockquote>|<hr>)/g, '$1')
        .replace(/(<\/ul>|<\/ol>|<\/blockquote>|<hr>)<\/p>/g, '$1')
        .replace(/<p><p>/g, '<p>')
        .replace(/<\/p><\/p>/g, '</p>')
      
      return content
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
