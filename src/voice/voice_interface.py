#!/usr/bin/env python3
"""
NOVA Voice Interface - Speech recognition and synthesis
"""

import asyncio
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import subprocess
import wave
import json

# Optional imports for advanced features
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


class VoiceInterface:
    """
    Voice interface for NOVA with fallback to macOS native tools
    """
    
    def __init__(self):
        self.logger = logging.getLogger('NOVA.Voice')
        self.recognizer = None
        self.microphone = None
        self.tts_engine = None
        self.is_listening = False
        self.voice_enabled = False
        
        # Voice settings
        self.voice_settings = {
            'rate': 200,  # Words per minute
            'volume': 0.9,
            'voice': 'com.apple.speech.synthesis.voice.samantha'  # macOS voice
        }
        
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize voice components with fallbacks"""
        # Initialize speech recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.logger.info("Speech recognition initialized")
        else:
            self.logger.warning("Speech recognition not available, using macOS dictation")
            
        # Initialize text-to-speech
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self._configure_tts()
                self.logger.info("Text-to-speech initialized")
            except:
                self.logger.warning("pyttsx3 failed, using macOS 'say' command")
        else:
            self.logger.info("Using macOS 'say' command for text-to-speech")
            
    def _configure_tts(self):
        """Configure TTS engine settings"""
        if self.tts_engine:
            # Set properties
            self.tts_engine.setProperty('rate', self.voice_settings['rate'])
            self.tts_engine.setProperty('volume', self.voice_settings['volume'])
            
            # Try to set voice
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if self.voice_settings['voice'] in voice.id:
                    self.tts_engine.setProperty('voice', voice.id)
                    break
                    
    async def listen(self, timeout: float = 5.0) -> Optional[str]:
        """
        Listen for voice input and return transcribed text
        """
        if SPEECH_RECOGNITION_AVAILABLE and self.recognizer and self.microphone:
            return await self._listen_with_speech_recognition(timeout)
        else:
            return await self._listen_with_macos_dictation()
            
    async def _listen_with_speech_recognition(self, timeout: float) -> Optional[str]:
        """Use speech_recognition library"""
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                self.logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout)
                
            # Recognize speech using Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio)
                self.logger.info(f"Recognized: {text}")
                return text
            except sr.UnknownValueError:
                self.logger.warning("Could not understand audio")
                return None
            except sr.RequestError as e:
                self.logger.error(f"Speech recognition error: {e}")
                # Fallback to macOS
                return await self._listen_with_macos_dictation()
                
        except sr.WaitTimeoutError:
            self.logger.info("Listening timed out")
            return None
        except Exception as e:
            self.logger.error(f"Listening error: {e}")
            return None
            
    async def _listen_with_macos_dictation(self) -> Optional[str]:
        """Use macOS native dictation via AppleScript"""
        try:
            # Create AppleScript for dictation
            script = '''
            tell application "System Events"
                -- Start dictation
                key code 63 using {fn down} -- Fn Fn to start dictation
                delay 0.5
                
                -- Wait for user to speak (max 10 seconds)
                set startTime to current date
                repeat
                    delay 0.1
                    if (current date) - startTime > 10 then
                        exit repeat
                    end if
                end repeat
                
                -- Stop dictation
                key code 63 using {fn down}
                delay 0.5
                
                -- Get the text (this is tricky, might need clipboard)
                keystroke "a" using command down
                delay 0.1
                keystroke "c" using command down
                delay 0.1
                
                return (the clipboard)
            end tell
            '''
            
            # Note: This is a simplified approach. In practice, you'd need
            # a more sophisticated method to capture dictation text
            self.logger.warning("macOS dictation integration is limited")
            return None
            
        except Exception as e:
            self.logger.error(f"macOS dictation error: {e}")
            return None
            
    async def speak(self, text: str, wait: bool = True):
        """
        Convert text to speech
        """
        if PYTTSX3_AVAILABLE and self.tts_engine:
            await self._speak_with_pyttsx3(text, wait)
        else:
            await self._speak_with_macos_say(text, wait)
            
    async def _speak_with_pyttsx3(self, text: str, wait: bool):
        """Use pyttsx3 for text-to-speech"""
        try:
            self.tts_engine.say(text)
            
            if wait:
                self.tts_engine.runAndWait()
            else:
                # Run in background
                asyncio.create_task(
                    asyncio.get_event_loop().run_in_executor(
                        None, self.tts_engine.runAndWait
                    )
                )
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            # Fallback to macOS say
            await self._speak_with_macos_say(text, wait)
            
    async def _speak_with_macos_say(self, text: str, wait: bool):
        """Use macOS 'say' command"""
        try:
            cmd = [
                'say',
                '-v', self.voice_settings['voice'].split('.')[-1],  # Extract voice name
                '-r', str(self.voice_settings['rate']),
                text
            ]
            
            if wait:
                subprocess.run(cmd, check=True)
            else:
                subprocess.Popen(cmd)
                
        except Exception as e:
            self.logger.error(f"macOS say error: {e}")
            
    async def record_audio(self, duration: float = 5.0, 
                         filepath: Optional[str] = None) -> Optional[str]:
        """
        Record audio to file
        """
        if not filepath:
            filepath = tempfile.mktemp(suffix='.wav')
            
        if SPEECH_RECOGNITION_AVAILABLE and self.microphone:
            return await self._record_with_speech_recognition(duration, filepath)
        else:
            return await self._record_with_macos(duration, filepath)
            
    async def _record_with_speech_recognition(self, duration: float, 
                                            filepath: str) -> Optional[str]:
        """Record using speech_recognition"""
        try:
            with self.microphone as source:
                self.logger.info(f"Recording for {duration} seconds...")
                audio = self.recognizer.record(source, duration=duration)
                
            # Save to file
            with open(filepath, "wb") as f:
                f.write(audio.get_wav_data())
                
            self.logger.info(f"Audio saved to {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Recording error: {e}")
            return None
            
    async def _record_with_macos(self, duration: float, 
                               filepath: str) -> Optional[str]:
        """Record using macOS 'sox' or 'afrecord'"""
        try:
            # Try using afrecord (built into macOS)
            cmd = [
                'afrecord',
                '-f', 'WAVE',
                '-d', str(duration),
                filepath
            ]
            
            subprocess.run(cmd, check=True)
            self.logger.info(f"Audio recorded to {filepath}")
            return filepath
            
        except FileNotFoundError:
            self.logger.error("afrecord not found, install with: brew install sox")
            return None
        except Exception as e:
            self.logger.error(f"macOS recording error: {e}")
            return None
            
    def toggle_voice(self) -> bool:
        """Toggle voice interface on/off"""
        self.voice_enabled = not self.voice_enabled
        
        if self.voice_enabled:
            asyncio.create_task(self.speak("Voice interface activated", wait=False))
        else:
            asyncio.create_task(self.speak("Voice interface deactivated", wait=False))
            
        return self.voice_enabled
        
    async def process_voice_command(self, callback: Callable[[str], Any]):
        """
        Continuously listen for voice commands and process them
        """
        self.is_listening = True
        
        while self.is_listening and self.voice_enabled:
            try:
                # Listen for command
                text = await self.listen(timeout=10.0)
                
                if text:
                    # Check for wake word (optional)
                    wake_words = ['nova', 'hey nova', 'okay nova']
                    
                    text_lower = text.lower()
                    is_wake_word = any(wake in text_lower for wake in wake_words)
                    
                    if is_wake_word or not wake_words:  # Process if wake word or no wake word required
                        # Remove wake word from command
                        for wake in wake_words:
                            if text_lower.startswith(wake):
                                text = text[len(wake):].strip()
                                break
                                
                        # Process command
                        if text:
                            await callback(text)
                            
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Voice command processing error: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying
                
        self.is_listening = False
        
    def stop_listening(self):
        """Stop listening for voice commands"""
        self.is_listening = False
        
    async def transcribe_audio_file(self, filepath: str) -> Optional[str]:
        """Transcribe an audio file to text"""
        if SPEECH_RECOGNITION_AVAILABLE and self.recognizer:
            try:
                with sr.AudioFile(filepath) as source:
                    audio = self.recognizer.record(source)
                    
                text = self.recognizer.recognize_google(audio)
                return text
                
            except Exception as e:
                self.logger.error(f"Transcription error: {e}")
                return None
        else:
            # Could use macOS speech recognition API here
            self.logger.warning("Audio file transcription not available without speech_recognition")
            return None
            
    def list_available_voices(self) -> list:
        """List available TTS voices"""
        voices = []
        
        if PYTTSX3_AVAILABLE and self.tts_engine:
            for voice in self.tts_engine.getProperty('voices'):
                voices.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages,
                    'gender': voice.gender
                })
        else:
            # Get macOS voices
            try:
                result = subprocess.run(['say', '-v', '?'], 
                                      capture_output=True, text=True)
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 2:
                        voices.append({
                            'id': parts[0],
                            'name': parts[0],
                            'languages': [parts[1]] if len(parts) > 1 else [],
                            'gender': 'unknown'
                        })
            except:
                pass
                
        return voices
        
    def set_voice(self, voice_id: str):
        """Set the TTS voice"""
        self.voice_settings['voice'] = voice_id
        
        if PYTTSX3_AVAILABLE and self.tts_engine:
            self.tts_engine.setProperty('voice', voice_id)
            
    def set_speech_rate(self, rate: int):
        """Set speech rate (words per minute)"""
        self.voice_settings['rate'] = rate
        
        if PYTTSX3_AVAILABLE and self.tts_engine:
            self.tts_engine.setProperty('rate', rate)
            
    def set_volume(self, volume: float):
        """Set speech volume (0.0 to 1.0)"""
        self.voice_settings['volume'] = max(0.0, min(1.0, volume))
        
        if PYTTSX3_AVAILABLE and self.tts_engine:
            self.tts_engine.setProperty('volume', self.voice_settings['volume'])


# Example usage
async def demo():
    """Demo the voice interface"""
    voice = VoiceInterface()
    
    # List available voices
    print("Available voices:")
    for v in voice.list_available_voices()[:5]:
        print(f"  - {v['name']} ({v.get('languages', ['unknown'])[0]})")
        
    # Test TTS
    await voice.speak("Hello, I'm NOVA, your AI co-founder.")
    
    # Test listening
    print("\nSay something...")
    text = await voice.listen()
    if text:
        print(f"You said: {text}")
        await voice.speak(f"You said: {text}")
    else:
        print("No speech detected")
        
    # Test recording
    print("\nRecording 3 seconds of audio...")
    audio_file = await voice.record_audio(duration=3.0)
    if audio_file:
        print(f"Audio saved to: {audio_file}")
        
        # Try to transcribe it
        text = await voice.transcribe_audio_file(audio_file)
        if text:
            print(f"Transcription: {text}")


if __name__ == "__main__":
    asyncio.run(demo())