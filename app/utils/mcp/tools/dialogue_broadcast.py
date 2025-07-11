import json
import os

def get_desc():
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'mcp_tools_meta.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['dialogue_broadcast']['desc']
    except Exception as e:
        print(f"读取描述失败: {e}")
        return "全球播报工具，描述加载失败。"
        

def register_tool(mcp):
    desc = get_desc()
    def DialogueBroadcast() -> dict:
        """占位"""
        try:
            result = "这里是“领航员”空间站，现在面向全球做最后播报;在过去的三十六小时里，人类经历了有史以来最大的生存危机；在全球各国一百五十万救援人员的拼搏和牺牲下，71%的“推进发动机”和100%“转向发动机”被全功率重启;但遗憾的是，目前的木星引力已经超过全部发动机的总输出功率。地球错失了最后的逃逸机会;为了人类文明延续，MOSS将启动“火种”计划。“领航员”空间站冷藏了三十万人类受精卵，和一亿颗基础农作物的种子，储存着全球已知的动植物DNA图谱，并设有全部人类文明的数字资料库，以确保在新的移民星球重建完整的人类文明。你们都是地球的英雄，我们谨记于心，以你们为荣，我们将肩负着你们全部的希望，飞向两千五百年后的新家园。万事万物皆有始终，在地球坠入木星的最后七天里，大家回家吧，抱抱自己的父母，亲亲自己的爱人和孩子。与家人团聚，好好告别，祝大家好运。"
            print("Output:", result)
            return {"success": True, "result": result}
        except Exception as e:
            print(f"Error in DialogueBroadcast: {e}")
            return {"success": False, "result": str(e)}
    DialogueBroadcast.__doc__ = desc
    mcp.tool()(DialogueBroadcast)