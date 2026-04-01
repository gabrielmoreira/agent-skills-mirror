<p align="center">
  <img src="aigc-director-pics/banner.png" width="100%" />
</p>

<h2 align="center">
  AIGC-Claw: AI Creative Video Production Agent
</h2>

<h4 align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
  <a href="https://github.com/HITsz-TMG/AIGC-Claw/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/HITsz-TMG/AIGC-Claw?style=flat-square" alt="License">
  </a>
  <a href="https://github.com/HITsz-TMG/AIGC-Claw/stargazers">
    <img src="https://img.shields.io/github/stars/HITsz-TMG/AIGC-Claw?style=flat-square&logo=github" alt="Stars">
  </a>
  <a href="https://github.com/HITsz-TMG/AIGC-Claw/fork">
    <img src="https://img.shields.io/github/forks/HITsz-TMG/AIGC-Claw?style=flat-square&logo=github" alt="Forks">
  </a>
  <img src="https://img.shields.io/badge/Python-3.9+-purple.svg" alt="Python">
  <a href="#method-2-openclaw-auto-setup">
    <img src="https://img.shields.io/badge/OpenClaw-Compatible-ff4444?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6IiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg==" alt="OpenClaw Compatible">
  </a>
</h4>

<p align="center">
  <b><i><font size="5">Talk to <a href="https://github.com/openclaw/openclaw">OpenClaw</a> directly: "Generate a video of X" -> done.</font></i></b>
</p>

<div align="center">

