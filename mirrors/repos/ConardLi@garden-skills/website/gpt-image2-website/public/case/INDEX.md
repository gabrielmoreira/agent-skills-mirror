# GPT Image 2 提示词案例库 · 总目录索引

本目录是为 `gpt-image-2` Skill 编写的**典型提示词案例库**：每个 `references/` 下的模板都对应 `prompts/<category>/<template-name>/` 下的一个目录，目录里给出 1–3 条可直接交给图像模型出图的真实提示词案例（每条一个独立 JSON 文件）。

**说明：** 本目录不是模板本身，而是模板的「已填好参数、可直接复用」版本，可作为：

- 文章配图素材（每条提示词 → 一张文章配图）
- 模板效果对照（用于评估与回归）
- 团队内部 prompt benchmark

索引底部还附带机器可读的 [`_mapping.json`](./_mapping.json)，记录「模板 ↔ JSON 文件」的完整映射，可被脚本直接消费。

---

## 总览

| 分类 | 模板数 | 案例数 | 图片进度 |
|---|---|---|---|
| ui-mockups | 5 | 13 | ✅ 13 / 13 |
| product-visuals | 5 | 10 | ✅ 10 / 10 |
| maps | 4 | 8 | ✅ 8 / 8 |
| slides-and-visual-docs | 4 | 8 | ✅ 8 / 8 |
| poster-and-campaigns | 4 | 8 | ✅ 8 / 8 |
| portraits-and-characters | 4 | 8 | ✅ 8 / 8 |
| scenes-and-illustrations | 4 | 8 | ✅ 8 / 8 |
| editing-workflows | 5 | 10 | ✅ 10 / 10 |
| avatars-and-profile | 5 | 10 | ✅ 10 / 10 |
| storyboards-and-sequences | 5 | 10 | ✅ 10 / 10 |
| grids-and-collages | 4 | 8 | ✅ 8 / 8 |
| branding-and-packaging | 4 | 8 | ✅ 8 / 8 |
| typography-and-text-layout | 2 | 4 | ✅ 4 / 4 |
| assets-and-props | 2 | 4 | ✅ 4 / 4 |
| academic-figures | 9 | 18 | ✅ 18 / 18 |
| infographics | 6 | 12 | ✅ 12 / 12 |
| technical-diagrams | 7 | 14 | ✅ 14 / 14 |
| **合计** | **79** | **161** | **✅ 161 / 161** |

模板根目录：`<skill>/references/`  
提示词根目录：`prompts/`  
图片根目录：`prompts/`（与提示词文件同目录、同名，仅扩展名为 `.png`）

---

## 1. UI Mockups（界面样机）

各种「界面 + 内容」的样机视觉。

### 1.1 电商直播 / 社交直播 UI 样机

- **模板简介**：电商 / 社交直播带货截图样机（主播 + 聊天区 + 礼物区 + 商品卡）。
- **模板路径**：[`references/ui-mockups/live-commerce-ui.md`](../references/ui-mockups/live-commerce-ui.md)
- **提示词目录**：[`prompts/ui-mockups/live-commerce-ui/`](./ui-mockups/live-commerce-ui/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./ui-mockups/live-commerce-ui/1.json) | [`1.png`](./ui-mockups/live-commerce-ui/1.png) | Elon Musk 直播带 Cybertruck（科技带货旗舰场景） | 典型的"科技公司创始人本人下场带货"场景，主播是 Elon Musk，商品是 Tesla Cybertruck，整体氛围既像真实直播截图，又有发布会主视觉的高级感。是该模板最具代表性的旗舰用例。 |
  | 2 | [`2.json`](./ui-mockups/live-commerce-ui/2.json) | [`2.png`](./ui-mockups/live-commerce-ui/2.png) | Taylor Swift 直播开箱限定香水（明星个人 IP 带货） | 明星个人 IP 跨界美妆带货的典型场景。商品紧扣明星人设、聊天与礼物文案围绕粉丝向语言展开，是该模板"明星 + 美妆 / 文创"方向的代表用例。 |

### 1.2 社交平台界面样机

- **模板简介**：社交平台动态详情页样机（Twitter/X、小红书、微博、Threads 等）。
- **模板路径**：[`references/ui-mockups/social-interface-mockup.md`](../references/ui-mockups/social-interface-mockup.md)
- **提示词目录**：[`prompts/ui-mockups/social-interface-mockup/`](./ui-mockups/social-interface-mockup/)
- **图片进度**：✅ 3 / 3
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./ui-mockups/social-interface-mockup/1.json) | [`1.png`](./ui-mockups/social-interface-mockup/1.png) | Elon Musk 在 X 上发火星殖民推文（Twitter / X 暗色模式） | 典型的"知名科技人物在 X 上发布一条带配图的高互动推文"场景，深色模式 + 中文界面 + 多图九宫格，是该模板最具传播力的代表案例。 |
  | 2 | [`2.json`](./ui-mockups/social-interface-mockup/2.json) | [`2.png`](./ui-mockups/social-interface-mockup/2.png) | 小红书风格上海 City Walk 笔记（浅色模式） | 典型小红书图文笔记详情页，亲切、生活化、带 4 张可滑动配图。是该模板"内容创作者 + 生活方式"方向的代表案例。 |
  | 3 | [`3.json`](./ui-mockups/social-interface-mockup/3.json) | [`3.png`](./ui-mockups/social-interface-mockup/3.png) | Anthropic 官方账号在 X 上发布 Claude Opus 4.7（品牌官方公告） | 科技品牌账号在 X 上发布产品更新公告的典型场景，浅色模式 + 高互动量级 + 单图发布主视觉，是该模板"品牌官方账号"方向的代表案例。 |

### 1.3 商品卡叠加样机

- **模板简介**：落地页 hero / 详情页主图（人物 + 商品 + 卖点 + 价格）。
- **模板路径**：[`references/ui-mockups/product-card-overlay.md`](../references/ui-mockups/product-card-overlay.md)
- **提示词目录**：[`prompts/ui-mockups/product-card-overlay/`](./ui-mockups/product-card-overlay/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./ui-mockups/product-card-overlay/1.json) | [`1.png`](./ui-mockups/product-card-overlay/1.png) | DERMA CALM 敏感肌精华 — 临床感落地页 hero（女性向护肤） | 典型的"敏感肌护肤品牌"电商详情页主视觉，三栏结构 + 临床感配色 + 模特 + 产品 + 卖点徽章，是该模板最具代表性的女性向护肤用例。 |
  | 2 | [`2.json`](./ui-mockups/product-card-overlay/2.json) | [`2.png`](./ui-mockups/product-card-overlay/2.png) | NEX SKIN 男士护肤暗色科技款落地页（男性向数码感） | 男士护肤品牌的暗色科技感 hero 主视觉，硬朗、专业、可信赖，底部带销量条。是该模板"男性向 / 数码感"方向的代表用例。 |

### 1.4 聊天界面 / 对话气泡场景

- **模板简介**：聊天 / 对话界面样机（微信、AI 助手、群聊）。
- **模板路径**：[`references/ui-mockups/chat-interface-scene.md`](../references/ui-mockups/chat-interface-scene.md)
- **提示词目录**：[`prompts/ui-mockups/chat-interface-scene/`](./ui-mockups/chat-interface-scene/)
- **图片进度**：✅ 3 / 3
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./ui-mockups/chat-interface-scene/1.json) | [`1.png`](./ui-mockups/chat-interface-scene/1.png) | 微信双人聊天 — Elon Musk × Mark Zuckerberg "八角笼约架"对话 | 复刻 2023 年硅谷顶流梗——Elon 提出和 Zuck 在八角笼里 cage match，Zuck 回复 "send location"。这里把它搬到中文微信场景：Elon Musk 用中英混合发挑衅，Zuck 一本正经技术宅式接招，包含文字、语音条、Cybertruck 自拍、定位卡片、表情包等典型微信元素。… |
  | 2 | [`2.json`](./ui-mockups/chat-interface-scene/2.json) | [`2.png`](./ui-mockups/chat-interface-scene/2.png) | 硅谷 CEO 微信群聊 — 「Tech CEO 互助会 (8)」深夜吐槽现场 | 把"产品组日常"升级成顶配名人群聊——Tim Cook、Sundar Pichai、Sam Altman、Jensen Huang、Mark Zuckerberg、Satya Nadella、Jeff Bezos 都在群里，本机视角是 Elon Musk。内容是周五深夜大家互相吐槽：GPU 不够用、Vision P… |
  | 3 | [`3.json`](./ui-mockups/chat-interface-scene/3.json) | [`3.png`](./ui-mockups/chat-interface-scene/3.png) | Claude Opus 4.7 AI 助手对话 — 帮 Elon Musk 整理"硅谷 CEO 群"周报 | 典型的 AI 助手桌面产品截图，用户视角是 Elon Musk，把案例 2 的群聊上下文丢给 Claude，让它帮整理成"硅谷 drama 周报"。包含用户提问、Claude 结构化回答、再次追问让 Claude 改写成 Twitter / X 推文。是该模板"AI 产品演示 + 名人使用场景"方向的代表案例。 |

### 1.5 短视频封面 / Stream 缩略图 UI

- **模板简介**：短视频封面 / 直播缩略图（YouTube、抖音、B 站、VTuber stream）。
- **模板路径**：[`references/ui-mockups/short-video-cover-ui.md`](../references/ui-mockups/short-video-cover-ui.md)
- **提示词目录**：[`prompts/ui-mockups/short-video-cover-ui/`](./ui-mockups/short-video-cover-ui/)
- **图片进度**：✅ 3 / 3
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./ui-mockups/short-video-cover-ui/1.json) | [`1.png`](./ui-mockups/short-video-cover-ui/1.png) | 知识科普封面 — 「99% 的人都不知道的 Claude 用法」（高对比醒目风） | 典型的"知识科普 / 工具教程"短视频封面，深色渐变 + 高亮黄标题 + 主体人物 + 三条要点，是该模板最具代表性的"高点击率知识号"用例。 |
  | 2 | [`2.json`](./ui-mockups/short-video-cover-ui/2.json) | [`2.png`](./ui-mockups/short-video-cover-ui/2.png) | 可爱风 VTuber 直播预告封面 — 「樱粉杂谈直播」 | 典型的女性 VTuber 直播开播预告封面，粉色主调 + 卡通主播 + 多层文字丝带，是该模板"VTuber / 主播预告"方向的代表案例。 |
  | 3 | [`3.json`](./ui-mockups/short-video-cover-ui/3.json) | [`3.png`](./ui-mockups/short-video-cover-ui/3.png) | 开箱评测封面 — 「我把 Vision Pro 2 拆了」（强诱因） | 典型的 YouTube 数码博主开箱评测视频封面，主体半身 + 神秘包装盒 + 强好奇感标题。是该模板"开箱评测"方向的代表案例。 |

---

## 2. Product Visuals（产品视觉）

以商品为视觉中心的图。

### 2.1 产品爆炸视图海报

- **模板简介**：产品爆炸视图海报（主体垂直堆叠 + callout + 顶部 logo + 底部品牌区）。
- **模板路径**：[`references/product-visuals/exploded-view-poster.md`](../references/product-visuals/exploded-view-poster.md)
- **提示词目录**：[`prompts/product-visuals/exploded-view-poster/`](./product-visuals/exploded-view-poster/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./product-visuals/exploded-view-poster/1.json) | [`1.png`](./product-visuals/exploded-view-poster/1.png) | Tesla Cybertruck 工程结构爆炸主视觉 | 电动皮卡品类里最具辨识度的不锈钢蒙皮与线控架构，适合作为「硬核工程 + 发布会主视觉」的代表；九层垂直展开、左右双语式技术标注，突出结构进化与品牌叙事。 |
  | 2 | [`2.json`](./product-visuals/exploded-view-poster/2.json) | [`2.png`](./product-visuals/exploded-view-poster/2.png) | Apple Vision Pro 2 头显光机与算力模块爆炸主视觉 | 空间计算品类的代表形态；Pancake 光路、眼动与透视传感器、M 系列系留算力等分层，适合作为「近眼显示 + 工程拆解」主视觉，与深紫极光背景形成科技仪式感。 |

### 2.2 白底产品图

- **模板简介**：电商纯白底主图（单品 / 多角度 / 极简营销叠层）。
- **模板路径**：[`references/product-visuals/white-background-product.md`](../references/product-visuals/white-background-product.md)
- **提示词目录**：[`prompts/product-visuals/white-background-product/`](./product-visuals/white-background-product/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./product-visuals/white-background-product/1.json) | [`1.png`](./product-visuals/white-background-product/1.png) | AirPods Pro 3 单品白底主图（数码耳机典型） | TWS 降噪耳机类目里最常见的上架主图需求：充电盒与耳机本体的材质、合模线、闪电口与耳塞细节需清晰可辨，白底无道具，适合作为 Apple 系配件店与平台首图规范参考。 |
  | 2 | [`2.json`](./product-visuals/white-background-product/2.json) | [`2.png`](./product-visuals/white-background-product/2.png) | Dyson Supersonic Nural 吹风机白底主图（小家电典型） | 高端小家电常需「科技灰 + 金属环 + 进风口细节」在同一张白底里交代清楚；本案例强调主机 + 磁吸风嘴组合，适合品牌旗舰店与京东家电首图。 |

