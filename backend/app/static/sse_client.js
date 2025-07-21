/**
 * Enhanced SSE Client for GENESIS Streaming
 * =========================================
 * 
 * A robust client for consuming Server-Sent Events with:
 * - Automatic reconnection
 * - Error handling
 * - Progress tracking
 * - Event buffering
 * - Performance metrics
 */

class GenesisSSEClient {
    constructor(config = {}) {
        // Configuration
        this.config = {
            baseUrl: config.baseUrl || '/api/v2/stream',
            reconnectInterval: config.reconnectInterval || 3000,
            maxReconnectAttempts: config.maxReconnectAttempts || 5,
            heartbeatTimeout: config.heartbeatTimeout || 60000,
            bufferSize: config.bufferSize || 100,
            debug: config.debug || false,
            ...config
        };

        // State
        this.eventSource = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.eventBuffer = [];
        this.metrics = {
            startTime: null,
            firstChunkTime: null,
            chunkCount: 0,
            errorCount: 0,
            reconnectCount: 0
        };

        // Callbacks
        this.handlers = {
            onStart: null,
            onChunk: null,
            onIntent: null,
            onAgents: null,
            onArtifacts: null,
            onProgress: null,
            onError: null,
            onEnd: null,
            onHeartbeat: null,
            onReconnect: null,
            onMetrics: null
        };

        // Heartbeat monitoring
        this.heartbeatTimer = null;
        this.lastHeartbeat = null;
    }

