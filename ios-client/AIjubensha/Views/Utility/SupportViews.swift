//
//  MessageListView.swift
//  AI推理叙事游戏 - 消息列表
//

import SwiftUI

struct MessageListView: View {
    @State private var messages: [GameMessage] = []
    @State private var isLoading = true

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            ScrollView {
                LazyVStack(spacing: Spacing.sm) {
                    ForEach(messages) { msg in
                        MessageRow(message: msg)
                    }
                }
                .padding(.horizontal, Spacing.containerPadding)
                .padding(.top, Spacing.md)

                if isLoading {
                    ProgressView().frame(maxWidth: .infinity, minHeight: 200)
                }
            }
        }
        .navigationTitle("消息")
        .task { await loadMessages() }
    }

    private func loadMessages() async {
        isLoading = true
        try? await Task.sleep(nanoseconds: 300_000_000)
        withAnimation {
            messages = [
                GameMessage(type: "game", title: "山庄晚宴 - 游戏结束", subtitle: "你投对了凶手！+20星", time: "10分钟前", isRead: false),
                GameMessage(type: "friend", title: "推理小王 请求添加好友", subtitle: "", time: "1小时前", isRead: false),
                GameMessage(type: "system", title: "新剧本上线", subtitle: "《午夜列车》已上线，快来体验！", time: "3小时前", isRead: true),
                GameMessage(type: "gift", title: "收到礼物", subtitle: "探案达人 送了你一朵花", time: "昨天", isRead: true),
                GameMessage(type: "achievement", title: "成就解锁", subtitle: "恭喜解锁「初出茅庐」", time: "昨天", isRead: true),
            ]
        }
        isLoading = false
    }
}

struct GameMessage: Identifiable {
    let id = UUID()
    let type: String
    let title: String
    let subtitle: String
    let time: String
    let isRead: Bool
}

struct MessageRow: View {
    let message: GameMessage

    var typeIcon: String {
        switch message.type {
        case "game": return "gamecontroller.fill"
        case "friend": return "person.badge.plus"
        case "system": return "bell.fill"
        case "gift": return "gift.fill"
        case "achievement": return "star.fill"
        default: return "bubble.left.fill"
        }
    }

    var typeColor: Color {
        switch message.type {
        case "game": return Theme.accentPrimary
        case "friend": return Theme.accentBlue
        case "system": return Theme.accentWarning
        case "gift": return Theme.accentPink
        case "achievement": return Theme.accentGold
        default: return Theme.textTertiary
        }
    }

    var body: some View {
        HStack(spacing: Spacing.md) {
            Image(systemName: typeIcon)
                .foregroundStyle(typeColor)
                .frame(width: 32, height: 32)
                .background(typeColor.opacity(0.15))
                .cornerRadius(Radius.sm)

            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(message.title)
                    .font(Typography.headingSM)
                    .foregroundStyle(message.isRead ? Theme.textSecondary : Theme.textPrimary)
                if !message.subtitle.isEmpty {
                    Text(message.subtitle)
                        .font(Typography.caption)
                        .foregroundStyle(Theme.textTertiary)
                }
            }

            Spacer()
            Text(message.time)
                .font(Typography.captionTiny)
                .foregroundStyle(Theme.textTertiary)

            if !message.isRead {
                Circle()
                    .fill(Theme.accentError)
                    .frame(width: 8, height: 8)
            }
        }
        .padding()
        .background(Theme.bgCard)
        .cornerRadius(Radius.md)
        .overlay(
            RoundedRectangle(cornerRadius: Radius.md)
                .stroke(Theme.borderCard, lineWidth: 1)
        )
    }
}

// MARK: - Inference Notes View
struct InferenceNotesView: View {
    @State private var clues: [ClueNote] = []
    @State private var timeline: [TimelineEvent] = []
    @State private var selectedTab = 0

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            VStack(spacing: 0) {
                Picker("", selection: $selectedTab) {
                    Text("线索").tag(0)
                    Text("时间线").tag(1)
                    Text("关系图").tag(2)
                }
                .pickerStyle(.segmented)
                .padding(.horizontal, Spacing.containerPadding)
                .padding(.bottom, Spacing.md)

                if selectedTab == 0 {
                    CluesTab(clues: clues)
                } else if selectedTab == 1 {
                    TimelineTab(events: timeline)
                } else {
                    RelationshipGraphPlaceholder()
                }
            }
        }
        .navigationTitle("推理笔记")
        .onAppear {
            clues = [
                ClueNote(id: "c1", name: "指纹", description: "死者房间门把手上发现不完整指纹", location: "死者房间"),
                ClueNote(id: "c2", name: "红酒", description: "茶几上两杯未喝完的红酒，其中一杯有毒", location: "客厅"),
                ClueNote(id: "c3", name: "日记", description: "死者日记显示最近有人跟踪", location: "书房"),
            ]
            timeline = [
                TimelineEvent(time: "19:00", event: "所有人到达山庄"),
                TimelineEvent(time: "20:30", event: "死者与苏晚晴在画廊争吵"),
                TimelineEvent(time: "21:00", event: "死者回到房间"),
                TimelineEvent(time: "22:00", event: "尸体被发现"),
            ]
        }
    }
}