### 2.3 高级影棚商业产品图

- **模板简介**：高级影棚商业产品图（杂志广告级氛围）。
- **模板路径**：[`references/product-visuals/premium-studio-product.md`](../references/product-visuals/premium-studio-product.md)
- **提示词目录**：[`prompts/product-visuals/premium-studio-product/`](./product-visuals/premium-studio-product/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./product-visuals/premium-studio-product/1.json) | [`1.png`](./product-visuals/premium-studio-product/1.png) | 海蓝之谜（La Mer）经典面霜单页主视觉 | 高端护肤面霜品类里最具符号性的瓷瓶、薄荷绿与烫银字，配合丝绒与暗角暖光，呈现「可上杂志跨页」的 luxury still life，强调质地叙事而非白底平铺。 |
  | 2 | [`2.json`](./product-visuals/premium-studio-product/2.json) | [`2.png`](./product-visuals/premium-studio-product/2.png) | Rolex 星期日历型 40 暗调金表影棚主视觉 | 奢侈品腕表在暗调高反差下的金壳、总统链与表盘细节，是「影棚 + 无 lifestyle」的教科书级用例；适合官网 hero、平面投放与经销商灯箱。 |

### 2.4 礼盒 / 包装展示图

- **模板简介**：礼盒 / 包装展示图（外盒 + 内容物展示）。
- **模板路径**：[`references/product-visuals/packaging-showcase.md`](../references/product-visuals/packaging-showcase.md)
- **提示词目录**：[`prompts/product-visuals/packaging-showcase/`](./product-visuals/packaging-showcase/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./product-visuals/packaging-showcase/1.json) | [`1.png`](./product-visuals/packaging-showcase/1.png) | iPhone 16 Pro 首发套装式包装展示 | 数码旗舰常见「黑底白字 + 撕膜体验」的礼盒叙事；本案例以深空黑硬盒、开盖泡棉位与主机、线缆、说明卡同屏呈现，适合电商首屏与开箱活动主视觉。 |
  | 2 | [`2.json`](./product-visuals/packaging-showcase/2.json) | [`2.png`](./product-visuals/packaging-showcase/2.png) | 星巴克中国「冬悦」节日礼盒 | 食品零售节日档典型「中国红 + 咖啡绿 + 烫金」组合；本案例为双杯装咖啡豆 + 马克杯 + 星礼卡，适合门店橱窗与礼赠电商页。 |

### 2.5 生活方式产品场景图

- **模板简介**：生活方式产品场景图（商品出现在真实场景中）。
- **模板路径**：[`references/product-visuals/lifestyle-product-scene.md`](../references/product-visuals/lifestyle-product-scene.md)
- **提示词目录**：[`prompts/product-visuals/lifestyle-product-scene/`](./product-visuals/lifestyle-product-scene/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./product-visuals/lifestyle-product-scene/1.json) | [`1.png`](./product-visuals/lifestyle-product-scene/1.png) | 便携意式机与露营木桌（户外咖啡季） | 户外生活电器典型用法：晨间湖边营地、手冲级仪式感但设备为电动便携机；无具体名人入画，以器具与光营造「可上小红书封面」的克制杂志感。 |
  | 2 | [`2.json`](./product-visuals/lifestyle-product-scene/2.json) | [`2.png`](./product-visuals/lifestyle-product-scene/2.png) | Apple Watch Ultra 2 与晨跑（LeBron James 运动背影） | 运动穿戴典型「跑道 + 腕部特写可联想」的构图：以 LeBron James 晨跑中的背影与抬腕看表动作为主叙事，表盘朝读者，品牌可读，无正脸，符合运动社交传播习惯。 |

---

## 3. Maps（地图）

信息密度较高的「地图风」图像。

### 3.1 城市美食手绘地图

- **模板简介**：城市美食手绘地图（编号点位 + 图例 + 中心吉祥物）。
- **模板路径**：[`references/maps/food-map.md`](../references/maps/food-map.md)
- **提示词目录**：[`prompts/maps/food-map/`](./maps/food-map/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./maps/food-map/1.json) | [`1.png`](./maps/food-map/1.png) | 上海武康路·梧桐区周末探吃地图 | 法租界街区尺度小、店密、网感强，适合作为「单街区美食地图片」的标杆：地标与轻食/咖啡/烘焙组合，配梧桐叶与武康大楼剪影，主标题突出 City Walk + 好味。 |
  | 2 | [`2.json`](./maps/food-map/2.json) | [`2.png`](./maps/food-map/2.png) | 东京新宿·深夜拉面与居酒屋巷地图 | 高密度夜间餐饮街区：以歌舞伎町与东口拉面横丁为精神原型，用「蒸汽、红灯笼、丼、拉面、烧鸟」为符号，配日式复古羊皮纸，适合日料自媒体与赴日攻略封面。 |

### 3.2 旅行路线图

- **模板简介**：旅行路线图（多日行程 / 单日 city walk / 户外路线）。
- **模板路径**：[`references/maps/travel-route-map.md`](../references/maps/travel-route-map.md)
- **提示词目录**：[`prompts/maps/travel-route-map/`](./maps/travel-route-map/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./maps/travel-route-map/1.json) | [`1.png`](./maps/travel-route-map/1.png) | 京都三日古典慢走（机铁 + 步行为主） | 关西最经典的「少城市跳点、多点寺庙庭园与町家」的三天节奏；东西向动线不回头，适合作为旅行路线图模板的代表：手绘羊皮纸、站点小插画、侧栏条列。 |
  | 2 | [`2.json`](./maps/travel-route-map/2.json) | [`2.png`](./maps/travel-route-map/2.png) | 美国 66 号公路七日西部段（公路片气质） | 长距离自驾线模板代表：以芝加哥方向感为起点、洛杉矶方向感为收束的「中段西部七日」选段，强调路边小镇、汽旅文化与国家公园节点，用沙漠色与路牌符号强化识别。 |

### 3.3 城市风貌插画地图

- **模板简介**：城市风貌插画地图（地标 + 江山 + 文化元素）。
- **模板路径**：[`references/maps/illustrated-city-map.md`](../references/maps/illustrated-city-map.md)
- **提示词目录**：[`prompts/maps/illustrated-city-map/`](./maps/illustrated-city-map/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./maps/illustrated-city-map/1.json) | [`1.png`](./maps/illustrated-city-map/1.png) | 北京中轴线·从永定门到钟鼓楼 | 以世界遗产中轴线为叙事主轴，突出故宫、天坛、钟鼓楼与景山万春亭的南北对位，国潮与 watercolor 可并存；是「单城文化推广主视觉」的典型命题。 |
  | 2 | [`2.json`](./maps/illustrated-city-map/2.json) | [`2.png`](./maps/illustrated-city-map/2.png) | 成都·巷陌与烟火市井文化地图 | 突出「无轴线城市」的向心平原与河网：以锦江为柔曲线骨架，宽窄巷子、望平街、青羊宫与东郊记忆为节点，配熊猫与茶碗符号，是西南休闲城市主视觉的常用结构。 |

### 3.4 品牌门店分布图

- **模板简介**：品牌门店 / 服务覆盖分布图。
- **模板路径**：[`references/maps/store-distribution-map.md`](../references/maps/store-distribution-map.md)
- **提示词目录**：[`prompts/maps/store-distribution-map/`](./maps/store-distribution-map/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./maps/store-distribution-map/1.json) | [`1.png`](./maps/store-distribution-map/1.png) | Starbucks 星巴克中国门店网络（扁平招商风） | 全国性连锁咖啡品牌典型「沿海与省会密度高、西部阶梯递减」的分布节奏；用reserve 与普通门店分层级，色板为品牌绿，适合官网「关于我们」与加盟说明页头图（示意为主）。 |
  | 2 | [`2.json`](./maps/store-distribution-map/2.json) | [`2.png`](./maps/store-distribution-map/2.png) | 海底捞全球服务网络与旗舰店锚点 | 中餐连锁出海的代表：以中国大陆为核心、向东亚东南亚欧美扩散；适合「全球火锅」主叙事，强调密度差与旗舰店城市，红底与火锅图形符号为品牌资产。 |

---

## 4. Slides & Visual Docs（视觉文档）

幻灯片 / 视觉报告 / 政务可视风格。

### 4.1 高密度讲解 Slide

- **模板简介**：Irasutoya × 霞关混合高密度讲解 Slide。
- **模板路径**：[`references/slides-and-visual-docs/dense-explainer-slides.md`](../references/slides-and-visual-docs/dense-explainer-slides.md)
- **提示词目录**：[`prompts/slides-and-visual-docs/dense-explainer-slides/`](./slides-and-visual-docs/dense-explainer-slides/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./slides-and-visual-docs/dense-explainer-slides/1.json) | [`1.png`](./slides-and-visual-docs/dense-explainer-slides/1.png) | 如何看懂一份大模型评测报告（公开课单页） | 面向产品与技术读者的「测评 literacy」一页通：从榜单到指标拆解，用温馨插画＋分块信息，适合培训开场或公众号长图首屏。是该模板在「技术科普 × 高信息密度」方向的代表用例。 |
  | 2 | [`2.json`](./slides-and-visual-docs/dense-explainer-slides/2.json) | [`2.png`](./slides-and-visual-docs/dense-explainer-slides/2.png) | AI Agent 工作机制（分步与组件一页通） | 用同一套版式把「感知—规划—行动—工具—记忆」串成可讲课的一页，适合企业内训与工程师向分享，突出流程而非口号。 |

### 4.2 政策风格 Slide

- **模板简介**：政策 / 政府公告 / 白皮书风格说明 Slide。
- **模板路径**：[`references/slides-and-visual-docs/policy-style-slide.md`](../references/slides-and-visual-docs/policy-style-slide.md)
- **提示词目录**：[`prompts/slides-and-visual-docs/policy-style-slide/`](./slides-and-visual-docs/policy-style-slide/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./slides-and-visual-docs/policy-style-slide/1.json) | [`1.png`](./slides-and-visual-docs/policy-style-slide/1.png) | 关于促进人工智能产业高质量发展的若干措施（政策解读单页） | 典型的产业促进类政策一页通：机构抬头、分块要点、数据高亮与底部溯源区齐全，主色政蓝，适合白皮书摘要图或内参封面拉页。 |
  | 2 | [`2.json`](./slides-and-visual-docs/policy-style-slide/2.json) | [`2.png`](./slides-and-visual-docs/policy-style-slide/2.png) | 某控股年度战略报告「封面拉页式」单页 | 用政策风的秩序感承载企业内部战略摘要：对高管汇报与内刊封面通用，主色政红增强「年初定调」感，突出里程碑数字。 |

### 4.3 视觉报告页

- **模板简介**：商业报告执行摘要 / 投资人简报 / 年报概览页。
- **模板路径**：[`references/slides-and-visual-docs/visual-report-page.md`](../references/slides-and-visual-docs/visual-report-page.md)
- **提示词目录**：[`prompts/slides-and-visual-docs/visual-report-page/`](./slides-and-visual-docs/visual-report-page/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./slides-and-visual-docs/visual-report-page/1.json) | [`1.png`](./slides-and-visual-docs/visual-report-page/1.png) | 苹果 2025 财年 Q4 业绩简报执行摘要 | 消费硬件与软服并重的典型单页：四格 KPI、营收趋势小图、一句核心判断，商业蓝主色，适合投研社群传播或内部战报头图。 |
  | 2 | [`2.json`](./slides-and-visual-docs/visual-report-page/2.json) | [`2.png`](./slides-and-visual-docs/visual-report-page/2.png) | Tesla 2025 全球交付与经营一页通 | 更偏汽车与能源业务的交付与平均售价结构叙事，黑银冷色强调制造感，适合产经报道配图或内部分享。 |

### 4.4 教学示意图 Slide

