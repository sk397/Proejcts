import random
import pyaudio
import wave
import pyttsx3
import speech_recognition as sr

# Adjectives and nouns to generate random names for audio files
adjectives = ["beautiful", "sad", "mystical", "serene", "whispering", "gentle", "melancholic"]
nouns = ["sea", "love", "dreams", "song", "rain", "sunrise", "silence", "echo"]

# Initialize pyttsx3 for text-to-speech output
engine = pyttsx3.init()
engine.setProperty('rate', 130)

def generate_random_name():
    """Generate a random name for the audio file using adjectives and nouns."""
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    return f"{adjective} {noun}"

def new_record_audio():
    """Record audio from the microphone and save it as a PCM WAV file."""
    print("Recording... Press 's' to stop.")
    fs = 44100
    seconds = 3
    audio_name = generate_random_name() + ".wav"

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=fs,
                    input=True,
                    frames_per_buffer=1024)

    frames = []
    for i in range(0, int(fs / 1024 * seconds)):
        data = stream.read(1024)
        frames.append(data)

    # Stop stream
    stream.stop_stream()
    stream.close()

    # Terminate PyAudio
    p.terminate()

    # Save the recorded audio as a WAV file
    with wave.open(audio_name, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))

    print("Recording stopped.")
    return audio_name

def transcribe_audio(audio_path):
    """Transcribe the recorded audio to text using Google Speech Recognition."""
    print(f"Transcribing audio from {audio_path}...")
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)  # Read the audio file
    try:
        transcript = recognizer.recognize_google(audio_data)  # Transcribe audio
        print("Transcript:", transcript)
        return transcript
    except sr.UnknownValueError:
        print("Speech recognition could not understand audio")
        return "No speech detected."
    except sr.RequestError as e:
        print(f"Error: {e}")
        return "Error occurred during transcription."

def speech_to_text(response):
    """Convert text response to speech."""
    engine.say(response)
    engine.runAndWait()

def match_intent(transcript):
    """Check if the transcript matches any predefined intents."""
    intents = {
        "greeting": {
            "keywords": ["hello", "hi", "hey"],
            "response": "Hello! How can I assist you today?"
        },
        "Working": {
            "keywords": ["Hours", "hours", "Working"],
            "response": "The Barber shop is open frpm 9AM-6PM Monday to Friday"
        },
        "thanks": {
            "keywords": ["thanks", "thank you"],
            "response": "You're welcome! Happy to help."
        },
        # Add more intents as needed
    }
    print("Transcript:", transcript)
    for intent, data in intents.items():
        print(f"Checking intent: {intent}")
        for keyword in data["keywords"]:
            print(f"Checking keyword: {keyword}")
            if keyword in transcript:
                print("Match found!")
                return data["response"]
    return "I'm not sure how to respond to that."

def main():
    """Main function to handle the voice assistant logic."""
    print("Voice assistant activated. Speak your commands.")
    while True:
        print("Listening... (Say 'stop' to terminate)")
        recorded_audio_path = new_record_audio()
        print("Transcribing audio...")
        transcript = transcribe_audio(recorded_audio_path)
        print(f"Transcript: {transcript}")

        # Check for predefined intents
        response = match_intent(transcript)

        # Print and convert the response to speech
        print(f"Assistant: {response}")
        speech_to_text(response)

        # Terminate if 'stop' is detected
        if "stop" in transcript.lower():
            print("Voice assistant terminated.")
            break

if __name__ == "__main__":
    main()
