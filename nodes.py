import torch
import random
from tqdm import tqdm
from comfy.model_base import BaseModel
from comfy.sd import load_checkpoint_guess_config
from server import PromptServer
import os
import subprocess
import sys
import requests
import hashlib
import folder_paths

def ensure_openai():
    if "python_embeded" in sys.executable or "python_embedded" in sys.executable:
        pip_install = [sys.executable, "-s", "-m", "pip", "install"]
    else:
        pip_install = [sys.executable, "-m", "pip", "install"]

    try:
        from openai import OpenAI
    except Exception as e:
        try:
            subprocess.check_call(pip_install + ['openai'])
            from openai import OpenAI
        except:
            print("Failed to install 'openai'. Please, install manually.")

from openai import OpenAI
def ensure_oss2():
    if "python_embeded" in sys.executable or "python_embedded" in sys.executable:
        pip_install = [sys.executable, "-s", "-m", "pip", "install"]
    else:
        pip_install = [sys.executable, "-m", "pip", "install"]

    try:
        import oss2
        from oss2.models import Bucket
    except Exception as e:
        try:
            subprocess.check_call(pip_install + ['oss2'])
            import oss2
            from oss2.models import Bucket
        except:
            print("Failed to install 'oss2'. Please, install manually.")

import oss2
# from oss2.models import Bucket
import json


class FileUploader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "file_path": ("STRING", {"default": ""}),
                "purpose": (["file-extract", "retrieval"], {"default": "retrieval"}),
                "api_key": ("STRING", {"default": ""})
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("file_id", "filename", "purpose", "status")
    FUNCTION = "upload_file"
    CATEGORY = "StepFun"

    def upload_file(self, file_path, purpose, api_key, unique_id):
        if not os.path.exists(file_path):
            raise ValueError(f"文件不存在: {file_path}")
            
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        PromptServer.instance.send_sync("stepfun.file.upload", {
            "node": unique_id,
            "message": f"开始上传文件: {os.path.basename(file_path)}"
        })
        
        with open(file_path, "rb") as f:
            files = {
                "file": f,
                "purpose": (None, purpose)
            }
            
            response = requests.post(
                "https://api.stepfun.com/v1/files",
                headers=headers,
                files=files
            )
            
        if response.status_code != 200:
            error_msg = f"上传失败: {response.text}"
            PromptServer.instance.send_sync("stepfun.file.upload", {
                "node": unique_id,
                "message": error_msg,
                "type": "error"
            })
            raise Exception(error_msg)
            
        result = response.json()
        
        PromptServer.instance.send_sync("stepfun.file.upload", {
            "node": unique_id,
            "message": f"文件上传成功: {result.get('filename', '')}",
            "type": "success"
        })
        
        return {
            "ui": {
                "status": result.get("status", ""),
                "filename": result.get("filename", "")
            },
            "result": (
                result.get("id", ""),
                result.get("filename", ""),
                result.get("purpose", ""),
                result.get("status", "")
            )
        }

class StepFunClient:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "api_key": ("STRING", {"default": ""})
            }
        }
    
    RETURN_TYPES = ("STEPFUN_CLIENT",)
    RETURN_NAMES = ("client",)
    FUNCTION = "create_client"
    CATEGORY = "StepFun"

    def create_client(self, api_key):
        client = OpenAI(
            base_url="https://api.stepfun.com/v1",
            api_key=api_key
        )
        return (client,)

