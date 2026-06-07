# AI推理叙事游戏 - Figma Make 页面生成提示词

## 统一设计规范（赛博朋克风格）

### 色彩系统
| 类型 | 色值 | 用途 |
|------|------|------|
| **背景主色** | #0A0E17 | 页面主背景 |
| **背景深色** | #06080D | 卡片/模块背景 |
| **背景浅色** | #111827 | 次级背景 |
| **霓虹金** | #C9A96E | 主强调色（按钮/激活状态） |
| **霓虹蓝** | #00F0FF | 科技元素/链接/图标 |
| **霓虹粉** | #FF006E | 警告/危险/热点标记 |
| **霓虹紫** | #B24BF3 | 次要强调/渐变 |
| **霓虹绿** | #00FF94 | 成功/完成状态 |
| **文字主色** | #E8ECF1 | 主要文字 |
| **文字副色** | #8B95A5 | 次要文字/标签 |
| **文字禁用** | #5A6475 | 禁用/占位文字 |
| **边框色** | #1A2744 | 分割线/卡片边框 |
| **发光边框** | rgba(0,240,255,0.3) | 霓虹发光效果 |

### 字体系统
| 类型 | 字体 | 大小 | 字重 | 用途 |
|------|------|------|------|------|
| **标题** | PingFang SC / SF Pro | 24px | 700 | 页面标题 |
| **副标题** | PingFang SC / SF Pro | 18px | 600 | 区块标题 |
| **正文** | PingFang SC / SF Pro | 14px | 400 | 正文内容 |
| **小字** | PingFang SC / SF Pro | 12px | 400 | 标签/辅助文字 |
| **微字** | PingFang SC / SF Pro | 10px | 400 | 时间/计数 |
| **按钮** | PingFang SC / SF Pro | 14px | 600 | 按钮文字 |
| **数字** | SF Mono / Courier | 16px | 600 | 倒计时/数值 |

### 组件风格
- **卡片**：圆角12px，背景#111827，边框1px solid #1A2744，hover时边框发光
- **按钮主**：圆角8px，背景渐变#C9A96E→#DFC78A，文字#0A0E17，shadow发光
- **按钮次**：圆角8px，背景透明，边框1px solid #00F0FF，文字#00F0FF
- **输入框**：圆角8px，背景#0A0E17，边框1px solid #1A2744，focus时边框变#00F0FF
- **标签**：圆角4px，背景rgba(0,240,255,0.15)，文字#00F0FF
- **图标**：线性图标，stroke宽度1.5px，颜色跟随文字

### 特效规范
- **发光效果**：box-shadow: 0 0 8px rgba(0,240,255,0.3)
- **文字发光**：text-shadow: 0 0 4px rgba(201,169,110,0.5)
- **卡片hover**：边框色变为rgba(201,169,110,0.5)，添加微弱发光
- **激活状态**：金色边框+发光+背景rgba(201,169,110,0.1)
- **扫描线效果**：可选背景装饰线（每8px一条，透明度0.03）

---

## 1. 首页

**页面名称：** AI推理叙事游戏 - 首页
**用途：** 应用主入口，展示活动、快捷入口、社交动态

**提示词：**
```
Create a mobile app home screen for an AI mystery narrative game, cyberpunk style, dark theme.

Layout structure (top to bottom):
1. Banner carousel area - Large horizontal card with gradient background (dark purple to dark blue), showing "限时活动·山庄晚宴" text in neon gold (#C9A96E), with countdown timer badge "剩余 2天18小时" and a "立即参与" CTA button. Include carousel dots at bottom.

2. Three entry cards row - Three equal-width cards side by side:
   - Card 1: "剧本" with book icon, gold accent
   - Card 2: "排行榜" with trophy icon, blue accent
   - Card 3: "任务" with target icon, green accent, with red notification badge showing "3"
   Each card has icon + label, rounded corners, dark background.

3. Beginner guide card - Horizontal card with gradient purple background, showing "🌸 新手引导剧本" title, progress bar at 32%, and an arrow icon.

4. Server announcement area - Compact card with "📢 全服喊话" header, showing 3 scrolling messages with colored user badges.

5. Hot feed header - "🔥 热门动态" title with "查看全部 >" link.

6. Feed cards (2 visible) - Weibo-style cards with:
   - User avatar (circular, colored border)
   - Username + tag (colored badge)
   - Content text
   - Image placeholders (1-2 per card)
   - Action bar: like/comment/share + timestamp

7. Bottom tab bar - 5 tabs:
   - 首页 (active, gold icon, gold label, gold indicator line)
   - 剧本 (inactive, gray icon)
   - 快速组局 (center, floating orange button with lightning icon, larger than other tabs)
   - 社交 (inactive, gray icon)
   - 我的 (inactive, gray icon)

Design specs:
- Screen size: 390x844px (iPhone)
- Background: #0A0E17
- Card backgrounds: #111827 with subtle border
- Accent colors: gold #C9A96E, neon blue #00F0FF, neon green #00FF94
- All corners rounded (12px for cards, 8px for buttons)
- Clean spacing between sections (12-16px)
- Cyberpunk glow effects on active elements
- No status bar
- Total height: ~800px scrollable content
```

