/**
 * AI Placement Interview Practice Bot - Speech & Audio Manager
 * Handles:
 *  1. Text-to-Speech (AI Interviewer Voice) with animated waveforms & avatar pulse
 *  2. Speech-to-Text (Candidate Microphone) with live transcript streaming & visual mic meter
 */

class InterviewAudioController {
  constructor(options = {}) {
    this.avatarElement = options.avatarElement || document.getElementById('interviewerAvatar');
    this.waveElement = options.waveElement || document.getElementById('audioWaves');
    this.micBtn = options.micBtn || document.getElementById('micBtn');
    this.micStatusText = options.micStatusText || document.getElementById('micStatusText');
    this.answerInput = options.answerInput || document.getElementById('answerInput');
    
    this.isSpeaking = false;
    this.isRecording = false;
    this.recognition = null;
    this.speechSynthesis = window.speechSynthesis || null;
    this.selectedVoice = null;
    this.speechRate = 1.0;

    this.initSpeechSynthesis();
    this.initSpeechRecognition();
  }

  /* =========================================================================
     Text-To-Speech (AI Interviewer Speaks)
     ========================================================================= */
  initSpeechSynthesis() {
    if (!this.speechSynthesis) {
      console.warn("Speech Synthesis is not supported in this browser.");
      return;
    }

    const setVoice = () => {
      const voices = this.speechSynthesis.getVoices();
      // Look for natural English voices (Google US English, Microsoft, Samantha, etc.)
      this.selectedVoice = voices.find(v => 
        (v.name.includes("Google") || v.name.includes("Natural") || v.name.includes("Samantha") || v.name.includes("Zira")) &&
        v.lang.startsWith("en")
      ) || voices.find(v => v.lang.startsWith("en")) || voices[0];
    };

    if (this.speechSynthesis.onvoiceschanged !== undefined) {
      this.speechSynthesis.onvoiceschanged = setVoice;
    }
    setVoice();
  }

  speak(text, onEndCallback = null) {
    if (!this.speechSynthesis) return;

    this.stopSpeaking();

    // Clean text of markdown stars/backticks for clean speech
    const cleanText = text.replace(/[*_`#]/g, '').trim();
    if (!cleanText) return;

    const utterance = new SpeechSynthesisUtterance(cleanText);
    if (this.selectedVoice) {
      utterance.voice = this.selectedVoice;
    }
    utterance.rate = this.speechRate;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      this.isSpeaking = true;
      if (this.avatarElement) this.avatarElement.classList.add('speaking');
      if (this.waveElement) this.waveElement.classList.add('active');
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      if (this.avatarElement) this.avatarElement.classList.remove('speaking');
      if (this.waveElement) this.waveElement.classList.remove('active');
      if (onEndCallback) onEndCallback();
    };

    utterance.onerror = (e) => {
      console.warn("Speech synthesis error:", e);
      this.isSpeaking = false;
      if (this.avatarElement) this.avatarElement.classList.remove('speaking');
      if (this.waveElement) this.waveElement.classList.remove('active');
    };

    this.speechSynthesis.speak(utterance);
  }

  stopSpeaking() {
    if (this.speechSynthesis && this.speechSynthesis.speaking) {
      this.speechSynthesis.cancel();
      this.isSpeaking = false;
      if (this.avatarElement) this.avatarElement.classList.remove('speaking');
      if (this.waveElement) this.waveElement.classList.remove('active');
    }
  }

  /* =========================================================================
     Speech-To-Text (Candidate Speaks into Microphone)
     ========================================================================= */
  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn("Web Speech API is not supported in this browser.");
      if (this.micStatusText) {
        this.micStatusText.innerText = "Voice input unavailable (Browser does not support SpeechRecognition). Please type your answer.";
      }
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';

    let currentSessionBaseText = '';

    this.recognition.onstart = () => {
      this.isRecording = true;
      if (this.micBtn) this.micBtn.classList.add('recording');
      if (this.micStatusText) {
        this.micStatusText.innerHTML = '<span style="color:#ef4444; font-weight:700;">● Recording...</span> Speak clearly into your microphone.';
      }
      currentSessionBaseText = this.answerInput ? this.answerInput.value.trim() : '';
      if (currentSessionBaseText.length > 0) {
        currentSessionBaseText += ' ';
      }
      this.playChime(600, 0.1);
    };

    this.recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      if (this.answerInput) {
        this.answerInput.value = currentSessionBaseText + finalTranscript + interimTranscript;
        // Trigger input event to update word counter
        this.answerInput.dispatchEvent(new Event('input'));
      }

      if (finalTranscript) {
        currentSessionBaseText += finalTranscript + ' ';
      }
    };

    this.recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      if (event.error === 'not-allowed') {
        if (this.micStatusText) {
          this.micStatusText.innerHTML = '<span style="color:#ef4444;">Microphone access blocked. Please allow mic permission in your browser or type your answer.</span>';
        }
      }
      this.stopRecording();
    };

    this.recognition.onend = () => {
      this.stopRecording();
    };
  }

  toggleRecording() {
    if (!this.recognition) {
      alert("Voice speech recognition is not supported in this browser. Please type your response directly!");
      return;
    }

    if (this.isRecording) {
      this.stopRecording();
    } else {
      // Pause interviewer voice if speaking
      this.stopSpeaking();
      try {
        this.recognition.start();
      } catch (err) {
        console.warn("Recognition already started or error:", err);
      }
    }
  }

  stopRecording() {
    if (this.recognition && this.isRecording) {
      try {
        this.recognition.stop();
      } catch (e) {}
    }
    this.isRecording = false;
    if (this.micBtn) this.micBtn.classList.remove('recording');
    if (this.micStatusText) {
      this.micStatusText.innerText = "Click microphone or press Space to dictate. You can also edit by typing.";
    }
    this.playChime(400, 0.1);
  }

  /* Audio Chime using Web Audio API */
  playChime(frequency, duration) {
    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(frequency, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {
      // AudioContext might be muted or blocked by autoplay policy
    }
  }
}

window.InterviewAudioController = InterviewAudioController;