- **模板简介**：教学示意图（概念 / 机制 / 流程分解）。
- **模板路径**：[`references/slides-and-visual-docs/educational-diagram-slide.md`](../references/slides-and-visual-docs/educational-diagram-slide.md)
- **提示词目录**：[`prompts/slides-and-visual-docs/educational-diagram-slide/`](./slides-and-visual-docs/educational-diagram-slide/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./slides-and-visual-docs/educational-diagram-slide/1.json) | [`1.png`](./slides-and-visual-docs/educational-diagram-slide/1.png) | 光合作用如何运作（初高中衔接） | 经典理科示意：叶横剖＋六步从光到糖，温和学院配色，主图锚定、步骤编号清晰，是教科补页与公开课封面的高复用用例。 |
  | 2 | [`2.json`](./slides-and-visual-docs/educational-diagram-slide/2.json) | [`2.png`](./slides-and-visual-docs/educational-diagram-slide/2.png) | Transformer 自注意力一图说清（大学 / 内训向） | 用同一结构讲「QKV—softmax—加权和」的直觉，主图为序列与小矩阵示意，是工程师入职培训中视觉化大模型的标配一页。 |

---

## 5. Poster & Campaigns（海报与营销主视觉）

面向传播的视觉海报与主视觉。

### 5.1 品牌主海报

- **模板简介**：品牌主海报（产品 / 人物 / 纯文字主张）。
- **模板路径**：[`references/poster-and-campaigns/brand-poster.md`](../references/poster-and-campaigns/brand-poster.md)
- **提示词目录**：[`prompts/poster-and-campaigns/brand-poster/`](./poster-and-campaigns/brand-poster/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./poster-and-campaigns/brand-poster/1.json) | [`1.png`](./poster-and-campaigns/brand-poster/1.png) | Apple 精神传承 × Tim Cook（「再来一步」主视觉） | 在合法表述下用品牌气质词与人物肖像＋产品同框，主句短、色板与官网银灰系一致，适合发布会后社交首图或线下灯箱。 |
  | 2 | [`2.json`](./poster-and-campaigns/brand-poster/2.json) | [`2.png`](./poster-and-campaigns/brand-poster/2.png) | Nike 体育精神 × LeBron James（城市晨跑主视觉） | 用篮球巨星人像与一句中文主张完成「人的意志」主叙事，黑红经典对比，主视觉偏竖版、适合开屏与电梯海报。 |

### 5.2 Campaign Key Visual

- **模板简介**：Campaign Key Visual + 衍生 layout 系统。
- **模板路径**：[`references/poster-and-campaigns/campaign-kv.md`](../references/poster-and-campaigns/campaign-kv.md)
- **提示词目录**：[`prompts/poster-and-campaigns/campaign-kv/`](./poster-and-campaigns/campaign-kv/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./poster-and-campaigns/campaign-kv/1.json) | [`1.png`](./poster-and-campaigns/campaign-kv/1.png) | 可口可乐夏季畅爽季（全渠道 KV 系统图） | 红与白为主、单 anchor 大玻璃瓶装视觉，claim 在中文夏促语境，下方 1:1、9:16、16:9 三格线框小稿展示同一系統延展。 |
  | 2 | [`2.json`](./poster-and-campaigns/campaign-kv/2.json) | [`2.png`](./poster-and-campaigns/campaign-kv/2.png) | Apple Vision 空间计算续章（产品季 KV） | 以「二代头戴」为 anchor 的发布季主视觉，冷银＋空灵的界面雾气，主 claim 双行，下方三比例展陈同一材质语言。 |

### 5.3 Web Hero / Banner

- **模板简介**：Web hero / 落地页 / app banner（横向构图 + CTA）。
- **模板路径**：[`references/poster-and-campaigns/banner-hero.md`](../references/poster-and-campaigns/banner-hero.md)
- **提示词目录**：[`prompts/poster-and-campaigns/banner-hero/`](./poster-and-campaigns/banner-hero/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./poster-and-campaigns/banner-hero/1.json) | [`1.png`](./poster-and-campaigns/banner-hero/1.png) | Notion 式「一块白板装下团队记忆」（浅色 Hero） | 典型 SaaS 首屏：左列标题副标题双 CTA，右列为「产品多区块界面」的 3D 轻透视，米灰渐变＋低噪，适合 B 站落地与官网首屏 A/B 测试素底。 |
  | 2 | [`2.json`](./poster-and-campaigns/banner-hero/2.json) | [`2.png`](./poster-and-campaigns/banner-hero/2.png) | Linear 式暗色工程效率 Hero（全宽横条） | 深色底＋高对比紫青点缀，主视觉为「问题列表＋Sprint 燃尽」抽象界面，强研发气质，适合作业流 / DevOps 品类落地页。 |

### 5.4 杂志 / 出版物封面

- **模板简介**：杂志 / 期刊 / 出版物封面。
- **模板路径**：[`references/poster-and-campaigns/editorial-cover.md`](../references/poster-and-campaigns/editorial-cover.md)
- **提示词目录**：[`prompts/poster-and-campaigns/editorial-cover/`](./poster-and-campaigns/editorial-cover/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./poster-and-campaigns/editorial-cover/1.json) | [`1.png`](./poster-and-campaigns/editorial-cover/1.png) | 《时代》式年度人物特辑 × Sam Altman | 高对比、红框记忆点、封面中央肖像与底部导读栏，主标题为中文专题名，期号用英文，整体像新闻周刊旗舰期。 |
  | 2 | [`2.json`](./poster-and-campaigns/editorial-cover/2.json) | [`2.png`](./poster-and-campaigns/editorial-cover/2.png) | 《Vogue 服饰与美容》中国版概念封面 × Taylor Swift | 时尚大刊的柔光时装肖像，主标题竖排，一侧竖栏英文刊名，整体暖金与米白，适合高奢与音乐跨界专题。 |

---

## 6. Portraits & Characters（人物视觉）

真实 / 虚拟人物的肖像与角色设定。

### 6.1 职业级商务肖像

- **模板简介**：职业级商务肖像（LinkedIn / 团队页 / 媒体配图）。
- **模板路径**：[`references/portraits-and-characters/professional-portrait.md`](../references/portraits-and-characters/professional-portrait.md)
- **提示词目录**：[`prompts/portraits-and-characters/professional-portrait/`](./portraits-and-characters/professional-portrait/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./portraits-and-characters/professional-portrait/1.json) | [`1.png`](./portraits-and-characters/professional-portrait/1.png) | Tim Cook 风格企业领袖胸像 | 科技制造业 CEO 气质：深海军蓝、银发、无夸张戏剧光，背板浅灰＋极弱环境交代，是「可上官网 About」级别的克制用法。 |
  | 2 | [`2.json`](./portraits-and-characters/professional-portrait/2.json) | [`2.png`](./portraits-and-characters/professional-portrait/2.png) | Sundar Pichai 风格全球科技业务负责人画像 | 偏技术决策者的暖灰背景、略休闲但仍有西装结构，适合作业软件品类或全球化团队首页。 |

### 6.2 创始人媒体大片肖像

- **模板简介**：创始人媒体大片肖像（戏剧灯光 + 留标题位）。
- **模板路径**：[`references/portraits-and-characters/founder-portrait.md`](../references/portraits-and-characters/founder-portrait.md)
- **提示词目录**：[`prompts/portraits-and-characters/founder-portrait/`](./portraits-and-characters/founder-portrait/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./portraits-and-characters/founder-portrait/1.json) | [`1.png`](./portraits-and-characters/founder-portrait/1.png) | Elon Musk 工业总部窗光半身影 | 科技制造跨界创始人：极简办公室＋大窗冷侧光、暗部有细节，右上预留标题安全区，整体偏冷、略颗粒。 |
  | 2 | [`2.json`](./portraits-and-characters/founder-portrait/2.json) | [`2.png`](./portraits-and-characters/founder-portrait/2.png) | Sam Altman 暖侧光＋书墙文献风 | 偏「思想型创始人」的柔和侧光＋书墙虚景，适合人物专访长文、播客主视觉，预留左侧竖排大引语位。 |

### 6.3 虚拟主播 / VTuber

- **模板简介**：VTuber / 虚拟主播个人卡 + 直播预览。
- **模板路径**：[`references/portraits-and-characters/virtual-host.md`](../references/portraits-and-characters/virtual-host.md)
- **提示词目录**：[`prompts/portraits-and-characters/virtual-host/`](./portraits-and-characters/virtual-host/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./portraits-and-characters/virtual-host/1.json) | [`1.png`](./portraits-and-characters/virtual-host/1.png) | 樱下川「初日」个人资料卡（9:16） | 春日系日系 anime 少女、和洋折衷服装，debut 信息与标签完整，是「新 V 首曝」高复用规格。 |
  | 2 | [`2.json`](./portraits-and-characters/virtual-host/2.json) | [`2.png`](./portraits-and-characters/virtual-host/2.png) | 铁犀「深潜」直播预告横封（16:9） | 男性机甲风味 VTuber、复古管线与做旧金属，大表情与主标题，适合 B 站与微信视频号直播预约封面双裁。 |

### 6.4 角色综合设定稿

- **模板简介**：角色综合设定稿（三视图 + 表情 + 服装 + 配色板）。
- **模板路径**：[`references/portraits-and-characters/character-sheet.md`](../references/portraits-and-characters/character-sheet.md)
- **提示词目录**：[`prompts/portraits-and-characters/character-sheet/`](./portraits-and-characters/character-sheet/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./portraits-and-characters/character-sheet/1.json) | [`1.png`](./portraits-and-characters/character-sheet/1.png) | 沈霜辞「墨羽」古风女剑客人设表 | 中国古典武侠女侠方向：高马尾、墨蓝与月白、软剑＋发簪，三视比例严锁，是古装战斗向 gacha 与动画常用的规格。 |
  | 2 | [`2.json`](./portraits-and-characters/character-sheet/2.json) | [`2.png`](./portraits-and-characters/character-sheet/2.png) | 阿瑟·克朗「雾都侦探」蒸汽朋克设定表 | 欧美维多利亚架空都市侦探：高帽、长风衣、机械左臂、齿轮放大镜，表情的「推理兴奋」与「被背叛」为剧情常用。 |

---

## 7. Scenes & Illustrations（氛围 / 故事 / 情绪插画）

氛围 / 故事 / 情绪导向的插画。

### 7.1 治愈系日常场景

- **模板简介**：治愈系日常 / 季节场景插画。
- **模板路径**：[`references/scenes-and-illustrations/healing-scene.md`](../references/scenes-and-illustrations/healing-scene.md)
- **提示词目录**：[`prompts/scenes-and-illustrations/healing-scene/`](./scenes-and-illustrations/healing-scene/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./scenes-and-illustrations/healing-scene/1.json) | [`1.png`](./scenes-and-illustrations/healing-scene/1.png) | 京都春日·町屋咖啡馆与 Taylor Swift 背影 | 以日本町屋木格窗、新绿与和纸灯光为底，美国知名艺人在靠窗高凳上看街景的柔和背影，猫或街景不抢戏；是「春樱季 × 旅拍情绪」的治愈系代表配置。 |
  | 2 | [`2.json`](./scenes-and-illustrations/healing-scene/2.json) | [`2.png`](./scenes-and-illustrations/healing-scene/2.png) | 北海道初雪·木造小屋与橘猫 | 以雪、暖灯与围炉意象构成「初雪天安心感」；无人物、仅动物，适合作为节气海报与夜间推文配图。 |

### 7.2 概念大场景 / IP key art

- **模板简介**：电影感概念大场景 / IP key art。
- **模板路径**：[`references/scenes-and-illustrations/concept-scene.md`](../references/scenes-and-illustrations/concept-scene.md)
- **提示词目录**：[`prompts/scenes-and-illustrations/concept-scene/`](./scenes-and-illustrations/concept-scene/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./scenes-and-illustrations/concept-scene/1.json) | [`1.png`](./scenes-and-illustrations/concept-scene/1.png) | 赛博朋克上海 2099·外滩雨夜 | 东方都会 × 高密霓虹的科幻母题；前景行人剪影、中景悬浮车道与江面航迹、远景陆家嘴超巨构与全息广告，色板为品红+电青+雨雾灰，是概念场景模板在「近未来东亚都市」向的代表题。 |
  | 2 | [`2.json`](./scenes-and-illustrations/concept-scene/2.json) | [`2.png`](./scenes-and-illustrations/concept-scene/2.png) | 火星黎明·穹顶外骨骼工人面向太阳 | 太空拓荒史诗向：近景渺小火星服剪影、中景矿车轨迹与制氧站管线、穹顶外高压橙雾与远地平线上刚升起的苍白太阳，是「非地球尺度」与「第一缕工业黎明」的命题。 |

### 7.3 童书 / 绘本内页

