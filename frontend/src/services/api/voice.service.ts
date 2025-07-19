/**
 * Voice Service for NGX Agents
 * Handles voice transcription, synthesis, and conversational AI
 * Enhanced with ElevenLabs integration and real-time processing
 */

import { apiClient, API_ENDPOINTS } from './client';
import { useAuthStore } from '../../store/authStore';

// Voice configuration types
export interface VoiceConfig {
  language: string;
  model: 'whisper-1' | 'whisper-large' | 'gemini-voice';
  voice: string;
  stability: number;
  similarityBoost: number;
  style: number;
  speakerBoost: boolean;
}

export interface TranscriptionRequest {
  audioData: Blob | ArrayBuffer;
  config?: Partial<VoiceConfig>;
  context?: {
    conversationId?: string;
    agentId?: string;
    previousTranscripts?: string[];
  };
}

export interface TranscriptionResponse {
  id: string;
  text: string;
  confidence: number;
  language: string;
  duration: number;
  segments?: Array<{
    start: number;
    end: number;
    text: string;
    confidence: number;
  }>;
  metadata: {
    model: string;
    processingTime: number;
    tokensUsed: number;
  };
}

export interface SynthesisRequest {
  text: string;
  config?: Partial<VoiceConfig>;
  context?: {
    agentId?: string;
    emotion?: 'neutral' | 'happy' | 'sad' | 'excited' | 'calm' | 'professional';
    speed?: number;
    pitch?: number;
  };
}

export interface SynthesisResponse {
  id: string;
  audioUrl: string;
  audioData?: ArrayBuffer;
  duration: number;
  format: 'mp3' | 'wav' | 'ogg';
  metadata: {
    voice: string;
    model: string;
    processingTime: number;
    tokensUsed: number;
  };
}

export interface ConversationalRequest {
  audioData: Blob | ArrayBuffer;
  agentId: string;
  conversationId?: string;
  config?: {
    enableRealTimeResponse?: boolean;
    includeEmotions?: boolean;
    contextAware?: boolean;
    streamResponse?: boolean;
  };
}

export interface ConversationalResponse {
  id: string;
  transcription: TranscriptionResponse;
  response: {
    text: string;
    audio: SynthesisResponse;
    emotion: string;
    confidence: number;
  };
  metadata: {
    totalProcessingTime: number;
    tokensUsed: number;
    agentName: string;
  };
}

export interface VoiceActivityDetection {
  isActive: boolean;
  energy: number;
  frequency: number;
  timestamp: number;
}

/**
 * Voice Service Class
 * Central service for all voice operations
 */
export class VoiceService {
  private static instance: VoiceService;
  private mediaRecorder: MediaRecorder | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphone: MediaStreamAudioSourceNode | null = null;
  private isRecording = false;
  private vadCallbacks: Array<(vad: VoiceActivityDetection) => void> = [];
  private audioChunks: Blob[] = [];
  
  private constructor() {}
  
  static getInstance(): VoiceService {
    if (!VoiceService.instance) {
      VoiceService.instance = new VoiceService();
    }
    return VoiceService.instance;
  }