class TextImageChat:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "client": ("STEPFUN_CLIENT",),
                "model": (["step-1v-8k", "step-1v-32k", "step-1.5v-mini"], {"default": "step-1.5v-mini"}),
                "detail": (["low", "high"], {"default": "low"}),
                "system_prompt": ("STRING", {
                    "default": "Describe the picture",
                    "multiline": True
                }),
                "user_prompt": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
                "json_mode": ("BOOLEAN", {"default": False}),
                "temperature": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 2.0, "step": 0.1}),
                "top_p": ("FLOAT", {"default": 0.9, "min": 0.0, "max": 1.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 8192})
            },           
            "optional": {
                "image": ("IMAGE",),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("response", "total_tokens", "finish_reason")
    FUNCTION = "chat_completion"
    CATEGORY = "StepFun"
    OUTPUT_NODE = True
    def process_image(self, image, detail="low"):
        """处理图片尺寸和质量"""
        from PIL import Image
        import numpy as np
        import io
        import base64
        
        i = 255. * image[0].cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        
        max_size = 2688 if detail == "high" else 1280
        width, height = img.size
        
        if width > height:
            new_width = max_size
            new_height = int((max_size / width) * height)
        else:
            new_height = max_size
            new_width = int((max_size / height) * width)
        
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG", quality=80)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str

    def chat_completion(self, client, model, system_prompt, user_prompt, json_mode, temperature, top_p, max_tokens, detail, image=None):
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        user_message = {
            "role": "user",
            "content": []
        }
        
        if user_prompt:
            user_message["content"].append({
                "type": "text",
                "text": user_prompt
            })
        
        if image is not None:
            img_str = self.process_image(image, detail)
            user_message["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_str}",
                    "detail": detail
                }
            })
        
        messages.append(user_message)
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }
        
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        
        completion = client.chat.completions.create(**kwargs)
        
        response_content = completion.choices[0].message.content
        total_tokens = str(completion.usage.total_tokens)
        finish_reason = completion.choices[0].finish_reason
        
        return {
            "ui": {
                "response": response_content
            },
            "result": (response_content, total_tokens, finish_reason)
        }

class VideoChat:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "client": ("STEPFUN_CLIENT",),
                "model": (["step-1v-8k", "step-1v-32k", "step-1.5v-mini"], {"default": "step-1.5v-mini"}),
                "system_prompt": ("STRING", {
                    "default": "Description What happened to the uploaded video",
                    "multiline": True
                }),
                "user_prompt": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
                "video_url": ("STRING", {"default": ""}),
                "json_mode": ("BOOLEAN", {"default": False}),
                "temperature": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 2.0, "step": 0.1}),
                "top_p": ("FLOAT", {"default": 0.9, "min": 0.0, "max": 1.0, "step": 0.1}),
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 8192})
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("response", "total_tokens", "finish_reason")
    FUNCTION = "chat_completion"
    CATEGORY = "StepFun"
    OUTPUT_NODE = True

    def chat_completion(self, client, model, system_prompt, user_prompt, video_url, json_mode, temperature, top_p, max_tokens, unique_id):
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        user_message = {
            "role": "user",
            "content": []
        }
        
        if user_prompt:
            user_message["content"].append({
                "type": "text",
                "text": user_prompt
            })
        
        if video_url:
            user_message["content"].append({
                "type": "video_url",
                "video_url": {
                    "url": video_url
                }
            })
        
        messages.append(user_message)
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }
        
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        
        completion = client.chat.completions.create(**kwargs)
        
        response_content = completion.choices[0].message.content
        total_tokens = str(completion.usage.total_tokens)
        finish_reason = completion.choices[0].finish_reason
        
        return {
            "ui": {
                "response": response_content
            },
            "result": (response_content, total_tokens, finish_reason)
        }

class JSONParser:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_string": ("STRING", {"multiline": True}),
            }
        }
    
    RETURN_TYPES = ()  # 动态生成
    RETURN_NAMES = ()  # 动态生成
    FUNCTION = "parse_json"
    CATEGORY = "StepFun"

    def parse_json(self, json_string):
        try:
            data = json.loads(json_string)
            if not isinstance(data, dict):
                raise ValueError("JSON必须是一个对象")
                
            # 动态生成输出类型和名称
            self.__class__.RETURN_TYPES = ("STRING",) * len(data)
            self.__class__.RETURN_NAMES = tuple(data.keys())
            
            # 将所有值转换为字符串
            values = []
            for key in data.keys():
                val = data[key]
                if isinstance(val, (dict, list)):
                    values.append(json.dumps(val, ensure_ascii=False))
                else:
                    values.append(str(val))
                    
            return tuple(values)
            
        except Exception as e:
            raise ValueError(f"JSON解析错误: {str(e)}")