- **模板简介**：童书 / 绘本内页 / 节日卡片。
- **模板路径**：[`references/scenes-and-illustrations/picture-book-scene.md`](../references/scenes-and-illustrations/picture-book-scene.md)
- **提示词目录**：[`prompts/scenes-and-illustrations/picture-book-scene/`](./scenes-and-illustrations/picture-book-scene/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./scenes-and-illustrations/picture-book-scene/1.json) | [`1.png`](./scenes-and-illustrations/picture-book-scene/1.png) | 中秋夜·会飞的小狐狸与第一缕月华 | 中国传统节日 + 夜空中童话飞行物：小狐狸乘月饼形云舸掠过屋顶与河灯，画面保留一句可亲子朗读的旁白，暖橙、薄靛、米白为板。 |
  | 2 | [`2.json`](./scenes-and-illustrations/picture-book-scene/2.json) | [`2.png`](./scenes-and-illustrations/picture-book-scene/2.png) | 兔子先生的下午茶与迟到的怀表 | 经典童话感但不直接复制名著：高礼帽、三层层架点心与会冒气的茶壶，以「时间迟到一点点也没关系」的温柔教训为内核，适读年龄 3–6。 |

### 7.4 极简留白氛围图

- **模板简介**：极简留白氛围图 / 文学性壁纸。
- **模板路径**：[`references/scenes-and-illustrations/minimalist-mood-scene.md`](../references/scenes-and-illustrations/minimalist-mood-scene.md)
- **提示词目录**：[`prompts/scenes-and-illustrations/minimalist-mood-scene/`](./scenes-and-illustrations/minimalist-mood-scene/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./scenes-and-illustrations/minimalist-mood-scene/1.json) | [`1.png`](./scenes-and-illustrations/minimalist-mood-scene/1.png) | 雨夜东京·便利店氖光在积水里走散 | 都市孤独感与安全感并置：小主体为远角便利店门廊的窄条暖光，大面积冷雨灰留白，配一句中文旁白，适合作为深夜推文尾图与锁屏情绪壁纸。 |
  | 2 | [`2.json`](./scenes-and-illustrations/minimalist-mood-scene/2.json) | [`2.png`](./scenes-and-illustrations/minimalist-mood-scene/2.png) | 一个人的清晨咖啡·雾白与杯沿一线金 | 与雨夜对仗的「晨间独处」：偏左上的一只白杯与上升直线蒸汽，大面雾米白与一线暖金，适合清晨推送与产品无关的普适情绪品牌。 |

---

## 8. Editing Workflows（图像编辑工作流）

局部修改、替换、移除、修图等编辑型工作流。

### 8.1 背景替换

- **模板简介**：背景替换（商品 / 人像 / 户外 / 棚景）。
- **模板路径**：[`references/editing-workflows/background-replacement.md`](../references/editing-workflows/background-replacement.md)
- **提示词目录**：[`prompts/editing-workflows/background-replacement/`](./editing-workflows/background-replacement/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./editing-workflows/background-replacement/1.json) | [`1.png`](./editing-workflows/background-replacement/1.png) | LeBron James 户外半身照换纽约时代广场夜景 | 典型的人像从日间户外杂乱背景置换为标志性城市夜景，需统一冷暖对比与重新生成与霓虹灯方向一致的边缘光、地面反光，是体育明星肖像电商 / 社媒素材方向的代表任务。 |
  | 2 | [`2.json`](./editing-workflows/background-replacement/2.json) | [`2.png`](./editing-workflows/background-replacement/2.png) | 白底精拍 AirPods Pro 3 主图换日落沙滩 | 典型电商主图从影棚白底迁往生活方式场景，强调产品身份不变、新环境下阴影与亚克力充电盒反光的重算，是 3C 小电类目详情页最常用背景替换类需求。 |

### 8.2 局部对象替换

- **模板简介**：局部对象替换（配合或不配合蒙版）。
- **模板路径**：[`references/editing-workflows/local-object-replacement.md`](../references/editing-workflows/local-object-replacement.md)
- **提示词目录**：[`prompts/editing-workflows/local-object-replacement/`](./editing-workflows/local-object-replacement/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./editing-workflows/local-object-replacement/1.json) | [`1.png`](./editing-workflows/local-object-replacement/1.png) | Tesla Cybertruck 电单车展示图，车身从不锈钢银换为磨砂黑 | 典型车品 / 科技露出图中仅更换车漆材质与色而不改车型轮廓与场景透视，是局部对象替换里对高光与金属颗粒感重算要求最高的用例之一。 |
  | 2 | [`2.json`](./editing-workflows/local-object-replacement/2.json) | [`2.png`](./editing-workflows/local-object-replacement/2.png) | LeBron James 比赛上身照，球衣从湖人紫金换为迈阿密热火红黑 | 典型运动肖像中仅替换队服主色而保留队形、织纹与球员可识别性，对布料褶皱阴影与热印号码边缘的贴合度要求高，属于服饰类局部替换代表场景。 |

### 8.3 杂物 / 路人去除

- **模板简介**：杂物 / 路人 / 电线 / 瑕疵去除。
- **模板路径**：[`references/editing-workflows/object-removal.md`](../references/editing-workflows/object-removal.md)
- **提示词目录**：[`prompts/editing-workflows/object-removal/`](./editing-workflows/object-removal/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./editing-workflows/object-removal/1.json) | [`1.png`](./editing-workflows/object-removal/1.png) | 大学毕业典礼草坪合影，去除画面边缘误入路人 | 群体合影中保留主体排面完整、仅抹掉边缘干扰人物，是人物类杂物去除最典型、对「无接缝」要求极高的一类任务。 |
  | 2 | [`2.json`](./editing-workflows/object-removal/2.json) | [`2.png`](./editing-workflows/object-removal/2.png) | Oprah Winfrey 城市街拍，去除人行道旁电线杆与空中电线 | 单人人像街拍里竖线杆与横飞线对构图切割感强，去除后需同时修补天空与路面透视，是街景类杂物去除代表用例。 |

### 8.4 产品精修

- **模板简介**：产品精修（光泽 / 标签 / 阴影 / 瑕疵）。
- **模板路径**：[`references/editing-workflows/product-retouching.md`](../references/editing-workflows/product-retouching.md)
- **提示词目录**：[`prompts/editing-workflows/product-retouching/`](./editing-workflows/product-retouching/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./editing-workflows/product-retouching/1.json) | [`1.png`](./editing-workflows/product-retouching/1.png) | AirPods Pro 3 白底主图质感与标签锐化 | 小体积白色塑料与开盖结构在电商主图中易显灰雾与微痕，精修强调克制的光泽提升与合模线净化，是 3C 白底图最典型精修路径。 |
  | 2 | [`2.json`](./editing-workflows/product-retouching/2.json) | [`2.png`](./editing-workflows/product-retouching/2.png) | 香水瓶柱面与金属盖高光精修、液体通透感强化 | 玻璃、液体与金属三材质交界处易出现脏点、焦散断裂与标贴气泡感，是美妆香氛精修中「质感升级不整容」的标杆场景。 |

### 8.5 人像局部修改

- **模板简介**：人像局部修改（发型 / 服装 / 妆容 / 配饰）。
- **模板路径**：[`references/editing-workflows/portrait-local-edit.md`](../references/editing-workflows/portrait-local-edit.md)
- **提示词目录**：[`prompts/editing-workflows/portrait-local-edit/`](./editing-workflows/portrait-local-edit/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./editing-workflows/portrait-local-edit/1.json) | [`1.png`](./editing-workflows/portrait-local-edit/1.png) | Taylor Swift 头像级肖像，金长发变为深冷棕中卷 | 发色与卷度改变但保留面型与妆面结构，是发型 / 发色路径下最典型、也最易踩「换脸」边线的任务，需强约束灯向与发际线自然度。 |
  | 2 | [`2.json`](./editing-workflows/portrait-local-edit/2.json) | [`2.png`](./editing-workflows/portrait-local-edit/2.png) | Elon Musk 胸像，增加整齐短络腮胡与上唇髭，其余不变 | 须型为局部毛发增量编辑，在棚拍或发布会风格肖像中常用来测试「更成熟 / 更亲和」两档反馈，对下颌阴影重算与肤色一致性要求高。 |

---

## 9. Avatars & Profile（头像 / 人设 / 贴纸）

头像、人设、贴纸、3D 图标等个人化视觉。

### 9.1 风格化头像（Style Transfer Selfie）

- **模板简介**：把参考图人物转成 cosplay / 哥特 / 复古胶片 / 偶像写真等任意风格。
- **模板路径**：[`references/avatars-and-profile/style-transfer-selfie.md`](../references/avatars-and-profile/style-transfer-selfie.md)
- **提示词目录**：[`prompts/avatars-and-profile/style-transfer-selfie/`](./avatars-and-profile/style-transfer-selfie/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./avatars-and-profile/style-transfer-selfie/1.json) | [`1.png`](./avatars-and-profile/style-transfer-selfie/1.png) | 将 Stephen Curry 参考照转为雨夜赛博朋克城市场 | 高饱和霓虹、湿路面反射与机能风穿搭共同构成「次世代夜都市」标准审美，是风格转换中场景与光比变化幅度大、但身份锚点须钉死的人像任务。 |
  | 2 | [`2.json`](./avatars-and-profile/style-transfer-selfie/2.json) | [`2.png`](./avatars-and-profile/style-transfer-selfie/2.png) | 将 Beyoncé 参考照转为吉卜力工作室式手绘动画风 | 柔线轮廓、平涂肤色与层叠田园云隙光是吉卜力美术最具辨识度的组合，在名人肖像转换中需弱化 Hollywood 硬修容、转向手绘通透色阶。 |

### 9.2 角色网格肖像

- **模板简介**：同一角色 n×n 网格肖像（多职业 / 多表情 / 多朝代 / 多风格）。
- **模板路径**：[`references/avatars-and-profile/character-grid-portrait.md`](../references/avatars-and-profile/character-grid-portrait.md)
- **提示词目录**：[`prompts/avatars-and-profile/character-grid-portrait/`](./avatars-and-profile/character-grid-portrait/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./avatars-and-profile/character-grid-portrait/1.json) | [`1.png`](./avatars-and-profile/character-grid-portrait/1.png) | Taylor Swift 3×3 古今形象肖像网格（自汉至现代九格） | 同一可识别名人在时间轴上切换衣冠与场域，是角色网格中「单维变量（时代）多档位」的教科书式用法，对脸型一致与每格打光可区分的要求高。 |
  | 2 | [`2.json`](./avatars-and-profile/character-grid-portrait/2.json) | [`2.png`](./avatars-and-profile/character-grid-portrait/2.png) | Sam Altman 4×4 开发者人设与表情合辑 | 「同一公人物」在统一浅灰工位语境下以表情与微动作为主变量，是科技报道配图与社媒条漫常用的 4×4 规格。 |

### 9.3 主题 3D 图标式头像

- **模板简介**：Kawaii 3D / Minecraft / 拟物 3D 应用图标式头像。
- **模板路径**：[`references/avatars-and-profile/themed-3d-icon.md`](../references/avatars-and-profile/themed-3d-icon.md)
- **提示词目录**：[`prompts/avatars-and-profile/themed-3d-icon/`](./avatars-and-profile/themed-3d-icon/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./avatars-and-profile/themed-3d-icon/1.json) | [`1.png`](./avatars-and-profile/themed-3d-icon/1.png) | Mark Zuckerberg 元宇宙创作者主题的 Kawaii 3D 拟猫胸像 | 将公众人物的温和气质翻译为低威胁 Q 版动物拟人 + 轻科技符号，是主题 3D 头像里品牌人格化、又不落入写实像侵权的常见商业化落点。 |
  | 2 | [`2.json`](./avatars-and-profile/themed-3d-icon/2.json) | [`2.png`](./avatars-and-profile/themed-3d-icon/2.png) | Jensen Huang 为灵感的 Minecraft 体素 3D 皮套头像 | 名人标志性皮衣与发布会手势在降采样体素中仍可被联想，是主题 3D 与像素体素两风格交界处的轻量个人 IP 头像方案。 |

### 9.4 贴纸套装

- **模板简介**：贴纸套装 / 表情包合集（独立元素 + 描边 + 标签）。
- **模板路径**：[`references/avatars-and-profile/sticker-set.md`](../references/avatars-and-profile/sticker-set.md)
- **提示词目录**：[`prompts/avatars-and-profile/sticker-set/`](./avatars-and-profile/sticker-set/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./avatars-and-profile/sticker-set/1.json) | [`1.png`](./avatars-and-profile/sticker-set/1.png) | 微信场景 16 枚「打工人日常」Q 萌贴纸合图 | 4×4 排布、白描边、轻阴影、每格带两字或三字中文情绪标签，是国内 IM 表情包投放最常用商业规格之一。 |
  | 2 | [`2.json`](./avatars-and-profile/sticker-set/2.json) | [`2.png`](./avatars-and-profile/sticker-set/2.png) | Taylor Swift 梗图 9 枚 3×3 贴纸（简笔 Q 版） | 以明星 public 形象做漫化二创梗图时，强调「神似不写真」与统一线色，避免侵犯肖像的写实照片感；九格为专辑宣发 / 粉圈活动常见投放量。 |

