# ComfyUI StepFun Nodes

This is a collection of ComfyUI custom nodes based on the [StepFun](https://platform.stepfun.com/) API. These nodes enable easy implementation of intelligent analysis and processing for images and videos.
Currently, video upload is not implemented, and video URL links are required.
> 🚧 **More nodes are being updated...**

## Key Features

- 🖼️ Image Content Understanding and Analysis
- 🎬 Video Content Understanding and Analysis
- ✨ Intelligent Prompt Generation
- 💰 Cost-effective API Pricing
- 🚀 Cloud Processing without Local GPU Resources

## Installation

1. Clone this repository to your ComfyUI's `custom_nodes` directory:
```bash
cd custom_nodes
git clone https://github.com/your-repo/ComfyUI_StepFun.git
```

2. Install dependencies:
```bash
cd ComfyUI_StepFun
pip install -r requirements.txt
```

## API Key Configuration

1. Register an account at [StepFun Platform](https://platform.stepfun.com/account-overview)
2. Get your API key from the account overview page
3. Add the API key to the configuration file

## Usage

### Example Workflows

The following examples are provided in the `workflow` folder:

#### Role2Story Workflow
- File: `workflow/role2story.json`
- Features: By inputting character/scene/story descriptions, automatically generate:
  - 🎨 Theme Poster
  - 🎬 Three Key Plot Shots
- This workflow demonstrates the model's content understanding and intelligent prompt generation capabilities

![Role2Story Workflow Example](imgs/role2story.jpg)

> 🚧 **More workflow examples are being updated...**

## Supported Features

- Image Content Recognition and Description
- Video Scene Analysis
- Intelligent Prompt Generation
- [Other Features]

## Notes

- API calls require internet connection
- Ensure correct API key configuration
- Comply with API usage limits and terms

## Contact

- Email: 3354405250@qq.com
- [Other Contact Methods]

If you encounter any issues while using this project, please feel free to contact us through the above methods.
