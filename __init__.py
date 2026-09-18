import traceback

try:
    from .AceStep15Generator import AceStep15PromptGenerator
    from .AceStepAudioTextSaver import AceStepAudioTextSaver
    from .prompt_data import GENRE_DATA, MOOD_DATA

    # Keep the generator implementation focused while exposing the extended
    # selectable genre and mood catalog from a dedicated data module.
    AceStep15PromptGenerator.GENRE_DATA = GENRE_DATA
    AceStep15PromptGenerator.MOOD_DATA = MOOD_DATA

    NODE_CLASS_MAPPINGS = {
        "AceStep15PromptGenerator": AceStep15PromptGenerator,
        "AceStepAudioTextSaver": AceStepAudioTextSaver,
    }

    NODE_DISPLAY_NAME_MAPPINGS = {
        "AceStep15PromptGenerator": "🎵 ACE-Step 1.5 Prompt Generator",
        "AceStepAudioTextSaver": "💾 ACE-Step Audio & Metadata Saver",
    }

    __all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
    print("✅ ACE-Step 1.5 Nodes Loaded Successfully")

except Exception:
    print("❌ ACE-Step 1.5 Load Failed")
    traceback.print_exc()
    raise