### 9.5 文化 / 朝代肖像系列

- **模板简介**：朝代 / 神话 / 文学 / 民族系列肖像。
- **模板路径**：[`references/avatars-and-profile/cultural-portrait-series.md`](../references/avatars-and-profile/cultural-portrait-series.md)
- **提示词目录**：[`prompts/avatars-and-profile/cultural-portrait-series/`](./avatars-and-profile/cultural-portrait-series/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./avatars-and-profile/cultural-portrait-series/1.json) | [`1.png`](./avatars-and-profile/cultural-portrait-series/1.png) | 唐、宋、元、明、清五朝帝王胸像横五联 | 五联长图或横排 banner 在教育类公众号与博物馆数字展陈中常见，格量少于九格时每格面积更大、服饰考据更显眼。 |
  | 2 | [`2.json`](./avatars-and-profile/cultural-portrait-series/2.json) | [`2.png`](./avatars-and-profile/cultural-portrait-series/2.png) | 希腊神话十二主神胸像 4×3 格古典油画 | 奥林匹斯十二神为英语世界通识教育固定组合，古典油画厚涂 + 司职标签是海外慕课与桌游美术常采版式。 |

---

## 10. Storyboards & Sequences（叙事性序列）

多格漫画 / 关键画面 / 关系网等叙事性图。

### 10.1 4 格漫画

- **模板简介**：4 格漫画 / 讽刺漫画 / 段子漫画（起承转合 + 对话气泡）。
- **模板路径**：[`references/storyboards-and-sequences/four-panel-comic.md`](../references/storyboards-and-sequences/four-panel-comic.md)
- **提示词目录**：[`prompts/storyboards-and-sequences/four-panel-comic/`](./storyboards-and-sequences/four-panel-comic/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./storyboards-and-sequences/four-panel-comic/1.json) | [`1.png`](./storyboards-and-sequences/four-panel-comic/1.png) | 程序员与「合并不了」的周一 | 互联网打工人段子四格，主角是戴眼镜的年轻男程序员，从满怀信心到被现实打脸的反转节奏，对话短、可截屏发微信群。 |
  | 2 | [`2.json`](./storyboards-and-sequences/four-panel-comic/2.json) | [`2.png`](./storyboards-and-sequences/four-panel-comic/2.png) | 周一早会上的 Tim Cook 梗四格 | 用会议室场景做职场讽刺，主角造型偏美式卡通，梗落在「PPT 很满、结论很虚」，适合内部通讯或社媒长图裁切。 |

### 10.2 漫画跨页

- **模板简介**：单页 / 跨页漫画分镜（不规则格子 + 对话 + 心声）。
- **模板路径**：[`references/storyboards-and-sequences/manga-spread-page.md`](../references/storyboards-and-sequences/manga-spread-page.md)
- **提示词目录**：[`prompts/storyboards-and-sequences/manga-spread-page/`](./storyboards-and-sequences/manga-spread-page/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./storyboards-and-sequences/manga-spread-page/1.json) | [`1.png`](./storyboards-and-sequences/manga-spread-page/1.png) | 仙侠少年剑意初成（彩色跨页 8 格） | 国产仙侠战斗页，主角为束发青衫少年，对手为雾中妖影，大格起势、大格收刀，适合「连载漫画」内页或 PV 分镜展示。 |
  | 2 | [`2.json`](./storyboards-and-sequences/manga-spread-page/2.json) | [`2.png`](./storyboards-and-sequences/manga-spread-page/2.png) | 校园走廊误会-dialogue 6 格（黑白 + 网点） | 青春校园向，主角为短发女生，与楼梯转角男生擦肩而过引发一连串误会，适合「少女漫画单页」式叙事，强调表情特写与空镜。 |

### 10.3 动漫主视觉

- **模板简介**：单图动漫 KV / 轻小说封面 / IP 海报。
- **模板路径**：[`references/storyboards-and-sequences/anime-key-visual.md`](../references/storyboards-and-sequences/anime-key-visual.md)
- **提示词目录**：[`prompts/storyboards-and-sequences/anime-key-visual/`](./storyboards-and-sequences/anime-key-visual/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./storyboards-and-sequences/anime-key-visual/1.json) | [`1.png`](./storyboards-and-sequences/anime-key-visual/1.png) | 国产仙侠游《青麓行》首发 KV | 三人一兽的东方玄幻构图，青绿主色与金色天光，标题区置顶，适合横竖裁切，强调主角剑意与门派的史诗感。 |
  | 2 | [`2.json`](./storyboards-and-sequences/anime-key-visual/2.json) | [`2.png`](./storyboards-and-sequences/anime-key-visual/2.png) | 蒸汽朋克少女单角色强氛围 KV | 单主视觉+极强逆光与齿轮城市场景，赛博与维多利亚混搭，适合女性向新番或音游主宣。 |

### 10.4 角色关系图

- **模板简介**：角色关系图海报（卡片 + 关系连线 + 图例）。
- **模板路径**：[`references/storyboards-and-sequences/character-relationship-diagram.md`](../references/storyboards-and-sequences/character-relationship-diagram.md)
- **提示词目录**：[`prompts/storyboards-and-sequences/character-relationship-diagram/`](./storyboards-and-sequences/character-relationship-diagram/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./storyboards-and-sequences/character-relationship-diagram/1.json) | [`1.png`](./storyboards-and-sequences/character-relationship-diagram/1.png) | 《三体》核心人物关系图（9 人） | 以叶文洁、汪淼、史强、罗辑、章北海、程心、维德、智子拟人、云天明为节点，用颜色与线型区分敌友、技术联盟与执剑关系，适合科普与「入坑」长图。 |
  | 2 | [`2.json`](./storyboards-and-sequences/character-relationship-diagram/2.json) | [`2.png`](./storyboards-and-sequences/character-relationship-diagram/2.png) | 科技巨头「云端理事会」卡通组织架构图 | 以美国知名行业领袖为 Q 版头像节点，用汇报线、产品协作、公开竞争三种关系，做一张可对内分享的趣味组织图，非真实公司结构，仅供视觉创意。 |

### 10.5 食谱 / 流程步骤图

- **模板简介**：食谱 / 教程 / 流程步骤图（编号 + 插图 + 说明）。
- **模板路径**：[`references/storyboards-and-sequences/recipe-process-flowchart.md`](../references/storyboards-and-sequences/recipe-process-flowchart.md)
- **提示词目录**：[`prompts/storyboards-and-sequences/recipe-process-flowchart/`](./storyboards-and-sequences/recipe-process-flowchart/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./storyboards-and-sequences/recipe-process-flowchart/1.json) | [`1.png`](./storyboards-and-sequences/recipe-process-flowchart/1.png) | 番茄炒蛋 5 分钟家常版 | 5 步竖版食谱卡，食材区在右上，底部署成品，手绘水彩+米色纸感，色板与番茄/蛋一致。 |
  | 2 | [`2.json`](./storyboards-and-sequences/recipe-process-flowchart/2.json) | [`2.png`](./storyboards-and-sequences/recipe-process-flowchart/2.png) | 意式拿铁（家庭半自动）6 步流程 | 从磨豆到拉花简易心形的拿铁制作流程，偏扁平插画风，适合咖啡角菜单或教程海报。 |

---

## 11. Grids & Collages（多面板网格 / 拼贴）

Lookbook、Banner 网格、Pitch Board 等拼贴布局。

### 11.1 2×2 营销 Banner 套装

- **模板简介**：2×2 营销 banner 套装（一次出 4 张统一系列设计）。
- **模板路径**：[`references/grids-and-collages/banner-grid-2x2.md`](../references/grids-and-collages/banner-grid-2x2.md)
- **提示词目录**：[`prompts/grids-and-collages/banner-grid-2x2/`](./grids-and-collages/banner-grid-2x2/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./grids-and-collages/banner-grid-2x2/1.json) | [`1.png`](./grids-and-collages/banner-grid-2x2/1.png) | Apple Vision Pro 第二代·空间计算四象限 | 以「沉浸办公 / 协奏创作 / 空间健身 / 远程在场」为四格主题，统一苹果式留白与无衬线标题，每格 4:5 内区，可拆成四张社交投放。 |
  | 2 | [`2.json`](./grids-and-collages/banner-grid-2x2/2.json) | [`2.png`](./grids-and-collages/banner-grid-2x2/2.png) | 星巴克中国「四季特饮」2×2 | 春樱 / 夏冷萃 / 秋枫拿铁 / 冬焙茶四主题，同品牌色带与字系，每格一饮品 hero + 场景光，适朋友圈与小程序金刚位。 |

### 11.2 Lookbook 网格

- **模板简介**：7 日 lookbook / 9 宫 self-care / TOP N 清单图。
- **模板路径**：[`references/grids-and-collages/lookbook-grid.md`](../references/grids-and-collages/lookbook-grid.md)
- **提示词目录**：[`prompts/grids-and-collages/lookbook-grid/`](./grids-and-collages/lookbook-grid/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./grids-and-collages/lookbook-grid/1.json) | [`1.png`](./grids-and-collages/lookbook-grid/1.png) | Taylor Swift 时代巡演风「7 日穿搭」灵感板 | 以 Taylor Swift 公开造型语言为灵感的 7 套全身搭配，同一女性模特造型延续（风格化、非肖像写实），上四下三错位，适合音乐粉向穿搭账号。 |
  | 2 | [`2.json`](./grids-and-collages/lookbook-grid/2.json) | [`2.png`](./grids-and-collages/lookbook-grid/2.png) | 9 宫格 self-care 日常（治愈插画） | 3×3 无叙事清单，每格一图标+短句，柔粉与鼠尾草绿，可打印为打卡表或发社群。 |

### 11.3 多风格拼贴

- **模板简介**：多风格混合拼贴（同一主体不同画风演绎）。
- **模板路径**：[`references/grids-and-collages/mixed-style-multi-panel.md`](../references/grids-and-collages/mixed-style-multi-panel.md)
- **提示词目录**：[`prompts/grids-and-collages/mixed-style-multi-panel/`](./grids-and-collages/mixed-style-multi-panel/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./grids-and-collages/mixed-style-multi-panel/1.json) | [`1.png`](./grids-and-collages/mixed-style-multi-panel/1.png) | 同一中国女性五画风肖像（摄影 / 日漫 / 水墨 / 油画 / 赛博） | 28 岁齐肩黑发、米白衬衫为跨格识别锚；中央大格为影棚柔光摄影，四角依次为日式 anime、大写意水墨、伦勃朗式古典油画、赛博霓虹氛围，一图展示同一面容的媒介实验墙。 |
  | 2 | [`2.json`](./grids-and-collages/mixed-style-multi-panel/2.json) | [`2.png`](./grids-and-collages/mixed-style-multi-panel/2.png) | LeBron James 运动姿态「五连画风」墙贴 | 以篮球运动员突破上篮为统一点，中央大格为赛场摄影，四格为 anime、美漫厚涂、像素游戏、3D 卡通，适合体育自媒体头图。人物为可辨识公众人物，采用风格化、非商业代言写实。 |

### 11.4 二次元立项 Pitch Board

- **模板简介**：动漫 / 游戏 / 影视立项 pitch board（KV + 角色 + 世界观 + 文案）。
- **模板路径**：[`references/grids-and-collages/anime-pitch-board.md`](../references/grids-and-collages/anime-pitch-board.md)
- **提示词目录**：[`prompts/grids-and-collages/anime-pitch-board/`](./grids-and-collages/anime-pitch-board/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./grids-and-collages/anime-pitch-board/1.json) | [`1.png`](./grids-and-collages/anime-pitch-board/1.png) | 国产二次元 RPG《星枢编年史》立项板 | 近未来东方城邦 + 星轨神话，三人队伍 + 机甲与符箓混搭，KV 占上半 60%，左下三角色卡，右下地图与系统关键词，底部工作室落款。 |
  | 2 | [`2.json`](./grids-and-collages/anime-pitch-board/2.json) | [`2.png`](./grids-and-collages/anime-pitch-board/2.png) | 都市玄幻网络动画《江声异闻录》IP 板 | 当代重庆雾都与水下古城交织，主角为青年律师兼兼职「契印人」，主视觉为江面裂隙与楼群剪影，偏悬疑治愈调。 |

---

## 12. Branding & Packaging（品牌识别 / 包装设计）

品牌识别板、包装与吉祥物视觉。

### 12.1 品牌识别系统板