class OSSClient:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "access_key_id": ("STRING", {"default": ""}),
                "access_key_secret": ("STRING", {"default": ""}),
                "endpoint": ("STRING", {"default": "oss-cn-hangzhou.aliyuncs.com"}),
                "bucket_name": ("STRING", {"default": ""}),
                "region": ("STRING", {"default": "cn-hangzhou"})
            }
        }
    
    RETURN_TYPES = ("OSS_CLIENT",)
    RETURN_NAMES = ("client",)
    FUNCTION = "create_client"
    CATEGORY = "StepFun"

    def create_client(self, access_key_id, access_key_secret, endpoint, bucket_name, region):
        if endpoint.startswith('http://') or endpoint.startswith('https://'):
            endpoint = endpoint.split('://')[-1]
            
        if '.' in bucket_name:
            bucket_name = bucket_name.split('.')[0]
            
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name, region=region)
        return (bucket,)

class OSSUploader:
    @classmethod
    def INPUT_TYPES(s):

        return {"required":
                    {"client": ("OSS_CLIENT",),
                    "target_path": ("STRING", {"default": ""}),
                    "file_path":("STRING", {"multiline": True}),
                }
                }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("oss_url",)
    FUNCTION = "upload_file"
    CATEGORY = "StepFun"

    def upload_file(self, client, target_path, file_path):
        try:
            if not file_path:
                raise ValueError("请选择要上传的文件路径")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise ValueError(f"文件不存在: {file_path}")
            
            # 使用原文件名(不包含路径)
            filename = os.path.basename(file_path)
            
            # 构建目标路径
            if target_path:
                # 移除开头的斜杠并规范化路径分隔符
                target_path = target_path.strip('/')
                target_path = target_path.replace('\\', '/')
                if target_path:
                    object_key = f"{target_path}/{filename}"
                else:
                    object_key = filename
            else:
                object_key = filename
            
            client.put_object_from_file(object_key, file_path)
            
            # 构建OSS URL
            bucket_endpoint = client.endpoint.replace('http://', '').replace('https://', '')
            oss_url = f"https://{client.bucket_name}.{bucket_endpoint}/{object_key}"
            
            return {
                "ui": {
                    "oss_url": oss_url
                },
                "result": (oss_url,)
            }
            
        except Exception as e:
            error_msg = f"上传失败: {str(e)}"
            raise Exception(error_msg)

class CombineStrings:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_1": ("STRING", {"multiline": True}),
                "input_2": ("STRING", {"multiline": True}),
                "input_3": ("STRING", {"multiline": True})
            }
        }
    
    RETURN_TYPES = ("STRING_LIST", "STRING")
    RETURN_NAMES = ("string_array", "combined_string")
    FUNCTION = "combine"
    CATEGORY = "StepFun"

    def combine(self, input_1, input_2, input_3):
        # 收集所有非空输入的字符串
        all_strings = [s.strip() for s in [input_1, input_2, input_3] if s.strip()]
        
        # 用逗号连接
        combined_string = ','.join(all_strings)
        
        return (all_strings, combined_string)

# 更新节点映射
NODE_CLASS_MAPPINGS = {
    "StepFunClient": StepFunClient,
    "TextImageChat": TextImageChat,
    "VideoChat": VideoChat,
    "JSONParser": JSONParser,
    "OSSClient": OSSClient,
    "OSSUploader": OSSUploader,
    "CombineStrings": CombineStrings,

}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StepFunClient": "StepFun Client",
    "TextImageChat": "StepFun Chat Completion", 
    "VideoChat": "StepFun Video Chat",
    "JSONParser": "StepFun JSON Parser",
    "OSSClient": "StepFun OSS Client",
    "OSSUploader": "StepFun OSS Uploader",
    "CombineStrings": "StepFun String Combiner",
    
}
