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
            },
            "optional": {
                "draft_path": ("STRING", {
                    "default": "C:\\Users\\" + os.getenv("USERNAME", "admin") + "\\Documents\\JianyingPro\\Drafts", 
                    "name": "草稿保存路径", 
                    "description": "剪映草稿保存路径，例如：C:\\Users\\用户名\\Documents\\JianyingPro\\Drafts"
                }),
                "project_name": ("STRING", {"default": "未命名项目", "name": "项目名称"}),
                "video_path": ("STRING", {"default": "", "name": "视频文件路径", "description": "用于指定项目中使用的主视频文件路径"}),
                "duration": ("FLOAT", {"default": 10.0, "min": 0.1, "max": 3600.0, "step": 0.1, "name": "项目时长(秒)"}),
                "resolution": (["1920x1080", "1280x720", "854x480", "1080x1920", "720x1280"], {"default": "1920x1080", "name": "分辨率"}),
                "fps": (["30", "60", "24"], {"default": "30", "name": "帧率"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("UUID", "草稿目录")
    FUNCTION = "create_draft"
    CATEGORY = "剪映工具"
    
    def create_draft(self, draft_path=None, project_name="未命名项目", video_path="", duration=10.0, resolution="1920x1080", fps="30"):
        """创建剪映草稿"""
        
        # 解析分辨率
        width, height = map(int, resolution.split('x'))
        
        # 生成UUID
        draft_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # 确保输出目录存在
        if draft_path is None or not draft_path or not os.path.exists(draft_path):
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
        
        return (draft_id, draft_folder)

class JianyingDraftAudioAdder:
    """向剪映草稿添加背景音乐的节点"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            },
            "optional": {
                "draft_path": ("STRING", {
                    "default": "", 
                    "name": "剪映草稿路径", 
                    "description": "剪映草稿文件夹路径，包含draft_meta_info.json和draft_content.json"
                }),
                "audio_path": ("STRING", {"default": "", "name": "音频文件路径", "description": "背景音乐文件路径"}),
                "audio_volume": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 1.0, "step": 0.1, "name": "音频音量", "description": "背景音乐的音量（0-1）"}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("草稿目录", "状态信息")
    FUNCTION = "add_audio_to_draft"
    CATEGORY = "剪映工具"
    
    def add_audio_to_draft(self, draft_path=None, audio_path="", audio_volume=0.8):
        """向剪映草稿添加背景音乐"""
        
        if draft_path is None or not draft_path:
            return ("", "错误：草稿路径不能为空")
        
        # 标准化路径
        draft_path = os.path.normpath(draft_path.strip())
        
        if not os.path.exists(draft_path):
            return ("", f"错误：草稿路径不存在: {draft_path}")
        
        meta_info_path = os.path.join(draft_path, "draft_meta_info.json")
        content_path = os.path.join(draft_path, "draft_content.json")
        
        if not os.path.exists(meta_info_path):
            return ("", f"错误：找不到文件 {meta_info_path}")
        
        if not os.path.exists(content_path):
            return ("", f"错误：找不到文件 {content_path}")
        
        try:
            # 读取现有草稿信息
            with open(meta_info_path, "r", encoding="utf-8") as f:
                meta_info = json.load(f)
            
            with open(content_path, "r", encoding="utf-8") as f:
                content_data = json.load(f)
            
            # 获取草稿的最大时长
            max_duration = 0
            if "materials" in content_data and "videos" in content_data["materials"]:
                for video in content_data["materials"]["videos"]:
                    if "duration" in video:
                        max_duration = max(max_duration, video["duration"])
            
            if max_duration == 0:
                max_duration = 10.0  # 默认值
            
            # 使用草稿的最大时长作为音频时长
            final_audio_duration = max_duration
            
            # 添加音频到元数据
            audio_id = f"audio_{uuid.uuid4().hex[:8]}"
            if "draft_materials" not in meta_info:
                meta_info["draft_materials"] = []
            
            meta_info["draft_materials"].append({
                "id": audio_id,
                "path": audio_path,
                "type": "audio"
            })
            
            # 添加音频到内容
            if "materials" not in content_data:
                content_data["materials"] = {}
            if "audios" not in content_data["materials"]:
                content_data["materials"]["audios"] = []
            
            content_data["materials"]["audios"].append({
                "id": audio_id,
                "path": audio_path,
                "duration": final_audio_duration,
                "volume": audio_volume,
                "inPoint": 0,
                "outPoint": final_audio_duration
            })
            
            # 添加音频轨道
            if "tracks" not in content_data:
                content_data["tracks"] = []
            
            content_data["tracks"].append({
                "id": f"track_audio_{audio_id}",
                "type": "audio",
                "clips": [{
                    "id": f"clip_audio_{audio_id}",
                    "materialId": audio_id,
                    "startTime": 0,
                    "duration": final_audio_duration,
                    "volume": audio_volume
                }]
            })
            
            # 保存更新后的文件
            with open(meta_info_path, "w", encoding="utf-8") as f:
                json.dump(meta_info, f, ensure_ascii=False, indent=2)
            
            with open(content_path, "w", encoding="utf-8") as f:
                json.dump(content_data, f, ensure_ascii=False, indent=2)
            
            return (draft_path, f"成功添加背景音乐，音频时长设置为{final_audio_duration}秒")
            
        except Exception as e:
            return ("", f"错误：{str(e)}")

# 注册所有节点
NODE_CLASS_MAPPINGS = {
    "JianyingDraftNode": JianyingDraftNode,
    "JianyingDraftAudioAdder": JianyingDraftAudioAdder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "JianyingDraftNode": "剪映草稿创建器",
    "JianyingDraftAudioAdder": "剪映草稿音频添加器",
}