- **模板简介**：品牌识别系统板（logo + 配色 + 字体 + 应用 mockup）。
- **模板路径**：[`references/branding-and-packaging/brand-identity-board.md`](../references/branding-and-packaging/brand-identity-board.md)
- **提示词目录**：[`prompts/branding-and-packaging/brand-identity-board/`](./branding-and-packaging/brand-identity-board/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./branding-and-packaging/brand-identity-board/1.json) | [`1.png`](./branding-and-packaging/brand-identity-board/1.png) | 草本茶新中式品牌「清篱」 | 定位 25–40 岁注重养生的都市白领，标志为篱形叶片与茶汤涟漪几何化，主色松烟绿 + 米汤白，配名片、外带杯与线上海报 mockup。 |
  | 2 | [`2.json`](./branding-and-packaging/brand-identity-board/2.json) | [`2.png`](./branding-and-packaging/brand-identity-board/2.png) | 独立咖啡馆「砖缝光」 | 社区小馆定位，主色燧石黑与窑变橙，字标强调砖缝与光束负形，含杯套、门牌、小程序码卡片 mockup。 |

### 12.2 吉祥物品牌套装

- **模板简介**：吉祥物多面板品牌识别套装（主形象 + 三视图 + 表情 + 应用）。
- **模板路径**：[`references/branding-and-packaging/mascot-brand-kit.md`](../references/branding-and-packaging/mascot-brand-kit.md)
- **提示词目录**：[`prompts/branding-and-packaging/mascot-brand-kit/`](./branding-and-packaging/mascot-brand-kit/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./branding-and-packaging/mascot-brand-kit/1.json) | [`1.png`](./branding-and-packaging/mascot-brand-kit/1.png) | 故宫建筑精灵「小脊兽蹲蹲」 | 以太和殿脊兽为灵感的 Q 版黄色琉璃小兽，头顶迷你屋脊线，6 个常用表情 + 文创胶带、书签、导览易拉宝应用格。 |
  | 2 | [`2.json`](./branding-and-packaging/mascot-brand-kit/2.json) | [`2.png`](./branding-and-packaging/mascot-brand-kit/2.png) | 美团外卖小袋鼠速达强化版 Brand Kit | 在品牌已有袋鼠认知基础上做「30 分钟必达」子 IP 变体，黄黑主色，三视图、6 表情、头盔配送箱与电动车遮罩、小程序开屏、保温袋大印刷位。 |

### 12.3 化妆品包装

- **模板简介**：化妆品 / 护肤品单瓶 / 系列 / 礼盒包装。
- **模板路径**：[`references/branding-and-packaging/cosmetic-packaging.md`](../references/branding-and-packaging/cosmetic-packaging.md)
- **提示词目录**：[`prompts/branding-and-packaging/cosmetic-packaging/`](./branding-and-packaging/cosmetic-packaging/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./branding-and-packaging/cosmetic-packaging/1.json) | [`1.png`](./branding-and-packaging/cosmetic-packaging/1.png) | 国货高端护肤「云纹瓷」光感修护系列礼盒 | 品牌名「东篱」，定位东方极简高奢，莫兰迪青灰瓷瓶 + 细腰曲线，礼盒半开露出一瓶一罐，真丝底与柔光，适合天旗舰店首屏。 |
  | 2 | [`2.json`](./branding-and-packaging/cosmetic-packaging/2.json) | [`2.png`](./branding-and-packaging/cosmetic-packaging/2.png) | 男士剃须理容套装（洁面 + 须泡 + 须后 + 皮套刀架） | 深海军蓝 + 冷银，直立挤压管与金属盖，外盒为抽拉式，摄影台偏冷，强调清晨浴室理性气质。 |

### 12.4 饮料标签设计

- **模板简介**：饮料 / 食品 / 调味品标签设计（国潮 / 日式 / 西式）。
- **模板路径**：[`references/branding-and-packaging/beverage-label-design.md`](../references/branding-and-packaging/beverage-label-design.md)
- **提示词目录**：[`prompts/branding-and-packaging/beverage-label-design/`](./branding-and-packaging/beverage-label-design/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./branding-and-packaging/beverage-label-design/1.json) | [`1.png`](./branding-and-packaging/beverage-label-design/1.png) | 国潮气泡水「荔潮」 | 透明玻瓶+金属旋盖，米白主标水墨荔枝与金线，底部配料与营养成分条带，配竹编垫与切半荔枝静物，4:5 商拍。 |
  | 2 | [`2.json`](./branding-and-packaging/beverage-label-design/2.json) | [`2.png`](./branding-and-packaging/beverage-label-design/2.png) | 精酿「雾港 IPA」酒标 | 470ml 棕色长颈瓶+侧招纸标，主插画为夜航灯塔与海雾，IBU 与酒精度在正面下半，背标故事区，配橡木条与开瓶器场景，偏美式西海岸 IPA 调性但中文沟通。 |

---

## 13. Typography & Text Layout（字面 / 双语版式）

以文字本身为主体的版式视觉。

### 13.1 大字主张型海报

- **模板简介**：大字主张型海报（日式高能量 / 瑞士极简 / 复古印刷）。
- **模板路径**：[`references/typography-and-text-layout/title-safe-poster.md`](../references/typography-and-text-layout/title-safe-poster.md)
- **提示词目录**：[`prompts/typography-and-text-layout/title-safe-poster/`](./typography-and-text-layout/title-safe-poster/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./typography-and-text-layout/title-safe-poster/1.json) | [`1.png`](./typography-and-text-layout/title-safe-poster/1.png) | 春季城市马拉松公益劝募（日式高能量） | 朱红＋米黄＋半色调网点，主标四字占幅超半，下缘英文与主办方小字，适合地铁灯箱与通栏下刊。 |
  | 2 | [`2.json`](./typography-and-text-layout/title-safe-poster/2.json) | [`2.png`](./typography-and-text-layout/title-safe-poster/2.png) | 建筑事务所开年论坛（瑞士极简字即图） | 纯黑字白底、仅一条线做节奏，全幅留白大于 60%，适合作业现场围挡与主屏待机。 |

### 13.2 中英 / 中日双语版式

- **模板简介**：中英 / 中日双语版式视觉（文化 / 学术 / 跨文化品牌）。
- **模板路径**：[`references/typography-and-text-layout/bilingual-layout-visual.md`](../references/typography-and-text-layout/bilingual-layout-visual.md)
- **提示词目录**：[`prompts/typography-and-text-layout/bilingual-layout-visual/`](./typography-and-text-layout/bilingual-layout-visual/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./typography-and-text-layout/bilingual-layout-visual/1.json) | [`1.png`](./typography-and-text-layout/bilingual-layout-visual/1.png) | 东西互鉴当代工艺展（中英对照） | 中文主标题最大，英文为气质副行，下附展期与场馆，主视觉在右下为抽象山水几何切割，朱砂红＋古纸色，美术馆投放通用。 |
  | 2 | [`2.json`](./typography-and-text-layout/bilingual-layout-visual/2.json) | [`2.png`](./typography-and-text-layout/bilingual-layout-visual/2.png) | 静冈 × 福鼎「一叶渡海」茶与器联展（中日对照） | `main_en` 排印日文书名「海を越える一葉」，`main_zh` 为中文并列名；`subtitle_en` 内为日文副行。和纸底＋靛与若草，主视觉为茶碗与单叶。 |

---

## 14. Assets & Props（成套素材 / 游戏资产）

图标资产、游戏内截图等成套素材。

### 14.1 拟物 / Y2K / 像素图标集

- **模板简介**：拟物 / Y2K / 像素图标集（成套统一风格）。
- **模板路径**：[`references/assets-and-props/retro-skeuomorphic-icons.md`](../references/assets-and-props/retro-skeuomorphic-icons.md)
- **提示词目录**：[`prompts/assets-and-props/retro-skeuomorphic-icons/`](./assets-and-props/retro-skeuomorphic-icons/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./assets-and-props/retro-skeuomorphic-icons/1.json) | [`1.png`](./assets-and-props/retro-skeuomorphic-icons/1.png) | iOS 拟物风 12 应用图标集（4×3 网格） | 亮面玻璃、皮纹、金属倒角与统一 24% 圆角方底，是千年代末高端智能手机主题包最具辨识度的「一眼拟物」配方。 |
  | 2 | [`2.json`](./assets-and-props/retro-skeuomorphic-icons/2.json) | [`2.png`](./assets-and-props/retro-skeuomorphic-icons/2.png) | Y2K Aero 风水晶玻璃音乐主题 8 图标（2×4） | 透明折射、高饱和品红与电青、镀铬描边是 Windows Vista / 早期媒体播放器皮肤常用的 Y2K 水晶系语言，与扁平时代形成强反差，适合歌单 / 电音向视觉包。 |

### 14.2 游戏内截图样机

- **模板简介**：游戏内截图 mockup（HUD + 字幕 + 任务面板）。
- **模板路径**：[`references/assets-and-props/game-screenshot-mockup.md`](../references/assets-and-props/game-screenshot-mockup.md)
- **提示词目录**：[`prompts/assets-and-props/game-screenshot-mockup/`](./assets-and-props/game-screenshot-mockup/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./assets-and-props/game-screenshot-mockup/1.json) | [`1.png`](./assets-and-props/game-screenshot-mockup/1.png) | 开放世界奇幻 RPG 黄昏雪原越肩视角 | 左下资源条、右下技能轮、左上小地图与右上任务追踪是现代 3A 开放世界默认 HUD 四分法，本例用女性游侠背身强化「正在玩」临场感。 |
  | 2 | [`2.json`](./assets-and-props/game-screenshot-mockup/2.json) | [`2.png`](./assets-and-props/game-screenshot-mockup/2.png) | 国产仙侠 MMO 云端浮岛斗法（第三人称略高机位） | 血条在头顶、右侧竖向技能栏、左下聊天与系统飘字是 PC 仙侠 MMO 常见布局；本例突出「御剑近身 + 法宝光效」以区隔西幻。 |

---

## 15. Academic Figures（学术配图）

论文 / 顶会投稿 / 学术海报 / 答辩 PPT 配图。整体偏白底 + 出版物字体 + 几何精确。

### 15.1 方法 Pipeline 总览

- **模板简介**：方法总览图 / pipeline figure（多 stage 块 + 数据流）。
- **模板路径**：[`references/academic-figures/method-pipeline-overview.md`](../references/academic-figures/method-pipeline-overview.md)
- **提示词目录**：[`prompts/academic-figures/method-pipeline-overview/`](./academic-figures/method-pipeline-overview/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./academic-figures/method-pipeline-overview/1.json) | [`1.png`](./academic-figures/method-pipeline-overview/1.png) | RAG-based Long-Context QA pipeline | 检索增强长上下文问答的端到端流程，从原始文档到最终答案，适合 ACL / NeurIPS 式 method overview。五阶段串联、标签全英文、适合双栏版式。 |
  | 2 | [`2.json`](./academic-figures/method-pipeline-overview/2.json) | [`2.png`](./academic-figures/method-pipeline-overview/2.png) | 图像扩散模型训练 pipeline（4 阶段） | 文生图扩散模型在训练阶段的模块级总览，从图文对到可生成权重的四阶段前向。强调数据、噪声、U-Net 与 VAE 的角色分工，无训练 loss 支路、纯推理式布局。 |

### 15.2 神经网络架构图

- **模板简介**：神经网络架构图（layer 块 + tensor shape + 跳连）。
- **模板路径**：[`references/academic-figures/neural-network-architecture.md`](../references/academic-figures/neural-network-architecture.md)
- **提示词目录**：[`prompts/academic-figures/neural-network-architecture/`](./academic-figures/neural-network-architecture/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./academic-figures/neural-network-architecture/1.json) | [`1.png`](./academic-figures/neural-network-architecture/1.png) | Encoder-only Transformer（12 层，768-d，8-head） | 典型 BERT / RoBERTa 系编码器，用于下游分类或表示学习。自注意力堆叠、残差与层归一化可辨，张量从 token 到池化后 logits。 |
  | 2 | [`2.json`](./academic-figures/neural-network-architecture/2.json) | [`2.png`](./academic-figures/neural-network-architecture/2.png) | Vision Transformer (ViT-B/16) 分类架构 | 从图像到 patch 序列、经 Transformer encoder 与 [CLS] 分类头，张量随空间 token 与模型宽度展开，含 PatchEmbed 与位置编码。适合 CVPR 论文 model figure。 |

### 15.3 定性对比网格

- **模板简介**：多方法 qualitative 对比网格（行 = 样本，列 = 方法）。
- **模板路径**：[`references/academic-figures/qualitative-comparison-grid.md`](../references/academic-figures/qualitative-comparison-grid.md)
- **提示词目录**：[`prompts/academic-figures/qualitative-comparison-grid/`](./academic-figures/qualitative-comparison-grid/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./academic-figures/qualitative-comparison-grid/1.json) | [`1.png`](./academic-figures/qualitative-comparison-grid/1.png) | 三种图像生成模型 × 四个固定 Prompt | 同一文本提示下对比 DALL·E 3、Midjourney v6、Stable Diffusion XL 与 Ours，四行文本提示、五列（含 Input 为 prompt 文本卡片）。适用于生成类论文 supplementary。 |
  | 2 | [`2.json`](./academic-figures/qualitative-comparison-grid/2.json) | [`2.png`](./academic-figures/qualitative-comparison-grid/2.png) | Cityscapes 语义分割 — 四方法与 Ground Truth 对比 | 同一张街景输入下比较经典 FCN、DeepLabV3+、Mask2Former 与 Ours，首列为 Input RGB，一列为 GT，最后一列为 Ours。单元格为彩色 overlay 或侧-by-side 小图。适用于 CVPR 分割论文。 |

