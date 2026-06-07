//
//  DiscussionPhaseView.swift
//  AI推理叙事游戏 - 讨论阶段（第一幕轮流发言、自由发言、第二幕、第三幕）
//

import SwiftUI

struct DiscussionPhaseView: View {
    let phaseType: DiscussionPhaseType
    @State private var messages: [ChatMessage] = []
    @State private var inputText = ""
    @State private var isTyping = false
    @State private var showPrivateChat = false
    @State private var showEvidenceBoard = false
    @State private var timeRemaining: Int
    @State private var speechCount = 0
    let maxSpeechCount = 15

    init(phaseType: DiscussionPhaseType, timeLimit: Int) {
        self.phaseType = phaseType
        self._timeRemaining = State(initialValue: timeLimit)
    }

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            VStack(spacing: 0) {
                // Phase header
                HStack {
                    VStack(alignment: .leading, spacing: Spacing.xs) {
                        Text(phaseType.title)
                            .font(Typography.headingMD)
                            .foregroundStyle(Theme.textPrimary)
                        Text(phaseType.subtitle)
                            .font(Typography.caption)
                            .foregroundStyle(Theme.textTertiary)
                    }
                    Spacer()
                    TimerBadge(seconds: timeRemaining)
                }
                .padding(.horizontal, Spacing.containerPadding)
                .padding(.vertical, Spacing.md)
                .background(Theme.bgBottomBar)

                // Speech counter
                if phaseType.hasSpeechLimit {
                    HStack {
                        Text("发言: \(speechCount)/\(maxSpeechCount)")
                            .font(Typography.caption)
                            .foregroundStyle(speechCount >= maxSpeechCount ? Theme.accentError : Theme.textTertiary)
                        Spacer()
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.top, Spacing.sm)
                }

                // Chat area
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: Spacing.lg) {
                            ForEach(messages) { message in
                                MessageBubble(message: message)
                            }
                            if isTyping {
                                TypingIndicator()
                            }
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                        .padding(.top, Spacing.md)
                    }
                    .onChange(of: messages.count) {
                        if let lastId = messages.last?.id {
                            proxy.scrollTo(lastId, anchor: .bottom)
                        }
                    }
                }

                // Action bar
                HStack(spacing: Spacing.md) {
                    Button(action: { showEvidenceBoard = true }) {
                        Image(systemName: "briefcase.fill")
                            .font(.system(size: 18))
                            .foregroundStyle(Theme.accentPrimary)
                    }

                    Button(action: { showPrivateChat = true }) {
                        Image(systemName: "bubble.left.and.bubble.right.fill")
                            .font(.system(size: 18))
                            .foregroundStyle(Theme.accentPrimary)
                    }

                    TextField("输入消息...", text: $inputText)
                        .font(Typography.body)
                        .foregroundStyle(Theme.textPrimary)
                        .padding(.vertical, Spacing.md)
                        .padding(.horizontal, Spacing.lg)
                        .background(Theme.bgSearchBar)
                        .cornerRadius(Radius.md)
                        .overlay(
                            RoundedRectangle(cornerRadius: Radius.md)
                                .stroke(Theme.borderCard, lineWidth: 1)
                        )

                    Button(action: sendMessage) {
                        Image(systemName: "paperplane.fill")
                            .font(.system(size: 18))
                            .foregroundStyle(inputText.isEmpty ? Theme.textTertiary : Theme.accentPrimary)
                    }
                    .disabled(inputText.isEmpty || (phaseType.hasSpeechLimit && speechCount >= maxSpeechCount))
                }
                .padding(.horizontal, Spacing.containerPadding)
                .padding(.vertical, Spacing.md)
                .background(Theme.bgBottomBar)
            }
        }
        .navigationTitle(phaseType.title)
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showPrivateChat) {
            PrivateChatView(targetName: "苏晚晴")
        }
        .sheet(isPresented: $showEvidenceBoard) {
            EvidenceBoardView(clues: [])
        }
        .onReceive(Timer.publish(every: 1, on: .main, in: .common).autoconnect()) { _ in
            if timeRemaining > 0 {
                timeRemaining -= 1
            }
        }
        .onAppear {
            // Add phase-specific system message
            messages.append(ChatMessage(
                sender_id: "system",
                sender_name: "",
                content: phaseType.systemMessage,
                is_system: true
            ))
        }
    }

    private func sendMessage() {
        guard !inputText.isEmpty else { return }
        if phaseType.hasSpeechLimit && speechCount >= maxSpeechCount { return }

        messages.append(ChatMessage(
            sender_id: "player_001",
            sender_name: "我",
            content: inputText
        ))
        speechCount += 1
        let sentContent = inputText
        inputText = ""

        isTyping = true
        Task {
            try? await Task.sleep(nanoseconds: 1_000_000_000)
            withAnimation {
                messages.append(ChatMessage(
                    sender_id: "npc_001",
                    sender_name: "苏晚晴",
                    content: "关于这件事...我记得不太清楚了。",
                    is_ai: true
                ))
                isTyping = false
            }
        }
    }
}