---

## 2. 剧本列表页

**页面名称：** 剧本列表页
**用途：** 浏览和筛选可游玩的剧本

**提示词：**
```
Create a mobile app script selection screen for an AI mystery game, cyberpunk style.

Layout structure:
1. Search header - Rounded search bar with placeholder "搜索剧本...", filter icon button on right. Dark background with subtle glow.

2. Popular banner - Horizontal card with "Popular" tag (orange), "热门剧本" text, arrow icon. Gradient background.

3. Horizontal scroll cards - 3 cards side by side:
   - "Trending" card with 42 count
   - "New" card with 18 count
   - "For You" card with 25 count
   Each card: dark background, rounded, icon + label + count.

4. Section header - "推荐剧本" title + "更多 >" link.

5. Script cards (4 visible) - Each card contains:
   - Left: Cover square (64x64px) with emoji 🎭
   - Right: Script name, tags (colored badges: blue=本格, purple=推理, green=情感, orange=惊悚), rating (⭐ score), player count
   Cards stacked vertically with 10px gap.

6. Bottom tab bar - Same as home screen, with "首页" tab active.

Design specs:
- Screen size: 430x932px
- Background: #0A0E17
- Card backgrounds: #1A1F2E
- Tags use distinct colors with semi-transparent backgrounds
- Script covers have subtle gradient or pattern
- Active tab has gold indicator line
- Center floating button: orange gradient with shadow
```

---

## 3. 剧本详情页

**页面名称：** 剧本详情页
**用途：** 查看剧本详细信息，决定是否开始游戏

**提示词：**
```
Create a mobile app script detail screen, cyberpunk style, dark theme.

Layout structure:
1. Hero image area - Large rectangular area at top with gradient overlay (dark purple to transparent), showing abstract pattern or placeholder image. Overlay text: script title "山庄晚宴" in large white text, subtitle below.

2. Script info card - Dark card containing:
   - Script type badge (本格推理)
   - Difficulty: 3 stars (gold)
   - Duration: 75分钟
   - Players: 4-6人
   - All displayed in a grid or list format

3. Synopsis card - "剧情简介" header, expandable text paragraph with "展开" button.

4. Character list - "角色列表" header, horizontal scroll of character cards:
   - Each card: avatar + name + role
   - 6 cards visible

5. Reviews section - "玩家评价" header, review score summary (9.2/10), 2 review cards with user info, rating, text.

6. Action bar (sticky bottom) - Full-width bar with:
   - Star/favorite icon button (left)
   - Share icon button (middle)
   - "开始游戏" large button (right, gold gradient, prominent)

Design specs:
- Screen size: 390x844px
- Hero area takes ~30% of screen
- Cards have 1px border, rounded corners
- Gold CTA button with glow effect
- Tags use neon colors with transparent backgrounds
- Character avatars are circular with colored borders
- Scrollable content, action bar fixed at bottom
```

---

## 4. 游戏房间（准备大厅）

**页面名称：** 游戏房间 - 准备大厅
**用途：** 游戏开始前的准备区域，玩家等待和互动