### 15.4 科学示意图

- **模板简介**：概念 / 原理 / 实验装置示意图（自由度高，自然语言模板）。
- **模板路径**：[`references/academic-figures/scientific-schematic.md`](../references/academic-figures/scientific-schematic.md)
- **提示词目录**：[`prompts/academic-figures/scientific-schematic/`](./academic-figures/scientific-schematic/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.txt`](./academic-figures/scientific-schematic/1.txt) | [`1.png`](./academic-figures/scientific-schematic/1.png) | CRISPR-Cas9 靶向双链断裂与非同源末端连接 | 以 guide RNA 与目标 DNA 配对、Cas9 切割、NHEJ 或 HDR 为叙事主线，白底、标注线与基因序列样式符号，适合作 Nature Methods 风格图注或综述插图。 |
  | 2 | [`2.txt`](./academic-figures/scientific-schematic/2.txt) | [`2.png`](./academic-figures/scientific-schematic/2.png) | 双光子与纠缠光子对产生的简化实验光路 | 泵浦激光、非线性 BBO 晶体中的自发参量下转换、分束与符合计数，带角度标注，适合 PRL 式 optics schematic，强调几何与波长标注。 |

### 15.5 Publication-Ready 数据图表

- **模板简介**：publication-ready 数据图表（bar / line / scatter / heatmap / box）。
- **模板路径**：[`references/academic-figures/publication-chart.md`](../references/academic-figures/publication-chart.md)
- **提示词目录**：[`prompts/academic-figures/publication-chart/`](./academic-figures/publication-chart/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./academic-figures/publication-chart/1.json) | [`1.png`](./academic-figures/publication-chart/1.png) | SWE-Bench Verified 上多代理系统的 Resolve Rate 对比 | 软件工程基准 SWE-Bench 上的方法对比，纵轴为 resolve rate、横轴为公开代理系统名称，Ours 用强调色。适合系统论文主文图或附录表图。 |
  | 2 | [`2.json`](./academic-figures/publication-chart/2.json) | [`2.png`](./academic-figures/publication-chart/2.png) | LLM 预训练「Scaling law」双对数曲线（Test loss vs. compute C） | 纵轴为测试交叉熵、横轴为训练算力 C（FLOP，log₁₀），多系列等参放大曲线与趋势线，体现幂律区段。采用折线模板变体，论文常见 NeurIPS 式。 |

### 15.6 论文图形摘要 Graphical Abstract

- **模板简介**：期刊投稿用 Graphical Abstract / 图形摘要 / 投稿封面图（4 段式 / 中心展开 / 方形 / 竖版）。
- **模板路径**：[`references/academic-figures/graphical-abstract.md`](../references/academic-figures/graphical-abstract.md)
- **提示词目录**：[`prompts/academic-figures/graphical-abstract/`](./academic-figures/graphical-abstract/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./academic-figures/graphical-abstract/1.json) | [`1.png`](./academic-figures/graphical-abstract/1.png) | 横向 4 段式 — 大模型长上下文检索增强问答 | 面向 ACL / EMNLP / TPAMI 风格的 Graphical Abstract，把"长上下文 QA 中的检索-排序-推理"压缩成 Problem → Method → Mechanism → Outcome 四段式，比例 2:1，全英标注，灰蓝主色 + 单一暖色提示重点结果。 |
  | 2 | [`2.json`](./academic-figures/graphical-abstract/2.json) | [`2.png`](./academic-figures/graphical-abstract/2.png) | 方形 1:1 — 锂电池硅碳负极循环稳定性 | 面向 ACS Energy Letters / Journal of Power Sources 等要求方形 Graphical Abstract 的期刊。2×2 网格布局：左上为研究问题（硅负极体积膨胀），右上为方法（梯度孔径硅碳复合材料），左下为关键机制（柔性 SEI 缓冲），右下为定性结果（容量保持率柱图）。 |

### 15.7 学术机理示意图

- **模板简介**：论文机制 / 机理 / 反应路径 / 演化机制图（中心对象 + 多阶段 / 三段式 / 循环 / 多分支）。
- **模板路径**：[`references/academic-figures/mechanism-diagram.md`](../references/academic-figures/mechanism-diagram.md)
- **提示词目录**：[`prompts/academic-figures/mechanism-diagram/`](./academic-figures/mechanism-diagram/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./academic-figures/mechanism-diagram/1.json) | [`1.png`](./academic-figures/mechanism-diagram/1.png) | 硅碳负极循环过程中的体积膨胀与 SEI 演化机理 | 典型工程类期刊机制图。中心是硅碳复合颗粒的简化剖面，周围按"嵌锂 → 体积膨胀 → SEI 应力累积 → SEI 破裂 → 新 SEI 重构"五阶段展开，第 3、4 阶段叠加低饱和暖色作为应力 / 失效高亮。可直接用于论文正文 mechanism figure 或答辩 PPT 机制说明页。 |
  | 2 | [`2.json`](./academic-figures/mechanism-diagram/2.json) | [`2.png`](./academic-figures/mechanism-diagram/2.png) | 三段式因果链 — 光催化降解水中有机污染物机制 | 环境 / 化工类机制图变体 1（左 → 中 → 右 三段式因果链）。左侧为初始体系（光催化剂 + 污染物 + 紫外光），中间为多阶段反应机制（电子-空穴对生成 → 自由基产生 → 污染物开环 → 矿化），右侧为最终产物（CO₂ + H₂O + 无机离子）。整图保持期刊正文 figure 风格。 |

### 15.8 多工况 / 多条件结果对比图

- **模板简介**：同一研究对象在不同工况 / 条件下的多面板结果对比图（2×2 / 1×N / 双因子矩阵 / 定性场图）。
- **模板路径**：[`references/academic-figures/multi-condition-comparison.md`](../references/academic-figures/multi-condition-comparison.md)
- **提示词目录**：[`prompts/academic-figures/multi-condition-comparison/`](./academic-figures/multi-condition-comparison/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./academic-figures/multi-condition-comparison/1.json) | [`1.png`](./academic-figures/multi-condition-comparison/1.png) | 2×2 — 不同进风系数 λ 下的炉膛温度场分布对比（定性场图） | 燃烧 / 能源工程方向典型 result figure。同一炉膛纵剖面在 4 种过量空气系数下的温度场对比，4 个 panel 共享同一 viridis-like 色标，标签 (a)(b)(c)(d) 严格统一。无真实 CFD 数据，按定性场图渲染（色标只显示 low → high，无数值刻度）。 |
  | 2 | [`2.json`](./academic-figures/multi-condition-comparison/2.json) | [`2.png`](./academic-figures/multi-condition-comparison/2.png) | 1×4 横向 — 不同退火温度下镍基合金微观组织对比（micrograph） | 材料科学方向 result figure 横向变体。一行 4 个 SEM micrograph，对比 700 / 800 / 900 / 1000 ℃ 退火后的 γ' 相形貌。所有 panel 共享同一比例尺，labels (a)(b)(c)(d) 位置统一。无真实图像数据，按定性 micrograph 风格渲染（… |

### 15.9 开题 / 答辩 / 汇报研究总览图

- **模板简介**：开题 / 中期 / 终期答辩首页 + 论文汇报 + 组会引导页的研究总览图（上中下三层 / 中心辐射 / 双栏 / 极简）。
- **模板路径**：[`references/academic-figures/research-overview-poster.md`](../references/academic-figures/research-overview-poster.md)
- **提示词目录**：[`prompts/academic-figures/research-overview-poster/`](./academic-figures/research-overview-poster/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./academic-figures/research-overview-poster/1.json) | [`1.png`](./academic-figures/research-overview-poster/1.png) | 中文硕士开题答辩首页 — 锂电池热失控早期预警 | 硕士开题答辩 PPT 首页用研究总览图，主题是"基于多源传感数据的锂电池热失控早期预警"。上方主标题 + 副标题，中间为"背景 → 目标 → 三个研究模块（机理 / 模型 / 验证）"层级结构，下方为预期成果带，全部中文标注，模块严格等大，色调克制（深蓝 + 灰蓝 + 黑灰），可直接放进硕士开题答辩首页。 |
  | 2 | [`2.json`](./academic-figures/research-overview-poster/2.json) | [`2.png`](./academic-figures/research-overview-poster/2.png) | 左右双栏（变体 2）— 博士中期答辩 · 多模态大模型辅助医疗影像诊断 | 博士中期答辩首页 + 项目进度，左栏 = 4 个研究内容模块（垂直堆叠），右栏 = 极简 gantt 时间表（按学期划分里程碑）。中英双语，主标题英文 + 中文副标题，色调保持深蓝 / 灰蓝 / 黑灰，时间轴用细线 + 节点圆。 |

---

## 16. Infographics（信息图）

信息图 / 高密度科普 / 手绘信息图 / KPI 仪表盘。

### 16.1 高图例密度科普图

- **模板简介**：高图例密度科普 / 因果链 / 演化 / 解剖图（双语）。
- **模板路径**：[`references/infographics/legend-heavy-infographic.md`](../references/infographics/legend-heavy-infographic.md)
- **提示词目录**：[`prompts/infographics/legend-heavy-infographic/`](./infographics/legend-heavy-infographic/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./infographics/legend-heavy-infographic/1.json) | [`1.png`](./infographics/legend-heavy-infographic/1.png) | 气候变化对全球主粮作物的因果链 | 以半剖面地球 / 农区为视觉锚，辐射状编号块解释升温、CO₂ 施肥效应、水分胁迫、病虫害与价格传导，适合环境经济学课堂或机构科普长图主视觉。 |
  | 2 | [`2.json`](./infographics/legend-heavy-infographic/2.json) | [`2.png`](./infographics/legend-heavy-infographic/2.png) | 大语言模型关键演化 2017–2026 时间系谱 | 以水平时间链 / 系谱树为心，从 Transformer 到 GPT、开源 Llama 系列、多模态与推理 o1 类，强调「架构、数据、算力、对齐」四标签，适合技术博客头图或课程讲义。 |

### 16.2 手绘风信息图

- **模板简介**：手绘风信息图（macaron / morandi / 黑板 / 牛皮纸；自然语言模板）。
- **模板路径**：[`references/infographics/hand-drawn-infographic.md`](../references/infographics/hand-drawn-infographic.md)
- **提示词目录**：[`prompts/infographics/hand-drawn-infographic/`](./infographics/hand-drawn-infographic/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.txt`](./infographics/hand-drawn-infographic/1.txt) | [`1.png`](./infographics/hand-drawn-infographic/1.png) | 如何在家自制希腊酸奶 | 厨房手账感、竖版 3:4，适合公众号或小红书。步骤 6 条，材料与时长写清，无电脑字体要求。 |
  | 2 | [`2.txt`](./infographics/hand-drawn-infographic/2.txt) | [`2.png`](./infographics/hand-drawn-infographic/2.png) | 番茄红素的益处与摄入要点（马卡龙手账风） | 偏科普+生活方式，用柔和粉绿配色与 macaron 风，分条写抗氧化语境、脂溶性、食物来源、吸收小贴士，不宣称医疗功效。 |

### 16.3 便当格信息图

- **模板简介**：便当格模块化信息图（高密度多模块 widget 排布）。
- **模板路径**：[`references/infographics/bento-grid-infographic.md`](../references/infographics/bento-grid-infographic.md)
- **提示词目录**：[`prompts/infographics/bento-grid-infographic/`](./infographics/bento-grid-infographic/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./infographics/bento-grid-infographic/1.json) | [`1.png`](./infographics/bento-grid-infographic/1.png) | iPhone 16 Pro 全方位解析（便当格 8 模块） | Apple Newsroom 式浅灰白底、一大块 hero 放钛原色机背与「为何值得换」三条，其余为规格对比、算力/影像芯片、价格段、系统亮点与选购提示。适合数码自媒体一图流。 |
  | 2 | [`2.json`](./infographics/bento-grid-infographic/2.json) | [`2.png`](./infographics/bento-grid-infographic/2.png) | Tesla Model Y 改款全面盘点 | 面向「考虑换电车」的读者，bento 强调续航区间、电耗、空间、FSD/辅助驾驶、充电与价格带，不采用过分促销语气。 |

