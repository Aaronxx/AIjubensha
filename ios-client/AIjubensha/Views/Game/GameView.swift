//
//  GameView.swift
//  AI推理叙事游戏 - 游戏主界面
//

import SwiftUI

struct GameView: View {
    @State private var messages: [ChatMessage] = []
    @State private var inputText = ""
    @State private var isTyping = false
    @State private var showInvestigation = false
    @State private var currentPhase: String = "等待中"
    @State private var phaseStep: String = "1/7"
    @State private var isLoading = true
    @EnvironmentObject var appState: AppState

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            if appState.currentGameSessionId == nil {
                NoActiveGameView()
            } else {
                VStack(spacing: 0) {
                    // Phase header
                    PhaseHeader(phase: currentPhase, step: phaseStep)
                        .padding(.bottom, Spacing.md)

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
                        Button(action: { showInvestigation.toggle() }) {
                            Image(systemName: "book.fill")
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
                        .disabled(inputText.isEmpty)
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.vertical, Spacing.md)
                    .background(Theme.bgBottomBar)
                }
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .navigationBarTrailing) {
                        HStack(spacing: Spacing.lg) {
                            Button(action: { showInvestigation.toggle() }) {
                                Image(systemName: "magnifyingglass")
                                    .foregroundStyle(Theme.accentPrimary)
                            }
                            Button(action: { appState.exitGame() }) {
                                Image(systemName: "xmark.circle.fill")
                                    .foregroundStyle(Theme.accentError)
                            }
                        }
                    }
                }
                .task {
                    if let sessionId = appState.currentGameSessionId {
                        await loadGame(roomId: sessionId)
                    }
                }
            }
        }
    }

    private func loadGame(roomId: String) async {
        isLoading = true
        do {
            let state = try await APIService.shared.getGameState(roomId: roomId)
            withAnimation {
                currentPhase = phaseName(for: state.current_phase)
                phaseStep = "\(state.players.count)人"

                // Add system message for game start
                messages.append(ChatMessage(
                    sender_id: "system",
                    sender_name: "",
                    content: "游戏已开始，当前阶段：\(currentPhase)",
                    is_system: true
                ))

                // Add welcome messages for each player
                for player in state.players where !player.is_ai {
                    messages.append(ChatMessage(
                        sender_id: "system",
                        sender_name: "",
                        content: "\(player.player_id) 已加入游戏",
                        is_system: true
                    ))
                }
            }
        } catch {
            print("Failed to load game state: \(error)")
            messages.append(ChatMessage(
                sender_id: "system",
                sender_name: "",
                content: "无法加载游戏状态: \(error.localizedDescription)",
                is_system: true
            ))
        }
        isLoading = false
    }

    private func phaseName(for phase: String) -> String {
        switch phase {
        case "preparation": return "个人准备"
        case "act_1_turn": return "轮流发言"
        case "round_1_search": return "第一轮搜证"
        case "act_2_discuss": return "第二幕讨论"
        case "detective_vote": return "侦探投票"
        case "round_2_search": return "第二轮搜证"
        case "act_3_discuss": return "第三幕讨论"
        case "final_vote": return "最终投票"
        case "result": return "结果公示"
        case "finished": return "游戏结束"
        default: return phase
        }
    }

    private func sendMessage() {
        guard !inputText.isEmpty else { return }

        let newMessage = ChatMessage(
            sender_id: "player_001",
            sender_name: "我",
            content: inputText
        )
        messages.append(newMessage)
        let sentContent = inputText
        inputText = ""

        isTyping = true
        Task {
            try? await Task.sleep(nanoseconds: 1_000_000_000)
            withAnimation {
                messages.append(ChatMessage(
                    sender_id: "npc_001",
                    sender_name: "苏晚晴",
                    content: "那天晚上我确实在画廊，不过很早就离开了。",
                    is_ai: true
                ))
                isTyping = false
            }
        }
    }
}

