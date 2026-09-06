import { WebSocketTransport } from '@pipecat-ai/websocket-transport';
import {
  AggregationType,
  type BotOutputData,
  type Participant,
  PipecatClient,
  type PipecatClientOptions,
  type TranscriptData,
  type TransportState,
} from '@pipecat-ai/client-js';

class WebSocketApp {
  private connectBtn!: HTMLButtonElement;
  private disconnectBtn!: HTMLButtonElement;
  private debugLog!: HTMLElement;
  private statusSpan!: HTMLElement;
  private pcClient!: PipecatClient;
  private wsUrl: string;

  constructor() {
    this.wsUrl = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8765';
    this.setupDOMElements();
    this.setupDOMEventListeners();
    this.initializePipecatClient();
  }

  private initializePipecatClient(): void {
    const opts: PipecatClientOptions = {
      transport: new WebSocketTransport({
        wsUrl: this.wsUrl
      }),
      enableMic: true,
      enableCam: false,
      callbacks: {
        onTransportStateChanged: (state: TransportState) => {
          this.log(`Transport state: ${state}`);
        },
        onConnected: () => {
          this.onConnectedHandler();
        },
        onDisconnected: () => {
          this.onDisconnectedHandler();
        },
        onUserStartedSpeaking: () => {
          this.log('User started speaking.');
        },
        onUserStoppedSpeaking: () => {
          this.log('User stopped speaking.');
        },
        onBotStartedSpeaking: () => {
          this.log('Bot started speaking.');
        },
        onBotStoppedSpeaking: () => {
          this.log('Bot stopped speaking.');
        },
        onUserTranscript: (transcript: TranscriptData) => {
          if (transcript.final) {
            this.log(`User transcript: ${transcript.text}`);
          }
        },
        onBotOutput: (data: BotOutputData) => {
          if (data.aggregated_by === AggregationType.SENTENCE) {
            this.log(`Bot output: ${data.text}`);
          }
        },
        onTrackStarted: (track: MediaStreamTrack, participant?: Participant) => {
          if (!participant?.local && track.kind === 'audio') {
            this.onBotTrackStarted(track);
          }
        },
        onServerMessage: (msg: unknown) => {
          this.log(`Server message: ${JSON.stringify(msg)}`);
        },
        onError: (error: unknown) => {
          this.log(`Client Error: ${JSON.stringify(error)}`);
        }
      },
    };
    
    this.pcClient = new PipecatClient(opts);
  }

  private setupDOMElements(): void {
    this.connectBtn = document.getElementById('connect-btn') as HTMLButtonElement;
    this.disconnectBtn = document.getElementById('disconnect-btn') as HTMLButtonElement;
    this.debugLog = document.getElementById('debug-log') as HTMLElement;
    this.statusSpan = document.getElementById('connection-status') as HTMLElement;
  }

  private setupDOMEventListeners(): void {
    this.connectBtn.addEventListener('click', () => this.start());
    this.disconnectBtn.addEventListener('click', () => this.stop());
  }

  private log(message: string): void {
    if (!this.debugLog) return;
    const entry = document.createElement('div');
    entry.textContent = `${new Date().toISOString()} - ${message}`;
    
    if (message.startsWith('User transcript:')) {
      entry.style.color = '#2196F3';
    } else if (message.startsWith('Bot output:')) {
      entry.style.color = '#4CAF50';
    } else if (message.includes('Error')) {
      entry.style.color = '#F44336';
    }
    
    this.debugLog.appendChild(entry);
    this.debugLog.scrollTop = this.debugLog.scrollHeight;
  }

  private updateStatus(status: string): void {
    if (this.statusSpan) {
      this.statusSpan.textContent = status;
    }
    this.log(`Status: ${status}`);
  }

  private onConnectedHandler() {
    this.updateStatus('Connected');
    this.connectBtn.disabled = true;
    this.disconnectBtn.disabled = false;
  }

  private onDisconnectedHandler() {
    this.updateStatus('Disconnected');
    this.connectBtn.disabled = false;
    this.disconnectBtn.disabled = true;
  }

  private onBotTrackStarted(track: MediaStreamTrack) {
    this.log('Attaching remote audio track to DOM.');
    const audioEl = document.createElement('audio');
    audioEl.autoplay = true;
    audioEl.srcObject = new MediaStream([track]);
    document.body.appendChild(audioEl);
  }

  private async start(): Promise<void> {
    this.debugLog.innerText = '';
    this.connectBtn.disabled = true;
    
    try {
      this.updateStatus('Connecting to WebSocket server...');
      await this.pcClient.connect();
    } catch (e) {
      this.log(`Failed to connect: ${e}`);
      this.stop();
    }
  }

  private stop(): void {
    this.pcClient.disconnect();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new WebSocketApp();
});