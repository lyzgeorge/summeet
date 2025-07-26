<template>
  <div class="min-h-screen flex-col">
    <!-- Header -->
    <header class="header sticky top-0 z-10">
      <div class="container-wide header-content flex items-center justify-between py-4">
        <div class="flex items-center gap-4">
          <div class="logo flex items-center gap-2">
            <div class="logo-icon">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <h1 class="text-heading">Summeet</h1>
          </div>
        </div>
        
        <!-- Progress indicator -->
        <div class="flex items-center justify-center gap-4">
          <div class="flex items-center gap-2">
            <div class="step-dot completed"></div>
            <span class="text-sm text-green-400">Input</span>
          </div>
          <div class="step-line active"></div>
          <div class="flex items-center gap-2">
            <div :class="currentTranscription ? 'step-dot active' : 'step-dot'"></div>
            <span :class="currentTranscription ? 'text-primary' : 'text-muted'" class="text-caption">Transcript</span>
          </div>
          <div class="step-line" :class="currentSummary ? 'active' : ''"></div>
          <div class="flex items-center gap-2">
            <div :class="currentSummary ? 'step-dot active' : 'step-dot'"></div>
            <span :class="currentSummary ? 'text-primary' : 'text-muted'" class="text-caption">Summary</span>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <div class="badge badge-success">
            Open Source
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container-wide py-12 flex-1">
      <div class="space-y-12">
        <!-- Input Methods Selection -->
        <section v-if="!currentTranscription" class="animate-fade-in">
          
          <div class="grid grid-cols-1 xl:grid-cols-2 gap-8 max-w-6xl mx-auto">
            <!-- Audio Upload Option -->
            <div class="card animate-slide-up">
              <div class="card-header-success">
                <div class="flex items-center gap-3">
                  <div class="logo-icon bg-accent-success">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-title">Audio Upload</h3>
                    <p class="text-caption text-accent-success">Automatically transcribe audio files</p>
                  </div>
                </div>
              </div>
              <div class="card-body">
                <AudioUpload @transcription-complete="handleTranscriptionComplete" />
              </div>
            </div>

            <!-- Direct Transcript Input Option -->
            <div class="card animate-slide-up animation-delay-100">
              <div class="card-header-success">
                <div class="flex items-center gap-3">
                  <div class="logo-icon bg-accent-success">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-title">Text Input</h3>
                    <p class="text-caption text-accent-success">Already have a transcript? Start here</p>
                  </div>
                </div>
              </div>
              <div class="card-body">
                <DirectTranscriptInput @transcript-entered="handleDirectTranscript" />
              </div>
            </div>
          </div>
        </section>

        <!-- Transcript Editor -->
        <section v-if="currentTranscription" class="animate-fade-in">
          <TranscriptEditor 
            :transcription-data="currentTranscription"
            @summary-generated="handleSummaryGenerated"
            @back-to-input="resetToInput"
          />
        </section>

        <!-- Summary Panel -->
        <section v-if="currentSummary" class="animate-fade-in">
          <SummaryPanel 
            :summary-data="currentSummary" 
            @new-session="resetToInput"
          />
        </section>
      </div>
    </main>

    <!-- Footer -->
    <footer class="glass border-t py-8">
      <div class="container-wide text-center">
        <div class="flex flex-wrap items-center justify-center gap-x-4 gap-y-2">
          <div class="flex items-center gap-2">
            <div class="logo-icon size-6">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <span class="text-mono text-primary font-medium">Summeet</span>
          </div>
          <span class="text-secondary">&copy; 2024 AI-powered transcription & summarization platform</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref } from 'vue'
import AudioUpload from './components/AudioUpload.vue'
import DirectTranscriptInput from './components/DirectTranscriptInput.vue'
import TranscriptEditor from './components/TranscriptEditor.vue'
import SummaryPanel from './components/SummaryPanel.vue'

export default {
  name: 'App',
  components: {
    AudioUpload,
    DirectTranscriptInput,
    TranscriptEditor,
    SummaryPanel
  },
  setup() {
    const currentTranscription = ref(null)
    const currentSummary = ref(null)

    const handleTranscriptionComplete = (transcriptionData) => {
      currentTranscription.value = transcriptionData
      currentSummary.value = null // Reset summary when new transcription is available
    }

    const handleDirectTranscript = (transcriptData) => {
      currentTranscription.value = transcriptData
      currentSummary.value = null
    }

    const handleSummaryGenerated = (summaryData) => {
      currentSummary.value = summaryData
    }

    const resetToInput = () => {
      currentTranscription.value = null
      currentSummary.value = null
    }

    return {
      currentTranscription,
      currentSummary,
      handleTranscriptionComplete,
      handleDirectTranscript,
      handleSummaryGenerated,
      resetToInput
    }
  }
}
</script>