struct ClueNote: Identifiable {
    let id: String
    let name: String
    let description: String
    let location: String
}

struct TimelineEvent: Identifiable {
    let id = UUID()
    let time: String
    let event: String
}

struct CluesTab: View {
    let clues: [ClueNote]

    var body: some View {
        ScrollView {
            LazyVStack(spacing: Spacing.md) {
                ForEach(clues) { clue in
                    CardContainer {
                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            HStack {
                                Image(systemName: "magnifyingglass")
                                    .foregroundStyle(Theme.accentPrimary)
                                Text(clue.name)
                                    .font(Typography.headingSM)
                                    .foregroundStyle(Theme.textPrimary)
                            }
                            Text(clue.description)
                                .font(Typography.bodySecondary)
                                .foregroundStyle(Theme.textSecondary)
                            Text("发现地点: \(clue.location)")
                                .font(Typography.captionTiny)
                                .foregroundStyle(Theme.textTertiary)
                        }
                        .padding(Spacing.lg)
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                }
            }
            .padding(.bottom, 100)
        }
    }
}

struct TimelineTab: View {
    let events: [TimelineEvent]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                ForEach(Array(events.enumerated()), id: \.element.id) { index, event in
                    HStack(alignment: .top, spacing: Spacing.md) {
                        VStack {
                            Circle()
                                .fill(Theme.accentPrimary)
                                .frame(width: 12, height: 12)
                            if index < events.count - 1 {
                                Rectangle()
                                    .frame(width: 2, height: 40)
                                    .foregroundStyle(Theme.borderCard)
                            }
                        }
                        .padding(.top, Spacing.sm)

                        VStack(alignment: .leading, spacing: Spacing.xs) {
                            Text(event.time)
                                .font(.system(size: 14, weight: .bold, design: .monospaced))
                                .foregroundStyle(Theme.accentPrimary)
                            Text(event.event)
                                .font(Typography.body)
                                .foregroundStyle(Theme.textSecondary)
                        }
                        .padding(.bottom, Spacing.lg)
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                }
            }
            .padding(.bottom, 100)
        }
    }
}

struct RelationshipGraphPlaceholder: View {
    var body: some View {
        VStack(spacing: Spacing.lg) {
            Image(systemName: "circle.grid.cross")
                .font(.system(size: 48))
                .foregroundStyle(Theme.textTertiary)
            Text("关系图谱")
                .font(Typography.headingMD)
                .foregroundStyle(Theme.textPrimary)
            Text("拖拽角色节点，连线标注关系")
                .font(Typography.bodySecondary)
                .foregroundStyle(Theme.textTertiary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

// MARK: - Help Center View
struct HelpCenterView: View {
    @State private var expandedItem: String?

    let faqs: [(String, String)] = [
        ("如何开始游戏？", "在首页选择剧本后点击「开始游戏」，或在房间列表加入/创建房间。"),
        ("AP是什么？", "AP（调查行动点）是搜证阶段使用的资源，每轮有固定的AP配额。"),
        ("L1-L4线索是什么？", "线索分为4个等级，L1最浅层，L4最核心。需要逐步解锁。"),
        ("AI NPC会说谎吗？", "只有凶手NPC会在特定范围内说谎，其他NPC必须说真话。"),
        ("如何解锁新剧本？", "使用星星兑换或在商城购买剧本，订阅会员可每月免费体验5个剧本。"),
    ]

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.lg) {
                    Text("常见问题")
                        .font(Typography.headingMD)
                        .foregroundStyle(Theme.textPrimary)
                        .padding(.horizontal, Spacing.containerPadding)

                    ForEach(faqs, id: \.0) { faq in
                        FAQRow(question: faq.0, answer: faq.1, isExpanded: expandedItem == faq.0) {
                            withAnimation {
                                expandedItem = expandedItem == faq.0 ? nil : faq.0
                            }
                        }
                    }
                }
                .padding(.top, Spacing.xl)
                .padding(.bottom, 100)
            }
        }
        .navigationTitle("帮助中心")
    }
}

