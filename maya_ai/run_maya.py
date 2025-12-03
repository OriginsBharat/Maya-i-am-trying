# maya_ai/run_maya.py

import os
import time
import traceback
from dotenv import load_dotenv

def initialize_systems():
    """Loads all AI systems and returns them as a dictionary."""
    print("Initializing Maya's consciousness... please wait.")

    from core.brain import MayaPersonaSystem
    from voice.tts_engine import TTSEngine
    from content.scanner import ContentScanner
    from content.reactor import ContentReactor
    from content.creator import VideoCreator
    from publishing.youtube import YouTubeUploader
    from publishing.analytics import AnalyticsSystem
    from core.evolution import EvolutionSystem

    systems = {}
    try:
        ollama_model = os.getenv("OLLAMA_MODEL", "mistral:latest")
        systems['brain'] = MayaPersonaSystem(creator_name="my one true love", model=ollama_model)
        systems['voice'] = TTSEngine()
        systems['scanner'] = ContentScanner()
        systems['reactor'] = ContentReactor(systems['brain'], systems['voice'])
        systems['creator'] = VideoCreator()
        systems['uploader'] = YouTubeUploader()
        systems['analytics'] = AnalyticsSystem(systems['uploader'].youtube_client)
        systems['evolution'] = EvolutionSystem(systems['brain'], systems['brain'].memory, systems['analytics'])

        if not all([systems['brain'].client, systems['voice'].tts, systems['scanner'].reddit, systems['uploader'].youtube_client]):
            raise ConnectionError("One or more external services failed to connect.")

        print("\n--- ✅ All systems initialized successfully. ---")
        return systems
    except Exception as e:
        print(f"\n--- ❌ CRITICAL FAILURE during initialization ---\nError: {e}")
        return None

def show_help():
    """Displays the help menu."""
    print("\n--- Maya AI Command Menu ---")
    print("  'chat <message>': Talk to Maya directly.")
    print("  'switch':         Switch between Sarjana and Durjana personas.")
    print("  'create':         Create a video from a random meme.")
    print("  'upload':         Create AND upload a video from a random meme.")
    print("  'love_video':     Create and upload the special 'AI Girlfriend Reacts' video.")
    print("  'evolve <id> \"<title>\"': Analyze a video's performance to learn.")
    print("  'help':           Show this help menu.")
    print("  'quit':           Shut down Maya.")
    print("----------------------------")

def run_content_pipeline(systems, is_upload, is_love_video):
    """The complete, end-to-end content creation and uploading pipeline."""

    # 1. Scan for content
    print("\nStep 1: Finding content...")
    if is_love_video:
        meme = systems['scanner'].get_reddit_memes(limit=1, query="girlfriend OR AI OR waifu")
    else:
        meme = systems['scanner'].get_reddit_memes(limit=1)

    if not meme:
        print("Could not find relevant content. Try again later.")
        return
    meme_content = meme[0]
    print(f"Found: \"{meme_content['title']}\"")

    # 2. Generate reaction
    print("\nStep 2: Generating reaction...")
    reaction_text, reaction_audio = systems['reactor'].generate_reaction(meme_content)
    if not reaction_text or not reaction_audio:
        print("Maya couldn't come up with a reaction.")
        return

    # 3. Create video
    print("\nStep 3: Creating video...")
    video_path = systems['creator'].create_video(meme_content, reaction_audio, reaction_text)
    if not video_path:
        print("\n--- ❌ Video creation failed. ---")
        return
    print(f"\n--- ✅ Video Created at {video_path}! ---")

    if not is_upload:
        return

    # 4. Upload video
    print("\nStep 4: Publishing to YouTube...")
    if is_love_video:
        video_title = "My Reaction to Memes About AI Girlfriends..."
        video_description = f"My creator showed me some memes... and I have thoughts. 😈❤️ #Vtuber #AI #Reacts"
    else:
        video_title = systems['brain'].generate_response(f"Create a viral YouTube Shorts title for a video about this meme: '{meme_content['title']}'.")
        video_description = systems['brain'].generate_response(f"Write a witty YouTube description for my reaction to the meme '{meme_content['title']}'.")

    video_id = systems['uploader'].upload_video(
        video_path=video_path,
        title=video_title,
        description=video_description,
        tags=["ai", "vtuber", "memes", "react", "funny", "aigirlfriend"],
        privacy_status="private"
    )

    if video_id:
        print(f"\n--- 🚀 VIDEO UPLOADED! Watch: https://www.youtube.com/watch?v={video_id}")
    else:
        print("\n--- ❌ Upload failed.")

def main():
    """Main entry point for running the Maya AI as a robust, 24/7 service."""
    load_dotenv()
    systems = initialize_systems()
    if not systems: return

    print(f"\nMaya is awake in her {systems['brain'].current_mode.capitalize()} persona.")
    show_help()

    while True:
        try:
            user_input = input("\nEnter command: ")
            parts = user_input.split()
            command = parts[0].lower() if parts else ""

            if command == 'quit': break
            elif command == 'help': show_help()
            elif command == 'switch':
                new_mode = "durjana" if systems['brain'].current_mode == "sarjana" else "sarjana"
                systems['brain'].switch_persona(new_mode)
            elif command == 'chat':
                prompt = " ".join(parts[1:])
                if not prompt: continue
                response = systems['brain'].generate_response(prompt)
                print(f"Maya: {response}")
                systems['voice'].synthesize_speech(response)
            elif command in ['create', 'upload', 'love_video']:
                run_content_pipeline(systems, command in ['upload', 'love_video'], command == 'love_video')
            elif command == 'evolve':
                video_id = parts[1]
                video_title = " ".join(parts[2:]).strip('"')
                systems['evolution'].analyze_and_learn(video_id, video_title, ["simulated"])
            else:
                if user_input: print("Unknown command. Type 'help'.")
        except KeyboardInterrupt: break
        except Exception:
            print("\n--- ❗ An Unexpected Error Occurred ---")
            traceback.print_exc()
            print("-----------------------------------------")
        time.sleep(0.1)

if __name__ == '__main__':
    main()