### 16.4 二元 / 多元对比信息图

- **模板简介**：二元 / 多元对比信息图（A vs B / 套餐档位 / 误区 vs 正解）。
- **模板路径**：[`references/infographics/comparison-infographic.md`](../references/infographics/comparison-infographic.md)
- **提示词目录**：[`prompts/infographics/comparison-infographic/`](./infographics/comparison-infographic/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./infographics/comparison-infographic/1.json) | [`1.png`](./infographics/comparison-infographic/1.png) | iPhone 16 Pro 与三星 Galaxy S25 Ultra 谁更适合你 | 从屏幕形态、长焦、录像、系统生态、维修与起售价看差异，避免攻击品牌，用「你更看重什么」作结。3:4 竖版、浅暖底、中央 VS 符号可细线可几何。 |
  | 2 | [`2.json`](./infographics/comparison-infographic/2.json) | [`2.png`](./infographics/comparison-infographic/2.png) | 燕麦奶 Oat 饮 vs 全脂牛奶 | 从蛋白品质、脂溶性营养、价格、升糖/饱腹、环境足迹到咖啡拉花适配，帮助乳糖不耐与健身人群自判。不宣称医疗功效，语气科普。 |

### 16.5 步骤教程信息图

- **模板简介**：步骤教程信息图（插画感、温暖；非工程流程图）。
- **模板路径**：[`references/infographics/step-by-step-infographic.md`](../references/infographics/step-by-step-infographic.md)
- **提示词目录**：[`prompts/infographics/step-by-step-infographic/`](./infographics/step-by-step-infographic/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./infographics/step-by-step-infographic/1.json) | [`1.png`](./infographics/step-by-step-infographic/1.png) | 新手家庭健身 7 步入门 | 无器械起步，从热身、呼吸、分部位训练到拉伸与恢复，配色薄荷+珊瑚+深棕，适合运动小白跟练海报。 |
  | 2 | [`2.json`](./infographics/step-by-step-infographic/2.json) | [`2.png`](./infographics/step-by-step-infographic/2.png) | 10 分钟戚风备料+烘烤(家用 6 寸模) | 把称量、分蛋、打蛋白、翻拌、入炉、倒扣冷却浓缩为 6 步，时间轴是「你动手的前 10 分钟 + 烤时另计」。暖橙+鼠尾草色，烤箱与打蛋器小插画。 |

### 16.6 KPI 仪表盘信息图

- **模板简介**：KPI 仪表盘式信息图（年度回顾 / Wrapped / 业务 dashboard）。
- **模板路径**：[`references/infographics/kpi-dashboard-infographic.md`](../references/infographics/kpi-dashboard-infographic.md)
- **提示词目录**：[`prompts/infographics/kpi-dashboard-infographic/`](./infographics/kpi-dashboard-infographic/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./infographics/kpi-dashboard-infographic/1.json) | [`1.png`](./infographics/kpi-dashboard-infographic/1.png) | Northwind AI 的 2025 年度关键指标一页 | B2B SaaS 风暗色底，主标 ARR 与 NRR，附 pipeline、客诉、上云与员工人数，像投资人会前「一页快览」而非正式年报。所有金额与百分比为**示意**。 |
  | 2 | [`2.json`](./infographics/kpi-dashboard-infographic/2.json) | [`2.png`](./infographics/kpi-dashboard-infographic/2.png) | 个人 2025 读书报告 Wrapped | 类 Spotify Wrapped 的年度阅读快照：总本数、总页、体裁分布、最长一本、最忙阅读月、豆瓣均分(示意)与想读队列缩减，暖亮底+紫粉强调。适合导出为一张图**发到微信朋友圈**或收藏。 |

---

## 17. Technical Diagrams（技术工程示意图）

系统架构 / 流程图 / 时序 / 状态机 / ER / 思维导图 / 网络拓扑等工程示意图。

### 17.1 系统架构图

- **模板简介**：系统架构图（前端 + 后端 + DB + 缓存 + 队列 + 外部）。
- **模板路径**：[`references/technical-diagrams/system-architecture.md`](../references/technical-diagrams/system-architecture.md)
- **提示词目录**：[`prompts/technical-diagrams/system-architecture/`](./technical-diagrams/system-architecture/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./technical-diagrams/system-architecture/1.json) | [`1.png`](./technical-diagrams/system-architecture/1.png) | 多租户 AI 客服 SaaS 生产架构 | React/Next.js 公网入口、Kong 网关、FastAPI 业务层、Postgres+Redis+Kafka+Qdrant 数据面，以及 OpenAI、Stripe、Twilio 等外部依赖分区清晰，是 ToB 智能客服产线最常被引用的一类「全栈+向量检索+计费等」总览图。 |
  | 2 | [`2.json`](./technical-diagrams/system-architecture/2.json) | [`2.png`](./technical-diagrams/system-architecture/2.png) | 区域电商节秒杀下单链路（CDN + 微服务 + 主从 + MQ） | 高并发读路径经 CDN 与 Nginx 进入订单域，库存与订单解耦、RabbitMQ 削峰、MySQL 主从与 Redis 热点库存，是业务侧和基础设施同学对齐时的标准「大促架构」一屏讲清版。 |

### 17.2 流程图 / 决策图

- **模板简介**：流程图 / 决策图（BPMN 形状语义 + Yes/No 分支）。
- **模板路径**：[`references/technical-diagrams/flowchart-decision.md`](../references/technical-diagrams/flowchart-decision.md)
- **提示词目录**：[`prompts/technical-diagrams/flowchart-decision/`](./technical-diagrams/flowchart-decision/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./technical-diagrams/flowchart-decision/1.json) | [`1.png`](./technical-diagrams/flowchart-decision/1.png) | 用户注册（短信验证码 + 邮箱验证 + 风控分支） | 从提交手机号与密码到发送短信、人机校验、device_id 行为评分分支，邮箱验证链接 24h 内有效；未通过风控进入人工复核队列（子流程块）。`exception_branch` 控制异常颜色边。 |
  | 2 | [`2.json`](./technical-diagrams/flowchart-decision/2.json) | [`2.png`](./technical-diagrams/flowchart-decision/2.png) | 订单退款审核（原路退 / 部分退 / 财务驳回） | BPMN 泳道标清用户、商户 BFF、订单服务、支付适配、财务。含「已超售后期」「风控命中」「部分退款金额>剩余」等决策；启用泳道。 |

### 17.3 时序图

- **模板简介**：时序图（actor + lifeline + 消息箭头 + 激活条）。
- **模板路径**：[`references/technical-diagrams/sequence-diagram.md`](../references/technical-diagrams/sequence-diagram.md)
- **提示词目录**：[`prompts/technical-diagrams/sequence-diagram/`](./technical-diagrams/sequence-diagram/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./technical-diagrams/sequence-diagram/1.json) | [`1.png`](./technical-diagrams/sequence-diagram/1.png) | OAuth 2.0 授权码 + PKCE（User / Web / Keycloak / Resource） | 浏览器端机密公开场景下的标准四角色握手，从 `/authorize` 到 `code` 换 `access_token` 再带 `Bearer` 调业务 API，是内部 IdP 迁移说明里引用频率最高的一段时序。 |
  | 2 | [`2.json`](./technical-diagrams/sequence-diagram/2.json) | [`2.png`](./technical-diagrams/sequence-diagram/2.png) | 微信 Native 支付「统一下单—调起微信—支付结果」（用户 / 商户 / 微信） | 用户在微信内 H5/小程序外跳 Native 的常规三线模型：商户统一下单拿 prepay_id，客户端 `chooseWXPay` 调起，异步 notify 与查询补偿闭环，适合贴进对接章节。 |

### 17.4 状态机 / 生命周期图

- **模板简介**：状态机 / 生命周期图（state + transition + guard / action）。
- **模板路径**：[`references/technical-diagrams/state-machine.md`](../references/technical-diagrams/state-machine.md)
- **提示词目录**：[`prompts/technical-diagrams/state-machine/`](./technical-diagrams/state-machine/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./technical-diagrams/state-machine/1.json) | [`1.png`](./technical-diagrams/state-machine/1.png) | B2C 主单 OMS 状态机（从创建到终态含补偿） | 含「配货中」与微信/对公等支付后履约分支、超时关单与整单退款终态，与 `order_status` 枚举、幂等重试在评审里一一对齐，是交易域最常用的「一张图对齐全仓」主单机。 |
  | 2 | [`2.json`](./technical-diagrams/state-machine/2.json) | [`2.png`](./technical-diagrams/state-machine/2.png) | 内容平台 `Article` 审核与上下架状态机 | 覆盖草稿、机审、人审、已发布、用户举报后的下架、以及软删与从下架恢复，满足「信安 + 产品」对 `visibility` 与 `review_job_id` 联动的说明需求。 |

### 17.5 ER 图 / 数据模型图

- **模板简介**：ER 图 / 数据模型图（实体 + 字段 + PK/FK + crow's foot 关系）。
- **模板路径**：[`references/technical-diagrams/er-diagram.md`](../references/technical-diagrams/er-diagram.md)
- **提示词目录**：[`prompts/technical-diagrams/er-diagram/`](./technical-diagrams/er-diagram/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./technical-diagrams/er-diagram/1.json) | [`1.png`](./technical-diagrams/er-diagram/1.png) | 电商核心数据模型（用户 · 地址 · 商品 · 订单 · 券） | 覆盖 `users` 到 `orders`、`order_items`、`skus`，以及 `payments`、`coupons` 与多对多 `coupon_redemptions`。类型使用 PostgreSQL 习惯（`uuid`、`timestamptz`、`numeric(12,2)`），与典型 Pris… |
  | 2 | [`2.json`](./technical-diagrams/er-diagram/2.json) | [`2.png`](./technical-diagrams/er-diagram/2.png) | 多作者博客平台（分类 · 标签 · 评论 · 点赞） | `posts` 多对多 `tags` 经 `post_tags`，`categories` 树形自关联；`comments` 支持二级回复 `parent_id`；`likes` 以 `(user_id, post_id)` 保证唯一。适合文档站与社区轻量 CMS。 |

### 17.6 技术主题思维导图

- **模板简介**：技术主题思维导图（中央 + 放射式分支）。
- **模板路径**：[`references/technical-diagrams/mind-map-tech.md`](../references/technical-diagrams/mind-map-tech.md)
- **提示词目录**：[`prompts/technical-diagrams/mind-map-tech/`](./technical-diagrams/mind-map-tech/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./technical-diagrams/mind-map-tech/1.json) | [`1.png`](./technical-diagrams/mind-map-tech/1.png) | 前端工程师必备技能谱（TypeScript 生态为轴） | 从语言/运行时到构建、可观测、端侧与体验指标，对齐全链路交付责任，适合「高级工程师」与「全栈化前端」自评时一张图说清能力边界。 |
  | 2 | [`2.json`](./technical-diagrams/mind-map-tech/2.json) | [`2.png`](./technical-diagrams/mind-map-tech/2.png) | Kubernetes 知识全景（自集群到可观测的闭环） | 以集群生命周期、工作负载、网络、安全、存储、交付与 SRE 观测六扇面展开，覆盖 CNI/Cilium、Gateway API、OPA 与 HPA/VPA/CA，是平台组新人「八周上手」的导航图。 |

### 17.7 网络拓扑图

- **模板简介**：网络拓扑图（设备 glyph + zone / VPC + 带宽 / 协议标）。
- **模板路径**：[`references/technical-diagrams/network-topology.md`](../references/technical-diagrams/network-topology.md)
- **提示词目录**：[`prompts/technical-diagrams/network-topology/`](./technical-diagrams/network-topology/)
- **图片进度**：✅ 2 / 2
- **案例**：

  | # | 提示词 | 图片 | 案例标题 | 简介 |
  |---|---|---|---|---|
  | 1 | [`1.json`](./technical-diagrams/network-topology/1.json) | [`1.png`](./technical-diagrams/network-topology/1.png) | AWS 多可用区生产 VPC（ALB + WAF、NAT、RDS、ElastiCache、ECS） | 公网子网内 ALB+WAF、Private 子网内 ECS/任务与多 AZ 数据面，ElastiCache 与 RDS 的跨子网、NAT 出口与 IGW/CloudFront 入站路径一眼区分，是电商平台云上网络评审里最常见的定稿图。 |
  | 2 | [`2.json`](./technical-diagrams/network-topology/2.json) | [`2.png`](./technical-diagrams/network-topology/2.png) | 企业 SD-WAN：总部双机热备 + 分支 CPE 与 云专线融合 | 总部与两地分支经 MPLS+Internet 双上行（Active/Active）、hub 级防火墙、控制器纳管、以及一条至 VPC 的 VPN/Direct Connect 汇流，是零售或制造总部「一张网管门店」HLD 常见形态。 |

---