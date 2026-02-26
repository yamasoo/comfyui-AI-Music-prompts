try:
    from .AceStep15Generator import AceStep15PromptGenerator
    from .AceStepAudioTextSaver import AceStepAudioTextSaver

    NODE_CLASS_MAPPINGS = {
        "AceStep15PromptGenerator": AceStep15PromptGenerator,
        "AceStepAudioTextSaver": AceStepAudioTextSaver
    }

    NODE_DISPLAY_NAME_MAPPINGS = {
        "AceStep15PromptGenerator": "🎵 ACE-Step 1.5 Prompt Generator",
        "AceStepAudioTextSaver": "💾 ACE-Step Audio & Metadata Saver"
    }

    __all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
    print("✅ ACE-Step 1.5 Nodes Loaded Successfully")

except Exception as e:
    print(f"❌ ACE-Step 1.5 Load Failed: {e}")