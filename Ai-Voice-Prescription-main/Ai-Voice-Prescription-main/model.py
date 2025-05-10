import re
import speech_recognition as sr
from fuzzywuzzy import process
import pandas as pd

# Predefined list of common medicine names
KNOWN_MEDICINES = [
    "dolo 650", "paracetamol", "ibuprofen", "aspirin", "acetaminophen", 
    "Dolo 650"
]

# Load the dataset
dataset = pd.read_csv("D:\AI Prescription\medicine_dataset.csv")

# Fuzzy matching function to identify medicine names
def fuzzy_match_medicine(speech_text):
    best_match, score = process.extractOne(speech_text, KNOWN_MEDICINES)
    return best_match if score > 70 else "Unknown Medicine"

# Function to extract prescription details from voice input using enhanced pattern matching
def extract_prescription_details(speech_text):
    # Enhanced patterns for extracting prescription details in any order
    dosage = re.search(r'\b\d+ ?(mg|milligrams|ml|tablets|pills|units)\b', speech_text, re.IGNORECASE)
    frequency = re.search(r'\b(once|twice|thrice|one|two|three|every ?\d+ ?hours?) ?(a|per)? ?(day|week|hours?)?\b', speech_text, re.IGNORECASE)
    duration = re.search(r'\b\d+ ?(days?|weeks?|months?)\b', speech_text, re.IGNORECASE)
    
    # Capture all occurrences of morning, afternoon, night, etc.
    timing_matches = re.findall(r'\b(morning|afternoon|evening|night)\b', speech_text, re.IGNORECASE)
    timing = ', '.join(timing_matches) if timing_matches else 'Not mentioned'
    
    food_instruction = re.search(r'\b(before|after|with) ?(food|meal|meals)?\b', speech_text, re.IGNORECASE)

    # Return the extracted details, or 'Not mentioned' if not found
    return {
        'dosage': dosage.group() if dosage else 'Not mentioned',
        'frequency': frequency.group() if frequency else 'Not mentioned',
        'duration': duration.group() if duration else 'Not mentioned',
        'timing': timing,
        'food_instruction': food_instruction.group() if food_instruction else 'Not mentioned',
    }

# Function to recognize speech with 15 seconds of listening time
def recognize_speech_from_mic(prompt_message, timeout=15, phrase_time_limit=15):
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print(f"{prompt_message}")
        
        # Adjust for background noise dynamically
        recognizer.adjust_for_ambient_noise(source, duration=2)
        
        try:
            print("Listening...")
            # Listen with a maximum of 15 seconds for each phrase
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            print("Recognizing speech...")
            
            # Use Google Web Speech API for recognition
            user_speech = recognizer.recognize_google(audio)
            print(f"You said: {user_speech}")
            return user_speech
        
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start.")
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from the speech recognition service; {e}")
        
        return None

# Function to format the prescription output
def format_prescription(medicine_name, dosage, frequency, duration, timing, food_instruction):
    prescription = f"""
    =======================
    DOCTOR'S PRESCRIPTION
    =======================
    Medicine: {medicine_name}
    Dosage: {dosage}
    Frequency: {frequency}
    Duration: {duration}
    Timing: {timing}
    Food Instruction: {food_instruction}
    
    Notes: Please take the medicine as prescribed.
    =======================
    """
    return prescription

# Main function to handle full voice-based prescription input
if __name__ == "__main__":
    # Step 1: Ask for the medicine name and details from user's voice input
    print("Please speak the medicine name and prescription details.")
    
    # Step 2: Recognize the medicine name and prescription details from speech input
    # Set a 15-second listening time
    prescription_speech = recognize_speech_from_mic(
        "Please say the medicine name, dosage, frequency, timing, and food instructions.",
        timeout=30,  # Wait for up to 15 seconds for user input
        phrase_time_limit=30  # Allow up to 15 seconds of speaking
    )
    
    if prescription_speech:
        # Step 3: Extract the medicine name from the recognized speech using fuzzy matching
        medicine_name = fuzzy_match_medicine(prescription_speech)
        
        # Step 4: Extract the details from the recognized speech input
        prescription_details = extract_prescription_details(prescription_speech)
        
        # Step 5: Format and generate the prescription
        prescription = format_prescription(
            medicine_name,
            dosage=prescription_details['dosage'], 
            frequency=prescription_details['frequency'], 
            duration=prescription_details['duration'], 
            timing=prescription_details['timing'], 
            food_instruction=prescription_details['food_instruction']
        )

        # Output the formatted prescription
        print(prescription)