    /**
     * Start streaming with a message
     * @param {string} message - User message
     * @param {Object} options - Stream options
     * @returns {Promise<string>} - Conversation ID
     */
    async startStream(message, options = {}) {
        if (this.eventSource) {
            this.close();
        }

        // Reset metrics
        this.metrics = {
            startTime: Date.now(),
            firstChunkTime: null,
            chunkCount: 0,
            errorCount: 0,
            reconnectCount: this.metrics.reconnectCount || 0
        };

        // Prepare request
        const requestBody = {
            message,
            conversation_id: options.conversationId,
            metadata: options.metadata || {},
            stream_options: {
                chunk_size: options.chunkSize || 50,
                include_heartbeat: options.includeHeartbeat !== false,
                heartbeat_interval: options.heartbeatInterval || 30,
                include_progress: options.includeProgress !== false,
                format: 'sse'
            },
            preferences: options.preferences || {
                language: 'es',
                detail_level: 'normal',
                include_artifacts: true
            }
        };

        try {
            // Get auth token
            const token = await this.getAuthToken();

            // Create EventSource with POST support
            const url = `${this.config.baseUrl}/chat`;
            this.eventSource = new EventSourcePolyfill(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(requestBody)
            });

            this.setupEventHandlers();
            this.startHeartbeatMonitor();
            this.isConnected = true;
            this.reconnectAttempts = 0;

            return requestBody.conversation_id || 'pending';

        } catch (error) {
            this.handleError(error);
            throw error;
        }
    }

    /**
     * Setup event handlers for SSE
     */
    setupEventHandlers() {
        if (!this.eventSource) return;

        // Connection opened
        this.eventSource.onopen = () => {
            this.log('SSE connection opened');
            this.isConnected = true;
            
            if (this.reconnectAttempts > 0 && this.handlers.onReconnect) {
                this.handlers.onReconnect(this.reconnectAttempts);
            }
        };

        // Handle specific event types
        this.eventSource.addEventListener('start', (event) => {
            const data = this.parseEventData(event.data);
            this.log('Stream started:', data);
            
            if (this.handlers.onStart) {
                this.handlers.onStart(data);
            }
        });

        this.eventSource.addEventListener('chunk', (event) => {
            const data = this.parseEventData(event.data);
            this.metrics.chunkCount++;
            
            if (!this.metrics.firstChunkTime) {
                this.metrics.firstChunkTime = Date.now();
                const ttfb = this.metrics.firstChunkTime - this.metrics.startTime;
                this.log(`Time to first byte: ${ttfb}ms`);
            }

            this.bufferEvent('chunk', data);
            
            if (this.handlers.onChunk) {
                this.handlers.onChunk(data);
            }
        });

        this.eventSource.addEventListener('intent', (event) => {
            const data = this.parseEventData(event.data);
            this.log('Intent analyzed:', data);
            
            if (this.handlers.onIntent) {
                this.handlers.onIntent(data);
            }
        });

        this.eventSource.addEventListener('agents', (event) => {
            const data = this.parseEventData(event.data);
            this.log('Agents selected:', data);
            
            if (this.handlers.onAgents) {
                this.handlers.onAgents(data);
            }
        });

        this.eventSource.addEventListener('artifacts', (event) => {
            const data = this.parseEventData(event.data);
            this.log('Artifacts received:', data);
            
            if (this.handlers.onArtifacts) {
                this.handlers.onArtifacts(data);
            }
        });

        this.eventSource.addEventListener('progress', (event) => {
            const data = this.parseEventData(event.data);
            
            if (this.handlers.onProgress) {
                this.handlers.onProgress(data);
            }
        });

        this.eventSource.addEventListener('heartbeat', (event) => {
            this.lastHeartbeat = Date.now();
            const data = this.parseEventData(event.data);
            
            if (this.handlers.onHeartbeat) {
                this.handlers.onHeartbeat(data);
            }
        });

        this.eventSource.addEventListener('error', (event) => {
            const data = this.parseEventData(event.data);
            this.metrics.errorCount++;
            this.log('Stream error:', data);
            
            if (this.handlers.onError) {
                this.handlers.onError(data);
            }
        });

        this.eventSource.addEventListener('end', (event) => {
            const data = this.parseEventData(event.data);
            const duration = Date.now() - this.metrics.startTime;
            
            this.log('Stream ended:', data);
            this.log(`Total duration: ${duration}ms, chunks: ${this.metrics.chunkCount}`);
            
            // Calculate final metrics
            const metrics = {
                ...this.metrics,
                duration,
                averageChunkTime: duration / this.metrics.chunkCount,
                chunksPerSecond: (this.metrics.chunkCount / duration) * 1000
            };
            
            if (this.handlers.onMetrics) {
                this.handlers.onMetrics(metrics);
            }
            
            if (this.handlers.onEnd) {
                this.handlers.onEnd(data);
            }
            
            this.close();
        });

        // Handle connection errors
        this.eventSource.onerror = (error) => {
            this.log('SSE connection error:', error);
            this.isConnected = false;
            
            if (this.eventSource.readyState === EventSource.CLOSED) {
                this.handleConnectionClosed();
            } else {
                this.handleConnectionError(error);
            }
        };
    }

    /**
     * Monitor heartbeat for connection health
     */
    startHeartbeatMonitor() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
        }

        this.lastHeartbeat = Date.now();
        
        this.heartbeatTimer = setInterval(() => {
            const timeSinceLastHeartbeat = Date.now() - this.lastHeartbeat;
            
            if (timeSinceLastHeartbeat > this.config.heartbeatTimeout) {
                this.log('Heartbeat timeout, reconnecting...');
                this.reconnect();
            }
        }, this.config.heartbeatTimeout / 2);
    }

    /**
     * Handle connection closed
     */
    handleConnectionClosed() {
        this.log('Connection closed');
        
        if (this.reconnectAttempts < this.config.maxReconnectAttempts) {
            this.reconnect();
        } else {
            this.handleError(new Error('Max reconnection attempts reached'));
        }
    }

    /**
     * Handle connection error
     */
    handleConnectionError(error) {
        this.metrics.errorCount++;
        
        if (this.handlers.onError) {
            this.handlers.onError({
                type: 'connection_error',
                error: error.message || 'Connection error',
                recoverable: this.reconnectAttempts < this.config.maxReconnectAttempts
            });
        }
    }

    /**
     * Reconnect to SSE
     */
    async reconnect() {
        this.reconnectAttempts++;
        this.metrics.reconnectCount++;
        
        this.log(`Reconnecting... (attempt ${this.reconnectAttempts})`);
        
        await new Promise(resolve => setTimeout(resolve, this.config.reconnectInterval));
        
        if (this.lastMessage) {
            this.startStream(this.lastMessage.message, this.lastMessage.options);
        }
    }

    /**
     * Buffer events for replay or analysis
     */
    bufferEvent(type, data) {
        this.eventBuffer.push({
            type,
            data,
            timestamp: Date.now()
        });

        // Maintain buffer size
        if (this.eventBuffer.length > this.config.bufferSize) {
            this.eventBuffer.shift();
        }
    }

    /**
     * Parse event data
     */
    parseEventData(data) {
        try {
            return JSON.parse(data);
        } catch (error) {
            this.log('Failed to parse event data:', data);
            return data;
        }
    }

    /**
     * Get buffered events
     */
    getEventBuffer() {
        return [...this.eventBuffer];
    }

    /**
     * Register event handler
     */
    on(event, handler) {
        const handlerName = `on${event.charAt(0).toUpperCase() + event.slice(1)}`;
        if (handlerName in this.handlers) {
            this.handlers[handlerName] = handler;
        } else {
            throw new Error(`Unknown event: ${event}`);
        }
        return this;
    }

    /**
     * Close connection
     */
    close() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }

        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }

        this.isConnected = false;
    }

    /**
     * Get auth token (override this method)
     */
    async getAuthToken() {
        // Override this method to provide authentication
        const token = localStorage.getItem('auth_token');
        if (!token) {
            throw new Error('No auth token available');
        }
        return token;
    }

    /**
     * Handle errors
     */
    handleError(error) {
        this.log('Error:', error);
        
        if (this.handlers.onError) {
            this.handlers.onError({
                type: 'client_error',
                error: error.message,
                recoverable: false
            });
        }
    }

    /**
     * Debug logging
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[GenesisSSE]', ...args);
        }
    }
}

// EventSource polyfill for POST support
class EventSourcePolyfill {
    constructor(url, options = {}) {
        this.url = url;
        this.options = options;
        this.readyState = EventSource.CONNECTING;
        this.listeners = {};
        
        this.connect();
    }

    async connect() {
        try {
            const response = await fetch(this.url, {
                method: this.options.method || 'GET',
                headers: this.options.headers || {},
                body: this.options.body,
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            this.readyState = EventSource.OPEN;
            if (this.onopen) this.onopen();

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    this.processLine(line);
                }
            }

            this.readyState = EventSource.CLOSED;

        } catch (error) {
            this.readyState = EventSource.CLOSED;
            if (this.onerror) this.onerror(error);
        }
    }

    processLine(line) {
        if (!line.trim()) return;

        if (line.startsWith('event:')) {
            this.currentEvent = line.slice(6).trim();
        } else if (line.startsWith('data:')) {
            const data = line.slice(5).trim();
            this.dispatchEvent(this.currentEvent || 'message', data);
        }
    }

    addEventListener(event, handler) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(handler);
    }

    dispatchEvent(event, data) {
        const handlers = this.listeners[event] || [];
        const eventObject = { data };
        
        handlers.forEach(handler => {
            try {
                handler(eventObject);
            } catch (error) {
                console.error('Event handler error:', error);
            }
        });
    }

    close() {
        this.readyState = EventSource.CLOSED;
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GenesisSSEClient;
}