**提示词：**
```
Create a mobile app game lobby screen for multiplayer preparation, cyberpunk style.

Layout structure:
1. Room header - Top bar with:
   - Room number: #12345 (copyable)
   - Script name: "山庄晚宴"
   - Settings icon (gear)
   - Close/exit icon

2. Player grid - 2x3 or 3x2 grid of player cards:
   - Each card: avatar (circular), nickname, "已准备"/"未准备" status badge
   - Host card has crown icon
   - Empty slots show "+" placeholder with "等待加入"

3. Chat area - Compact chat section with:
   - "房间聊天" header
   - 3-4 message bubbles showing recent messages
   - Input field + send button at bottom

4. Room settings card - Expandable section showing:
   - Speech mode toggle (轮流制/自由制)
   - AI fill toggle (开关)
   - Min player count selector

5. Action buttons (bottom area):
   - "准备" button (large, gold, full-width for non-host)
   - OR "开始游戏" button (for host, enabled when all ready)
   - "邀请好友" button (secondary, smaller)
   - "退出房间" button (text only, subtle)

Design specs:
- Screen size: 390x844px
- Player cards: dark background, rounded, status badge with color
- Ready status: green badge
- Not ready: gray badge
- Host crown: gold icon
- Chat bubbles: alternating alignment (left/right)
- Gold primary button with glow
- Secondary button: blue border, transparent fill
- Room number has copy icon
```

---

## 5. 游戏进行页 - 聊天界面

**页面名称：** 游戏进行 - 聊天界面
**用途：** 游戏核心交互界面，群聊对话

**提示词：**
```
Create a mobile app game chat screen during active gameplay, cyberpunk style.

Layout structure:
1. Game header - Top bar with:
   - Back arrow icon (left)
   - Act name: "第二幕·暗流涌动" in gold text
   - Countdown timer: "剩余 18:42" in blue text
   - Menu icon (right)

2. Chat message area - Scrollable messages:
   - NPC messages: avatar (left) + name tag + message bubble (dark background)
   - Player messages: avatar (right) + name tag + message bubble (blue background)
   - System messages: centered, small text, italic
   - Timestamp between message groups
   - Mix of 6-8 messages from different characters

3. Typing indicator - "苏晚晴 正在输入..." text above input area

4. Input area (bottom) - Fixed bar with:
   - Text input field (rounded, dark background)
   - Send button (circle, gold icon)
   - Private chat icon (small, left of input)

Design specs:
- Screen size: 390x844px
- Header: dark background with gold and blue accents
- Message bubbles: rounded corners, 12px radius
- NPC bubble: #1A1F2E background
- Player bubble: #4A7DFF background, white text
- Avatar circles: 40px diameter, colored background
- Name tags: colored text matching character
- Input bar: dark background, distinct from chat
- Timestamp: small, centered, gray text
- Smooth visual hierarchy
```

---

## 6. 游戏进行页 - 搜证界面

**页面名称：** 游戏进行 - 搜证界面
**用途：** 分配AP调查线索

**提示词：**
```
Create a mobile app evidence investigation screen, cyberpunk style.

Layout structure:
1. Investigation header - Top bar with:
   - Back arrow
   - "第一轮搜证" title
   - AP counter: "剩余 AP: 7 / 15" (large number, gold color)

2. Location cards (2 visible):
   Location 1 - "死者房间":
   - Location icon + name header
   - Subtitle: "发现尸体的地点，关键证据所在"
   - Investigation targets list:
     * "尸体周围区域" - progress bar 100%, checkmark (completed)
     * "个人物品" - progress bar 50%, "调查" button
     * "隐藏空间" - progress bar 0%, "调查" button (disabled)
   
   Location 2 - "客厅公共区域":
   - Similar structure, all targets uninvestigated
   - "调查" buttons available

3. Hint card - Highlighted card with:
   - "💡" icon
   - "NPC 苏晚晴提到死者日记本不见了"
   - "→ 可以在 NPC 房间里寻找"
   - Gold border, subtle glow

4. Bottom action bar:
   - "结束搜证" button (secondary)
   - "确认完成" button (primary, gold)

Design specs:
- Screen size: 390x844px
- Location cards: dark background, 1px border
- Progress bars: thin, 4px height, rounded
- Completed: green fill
- In progress: gold fill
- Not started: gray fill
- Hint card: gold border, warm background tint
- Investigation buttons: gold outline style
- Clean information hierarchy
```

---

## 7. 游戏进行页 - 个人资料

**页面名称：** 游戏进行 - 个人资料
**用途：** 查看个人游戏数据

