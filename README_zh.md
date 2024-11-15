# ComfyUI StepFun Nodes

这是一个基于[阶跃星辰(StepFun)](https://platform.stepfun.com/)API的ComfyUI自定义节点集合。通过这些节点，您可以轻松实现图片和视频的智能分析与处理。
目前视频的上传暂未实现，需要传入视频url链接.
> 🚧 **更多节点正在更新中...**
## 主要特点

- 🖼️ 图片内容理解与分析
- 🎬 视频内容理解与分析  
- ✨ 智能提示词(Prompt)生成
- 💰 低成本的API定价
- 🚀 无需本地GPU资源，云端处理

## 安装说明

1. 将本仓库克隆到ComfyUI的`custom_nodes`目录下:
```bash
cd custom_nodes
git clone https://github.com/your-repo/ComfyUI_StepFun.git
```

2. 安装依赖:
```bash
cd ComfyUI_StepFun
pip install -r requirements.txt
```

## API密钥配置

1. 访问[StepFun平台](https://platform.stepfun.com/account-overview)注册账号
2. 在账户概览页面获取API密钥
3. 将API密钥添加到配置文件中

## 使用方法

### 示例工作流

在 `workflow` 文件夹中提供了以下示例：

#### Role2Story 工作流
- 文件：`workflow/role2story.json`
- 功能：通过输入角色/场景/故事描述，自动生成：
  - 🎨 主题海报
  - 🎬 三个关键剧情镜头
- 该工作流展示了模型对内容的理解能力和智能提示词生成能力

![Role2Story工作流示例](imgs/role2story.jpg)

> 🚧 **更多工作流示例正在更新中...**

## 支持的功能

- 图片内容识别与描述
- 视频场景分析
- 智能提示词生成
- [其他功能]

## 注意事项

- API调用需要联网
- 请确保API密钥配置正确
- 遵守API使用限制和条款



## 联系方式

- Email: 3354405250@qq.com
- [其他联系方式]

如果您在使用过程中遇到任何问题，欢迎通过以上方式联系我们。
