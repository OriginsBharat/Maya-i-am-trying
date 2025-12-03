# maya_ai/content/reactor.py

from core.brain import MayaPersonaSystem
from voice.tts_engine import TTSEngine

class ContentReactor:
    """
    Generates Maya's reaction to a given piece of content.
    It uses the brain to generate commentary and the voice engine to synthesize it.
    """
    def __init__(self, brain: MayaPersonaSystem, voice: TTSEngine):
        self.brain = brain
        self.voice = voice

    def generate_reaction(self, content_data: dict):
        """
        Creates a full reaction (text and audio) to a piece of content.

        Args:
            content_data (dict): A dictionary containing details about the content
                                 (e.g., from ContentScanner).

        Returns:
            tuple: A tuple containing (reaction_text, audio_filepath), or (None, None) if failed.
        """
        if not content_data:
            print("Error: No content data provided to generate reaction.")
            return None, None

        print(f"Generating reaction for: \"{content_data['title']}\"")

        # --- Construct a specialized prompt for generating a reaction ---
        reaction_prompt = (
            f"You are creating a short, viral-style video for YouTube Shorts and TikTok. "
            f"Your task is to react to the following content:\n"
            f"- Source: {content_data['source']}\n"
            f"- Title: {content_data['title']}\n"
            f"Your reaction should be engaging, concise, and perfectly match your current persona. "
            f"Keep it under 60 seconds of speaking time. Start the reaction directly, without any preamble like 'Here is my reaction...'"
        )

        # Generate the text part of the reaction
        reaction_text = self.brain.generate_response(reaction_prompt)
        print(f"Generated commentary: \"{reaction_text[:100]}...\"")

        if not reaction_text or "I'm sorry" in reaction_text:
            print("Failed to generate valid commentary.")
            return None, None

        # Synthesize the audio part of the reaction
        # Create a unique filename based on the content title
        safe_filename = "".join(x for x in content_data['title'] if x.isalnum())[:20]
        audio_filename = f"reaction_{safe_filename}.wav"

        audio_filepath = self.voice.synthesize_speech(reaction_text, filename=audio_filename)

        if not audio_filepath:
            print("Failed to synthesize audio for the reaction.")
            return reaction_text, None

        return reaction_text, audio_filepath

# --- Example Usage ---
if __name__ == '__main__':
    from dotenv import load_dotenv
    from content.scanner import ContentScanner
    load_dotenv()

    print("--- Testing Content Reactor ---")

    # Initialize all necessary systems
    brain = MayaPersonaSystem(model="mistral:latest")
    voice = TTSEngine()
    scanner = ContentScanner()

    if brain.client and voice.tts and scanner.reddit:
        # 1. Find some content
        print("\nStep 1: Finding content...")
        memes = scanner.get_reddit_memes(limit=1)

        if memes:
            # 2. React to the content
            print("\nStep 2: Generating reaction...")
            reactor = ContentReactor(brain, voice)
            # Switch to Durjana for a spicier reaction
            brain.switch_persona("durjana")
            text, audio = reactor.generate_reaction(memes[0])

            if text and audio:
                print("\n--- Reaction Generated Successfully! ---")
                print(f"  Text: {text}")
                print(f"  Audio saved at: {audio}")
            else:
                print("\n--- Failed to generate a complete reaction. ---")
        else:
            print("\nCould not find any content to react to.")

    print("\n--- Content Reactor Test Complete ---")