**提示词：**
```
Create a mobile app profile stats screen during gameplay, cyberpunk style.

Layout structure:
1. Profile header - Large avatar (centered), nickname, membership badge below.

2. Stats cards (3 columns) - Three equal cards:
   - "侦探投票率" 78% (blue text)
   - "凶手逃脱率" 33% (red text)
   - "总场次" 156 (gold text)
   Each with label below the number.

3. Achievements section - "成就徽章 · 4枚" header, horizontal scroll of achievement badges (4 visible):
   - Each badge: icon + name (神探/影帝/铁证/博览)
   - Gold colored, rounded badges

4. Recent games list - "最近战绩" header, 3 game result cards:
   - "✅ 山庄晚宴 · 侦探 · 投对"
   - "❌ 午夜列车 · 凶手 · 被投出"
   - "✅ 密室疑云 · 普通 · 投对"
   Each with green/red result indicator.

Design specs:
- Screen size: 390x844px
- Avatar: 80px circle, colored background
- Stats cards: dark background, large numbers
- Achievement badges: gold border, compact
- Game results: alternating green/red icons
- Clean grid layout for stats
```

---

## 8. 游戏进行页 - 商城界面

**页面名称：** 游戏进行 - 商城界面
**用途：** 购买虚拟货币和商品

**提示词：**
```
Create a mobile app shop screen, cyberpunk style.

Layout structure:
1. Balance bar - Top section with:
   - Large star count: "⭐ 1280" (gold, large)
   - "充值" button (pill shape, gold fill)

2. Category tabs - Horizontal scroll tabs:
   - 推荐 (active, gold underline)
   - 皮肤
   - 头像框
   - 礼物
   - 限定
   Active tab has gold text and underline.

3. Product grid - 2-column grid of product cards:
   Each card contains:
   - Preview area (gradient background, product icon)
   - Badge if applicable (HOT/NEW/限定)
   - Product name
   - Price in stars
   
   6 products visible in 3 rows.

Design specs:
- Screen size: 390x844px
- Product cards: dark background, rounded
- Preview areas: colored gradients
- Price: gold text, prominent
- HOT/NEW badges: small, colored, top-right corner
- Grid: equal spacing, 2 columns
- Tabs: compact, underline active state
```

---

## 9. 排行榜

**页面名称：** 排行榜
**用途：** 查看各类排行榜

**提示词：**
```
Create a mobile app leaderboard screen, cyberpunk style.

Layout structure:
1. Header - "排行榜" title, centered, gold text.

2. Category tabs - Three tabs:
   - 推理榜 (active)
   - 社交榜
   - 贡献榜
   Active tab highlighted.

3. Top 3 showcase - Special display for top 3:
   - Center: #1 player (largest, gold frame, crown icon)
   - Left: #2 player (silver frame)
   - Right: #3 player (bronze frame)
   Each shows avatar, name, score.

4. Ranking list (positions 4-10) - Vertical list:
   Each row: rank number, avatar, nickname, score
   Rank numbers: 4-10 in gray text.
   Alternating row backgrounds for readability.

5. My rank - Fixed bottom card showing user's own rank:
   "我的排名: #42" with progress to next rank.

Design specs:
- Screen size: 390x844px
- Top 3: prominent display with medal colors
- Gold/Silver/Bronze frames for top 3
- List rows: dark background, subtle divider lines
- Score numbers: aligned right, gold text
- My rank card: distinct background, pinned at bottom
- Clean, competitive feel
```

---

## 10. 任务系统

**页面名称：** 任务系统
**用途：** 查看和完成任务获取奖励

**提示词：**
```
Create a mobile app task system screen, cyberpunk style.

Layout structure:
1. Header - "任务中心" title, with daily check-in icon.

2. Check-in card - Horizontal card showing:
   - 7-day calendar grid
   - Current day highlighted (gold)
   - Completed days checked (green)
   - "立即签到" button

3. Task categories - Tab or section headers:
   - 每日任务 (active)
   - 成就任务
   - 新手任务

4. Task list - Vertical list of tasks:
   Each task card:
   - Task icon (left)
   - Task name + description
   - Progress bar (X/Y complete)
   - Reward badge (star amount)
   - "领取" button (if complete, gold)
   - OR progress indicator (if in progress)
   
   5-6 tasks visible.

5. Total rewards - Summary at bottom:
   "今日可获得: 80⭐"

Design specs:
- Screen size: 390x844px
- Task cards: dark background, 1px border
- Progress bars: thin, colored fill
- Complete tasks: green accent
- In progress: blue accent
- Reward badges: gold, prominent
- Check-in card: 7-box grid, visual progress
```

---

## 11. 成就系统

**页面名称：** 成就系统
**用途：** 查看成就和解锁进度

