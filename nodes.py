import json
import os
import uuid
from datetime import datetime

class JianyingDraftNode:
    """创建剪映草稿的节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "draft_path": ("STRING", {
                    "default": "C:\\Users\\" + os.getenv("USERNAME", "admin") + "\\Documents\\JianyingPro\\Drafts", 
                    "name": "草稿保存路径", 
                    "description": "剪映草稿保存路径，例如：C:\\Users\\用户名\\Documents\\JianyingPro\\Drafts"
                }),
            },
            "optional": {
                "project_name": ("STRING", {"default": "未命名项目", "name": "项目名称"}),
                "video_path": ("STRING", {"default": "", "name": "视频文件路径", "description": "用于指定项目中使用的主视频文件路径"}),
                "duration": ("FLOAT", {"default": 10.0, "min": 0.1, "max": 3600.0, "step": 0.1, "name": "项目时长(秒)"}),
                "resolution": (["1920x1080", "1280x720", "854x480", "1080x1920", "720x1280"], {"default": "1920x1080", "name": "分辨率"}),
                "fps": (["30", "60", "24"], {"default": "30", "name": "帧率"}),
            }
        }


    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("UUID",)
    FUNCTION = "create_draft"
    CATEGORY = "剪映工具"
    
    def create_draft(self, draft_path, project_name="未命名项目", video_path="", duration=10.0, resolution="1920x1080", fps="30"):
        """创建剪映草稿"""
        
        # 解析分辨率
        width, height = map(int, resolution.split('x'))
        
        # 生成UUID
        draft_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # 确保输出目录存在
        if not draft_path or not os.path.exists(draft_path):
            draft_path = os.path.join(os.path.expanduser("~"), "Documents", "JianyingPro", "Drafts")
            os.makedirs(draft_path, exist_ok=True)
        
        # 创建草稿文件夹
        folder_name = f"{datetime.now().strftime('%y%m%d')}_{project_name}"
        draft_folder = os.path.join(draft_path, folder_name)
        os.makedirs(draft_folder, exist_ok=True)
        
        # 创建元数据
        meta_info = {
            "id": draft_id,
            "name": project_name,
            "width": width,
            "height": height,
            "fps": int(fps),
            "createTime": current_time,
            "modifyTime": current_time,
            "draft_materials": [{
                "id": "video_0",
                "path": video_path,
                "type": "video"
            }]
        }
        
        # 创建内容
        content_data = {
            "version": "2.0",
            "app": "jianying",
            "canvas_config": {
                "width": width,
                "height": height,
                "aspectRatio": f"{width}:{height}"
            },
            "materials": {
                "videos": [{
                    "id": "video_0",
                    "path": video_path,
                    "duration": duration,
                    "inPoint": 0,
                    "outPoint": duration
                }]
            },
            "tracks": [{
                "id": "track_video_0",
                "type": "video",
                "clips": [{
                    "id": "clip_0",
                    "materialId": "video_0",
                    "startTime": 0,
                    "duration": duration,
                    "position": {"x": 0, "y": 0},
                    "scale": 1.0
                }]
            }],
            "effects": []
        }
        
        # 保存文件
        with open(os.path.join(draft_folder, "draft_meta_info.json"), "w", encoding="utf-8") as f:
            json.dump(meta_info, f, ensure_ascii=False, indent=2)
        
        with open(os.path.join(draft_folder, "draft_content.json"), "w", encoding="utf-8") as f:
            json.dump(content_data, f, ensure_ascii=False, indent=2)
        
        return (draft_id,)