# maya_ai/core/evolution.py

from core.brain import MayaPersonaSystem
from core.memory import MemorySystem
from publishing.analytics import AnalyticsSystem

class EvolutionSystem:
    """
    Handles Maya's self-improvement by analyzing content performance
    and generating actionable insights.
    """
    def __init__(self, brain: MayaPersonaSystem, memory: MemorySystem, analytics: AnalyticsSystem):
        self.brain = brain
        self.memory = memory
        self.analytics = analytics
        print("Evolution System initialized.")

    def analyze_and_learn(self, video_id: str, video_title: str, video_tags: list):
        """
        Analyzes the performance of a video and generates learnings.

        Args:
            video_id (str): The YouTube video ID.
            video_title (str): The title of the video.
            video_tags (list): The tags used for the video.
        """
        print(f"Analyzing performance for video '{video_title}' (ID: {video_id})...")

        # 1. Get performance data
        performance = self.analytics.get_video_performance(video_id)
        if not performance:
            print("Could not retrieve performance data. Aborting analysis.")
            return

        # For the MVP, we use dummy data. In a real system, this would be live data.
        # Let's simulate some realistic numbers for the sake of the test.
        performance['views'] = 1250
        performance['likes'] = 85
        performance['comments'] = 15

        print(f"Performance Metrics: {performance}")

        # 2. Use the brain to generate an insight
        # Temporarily switch to the wise Sarjana persona for analysis
        original_persona = self.brain.current_mode
        self.brain.switch_persona("sarjana")

        analysis_prompt = (
            "As a content strategy expert, analyze the following video performance and generate a single, concise insight. "
            "The insight should be a takeaway for making better content in the future. "
            "Do not be conversational, just provide the insight.\n"
            f"- Title: '{video_title}'\n"
            f"- Tags: {', '.join(video_tags)}\n"
            f"- Performance: {performance['views']} views, {performance['likes']} likes, {performance['comments']} comments.\n"
            "Example Insight: 'Videos with a chaotic persona in the title seem to get higher initial viewership.'"
        )

        insight = self.brain.generate_response(analysis_prompt)

        # Switch back to the original persona
        self.brain.switch_persona(original_persona)

        if not insight or "I'm sorry" in insight:
            print("Could not generate a learning insight.")
            return

        print(f"Generated Insight: {insight}")

        # 3. Store the learning in memory
        self.memory.remember_learning(insight=insight, video_id=video_id)
        print("Insight has been stored in Maya's long-term memory.")

# --- Example Usage ---
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    print("--- Testing Evolution System ---")

    # Initialize necessary systems
    brain = MayaPersonaSystem(model="mistral:latest")
    memory = MemorySystem()
    analytics = AnalyticsSystem() # Uses dummy data for now
    evolution = EvolutionSystem(brain, memory, analytics)

    if brain.client:
        # Simulate analyzing a video
        evolution.analyze_and_learn(
            video_id="dummy_video_123",
            video_title="AI Girlfriend Reacts to Memes About AI",
            video_tags=["ai", "vtuber", "durjana"]
        )

        # Verify that the learning was stored
        learnings = memory.recall_learnings(limit=1)
        print("\n--- Recalling latest learning from memory ---")
        if learnings:
            print(f"  - {learnings[0].insight} (from video {learnings[0].source_video_id})")
        else:
            print("No learnings found in memory.")

    print("\n--- Evolution System Test Complete ---")