// MARK: - Phase Types
enum DiscussionPhaseType {
    case act1Turn       // 第一幕轮流发言
    case act1Free       // 第一幕自由发言
    case act2Discuss    // 第二幕集中讨论
    case act3Discuss    // 第三幕最终讨论

    var title: String {
        switch self {
        case .act1Turn: return "轮流发言"
        case .act1Free: return "自由交流"
        case .act2Discuss: return "集中讨论"
        case .act3Discuss: return "最终讨论"
        }
    }

    var subtitle: String {
        switch self {
        case .act1Turn: return "每人限时3分钟"
        case .act1Free: return "自由发言阶段"
        case .act2Discuss: return "证据展示 + 自由讨论"
        case .act3Discuss: return "焦点收窄，最终推理"
        }
    }

    var systemMessage: String {
        switch self {
        case .act1Turn: return "第一幕开始。请各位玩家依次发言，介绍自己的身份和到场原因。"
        case .act1Free: return "自由交流开始。你可以向任何人提问或回应。"
        case .act2Discuss: return "第二幕讨论开始。请展示你发现的线索，并继续质问NPC。"
        case .act3Discuss: return "最终讨论。请整理所有线索，做出你的最终推理。"
        }
    }

    var hasSpeechLimit: Bool {
        switch self {
        case .act1Turn: return true
        case .act1Free: return true
        default: return false
        }
    }
}

// MARK: - Private Chat View
struct PrivateChatView: View {
    let targetName: String
    @Environment(\.dismiss) var dismiss
    @State private var inputText = ""
    @State private var messages: [ChatMessage] = []

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()
                VStack(spacing: 0) {
                    ScrollViewReader { proxy in
                        ScrollView {
                            LazyVStack(spacing: Spacing.lg) {
                                ForEach(messages) { message in
                                    MessageBubble(message: message)
                                }
                            }
                            .padding(.horizontal, Spacing.containerPadding)
                            .padding(.top, Spacing.md)
                        }
                        .onChange(of: messages.count) {
                            if let lastId = messages.last?.id {
                                proxy.scrollTo(lastId, anchor: .bottom)
                            }
                        }
                    }

                    HStack {
                        TextField("私聊消息...", text: $inputText)
                            .font(Typography.body)
                            .foregroundStyle(Theme.textPrimary)
                            .padding(.vertical, Spacing.md)
                            .padding(.horizontal, Spacing.lg)
                            .background(Theme.bgSearchBar)
                            .cornerRadius(Radius.md)

                        Button(action: {
                            guard !inputText.isEmpty else { return }
                            messages.append(ChatMessage(sender_id: "player_001", sender_name: "我", content: inputText))
                            inputText = ""
                        }) {
                            Image(systemName: "paperplane.fill")
                                .foregroundStyle(Theme.accentPrimary)
                        }
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.vertical, Spacing.md)
                }
            }
            .navigationTitle("私聊 - \(targetName)")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("结束") { dismiss() }
                        .foregroundStyle(Theme.accentPrimary)
                }
            }
            .onAppear {
                messages.append(ChatMessage(sender_id: "system", sender_name: "", content: "你开启了与 \(targetName) 的私聊", is_system: true))
            }
        }
    }
}

// MARK: - Evidence Board View
struct EvidenceBoardView: View {
    let clues: [String]
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()
                ScrollView {
                    VStack(alignment: .leading, spacing: Spacing.lg) {
                        Text("已公开线索")
                            .font(Typography.headingMD)
                            .foregroundStyle(Theme.textPrimary)
                            .padding(.horizontal, Spacing.containerPadding)

                        ForEach(0..<3, id: \.self) { i in
                            CardContainer {
                                HStack {
                                    Image(systemName: "doc.text.fill")
                                        .foregroundStyle(Theme.accentPrimary)
                                    Text("线索 \(i + 1)")
                                        .font(Typography.headingSM)
                                        .foregroundStyle(Theme.textPrimary)
                                    Spacer()
                                    Text("公开")
                                        .font(Typography.caption)
                                        .foregroundStyle(Theme.accentGreen)
                                }
                                .padding(Spacing.md)
                            }
                            .padding(.horizontal, Spacing.containerPadding)
                        }
                    }
                    .padding(.top, Spacing.xl)
                }
            }
            .navigationTitle("证据板")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("关闭") { dismiss() }
                        .foregroundStyle(Theme.accentPrimary)
                }
            }
        }
    }
}
