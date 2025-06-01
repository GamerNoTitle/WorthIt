import json

def load_config() -> dict:
    """
    从 config.json 文件加载配置。
    如果文件不存在或格式不正确，将返回一个空字典。
    :return: 配置字典
    """
    try:
        with open("config.json", "r", encoding="utf-8") as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        print("配置文件 config.json 未找到，返回空配置。")
        return {}
    except json.JSONDecodeError:
        print("配置文件格式错误，返回空配置。")
        return {}
    except Exception as e:
        print(f"加载配置时发生错误: {e}")
        return {}