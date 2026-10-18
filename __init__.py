import traceback

try:
    from . import AceStep15Generator, AceStepAudioTextSaver

    # Each module owns its node classes and display names; merge them here so
    # there is only one place to rename a node.
    NODE_CLASS_MAPPINGS = {
        **AceStep15Generator.NODE_CLASS_MAPPINGS,
        **AceStepAudioTextSaver.NODE_CLASS_MAPPINGS,
    }
    NODE_DISPLAY_NAME_MAPPINGS = {
        **AceStep15Generator.NODE_DISPLAY_NAME_MAPPINGS,
        **AceStepAudioTextSaver.NODE_DISPLAY_NAME_MAPPINGS,
    }

    __all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
    print("✅ ACE-Step 1.5 Nodes Loaded Successfully")

except Exception:
    print("❌ ACE-Step 1.5 Load Failed")
    traceback.print_exc()
    raise