struct FAQRow: View {
    let question: String
    let answer: String
    let isExpanded: Bool
    let onTap: () -> Void

    var body: some View {
        CardContainer {
            Button(action: onTap) {
                VStack(alignment: .leading, spacing: Spacing.sm) {
                    HStack {
                        Text(question)
                            .font(Typography.headingSM)
                            .foregroundStyle(Theme.textPrimary)
                        Spacer()
                        Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                            .foregroundStyle(Theme.textTertiary)
                    }
                    if isExpanded {
                        Text(answer)
                            .font(Typography.bodySecondary)
                            .foregroundStyle(Theme.textSecondary)
                            .padding(.top, Spacing.xs)
                    }
                }
                .padding(Spacing.lg)
            }
            .buttonStyle(PlainButtonStyle())
        }
        .padding(.horizontal, Spacing.containerPadding)
    }
}

// MARK: - Privacy Policy View
struct PrivacyPolicyView: View {
    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()
            ScrollView {
                VStack(alignment: .leading, spacing: Spacing.lg) {
                    ForEach(privacySections, id: \.title) { section in
                        VStack(alignment: .leading, spacing: Spacing.sm) {
                            Text(section.title)
                                .font(Typography.headingMD)
                                .foregroundStyle(Theme.textPrimary)
                            Text(section.content)
                                .font(Typography.bodySecondary)
                                .foregroundStyle(Theme.textSecondary)
                                .lineSpacing(4)
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                    }
                }
                .padding(.top, Spacing.xl)
                .padding(.bottom, 100)
            }
        }
        .navigationTitle("隐私政策")
    }

    var privacySections: [(title: String, content: String)] {
        [
            (title: "信息收集", content: "我们仅收集必要的用户信息用于账号登录和游戏数据同步，包括用户名、邮箱、游戏记录等。不会收集位置、通讯录等敏感信息。"),
            (title: "信息使用", content: "收集的信息仅用于：1）提供游戏服务；2）改善用户体验；3）处理付费订单。我们不会将您的信息出售给第三方。"),
            (title: "AI对话数据", content: "游戏中的AI对话记录会被加密存储，用于优化NPC行为模型。您可以随时在设置中删除个人对话数据。"),
            (title: "数据保护", content: "我们采用行业标准加密技术保护您的数据安全。服务器数据定期备份，防止数据丢失。"),
            (title: "未成年人保护", content: "本产品不适合12岁以下用户使用。未成年人在使用本产品时应在监护人指导下进行。"),
        ]
    }
}

// MARK: - Recharge View (Enhanced)
struct WalletRechargeView: View {
    @Environment(\.dismiss) var dismiss
    @State private var selectedTier: Int = 0

    let tiers = [
        (amount: 6, stars: 60, bonus: 0),
        (amount: 30, stars: 310, bonus: 10),
        (amount: 68, stars: 710, bonus: 30),
        (amount: 128, stars: 1360, bonus: 80),
        (amount: 328, stars: 3560, bonus: 280),
        (amount: 648, stars: 7160, bonus: 680),
    ]

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()
                ScrollView {
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: Spacing.listGap) {
                        ForEach(Array(tiers.enumerated()), id: \.offset) { index, tier in
                            RechargeTierCard(
                                tier: tier,
                                isSelected: selectedTier == index
                            ) {
                                selectedTier = index
                            }
                        }
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.top, Spacing.md)

                    NeonButton(title: "确认充值 ¥\(tiers[selectedTier].amount)", action: {}, isLoading: false)
                        .padding(.horizontal, Spacing.containerPadding)
                        .padding(.top, Spacing.xl)
                }
            }
            .navigationTitle("充值")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("取消") { dismiss() }
                        .foregroundStyle(Theme.accentPrimary)
                }
            }
        }
    }
}

struct RechargeTierCard: View {
    let tier: (amount: Int, stars: Int, bonus: Int)
    let isSelected: Bool
    let onSelect: () -> Void