  /**
   * Initialize voice service with microphone access
   */
  async initialize(): Promise<void> {
    try {
      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
          channelCount: 1
        }
      });

      // Initialize audio context
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 2048;
      this.analyser.smoothingTimeConstant = 0.8;

      // Connect microphone to analyser
      this.microphone = this.audioContext.createMediaStreamSource(stream);
      this.microphone.connect(this.analyser);

      // Initialize MediaRecorder
      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => {
        // Audio recording stopped, chunks are ready for processing
      };

      // Start voice activity detection
      this.startVoiceActivityDetection();

      console.log('Voice service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize voice service:', error);
      throw {
        message: 'Failed to initialize voice service. Please check microphone permissions.',
        code: 'VOICE_INIT_ERROR'
      };
    }
  }

  /**
   * Start voice activity detection
   */
  private startVoiceActivityDetection(): void {
    if (!this.analyser) return;

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const detectActivity = () => {
      if (!this.analyser) return;

      this.analyser.getByteFrequencyData(dataArray);

      // Calculate energy level
      let sum = 0;
      for (let i = 0; i < bufferLength; i++) {
        sum += dataArray[i];
      }
      const energy = sum / bufferLength;

      // Calculate dominant frequency
      let maxIndex = 0;
      let maxValue = 0;
      for (let i = 0; i < bufferLength; i++) {
        if (dataArray[i] > maxValue) {
          maxValue = dataArray[i];
          maxIndex = i;
        }
      }
      const frequency = (maxIndex * (this.audioContext?.sampleRate || 44100)) / (2 * bufferLength);

      // Determine if voice is active (simple threshold-based approach)
      const isActive = energy > 30 && frequency > 80 && frequency < 3000;

      const vad: VoiceActivityDetection = {
        isActive,
        energy,
        frequency,
        timestamp: Date.now()
      };

      // Notify callbacks
      this.vadCallbacks.forEach(callback => callback(vad));

      // Continue detection
      requestAnimationFrame(detectActivity);
    };

    detectActivity();
  }

  /**
   * Subscribe to voice activity detection
   */
  onVoiceActivity(callback: (vad: VoiceActivityDetection) => void): () => void {
    this.vadCallbacks.push(callback);
    
    // Return unsubscribe function
    return () => {
      const index = this.vadCallbacks.indexOf(callback);
      if (index > -1) {
        this.vadCallbacks.splice(index, 1);
      }
    };
  }

  /**
   * Start recording audio
   */
  async startRecording(): Promise<void> {
    if (!this.mediaRecorder) {
      throw { message: 'Voice service not initialized', code: 'NOT_INITIALIZED' };
    }

    if (this.isRecording) {
      throw { message: 'Recording already in progress', code: 'ALREADY_RECORDING' };
    }

    try {
      this.audioChunks = [];
      this.mediaRecorder.start(100); // Record in 100ms chunks
      this.isRecording = true;
      
      console.log('Recording started');
    } catch (error) {
      console.error('Failed to start recording:', error);
      throw {
        message: 'Failed to start recording',
        code: 'RECORDING_START_ERROR'
      };
    }
  }

  /**
   * Stop recording and get audio data
   */
  async stopRecording(): Promise<Blob> {
    if (!this.mediaRecorder || !this.isRecording) {
      throw { message: 'No recording in progress', code: 'NO_RECORDING' };
    }

    return new Promise((resolve, reject) => {
      this.mediaRecorder!.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm;codecs=opus' });
        this.audioChunks = [];
        this.isRecording = false;
        resolve(audioBlob);
      };

      this.mediaRecorder!.onerror = (event) => {
        reject({
          message: 'Recording failed',
          code: 'RECORDING_ERROR',
          details: event
        });
      };

      this.mediaRecorder!.stop();
    });
  }

  /**
   * Transcribe audio to text
   */
  async transcribeAudio(request: TranscriptionRequest): Promise<TranscriptionResponse> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      const formData = new FormData();
      
      // Convert audio data to blob if needed
      let audioBlob: Blob;
      if (request.audioData instanceof ArrayBuffer) {
        audioBlob = new Blob([request.audioData], { type: 'audio/webm' });
      } else {
        audioBlob = request.audioData;
      }

      formData.append('audio', audioBlob, 'audio.webm');
      formData.append('config', JSON.stringify(request.config || {}));
      formData.append('context', JSON.stringify(request.context || {}));

      const response = await apiClient.post<TranscriptionResponse>(
        API_ENDPOINTS.VOICE.TRANSCRIBE,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      return response.data;
    } catch (error: any) {
      console.error('Transcription error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to transcribe audio',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Synthesize text to speech
   */
  async synthesizeText(request: SynthesisRequest): Promise<SynthesisResponse> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      const response = await apiClient.post<SynthesisResponse>(
        API_ENDPOINTS.VOICE.SYNTHESIZE,
        {
          text: request.text,
          config: request.config || {},
          context: request.context || {},
        },
        {
          responseType: 'json'
        }
      );

      return response.data;
    } catch (error: any) {
      console.error('Synthesis error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to synthesize text',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Full conversational AI interaction
   */
  async conversationalInteraction(request: ConversationalRequest): Promise<ConversationalResponse> {
    try {
      const user = useAuthStore.getState().user;
      if (!user) {
        throw { message: 'User not authenticated', code: 401 };
      }

      const formData = new FormData();
      
      // Convert audio data to blob if needed
      let audioBlob: Blob;
      if (request.audioData instanceof ArrayBuffer) {
        audioBlob = new Blob([request.audioData], { type: 'audio/webm' });
      } else {
        audioBlob = request.audioData;
      }

      formData.append('audio', audioBlob, 'audio.webm');
      formData.append('agent_id', request.agentId);
      if (request.conversationId) {
        formData.append('conversation_id', request.conversationId);
      }
      formData.append('config', JSON.stringify(request.config || {}));

      const response = await apiClient.post<ConversationalResponse>(
        API_ENDPOINTS.VOICE.CONVERSATIONAL,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      return response.data;
    } catch (error: any) {
      console.error('Conversational interaction error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to process conversational interaction',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Get available voices
   */
  async getAvailableVoices(): Promise<Array<{
    id: string;
    name: string;
    language: string;
    gender: 'male' | 'female' | 'neutral';
    accent: string;
    style: string;
    preview?: string;
  }>> {
    try {
      const response = await apiClient.get('/api/v1/voice/voices');
      return response.data;
    } catch (error: any) {
      console.error('Get voices error:', error);
      throw {
        message: error.response?.data?.message || 'Failed to get available voices',
        code: error.response?.status || 500,
      };
    }
  }

  /**
   * Play audio from URL or ArrayBuffer
   */
  async playAudio(audioData: string | ArrayBuffer): Promise<void> {
    try {
      let audioUrl: string;
      
      if (typeof audioData === 'string') {
        audioUrl = audioData;
      } else {
        const blob = new Blob([audioData], { type: 'audio/mp3' });
        audioUrl = URL.createObjectURL(blob);
      }

      const audio = new Audio(audioUrl);
      
      return new Promise((resolve, reject) => {
        audio.onended = () => {
          if (typeof audioData !== 'string') {
            URL.revokeObjectURL(audioUrl);
          }
          resolve();
        };
        
        audio.onerror = (error) => {
          if (typeof audioData !== 'string') {
            URL.revokeObjectURL(audioUrl);
          }
          reject(error);
        };
        
        audio.play().catch(reject);
      });
    } catch (error) {
      console.error('Play audio error:', error);
      throw {
        message: 'Failed to play audio',
        code: 'AUDIO_PLAY_ERROR'
      };
    }
  }

  /**
   * Get current recording state
   */
  isCurrentlyRecording(): boolean {
    return this.isRecording;
  }

  /**
   * Get audio context for advanced operations
   */
  getAudioContext(): AudioContext | null {
    return this.audioContext;
  }

  /**
   * Get analyser node for real-time audio analysis
   */
  getAnalyser(): AnalyserNode | null {
    return this.analyser;
  }

  /**
   * Clean up resources
   */
  cleanup(): void {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
    }
    
    if (this.audioContext) {
      this.audioContext.close();
    }
    
    this.vadCallbacks = [];
    this.audioChunks = [];
    this.isRecording = false;
  }
}

// Export singleton instance
export const voiceService = VoiceService.getInstance();
export default voiceService;