// MARK: - Phase Header
struct PhaseHeader: View {
    let phase: String
    let step: String

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text(step)
                    .font(Typography.caption)
                    .foregroundStyle(Theme.accentPrimary)
                Text(phase)
                    .font(Typography.headingMD)
                    .foregroundStyle(Theme.textPrimary)
            }
            Spacer()
            Button(action: {}) {
                Image(systemName: "ellipsis.circle")
                    .foregroundStyle(Theme.textTertiary)
            }
        }
        .padding(.horizontal, Spacing.containerPadding)
        .padding(.vertical, Spacing.md)
        .background(Theme.bgBottomBar)
    }
}

// MARK: - Message Bubble
struct MessageBubble: View {
    let message: ChatMessage

    var body: some View {
        if message.is_system {
            Text(message.content)
                .font(Typography.caption)
                .foregroundStyle(Theme.textTertiary)
                .frame(maxWidth: .infinity, alignment: .center)
                .padding(.vertical, Spacing.xs)
        } else if message.is_ai {
            HStack(alignment: .top, spacing: Spacing.sm) {
                AvatarView(text: message.sender_name, size: 32)

                VStack(alignment: .leading, spacing: Spacing.xs) {
                    Text(message.sender_name)
                        .font(Typography.caption)
                        .foregroundStyle(Theme.accentPrimary)
                    Text(message.content)
                        .font(Typography.body)
                        .foregroundStyle(Theme.textSecondary)
                        .padding(Spacing.lg)
                        .background(Theme.bgCard)
                        .cornerRadius(Radius.md)
                        .overlay(
                            RoundedRectangle(cornerRadius: Radius.md)
                                .stroke(Theme.borderCard, lineWidth: 1)
                        )
                }
            }
        } else {
            HStack {
                Spacer()
                VStack(alignment: .trailing, spacing: Spacing.xs) {
                    Text(message.sender_name)
                        .font(Typography.caption)
                        .foregroundStyle(Theme.accentGold)
                    Text(message.content)
                        .font(Typography.body)
                        .foregroundStyle(Theme.textOnAccent)
                        .padding(Spacing.lg)
                        .background(Theme.accentPrimary.opacity(0.9))
                        .cornerRadius(Radius.md)
                }
                .frame(maxWidth: .infinity, alignment: .trailing)
            }
        }
    }
}

// MARK: - Typing Indicator
struct TypingIndicator: View {
    var body: some View {
        HStack(alignment: .top, spacing: Spacing.sm) {
            AvatarView(text: "...", size: 32)
            VStack(alignment: .leading, spacing: Spacing.xs) {
                Text("NPC")
                    .font(Typography.caption)
                    .foregroundStyle(Theme.accentPrimary)
                HStack(spacing: Spacing.xs) {
                    ForEach(0..<3) { i in
                        Circle()
                            .fill(Theme.textTertiary)
                            .frame(width: 6, height: 6)
                            .animation(.easeInOut(duration: 0.6).repeatForever().delay(Double(i) * 0.2), value: UUID())
                    }
                }
                .padding(Spacing.lg)
                .background(Theme.bgCard)
                .cornerRadius(Radius.md)
            }
        }
    }
}

// MARK: - No Active Game View
struct NoActiveGameView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        VStack(spacing: Spacing.xxl) {
            Image(systemName: "gamecontroller.fill")
                .font(.system(size: 64))
                .foregroundStyle(Theme.accentPrimary.opacity(0.6))

            Text("当前没有进行中的游戏")
                .font(Typography.headingLG)
                .foregroundStyle(Theme.textPrimary)

            Text("去房间列表加入或创建一局游戏吧")
                .font(Typography.bodySecondary)
                .foregroundStyle(Theme.textTertiary)

            GhostButton(title: "去房间列表", action: {})
                .padding(.horizontal, Spacing.xxl)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .navigationTitle("游戏")
    }
}

// MARK: - Corner Radius Extension
extension View {
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCornerShape(radius: radius, corners: corners))
    }
}

struct RoundedCornerShape: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners

    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(
            roundedRect: rect,
            byRoundingCorners: corners,
            cornerRadii: CGSize(width: radius, height: radius)
        )
        return Path(path.cgPath)
    }
}