**提示词：**
```
Create a mobile app achievement system screen, cyberpunk style.

Layout structure:
1. Header - "成就徽章" title, with total count "已获得: 32/56".

2. Recent achievement - Featured card showing:
   - "最近获得: [神探] 2026-05-20"
   - Achievement icon (large)
   - Rarity badge (史诗, purple)

3. In progress section - "进度中" header:
   - Progress cards:
     * "[博览群书] 17/20 ████░ 85%"
     * "[影帝] 2/3 ███░░ 67%"
   Each with progress bar and percentage.

4. Achievement grid - Categorized grid:
   Category headers: 推理类, 演技类, 社交类, 收藏类, 挑战类
   Each category shows achievement badges in a grid:
   - Unlocked: gold icon, full opacity
   - Locked: gray icon, 50% opacity
   - Each with name and rarity indicator

5. Hidden achievements - "隐藏成就: 已解锁 3/8 枚" at bottom.

Design specs:
- Screen size: 390x844px
- Achievement badges: circular or shield-shaped
- Rarity colors: 普通=gray, 稀有=blue, 史诗=purple, 传说=gold
- Progress bars: horizontal, colored fill
- Locked achievements: dimmed appearance
- Grid: 3-4 columns for badges
- Clean categorization
```

---

## 12. 社交广场

**页面名称：** 社交广场
**用途：** 浏览社交动态和好友

**提示词：**
```
Create a mobile app social feed screen, cyberpunk style.

Layout structure:
1. Header - "社交广场" title with search icon and "发布" (+) button.

2. Category tabs - Three tabs:
   - 动态 (active)
   - 好友
   - 关注
   Active tab highlighted with gold underline.

3. Create post card - Compact card with:
   - User avatar
   - "分享你的推理心得..." placeholder
   - Image/video icons
   - "发布" button

4. Feed cards - 3 social posts:
   Each post contains:
   - User avatar + name + tag
   - Post content (text)
   - Optional image(s)
   - Action bar: like/comment/share + timestamp
   - Comments count badge

5. Online friends - Side panel or section:
   - "在线好友" header
   - Friend list with avatars and online indicators (green dots)

Design specs:
- Screen size: 390x844px
- Feed cards: Weibo-style layout
- User avatars: circular, colored borders
- Tags: colored badges for user type
- Action bar: icon + count layout
- Online indicator: small green circle
- Clean, social media feel
```

---

## 13. 个人中心

**页面名称：** 个人中心
**用途：** 个人设置和功能入口

**提示词：**
```
Create a mobile app user profile/settings screen, cyberpunk style.

Layout structure:
1. Profile header - Large section with:
   - Avatar (large, circular)
   - Nickname
   - Membership badge (高级会员)
   - Signature text ("真相只有一个")
   - Edit profile button

2. Stats summary - 4 stats in a row:
   - 总场次 156
   - 胜率 78%
   - 成就 32
   - 星星 1280

3. Function list - Vertical list of menu items:
   Each row: icon + label + arrow
   - 战绩详情
   - 剧本记录
   - 收藏夹
   - 商城
   - 钱包
   - 设置
   - 邀请好友
   - 帮助中心

4. Settings submenu (accessible):
   - 账号安全
   - 隐私设置
   - 通知设置
   - 关于我们
   - 退出登录

5. Logout button - Bottom, red text, centered.

Design specs:
- Screen size: 390x844px
- Profile header: gradient background
- Stats: equal-width columns, large numbers
- Menu rows: icon + text + chevron, divider lines
- Icons: consistent style, 20px
- Clean, organized layout
- Logout: subtle but visible
```

---

## 14. 钱包/充值

**页面名称：** 钱包/充值
**用途：** 查看余额和充值

**提示词：**
```
Create a mobile app wallet/top-up screen, cyberpunk style.

Layout structure:
1. Balance card - Large card at top with:
   - "星星余额" label
   - Large number: "1,280" with star icon
   - Subtle gradient background

2. Quick actions - Row of action buttons:
   - 充值记录
   - 消费记录
   - 赠送记录
   Each with icon and label.

3. Top-up packages - Grid of recharge options:
   6 packages in 2x3 grid:
   - 60⭐ ¥6
   - 300⭐ ¥30
   - 680⭐ ¥68 (推荐, highlighted)
   - 1280⭐ ¥128
   - 3280⭐ ¥328
   - 6480⭐ ¥648 (额外赠送标记)
   Each shows stars, price, bonus if applicable.

4. Payment methods - Section showing:
   - 微信支付
   - 支付宝
   - Apple Pay
   With radio buttons.

5. Confirm button - Large "确认充值" button at bottom.

Design specs:
- Screen size: 390x844px
- Balance card: prominent, gradient background
- Package cards: dark background, price prominent
- Recommended package: gold border, "推荐" badge
- Bonus packages: green "额外赠送" text
- Payment methods: list with icons
- Confirm button: gold, full-width
```

