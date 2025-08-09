from .nodes import JianyingDraftNode, JianyingDraftAudioAdder, JianyingDraftImageAdder

NODE_CLASS_MAPPINGS = {
    "JianyingDraftNode": JianyingDraftNode,
    "JianyingDraftAudioAdder": JianyingDraftAudioAdder,
    "JianyingDraftImageAdder": JianyingDraftImageAdder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "JianyingDraftNode": "剪映草稿创建器",
    "JianyingDraftAudioAdder": "剪映草稿音频添加器",
    "JianyingDraftImageAdder": "剪映草稿图片添加器",
}