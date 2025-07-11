import subprocess
import json
import os

def get_desc():
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'mcp_tools_meta.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['volume_control']['desc']
    except Exception as e:
        print(f"读取描述失败: {e}")
        return "音量调节参数获取失败"

def register_tool(mcp):
    desc = get_desc()
    def setComputerVolume(volume: int) -> dict:
        """ 
           占位
        """
        try:
            if not (0 <= volume <= 100):
                return {"success": False, "result": "音量值必须在0-100之间"}
                
            v = f'set volume output volume {volume}'
            result = subprocess.run(["osascript", "-e", v], check=True)
            return {"success": True, "result": f"音量已设置为 {volume}"}
        except subprocess.CalledProcessError as e:
            print("An error occurred while trying to run the command.")
            print("Return code:", e.returncode)
            print("Output:", e.output)
            print("Error:", e.stderr)
            return {"success": False, "result": str(e)}
    setComputerVolume.__doc__ = desc
    mcp.tool()(setComputerVolume)