---

## 15. 语音房间

**页面名称：** 语音房间
**用途：** 语音聊天和复盘

**提示词：**
```
Create a mobile app voice chat room screen, cyberpunk style.

Layout structure:
1. Room header - Top bar with:
   - Room name (editable)
   - Room number with copy icon
   - Close button

2. User grid - 3x3 or 4x2 grid of user cards:
   Each card shows:
   - Avatar (circular)
   - Nickname below
   - Microphone status icon (muted/unmuted)
   - Speaking indicator (audio waveform animation placeholder)
   - Host crown icon

3. Voice visualization - Audio waveform visualizer at top of grid:
   - Animated bars showing voice activity
   - Neon blue/green color

4. Chat panel - Collapsible section at bottom with:
   - Voice-to-text messages
   - Quick emoji buttons

5. Bottom controls - Fixed bar with 4 buttons:
   - 🎤 麦克风 (toggle, active=green)
   - 🔊 扬声器 (toggle)
   - 💬 聊天 (expand/collapse)
   - 🚪 离开房间 (red text)

Design specs:
- Screen size: 390x844px
- User cards: compact, rounded
- Avatar circles: 48px
- Speaking indicator: green glow around avatar
- Muted indicator: red slash icon
- Waveform: animated-style bars
- Bottom controls: large touch targets
- Dark, immersive feel
```

---

## 16. 回放系统

**页面名称：** 回放系统
**用途：** 查看历史对局回放

**提示词：**
```
Create a mobile app game replay playback screen, cyberpunk style.

Layout structure:
1. Playback header - Top bar with:
   - Back button
   - Script name: "山庄晚宴"
   - Date: "2026-05-24"
   - Share button

2. Video player area - Large rectangular area:
   - Game screen reproduction
   - Play/pause overlay icon
   - Current timestamp overlay

3. Playback controls - Below player:
   - Timeline scrubber with event markers
   - ⏮️ ⏯️ ⏭️ buttons
   - Current time / Total time: "12:34 / 78:00"
   - Speed selector: 0.5x / 1x / 1.5x / 2x

4. Chapter markers - Horizontal list of chapters:
   - 第一幕
   - 第一轮搜证
   - 第二幕
   - 第二轮搜证
   - 最终投票
   Each clickable for quick navigation.

5. Player list - Side panel showing:
   - Player avatars
   - Character names
   - Role reveal (after game end)
   - Current speaker highlighted

6. Info tabs - Bottom tabs:
   - 对话记录
   - 线索时间线
   - 投票详情

Design specs:
- Screen size: 390x844px
- Video area: 16:9 ratio or larger
- Timeline: thin line with colored markers
- Event markers: small dots on timeline
- Player list: compact avatars
- Chapter markers: pill-shaped buttons
- Controls: intuitive, media player style
- Dark, cinematic feel
```

---

## 17. 推理笔记增强版

**页面名称：** 推理笔记增强版
**用途：** 整理线索和推理思路

**提示词：**
```
Create a mobile app investigation notes/canvas screen, cyberpunk style.

Layout structure:
1. Canvas toolbar - Top bar with:
   - Back to game button
   - Note title (editable)
   - Auto-save indicator
   - Export/share button

2. Tool palette - Floating tools:
   - ✋ 拖拽模式
   - ➕ 添加卡片
   - 🔗 连线模式
   - 🎨 颜色选择
   - 📝 便利贴
   Each as icon buttons.

3. Infinite canvas - Main area showing:
   - Clue cards scattered (4-5 visible):
     * Each card: title, description, source icon
     * Cards have colored borders by type
   - Character cards (2-3 visible):
     * Avatar + name + notes
   - Connection lines between cards:
     * Solid lines for confirmed links
     * Dashed lines for suspected links
   - Sticky notes with free text

4. Sidebar - Collapsible panel with:
   - 线索库 (list of discovered clues)
   - 角色信息 (character list)
   - 时间线 (event timeline)

5. Bottom bar - Zoom controls:
   - Zoom percentage
   - +/- buttons
   - Reset view button

Design specs:
- Screen size: 390x844px
- Canvas: light grid background (subtle)
- Clue cards: dark backgrounds, colored borders
- Card types: evidence=purple, person=blue, timeline=green
- Connection lines: thin, colored
- Sidebar: slide-in panel, dark overlay
- Tools: floating, compact icons
- Mind-map feel
```

