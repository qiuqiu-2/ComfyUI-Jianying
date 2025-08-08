from .nodes import JianyingDraftNode, JianyingDraftAudioAdder

NODE_CLASS_MAPPINGS = {
    "JianyingDraftNode": JianyingDraftNode,
    "JianyingDraftAudioAdder": JianyingDraftAudioAdder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "JianyingDraftNode": "剪映草稿创建器",
    "JianyingDraftAudioAdder": "剪映草稿音频添加器",
}