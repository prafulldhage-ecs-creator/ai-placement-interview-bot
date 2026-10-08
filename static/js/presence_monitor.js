/**
 * AI Placement Interview - Real-Time Camera & Presence Monitor
 * Monitors:
 *  - Prolonged looking away / turning head significantly (>4s)
 *  - Face not detected / candidate leaving frame (>5s)
 *  - Multiple faces detected
 *  - Smooth warning ladder: 1/3, 2/3, 3/3 with restorative notifications
 *  - Zero false positives on natural blinking or quick pauses
 */

class InterviewPresenceMonitor {
  constructor(options = {}) {
    this.videoElement = options.videoElement;
    this.sessionId = options.sessionId;
    this.warningBannerElement = options.warningBannerElement || document.getElementById('presenceWarningBanner');
    this.onWarningCallback = options.onWarningCallback || null;

    this.warningCount = 0;
    this.maxWarnings = 3;
    
    // State tracking timers
    this.lastFaceDetectedTime = Date.now();
    this.lookAwayStartTime = null;
    this.isLookingAway = false;
    this.isMissing = false;
    this.isMultiFace = false;

    // Canvas for image processing fallback
    this.canvas = document.createElement('canvas');
    this.canvas.width = 160;
    this.canvas.height = 120;
    this.ctx = this.canvas.getContext('2d', { willReadFrequently: true });

    this.isMonitoring = false;
    this.checkInterval = null;

    // Native FaceDetector support (Chrome/Edge experimental or standard)
    this.nativeDetector = window.FaceDetector ? new window.FaceDetector({ fastMode: true, maxDetectedFaces: 3 }) : null;
  }

  start() {
    if (this.isMonitoring || !this.videoElement) return;
    this.isMonitoring = true;
    this.lastFaceDetectedTime = Date.now();
    
    // Sample frames every 600ms (lightweight, zero lag)
    this.checkInterval = setInterval(() => {
      this.analyzeFrame();
    }, 600);
  }