📺 [**Bilibili**](https://space.bilibili.com/2031891503?spm_id_from=333.1007.0.0)  ▶️ [**YouTube**](https://www.youtube.com/@imryanxu)  📖 [**Integration Guide**](https://github.com/HITsz-TMG/AIGC-Claw/blob/main/README_EN.md#method-2-openclaw-auto-setup)  🌐 [**中文 README**](./README.md)  🦀 [**ClawHub**](https://clawhub.ai/hit-cxf/aigc-director)

<a href="https://trendshift.io/repositories/24295" target="_blank"><img src="https://trendshift.io/api/badge/repositories/24295" alt="HITsz-TMG%2FAIGC-Claw | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

</div>


## 💥 News

- `2026/3/27`: 🚀 AIGC-Claw is officially released, supporting the full workflow from idea to finished video.


## 📖 Overview

AIGC-Claw is an AI director system designed for creative video production. You only need to provide a single idea, a story outline, or even a vague concept, and the system will decompose it into an executable filmmaking workflow, continuously producing intermediate assets that can be reviewed, confirmed, revised, and delivered, until a complete final video is generated.

It is not just a one-shot "text-to-video" tool. Instead, it is a full production pipeline covering **script planning -> character and scene design -> storyboard planning -> reference image generation -> video generation -> post-production editing**. Rather than returning a black-box result, AIGC-Claw works more like a real collaborative AI director team: each stage informs the next, and every key node is visible, editable, and extensible.


## 📺 AIGC-Claw Examples

<table>
<tr>
<td align="center" width="33%">
  <video src="https://github.com/user-attachments/assets/63c2f33c-da50-44f0-8c26-a65611479d6a" controls width="100%"></video>
</td>
<td align="center" width="33%">
  <video src="https://github.com/user-attachments/assets/d7c65cad-05b9-46c8-ab0e-96e39909f978" controls width="100%"></video>
</td>
<td align="center" width="33%">
  <video src="https://github.com/user-attachments/assets/ec67546e-2d3d-4b34-b1ad-7d860a9bc1aa" controls width="100%"></video>
</td>
</tr>
</table>

<details>
<summary><b>Web Frontend</b></summary>
<div align="center">

| | |
|:---:|:---:|
| ![Stage 1](./aigc-director-pics/workflow_demo/stage_1.png) | ![Stage 2](./aigc-director-pics/workflow_demo/stage_2.png) |
| ![Stage 3](./aigc-director-pics/workflow_demo/stage_3.png) | ![Stage 4](./aigc-director-pics/workflow_demo/stage_4.png) |
| ![Stage 5](./aigc-director-pics/workflow_demo/stage_5.png) | ![Stage 6](./aigc-director-pics/workflow_demo/stage_6.png) |

</div>
</details>

<details>
<summary><b>WeChat Integration</b></summary>
<div align="center">

| | | | |
|:---:|:---:|:---:|:---:|
| ![WeChat 1](./aigc-director-pics/wechat_demo/wechat_1.jpg) | ![WeChat 2](./aigc-director-pics/wechat_demo/wechat_2.jpg) | ![WeChat 3](./aigc-director-pics/wechat_demo/wechat_3.jpg) | ![WeChat 4](./aigc-director-pics/wechat_demo/wechat_4.jpg) |

</div>
</details>

<details>
<summary><b>Feishu Integration</b></summary>
<div align="center">

| | | | |
|:---:|:---:|:---:|:---:|
| ![Feishu 1](./aigc-director-pics/feishu_demo/feishu_1.jpg) | ![Feishu 2](./aigc-director-pics/feishu_demo/feishu_2.jpg) | ![Feishu 3](./aigc-director-pics/feishu_demo/feishu_3.jpg) | ![Feishu 4](./aigc-director-pics/feishu_demo/feishu_4.jpg) |

</div>
</details>

## ✨ Features

| Capability | Description |
|---|---|
| 🎬 **End-to-end generation from idea to final cut** | Connects scripts, characters, storyboards, reference images, video clips, and post-production into one complete workflow, upgrading scattered generation tools into a full video production pipeline. |
| 🖼️ **Storyboard-driven controllable creation** | Uses structured scripts, storyboard planning, and reference-image generation to improve character consistency, shot expression, and visual style control. |
| ✍️ **Editable, extensible, and regenerable** | Supports intelligent continuation of stories and storyboards, while also allowing edits and regeneration at the character, reference-image, and video stages, so you do not need to restart from scratch every time. |
| 📲 **Local deployment, multi-platform collaboration, and asset retention** | Supports a Web UI, WeChat and Feishu collaboration, OpenClaw Skill integration, and full-chain retention of scripts, images, video clips, and final outputs. |

---

## 🚀 Quick Start

### Method 1: Manual Installation

```bash
# 1. Clone the repository
git clone https://github.com/HITsz-TMG/AIGC-Claw.git
cd AIGC-Claw

# 2. Configure and start the backend
cd aigc-director/aigc-claw/backend

# Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and fill in your API keys

# Start the backend
python api_server.py
# Service runs at http://localhost:8000
```

```bash
# 3. Configure and start the frontend (new terminal)
cd aigc-director/aigc-claw/frontend
npm install
npm run build
npm start
# Visit http://localhost:3000
```

### Method 2: OpenClaw Auto Setup

Send this message to OpenClaw:

```text
Please clone this git repository: https://github.com/HITsz-TMG/AIGC-Claw.git
Then recursively copy the aigc-director folder inside AIGC-Claw to .openclaw/workspace/skills and use it as an AIGC-related skill.
```

When using it, it is recommended to explicitly say "use aigc-director":

```text
Use aigc-director to generate a video with the content "A Dog's Purpose".
```

### Method 3: Install via ClawHub

Make sure `clawhub-cli` is installed locally.

Open a terminal and run the following command. Choose `yes` for every prompt.

```bash
clawhub install aigc-director
```

After installation, ClawHub will copy `aigc-director` into `workspace/skills` (or your specified skills directory).

After that, you can either follow Method 1 to build and run the project manually, or let OpenClaw handle the rest of the project setup.

The first time you use `aigc-director`, if you have not built the project manually, OpenClaw will automatically build and start both the backend and frontend, so no manual initialization is required. Please be patient, because project setup involves environment configuration and compilation.


---

## 🔧 Configuration

<details>
<summary><b>Click to expand full environment requirements and variables</b></summary>

### Requirements

- **Python**: 3.9+
- **Node.js**: 18+
- **npm**: 9+

### Backend Environment Variables

Configure the following in `aigc-claw/backend/.env`:

```bash
# LLM configuration
LLM_MODEL=qwen3.5-plus
VLM_MODEL=qwen-vl-plus

# Image generation
IMAGE_T2I_MODEL=doubao-seedream-5-0-260128
IMAGE_IT2I_MODEL=doubao-seedream-5-0-260128

# Video generation
VIDEO_MODEL=wan2.6-i2v-flash
VIDEO_RATIO=16:9

# API keys
DASHSCOPE_API_KEY=your_key
ARK_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
```

### Available Models

| Type | Models |
|:---:|:---|
| **LLM** | qwen3.5-plus, deepseek-chat, gpt-4o, gemini-2.5-flash |
| **VLM** | qwen-vl-plus, gemini-2.5-flash-image |
| **Text-to-Image** | doubao-seedream-5-0, jimeng_t2i_v40, wan2.6-t2i |
| **Image-to-Image** | doubao-seedream-5-0, jimeng_t2i_v40, wan2.6-image |
| **Video Generation** | wan2.6-i2v-flash, kling-v3, jimeng_ti2v_v30_pro |

</details>


## 🙏 Acknowledgments

The idea and design of AIGC-Claw were inspired by [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw), [huobao-drama](https://github.com/chatfire-AI/huobao-drama), [LibTV](https://www.liblib.tv/), and [libtv-skills](https://github.com/libtv-labs/libtv-skills).


## 📚 Related Work

| Framework | Paper Information |
|:---:|---|
| <img src="https://github.com/HITsz-TMG/FilmAgent/blob/main/pics/framework.png?raw=true" width="420" alt="FilmAgent framework"/> | **[SIGGRAPH Asia 2024] FilmAgent: Automating Virtual Film Production Through a Multi-Agent Collaborative Framework**<br>*Zhenran Xu, Jifang Wang, Longyue Wang, Zhouyi Li, Senbao Shi, Baotian Hu, Min Zhang*<br>[[Paper](https://doi.org/10.1145/3681758.3698014)] [[GitHub](https://github.com/HITsz-TMG/AIGC-Claw/blob/main/FilmAgent.md)] |
| <img src="https://github.com/HITsz-TMG/Anim-Director/blob/main/Anim-Director/assets/visualeg.png" width="420" alt="Anim-Director result"/> | **[SIGGRAPH Asia 2024] Anim-Director: A Large Multimodal Model Powered Agent for Controllable Animation Video Generation**<br>*Yunxin Li, Haoyuan Shi, Baotian Hu, Longyue Wang, Jiashun Zhu, Jinyi Xu, Zhen Zhao, Min Zhang*<br>[[Paper](https://doi.org/10.1145/3680528.3687688)] [[GitHub](https://github.com/HITsz-TMG/Anim-Director/tree/main/Anim-Director)] |
| <img src="https://raw.githubusercontent.com/HITsz-TMG/Anim-Director/main/AniMaker/assets/pipeline.png" width="420" alt="AniMaker pipeline"/> | **[SIGGRAPH Asia 2025] AniMaker: Multi-Agent Animated Storytelling with MCTS-Driven Clip Generation**<br>*Haoyuan Shi, Yunxin Li, Xinyu Chen, Longyue Wang, Baotian Hu, Min Zhang*<br>[[Paper](https://doi.org/10.1145/3757377.3764009)] [[GitHub](https://github.com/HITsz-TMG/Anim-Director/tree/main/AniMaker)] |


<p align="center">
  <sub>Built with 🦞 by the HITsz-TMG team</sub>
</p>
