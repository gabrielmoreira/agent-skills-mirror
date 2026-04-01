<p align="center">
  <img src="aigc-director-pics/banner.png" width="100%" />
</p>

<h2 align="center">
  AIGC-Claw: AI 创意视频生成员工
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
  <a href="#openclaw-integration">
    <img src="https://img.shields.io/badge/OpenClaw-Compatible-ff4444?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6IiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg==" alt="OpenClaw Compatible">
  </a>
</h4>

<p align="center">
  <b><i><font size="5">直接与 <a href="https://github.com/openclaw/openclaw">OpenClaw</a> 对话："生成 X 的视频" → 搞定。</font></i></b>
</p>

<div align="center">

🌐 [**English README**](./README_EN.md)  📺 [**Bilibili**](https://space.bilibili.com/2031891503?spm_id_from=333.1007.0.0)  ▶️ [**YouTube**](https://www.youtube.com/@imryanxu)  📖 [**集成指南**](https://github.com/HITsz-TMG/AIGC-Claw?tab=readme-ov-file#%E6%96%B9%E5%BC%8F%E4%BA%8Copenclaw-%E8%87%AA%E5%8A%A8%E9%85%8D%E7%BD%AE)   🦀 [**ClawHub**](https://clawhub.ai/hit-cxf/aigc-director) 

<a href="https://trendshift.io/repositories/24295" target="_blank"><img src="https://trendshift.io/api/badge/repositories/24295" alt="HITsz-TMG%2FAIGC-Claw | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

</div>


## 💥 News

- `2026/3/27`: 🚀 AIGC-Claw 正式发布，支持从想法到视频生成全流程



## 📖 项目介绍

AIGC-Claw 是一个面向创意视频生产的 AI 导演系统。你只需要给出一句想法、一个故事梗概，甚至一个模糊概念，系统就会把它拆解为可执行的影视工作流，持续产出可查看、可确认、可修改、可交付的中间资产，最终生成完整成片。

它不是单点式的“文生视频”工具，而是一条覆盖 **剧本策划 → 角色/场景设计 → 分镜规划 → 参考图生成 → 视频生成 → 后期剪辑** 的全流程生产线。相比只给你一个黑盒结果，AIGC-Claw 更像一个真正可协作的 AI 导演团队：前一阶段决定后一阶段，所有关键节点都可视化、可编辑、可继续生成。



## 📺 AIGC-Claw 示例

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
<summary><b>Web 前端界面</b></summary>
<div align="center">

| | |
|:---:|:---:|
| ![Stage 1](./aigc-director-pics/workflow_demo/stage_1.png) | ![Stage 2](./aigc-director-pics/workflow_demo/stage_2.png) |
| ![Stage 3](./aigc-director-pics/workflow_demo/stage_3.png) | ![Stage 4](./aigc-director-pics/workflow_demo/stage_4.png) |
| ![Stage 5](./aigc-director-pics/workflow_demo/stage_5.png) | ![Stage 6](./aigc-director-pics/workflow_demo/stage_6.png) |

</div>
</details>

<details>
<summary><b>微信交互</b></summary>
<div align="center">

| | | | |
|:---:|:---:|:---:|:---:|
| ![WeChat 1](./aigc-director-pics/wechat_demo/wechat_1.jpg) | ![WeChat 2](./aigc-director-pics/wechat_demo/wechat_2.jpg) | ![WeChat 3](./aigc-director-pics/wechat_demo/wechat_3.jpg) | ![WeChat 4](./aigc-director-pics/wechat_demo/wechat_4.jpg) |

</div>
</details>

<details>
<summary><b>飞书交互</b></summary>
<div align="center">

| | | | |
|:---:|:---:|:---:|:---:|
| ![Feishu 1](./aigc-director-pics/feishu_demo/feishu_1.jpg) | ![Feishu 2](./aigc-director-pics/feishu_demo/feishu_2.jpg) | ![Feishu 3](./aigc-director-pics/feishu_demo/feishu_3.jpg) | ![Feishu 4](./aigc-director-pics/feishu_demo/feishu_4.jpg) |

</div>
</details>

## ✨ 功能特性

| 能力 | 说明 |
|---|---|
| 🎬 **从创意到成片的全流程生成** | 一条链路打通剧本、角色、分镜、参考图、视频片段与后期剪辑，把零散生成能力升级为完整视频生产工作流。 |
| 🖼️ **分镜驱动的可控创作** | 通过结构化剧本、分镜规划与参考图生成，让角色一致性、镜头表达和画面风格更稳定、更可控。 |
| ✍️ **可修改、可续写、可继续生成** | 支持剧情 / 分镜智能续写，也支持角色、参考图、视频阶段修改后重新生成，避免每次都从头开始。 |
| 📲 **本地部署、多端协作、产物留存** | 支持 Web 界面、微信 / 飞书协作、OpenClaw Skill 集成，并对剧本、图片、视频片段和最终成片进行全链路留存。 |

---

## 🚀 快速开始

### 方式一：手动安装

```bash
# 1. 克隆项目
git clone https://github.com/HITsz-TMG/AIGC-Claw.git
cd AIGC-Claw

# 2. 配置并启动后端
cd aigc-director/aigc-claw/backend

# 创建虚拟环境并安装依赖
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 启动后端
python api_server.py
# 服务运行在 http://localhost:8000
```

```bash
# 3. 配置并启动前端（新终端）
cd aigc-director/aigc-claw/frontend
npm install
npm run build
npm start
# 访问 http://localhost:3000
```

### 方式二：OpenClaw 自动配置

向 OpenClaw 发送消息：

```
帮我克隆git仓库：https://github.com/HITsz-TMG/AIGC-Claw.git
然后把AIGC-Claw中的aigc-director文件夹递归复制到.openclaw/workspace/skills目录下，用作AIGC相关的skill
```

使用时建议指明 "使用 aigc-director"：

```
用aigc-director来生成一个视频，内容是"一条狗的使命"
```

### 方式三：通过 ClawHub 安装

请确保本地安装了clawhub-cli

打开终端，输入命令，所有询问均选择yes

```bash
clawhub install aigc-director
```

安装完成后，ClawHub 会将 `aigc-director` 复制到 `workspace/skills`（或指定的 skills 目录）。

之后可以参考方式一手动安装自行构建项目并运行，也可以使用OpenClaw完成后续项目构建。

在第一次使用 `aigc-director` 时，如果没有手动构建项目，OpenClaw会自动构建前后端并运行，无需手动初始化（构建项目需要配置环境和编译，请耐心等待）。


---

## 🔧 配置说明

<details>
<summary><b>点击展开完整环境要求和变量</b></summary>

### 环境要求

- **Python**: 3.9+
- **Node.js**: 18+
- **npm**: 9+

### 后端环境变量

在 `aigc-claw/backend/.env` 中配置：

```bash
# LLM 配置
LLM_MODEL=qwen3.5-plus
VLM_MODEL=qwen-vl-plus

# 图像生成
IMAGE_T2I_MODEL=doubao-seedream-5-0-260128
IMAGE_IT2I_MODEL=doubao-seedream-5-0-260128

# 视频生成
VIDEO_MODEL=wan2.6-i2v-flash
VIDEO_RATIO=16:9

# API Keys
DASHSCOPE_API_KEY=your_key
ARK_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
```

### 可用模型

| 类型 | 模型 |
|:---:|:---|
| **LLM** | qwen3.5-plus, deepseek-chat, gpt-4o, gemini-2.5-flash |
| **VLM** | qwen-vl-plus, gemini-2.5-flash-image |
| **文生图** | doubao-seedream-5-0, jimeng_t2i_v40, wan2.6-t2i |
| **图生图** | doubao-seedream-5-0, jimeng_t2i_v40, wan2.6-image |
| **视频生成** | wan2.6-i2v-flash, kling-v3, jimeng_ti2v_v30_pro |

</details>


## 🙏 致谢

AIGC-Claw 的想法和设计受到了 [AutoResearchClaw](https://github.com/aiming-lab/AutoResearchClaw)、[huobao-drama](https://github.com/chatfire-AI/huobao-drama)、[LibTV](https://www.liblib.tv/) 与 [libtv-skills](https://github.com/libtv-labs/libtv-skills) 的启发。



## 📚 系列工作

| 框架图 | 论文信息 |
|:---:|---|
| <img src="https://github.com/HITsz-TMG/FilmAgent/blob/main/pics/framework.png?raw=true" width="420" alt="FilmAgent framework"/> | **[SIGGRAPH Asia 2024] FilmAgent: Automating Virtual Film Production Through a Multi-Agent Collaborative Framework**<br>*Zhenran Xu, Jifang Wang, Longyue Wang, Zhouyi Li, Senbao Shi, Baotian Hu, Min Zhang*<br>[[Paper](https://doi.org/10.1145/3681758.3698014)] [[GitHub](https://github.com/HITsz-TMG/AIGC-Claw/blob/main/FilmAgent.md)] |
| <img src="https://github.com/HITsz-TMG/Anim-Director/blob/main/Anim-Director/assets/visualeg.png" width="420" alt="Anim-Director result"/> | **[SIGGRAPH Asia 2024] Anim-Director: A Large Multimodal Model Powered Agent for Controllable Animation Video Generation**<br>*Yunxin Li, Haoyuan Shi, Baotian Hu, Longyue Wang, Jiashun Zhu, Jinyi Xu, Zhen Zhao, Min Zhang*<br>[[Paper](https://doi.org/10.1145/3680528.3687688)] [[GitHub](https://github.com/HITsz-TMG/Anim-Director/tree/main/Anim-Director)] |
| <img src="https://raw.githubusercontent.com/HITsz-TMG/Anim-Director/main/AniMaker/assets/pipeline.png" width="420" alt="AniMaker pipeline"/> | **[SIGGRAPH Asia 2025] AniMaker: Multi-Agent Animated Storytelling with MCTS-Driven Clip Generation**<br>*Haoyuan Shi, Yunxin Li, Xinyu Chen, Longyue Wang, Baotian Hu, Min Zhang*<br>[[Paper](https://doi.org/10.1145/3757377.3764009)] [[GitHub](https://github.com/HITsz-TMG/Anim-Director/tree/main/AniMaker)] |


<p align="center">
  <sub>Built with 🦞 by the HITsz-TMG team</sub>
</p>