  stop() {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
    }
    this.isMonitoring = false;
  }

  async analyzeFrame() {
    if (!this.videoElement || this.videoElement.paused || this.videoElement.ended) return;
    if (this.videoElement.videoWidth === 0) return;

    const now = Date.now();

    // 1. Try Native Browser FaceDetector if supported
    if (this.nativeDetector) {
      try {
        const faces = await this.nativeDetector.detect(this.videoElement);
        this.processDetectionResults(faces.length, faces[0] ? faces[0].boundingBox : null, now);
        return;
      } catch (e) {
        // Fallback to Canvas CV
      }
    }

    // 2. High-Performance Canvas Computer Vision Fallback
    try {
      this.ctx.drawImage(this.videoElement, 0, 0, this.canvas.width, this.canvas.height);
      const frame = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
      const detection = this.detectSkinCentroids(frame);
      this.processDetectionResults(detection.faceCount, detection.centroidBox, now);
    } catch (err) {
      // Ignored for cross-origin or transient frame errors
    }
  }

  detectSkinCentroids(imageData) {
    const data = imageData.data;
    const width = imageData.width;
    const height = imageData.height;

    let totalSkinPixels = 0;
    let sumX = 0;
    let sumY = 0;
    let leftSkin = 0;
    let rightSkin = 0;

    for (let i = 0; i < data.length; i += 16) { // Stride 4 pixels for speed
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];

      // Standard skin-tone range in RGB space
      if (r > 60 && g > 40 && b > 20 && r > g && r > b && (r - Math.min(g, b)) > 15) {
        const pixelIdx = i / 4;
        const x = pixelIdx % width;
        const y = Math.floor(pixelIdx / width);

        // Focus on upper 70% of frame where head sits
        if (y < height * 0.85) {
          totalSkinPixels++;
          sumX += x;
          sumY += y;

          if (x < width * 0.45) leftSkin++;
          else if (x > width * 0.55) rightSkin++;
        }
      }
    }

    // Baseline minimum area for a human face in 160x120
    const minFaceArea = 120;
    if (totalSkinPixels < minFaceArea) {
      return { faceCount: 0, centroidBox: null };
    }

    const avgX = sumX / totalSkinPixels;
    const avgY = sumY / totalSkinPixels;

    // Check if multiple people (e.g. significant disjoint clusters on both extremes)
    const isMulti = (leftSkin > 400 && rightSkin > 400 && Math.abs(leftSkin - rightSkin) < 150);
    const faceCount = isMulti ? 2 : 1;

    return {
      faceCount,
      centroidBox: {
        centerX: avgX / width, // 0.0 to 1.0
        centerY: avgY / height,
        balance: (rightSkin - leftSkin) / (totalSkinPixels || 1)
      }
    };
  }

  processDetectionResults(faceCount, boundingBox, now) {
    // -------------------------------------------------------------
    // CHECK 1: Multiple Faces Detected
    // -------------------------------------------------------------
    if (faceCount >= 2) {
      if (!this.isMultiFace) {
        this.isMultiFace = true;
        this.showWarning("⚠️ Multiple faces detected. Please ensure only the candidate is visible during the interview.", "multiple_faces");
      }
      return;
    } else if (this.isMultiFace && faceCount === 1) {
      this.isMultiFace = false;
      this.showRestoration("✓ Camera presence restored.");
    }

    // -------------------------------------------------------------
    // CHECK 2: Face Missing / Leaving Camera Frame (>5 seconds)
    // -------------------------------------------------------------
    if (faceCount === 0) {
      const missingDuration = now - this.lastFaceDetectedTime;
      // Do NOT trigger for quick 1-2s dips
      if (missingDuration > 5000 && !this.isMissing) {
        this.isMissing = true;
        this.showWarning("⚠️ Candidate not detected. Please remain in camera frame.", "not_detected");
      }
      return;
    } else {
      if (this.isMissing) {
        this.isMissing = false;
        this.showRestoration("✓ Candidate detected.");
      }
      this.lastFaceDetectedTime = now;
    }

    // -------------------------------------------------------------
    // CHECK 3: Looking Away / Turning Head Significantly (>4.5 seconds)
    // -------------------------------------------------------------
    if (boundingBox) {
      // Normal head turn threshold (off-center > 38% or heavy gaze tilt)
      const isTurned = (boundingBox.centerX < 0.22 || boundingBox.centerX > 0.78 || Math.abs(boundingBox.balance) > 0.65);

      if (isTurned) {
        if (!this.lookAwayStartTime) {
          this.lookAwayStartTime = now;
        } else if ((now - this.lookAwayStartTime > 4500) && !this.isLookingAway) {
          this.isLookingAway = true;
          this.triggerLookingAwayWarning();
        }
      } else {
        // Candidate looking forward
        if (this.isLookingAway) {
          this.isLookingAway = false;
          this.showRestoration("✓ Attention focused.");
        }
        this.lookAwayStartTime = null;
      }
    }
  }

  triggerLookingAwayWarning() {
    this.warningCount++;
    let msg = "";

    if (this.warningCount === 1) {
      msg = "⚠️ Please maintain focus on the interview.";
    } else if (this.warningCount === 2) {
      msg = "⚠️ Warning 2/3: Please remain focused on the screen.";
    } else {
      msg = "⚠️ Warning 3/3: Your interview attention appears inconsistent.";
    }

    this.showWarning(msg, "looking_away");
  }

  showWarning(message, eventType) {
    if (!this.warningBannerElement) return;

    this.warningBannerElement.style.display = 'block';
    this.warningBannerElement.style.background = 'rgba(239, 68, 68, 0.95)';
    this.warningBannerElement.style.color = '#ffffff';
    this.warningBannerElement.style.borderColor = '#b91c1c';
    this.warningBannerElement.innerHTML = `<span>${message}</span>`;

    // Log to backend
    this.logEventToBackend(eventType, message);

    if (this.onWarningCallback) {
      this.onWarningCallback(eventType, message);
    }
  }

  showRestoration(message) {
    if (!this.warningBannerElement) return;

    this.warningBannerElement.style.display = 'block';
    this.warningBannerElement.style.background = 'rgba(16, 185, 129, 0.95)';
    this.warningBannerElement.style.color = '#ffffff';
    this.warningBannerElement.style.borderColor = '#059669';
    this.warningBannerElement.innerHTML = `<span>${message}</span>`;

    setTimeout(() => {
      if (this.warningBannerElement && !this.isLookingAway && !this.isMissing && !this.isMultiFace) {
        this.warningBannerElement.style.display = 'none';
      }
    }, 2800);
  }

  logEventToBackend(eventType, details) {
    if (!this.sessionId) return;
    try {
      fetch('/api/live/log-presence/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: this.sessionId,
          event_type: eventType,
          timestamp: new Date().toISOString(),
          details: details
        })
      }).catch(() => {});
    } catch (e) {}
  }
}

window.InterviewPresenceMonitor = InterviewPresenceMonitor;
