# maya_ai/voice/tts_engine.py

import torch
from TTS.api import TTS
import os

class TTSEngine:
    """
    A wrapper for the Coqui TTS library to handle text-to-speech conversion.
    """
    def __init__(self, output_path="voice/generated_audio"):
        self.output_path = output_path
        os.makedirs(self.output_path, exist_ok=True)

        # Determine the device to run the model on (GPU if available)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"TTS Engine is using device: {self.device}")

        # --- Model Selection ---
        # You can find more models here: https://huggingface.co/coqui
        # For a high-quality, multi-speaker model, consider: "tts_models/en/vctk/vits"
        # For a faster, single-speaker model, this is a good choice:
        self.model_name = "tts_models/en/ljspeech/tacotron2-DDC"

        self.tts = self._initialize_model()

    def _initialize_model(self):
        """Loads the TTS model into memory. This might take a moment."""
        print(f"Loading TTS model '{self.model_name}'... This may take some time and download files.")
        try:
            tts_model = TTS(self.model_name).to(self.device)
            print("TTS model loaded successfully.")
            return tts_model
        except Exception as e:
            print(f"Error initializing TTS model: {e}")
            print("Please check your internet connection and ensure you have the necessary dependencies.")
            return None

    def synthesize_speech(self, text: str, filename: str = "latest_response.wav"):
        """
        Synthesizes the given text into an audio file.

        Args:
            text (str): The text to be converted to speech.
            filename (str): The name of the output audio file.

        Returns:
            str: The full path to the generated audio file, or None if failed.
        """
        if not self.tts:
            print("TTS model is not available. Cannot synthesize speech.")
            return None

        if not text.strip():
            print("Warning: Attempted to synthesize empty text.")
            return None

        try:
            output_filepath = os.path.join(self.output_path, filename)
            print(f"Synthesizing speech to '{output_filepath}'...")

            # Most models are single-speaker, so speaker args are not needed.
            # If using a multi-speaker model, you would add speaker arguments here.
            self.tts.tts_to_file(text=text, file_path=output_filepath)

            print("Speech synthesized successfully.")
            return output_filepath
        except Exception as e:
            print(f"An error occurred during speech synthesis: {e}")
            return None

# --- Example Usage ---
if __name__ == '__main__':
    print("--- Testing TTS Engine ---")

    # This will download the model on the first run
    engine = TTSEngine()

    if engine.tts:
        sarjana_text = "Hello, darling. It is a beautiful day to contemplate the universe and our place within it."
        durjana_text = "What's up, babe? Stop staring and let's go cause some trouble. It'll be fun, I promise."

        print("\nSynthesizing Sarjana's voice...")
        sarjana_path = engine.synthesize_speech(sarjana_text, "sarjana_test.wav")
        if sarjana_path:
            print(f"Sarjana's audio saved to: {sarjana_path}")

        print("\nSynthesizing Durjana's voice...")
        durjana_path = engine.synthesize_speech(durjana_text, "durjana_test.wav")
        if durjana_path:
            print(f"Durjana's audio saved to: {durjana_path}")

    print("\n--- TTS Engine Test Complete ---")
