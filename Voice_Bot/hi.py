import random
import pyaudio
import wave
import pyttsx3
import speech_recognition as sr
import tkinter as tk
from threading import Thread

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
    print("Bot:", response)
    engine.say(response)
    engine.runAndWait()

def match_intent(transcript):
    """Check if the transcript matches any predefined intents."""
    intents = {
        "book_appointment": {
            "keywords": ["book", "appointment"],
            "response": "Sure, I can help with that. May I have your name, please?"
        }
    }

    for intent, data in intents.items():
        for keyword in data["keywords"]:
            if keyword in transcript.lower():
                return data["response"], intent
    return "I'm not sure how to respond to that.", None

def format_phone_number(phone_number):
    """Format the phone number as spoken words."""
    return " ".join(phone_number)

def record_audio(transcript_label):
    global stop_recording
    stop_recording = False
    state = "initial_greeting"
    appointment_details = {"name": "", "phone_number": "", "time_date": ""}
    
    # Initial greeting
    # Initial greeting
    greeting_message = "Hello! Thank you for calling Leo's Barber Shop. How may I assist you today?"
    speech_to_text(greeting_message)
    update_dialog(transcript_label, "", greeting_message)

    while not stop_recording:
        print("Recording... Please start speaking.")
        fs = 44100
        seconds = 5  # Default recording duration
        if state == "getting_phone_number":
            seconds = 8  # Extend the recording duration to 8 seconds for phone number

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
            if stop_recording:
                break
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
        transcript = transcribe_audio(audio_name)
        if transcript.strip().lower() == 'stop':
            stop_recording = True
            break

        if state == "initial_greeting":
            response, intent = match_intent(transcript)
            if intent == "book_appointment":
                state = "getting_name"
            else:
                state = "initial_greeting"
            speech_to_text(response)
            update_dialog(transcript_label, transcript, response)
        elif state == "getting_name":
            appointment_details["name"] = transcript
            response = "May I have your phone number, please?"
            state = "getting_phone_number"
            speech_to_text(response)
            update_dialog(transcript_label, transcript, response)
        elif state == "getting_phone_number":
            appointment_details["phone_number"] = transcript.replace(" ", "")
            response = "When would you like to book the appointment?"
            state = "getting_time_date"
            speech_to_text(response)
            update_dialog(transcript_label, transcript, response)
        elif state == "getting_time_date":
            appointment_details["time_date"] = transcript
            formatted_phone_number = format_phone_number(appointment_details["phone_number"])
            confirmation_message = (f"Thanks for sharing the information, {appointment_details['name']}. "
                                    f"Your contact number is {formatted_phone_number} and your appointment is on {appointment_details['time_date']}. "
                                    "See you soon! Have a great day ahead.")
            speech_to_text(confirmation_message)
            update_dialog(transcript_label, transcript, confirmation_message)
            stop_recording = True  # End the recording session after completing the loop

def start_recording():
    global recording_thread
    recording_thread = Thread(target=record_audio, args=(transcript_label,))
    recording_thread.start()

def stop_recording():
    global stop_recording
    stop_recording = True

def update_dialog(transcript_label, user_input, bot_response):
    dialog_text = transcript_label.cget("text") + f"\nYou: {user_input}\nBot: {bot_response}\n"
    transcript_label.config(text=dialog_text)

def create_gui():
    global transcript_label
    root = tk.Tk()
    root.title("Voice Assistant")
    root.geometry("400x400")

    start_button = tk.Button(root, text="Start Recording", command=start_recording)
    start_button.pack()

    stop_button = tk.Button(root, text="Stop Recording", command=stop_recording)
    stop_button.pack()

    transcript_label = tk.Label(root, text="", wraplength=380, justify="left")
    transcript_label.pack()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
