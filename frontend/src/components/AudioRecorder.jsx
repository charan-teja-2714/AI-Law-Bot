import React, { useState, useRef, useEffect } from 'react';

function AudioRecorder({ onRecordingComplete, disabled }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000
        }
      });

      streamRef.current = stream;
      audioChunksRef.current = [];

      // Try WAV format first, fallback to webm
      let mimeType = 'audio/webm';
      if (MediaRecorder.isTypeSupported('audio/wav')) {
        mimeType = 'audio/wav';
      } else if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
      }

      const mediaRecorder = new MediaRecorder(stream, { 
        mimeType,
        audioBitsPerSecond: 128000
      });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          console.log('[RECORDER] Data chunk received:', event.data.size, 'bytes');
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        
        console.log('[RECORDER] Recording stopped. Blob size:', audioBlob.size, 'bytes');
        console.log('[RECORDER] Chunks collected:', audioChunksRef.current.length);
        console.log('[RECORDER] MimeType:', mimeType);
        
        if (audioBlob.size > 100) { // At least 100 bytes
          const extension = mimeType.includes('wav') ? 'wav' : 'webm';
          const audioFile = new File(
            [audioBlob],
            `recording-${Date.now()}.${extension}`,
            { type: mimeType }
          );

          onRecordingComplete(audioFile);
        } else {
          alert('Recording is too short or empty. Please try again and speak clearly.');
        }

        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }

        setRecordingTime(0);
      };

      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);
      
      console.log('[RECORDER] Recording started, mimeType:', mimeType);

      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (recordingTime < 2) {
        alert('Please record for at least 2 seconds.');
        return;
      }
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume();
        timerRef.current = setInterval(() => {
          setRecordingTime(prev => prev + 1);
        }, 1000);
      } else {
        mediaRecorderRef.current.pause();
        if (timerRef.current) {
          clearInterval(timerRef.current);
        }
      }
      setIsPaused(!isPaused);
    }
  };

  const cancelRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.onstop = null;
      mediaRecorderRef.current.stop();

      audioChunksRef.current = [];
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }

      setIsRecording(false);
      setIsPaused(false);
      setRecordingTime(0);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (isRecording) {
    return (
      <div className="audio-recorder recording-active">
        <div className="recording-indicator">
          <div className="recording-dot"></div>
          <span className="recording-time">{formatTime(recordingTime)}</span>
        </div>

        <div className="recording-controls">
          <button
            type="button"
            className="recording-btn pause-btn"
            onClick={pauseRecording}
            title={isPaused ? "Resume" : "Pause"}
          >
            {isPaused ? '▶' : '⏸'}
          </button>

          <button
            type="button"
            className="recording-btn stop-btn"
            onClick={stopRecording}
            title="Stop and transcribe"
          >
            ⏹
          </button>

          <button
            type="button"
            className="recording-btn cancel-btn"
            onClick={cancelRecording}
            title="Cancel recording"
          >
            ✕
          </button>
        </div>
      </div>
    );
  }

  return (
    <button
      type="button"
      className="mic-btn"
      onClick={startRecording}
      disabled={disabled}
      title="Record audio"
    >
      🎤
    </button>
  );
}

export default AudioRecorder;