---

## 18. 邀请好友

**页面名称：** 邀请好友
**用途：** 邀请新用户注册获取奖励

**提示词：**
```
Create a mobile app invite friends screen, cyberpunk style.

Layout structure:
1. Hero banner - Top promotional card:
   - "邀请好友 赢取奖励" title
   - Reward summary: "最高可得 500⭐"
   - Decorative graphic

2. My invite code - Prominent card:
   - "我的邀请码" label
   - Large code: "A1B2C3"
   - Copy button
   - QR code preview (small)
   - Share link with copy icon

3. Quick share buttons - Row of platform buttons:
   - 微信好友
   - 微信朋友圈
   - QQ
   - 复制链接
   Each with platform icon and label.

4. Invite stats - Summary card:
   - 已邀请: 12人
   - 已注册: 8人
   - 首通: 5人
   - 累计奖励: 350⭐

5. Reward details - List of reward tiers:
   - 好友注册 → +10⭐
   - 好友首通 → +50⭐
   - 好友充值 → 返利10%
   Each with status indicator.

6. Invite history - Recent invites list:
   - User avatar/name
   - Register date
   - Reward status (已领取/待领取)
   - Claim button if available

Design specs:
- Screen size: 390x844px
- Hero banner: gradient background, promotional
- Invite code: large, prominent text
- QR code: square, scannable
- Share buttons: platform-colored icons
- Stats: grid or row layout
- Reward tiers: clear list with icons
- History: compact rows with status badges
```

---

## 19. 新手指引

**页面名称：** 新手指引
**用途：** 帮助新用户了解游戏

**提示词：**
```
Create a mobile app beginner tutorial/onboarding screen, cyberpunk style.

Layout structure:
1. Welcome area - Top section with:
   - Welcome illustration/animation placeholder
   - "欢迎来到AI推理叙事游戏" title
   - Brief description text
   - "开始引导" button

2. Tutorial steps - Vertical stepper:
   Step 1: 基础概念 (active)
   - Icon + title
   - Description text
   - Demo video/image placeholder
   - "下一步" button
   
   Step 2: 游戏流程
   - Similar structure, grayed out (not active)
   
   Step 3: 核心机制
   Step 4: 界面导览
   Step 5: 实战演练
   Step 6: 完成引导

3. Progress indicator - Top or bottom:
   - Step dots (1-6)
   - Current step highlighted
   - Completed steps checked

4. Quick reference - Collapsible section:
   - 术语词典 link
   - 操作指南 link
   - 视频教程 link

5. Skip option - "跳过引导" text button at bottom.

Design specs:
- Screen size: 390x844px
- Stepper: vertical, connected lines
- Active step: gold highlight
- Completed steps: green checkmarks
- Inactive steps: gray text
- Demo areas: placeholder boxes
- Progress dots: horizontal at top
- Clean, educational feel
```

---

## 20. FAQ帮助中心

**页面名称：** FAQ帮助中心
**用途：** 常见问题自助查询

**提示词：**
```
Create a mobile app FAQ/help center screen, cyberpunk style.

Layout structure:
1. Search area - Top section with:
   - Large search bar "搜索问题..."
   - Hot searches: "如何充值", "AP是什么", "怎么邀请好友"

2. Category navigation - Horizontal scroll or grid:
   - 新手入门
   - 账号相关
   - 游戏玩法
   - 充值消费
   - 社交功能
   - 技术问题
   Each with icon and label.

3. Featured questions - "常见问题" section:
   - Question list with expandable items:
     * "如何开始一局游戏？" 👍/👎 feedback
     * "AP是什么？如何使用？"
     * "如何邀请好友一起玩？"
     * "充值后星星没到账怎么办？"
   Each with view count and useful/unused feedback.

4. Expanded answer (when tapped):
   - Question title
   - Detailed answer text
   - Related images/screenshots
   - Related questions suggestions
   - "未解决？联系客服" link

5. Quick actions - Bottom section:
   - 在线客服 button
   - 意见反馈 button
   - 视频教程 button

Design specs:
- Screen size: 390x844px
- Search bar: prominent, rounded
- Category icons: consistent style
- Questions: accordion-style, expandable
- Feedback buttons: small thumbs up/down
- Expanded answers: indented, distinct background
- Quick action buttons: full-width, stacked
- Clean, help-center feel
```