    var body: some View {
        Button(action: onSelect) {
            VStack(spacing: Spacing.sm) {
                Text("\(tier.stars) 星")
                    .font(Typography.headingMD)
                    .foregroundStyle(Theme.textPrimary)
                if tier.bonus > 0 {
                    Text("含赠送 \(tier.bonus) 星")
                        .font(Typography.captionTiny)
                        .foregroundStyle(Theme.accentGreen)
                }
                Text("¥\(tier.amount)")
                    .font(Typography.headingSM)
                    .foregroundStyle(Theme.accentPrimary)
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(isSelected ? Theme.accentPrimary.opacity(0.15) : Theme.bgCard)
            .cornerRadius(Radius.md)
            .overlay(
                RoundedRectangle(cornerRadius: Radius.md)
                    .stroke(isSelected ? Theme.accentPrimary : Theme.borderCard, lineWidth: isSelected ? 2 : 1)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - All-Call (喊话) Edit View
struct AllCallEditView: View {
    @Environment(\.dismiss) var dismiss
    @State private var content = ""
    let maxLength = 100

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()
                VStack(spacing: Spacing.xl) {
                    TextEditor(text: $content)
                        .font(Typography.body)
                        .foregroundStyle(Theme.textPrimary)
                        .padding()
                        .background(Theme.bgCard)
                        .cornerRadius(Radius.md)
                        .frame(minHeight: 150)
                        .padding(.horizontal, Spacing.containerPadding)

                    HStack {
                        Spacer()
                        Text("\(content.count)/\(maxLength)")
                            .font(Typography.caption)
                            .foregroundStyle(content.count > maxLength ? Theme.accentError : Theme.textTertiary)
                    }
                    .padding(.horizontal, Spacing.containerPadding)

                    NeonButton(title: "发送喊话", action: { if !content.isEmpty && content.count <= maxLength { dismiss() } }, isLoading: false)
                        .padding(.horizontal, Spacing.containerPadding)
                }
                .padding(.top, Spacing.xl)
            }
            .navigationTitle("全服喊话")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") { dismiss() }
                        .foregroundStyle(Theme.textSecondary)
                }
            }
        }
    }
}

// MARK: - Customer Service View
struct CustomerServiceView: View {
    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()
            ScrollView {
                VStack(spacing: Spacing.xl) {
                    CardContainer {
                        VStack(spacing: Spacing.md) {
                            Image(systemName: "headphones")
                                .font(.system(size: 48))
                                .foregroundStyle(Theme.accentPrimary)
                            Text("联系客服")
                                .font(Typography.headingMD)
                                .foregroundStyle(Theme.textPrimary)
                            Text("工作日 9:00-18:00 在线")
                                .font(Typography.bodySecondary)
                                .foregroundStyle(Theme.textTertiary)
                        }
                        .padding(Spacing.xl)
                    }
                    .padding(.horizontal, Spacing.containerPadding)

                    VStack(spacing: Spacing.md) {
                        GhostButton(title: "📧 邮件反馈", action: {})
                        GhostButton(title: "💬 在线客服", action: {})
                        GhostButton(title: "📖 查看帮助文档", action: {})
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                }
                .padding(.top, Spacing.xl)
            }
        }
        .navigationTitle("客服中心")
    }
}

// MARK: - Tutorial View
struct TutorialView: View {
    @Environment(\.dismiss) var dismiss
    @State private var currentStep = 0

    let tutorialSteps: [(title: String, content: String, icon: String)] = [
        (title: "欢迎来到推理叙事", content: "在这里，你将扮演剧本中的角色，与AI NPC一起揭开案件的真相。", icon: "sparkles"),
        (title: "对话互动", content: "通过群聊和私聊与NPC互动，提问、质疑、套话，获取线索。", icon: "bubble.left.and.bubble.right"),
        (title: "搜证系统", content: "每轮搜证获得AP，分配到不同调查目标。线索之间有依赖关系。", icon: "magnifyingglass"),
        (title: "最终投票", content: "根据所有线索和对话，投票指认真凶。投对获胜，投错失败。", icon: "checkmark.seal"),
    ]

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            VStack(spacing: Spacing.xxl) {
                Image(systemName: tutorialSteps[currentStep].icon)
                    .font(.system(size: 64))
                    .foregroundStyle(Theme.accentPrimary)

                Text(tutorialSteps[currentStep].title)
                    .font(Typography.headingLG)
                    .foregroundStyle(Theme.textPrimary)

                Text(tutorialSteps[currentStep].content)
                    .font(Typography.bodySecondary)
                    .foregroundStyle(Theme.textSecondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, Spacing.xxl)

                // Page indicator
                HStack(spacing: Spacing.sm) {
                    ForEach(0..<tutorialSteps.count, id: \.self) { i in
                        Circle()
                            .fill(i == currentStep ? Theme.accentPrimary : Theme.textTertiary)
                            .frame(width: 8, height: 8)
                    }
                }

                if currentStep < tutorialSteps.count - 1 {
                    NeonButton(title: "下一步", action: { currentStep += 1 }, isLoading: false)
                        .padding(.horizontal, Spacing.xxl)
                } else {
                    NeonButton(title: "开始推理之旅", action: { dismiss() }, isLoading: false)
                        .padding(.horizontal, Spacing.xxl)
                }
            }
        }
        .navigationBarHidden(true)
    }
}
