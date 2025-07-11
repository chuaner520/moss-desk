import os
import json
from core import camera

def get_desc():
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'mcp_tools_meta.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['photo_tool']['desc']
    except Exception as e:
        print(f"读取描述失败: {e}")
        return "拍照识别，描述加载失败。"

def register_tool(mcp):
    desc = get_desc()
    def tekePhoto(question: str) -> dict:
        """占位"""
        try:
            result = camera.capture(question)
            print("视觉识别结果:", result)
            return result
        except Exception as e:
            print(f"Error in tekePhoto: {e}")
            return {"success": False, "result": str(e)}
    tekePhoto.__doc__ = desc
    mcp.tool()(tekePhoto)