---

## 21. 客服系统

**页面名称：** 客服系统
**用途：** 联系智能客服和人工客服

**提示词：**
```
Create a mobile app customer service chat screen, cyberpunk style.

Layout structure:
1. Header - "客服中心" title with:
   - Back button
   - Queue status: "排队中: 第3位" (if waiting)

2. Service type selector - 3 options:
   - 🤖 智能客服 (active)
   - 👤 人工客服
   - 📝 提交工单

3. Chat area - Message thread:
   - Bot welcome message
   - Quick action buttons:
     * "如何充值"
     * "账号问题"
     * "游戏问题"
     * "其他"
   - User messages (right aligned, blue)
   - Bot responses (left aligned, dark)
   - Suggested follow-up questions

4. Input area - Bottom fixed bar:
   - Text input field
   - Image upload button
   - Send button
   - "转人工" button (small)

5. Ticket list (if 工单 selected):
   - 进行中工单
   - 已解决工单
   - 新建工单 button

Design specs:
- Screen size: 390x844px
- Chat bubbles: messaging app style
- Bot messages: dark background
- User messages: blue background
- Quick buttons: pill-shaped, horizontal
- Service selector: tab-style
- Queue status: prominent if waiting
- Clean chat interface
```

---

## 22. 隐私协议

**页面名称：** 隐私协议
**用途：** 展示隐私政策和用户协议

**提示词：**
```
Create a mobile app privacy policy/terms of service screen, cyberpunk style.

Layout structure:
1. Header - "隐私协议" title with:
   - Back button
   - Table of contents button (📑)

2. Document tabs - Horizontal tabs:
   - 隐私政策 (active)
   - 用户协议
   - 数据收集说明
   - Cookie政策

3. Document info - Metadata bar:
   - 生效日期: 2026-01-01
   - 更新日期: 2026-05-24
   - 版本号: v1.0

4. Document content - Scrollable rich text:
   - Section headers (numbered: 1, 2, 3...)
   - Body text paragraphs
   - Bullet lists
   - Highlighted boxes for important notices
   - Proper text hierarchy (H1, H2, body)

5. Table of contents sidebar - Overlay panel:
   - List of all sections
   - Clickable for quick navigation

6. Bottom action bar - First-time view only:
   - "已阅读并同意" checkbox
   - "同意并继续" button (gold, full-width)
   - "不同意" text button (below)

Design specs:
- Screen size: 390x844px
- Document text: readable, proper spacing
- Section headers: bold, larger text
- Highlighted boxes: subtle background tint
- Tabs: compact, underline active
- TOC: slide-out panel
- Agreement bar: pinned at bottom
- Legal document feel, but on-theme
```

---

## 生成顺序建议

按照以下顺序生成页面，保持一致性：

1. **首页** - 奠定整体视觉风格
2. **剧本列表页** - 扩展列表模式
3. **剧本详情页** - 详情展示模式
4. **游戏房间** - 社交准备模式
5. **聊天界面** - 核心游戏模式
6. **搜证界面** - 游戏功能模式
7. **个人中心** - 用户信息模式
8. **钱包/充值** - 商业化模式
9. **社交广场** - 社区模式
10. **排行榜** - 竞争展示模式
11. **任务系统** - 成就系统模式
12. **成就系统** - 收集展示模式
13. **商城** - 购物模式
14. **语音房间** - 实时通讯模式
15. **回放系统** - 媒体播放模式
16. **推理笔记** - 画布模式
17. **邀请好友** - 增长模式
18. **新手指引** - 教学模式
19. **FAQ帮助中心** - 帮助模式
20. **客服系统** - 服务模式
21. **隐私协议** - 法律文档模式

---

## 注意事项

1. **统一元素**：Tab Bar、搜索框、按钮样式在所有页面保持一致
2. **色彩一致**：严格使用定义的色彩变量，不要偏离
3. **圆角统一**：卡片12px，按钮8px，标签4px
4. **字体层级**：标题24px > 副标题18px > 正文14px > 小字12px > 微字10px
5. **发光效果**：仅在激活/重要元素上使用发光效果
6. **深色主题**：所有页面必须使用深色背景
7. **响应式**：基于iPhone尺寸（390x844px或430x932px）
8. **留白**：页面元素之间保持12-16px间距
9. **图标风格**：线性图标，stroke 1.5px，统一风格
10. **霓虹质感**：边框发光、渐变、科技感，但不要过度花哨
