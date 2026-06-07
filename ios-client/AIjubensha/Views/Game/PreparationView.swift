//
//  PreparationView.swift
//  AI推理叙事游戏 - 个人准备阶段
//

import SwiftUI

struct PreparationView: View {
    let characterName: String
    let characterRole: String
    let characterDescription: String
    let secretHint: String
    let timeLimit: Int  // seconds
    @Binding var isConfirmed: Bool
    @State private var timeRemaining: Int
    @State private var showIdentityCard = false

    init(characterName: String, characterRole: String, characterDescription: String, secretHint: String, timeLimit: Int, isConfirmed: Binding<Bool>) {
        self.characterName = characterName
        self.characterRole = characterRole
        self.characterDescription = characterDescription
        self.secretHint = secretHint
        self.timeLimit = timeLimit
        self._timeRemaining = State(initialValue: timeLimit)
        self._isConfirmed = isConfirmed
    }

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            ScrollView {
                VStack(spacing: Spacing.xl) {
                    // Timer
                    VStack(spacing: Spacing.xs) {
                        Text("个人准备")
                            .font(Typography.headingLG)
                            .foregroundStyle(Theme.textPrimary)
                        TimerBadge(seconds: timeRemaining)
                    }
                    .padding(.top, Spacing.xxl)

                    // Identity card
                    CardContainer {
                        VStack(alignment: .leading, spacing: Spacing.md) {
                            HStack {
                                AvatarView(text: String(characterName.prefix(1)), size: 56)
                                VStack(alignment: .leading, spacing: Spacing.xs) {
                                    Text(characterName)
                                        .font(Typography.headingMD)
                                        .foregroundStyle(Theme.textPrimary)
                                    Tag(text: characterRole, color: Theme.accentPrimary)
                                }
                                Spacer()
                            }

                            ThemeDivider()

                            Text(characterDescription)
                                .font(Typography.body)
                                .foregroundStyle(Theme.textSecondary)
                                .lineSpacing(4)

                            ThemeDivider()

                            HStack(spacing: Spacing.sm) {
                                Image(systemName: "lock.fill")
                                    .foregroundStyle(Theme.accentWarning)
                                Text("个人秘密")
                                    .font(Typography.headingSM)
                                    .foregroundStyle(Theme.accentWarning)
                            }
                            .padding(.top, Spacing.sm)

                            Text(secretHint)
                                .font(Typography.bodySecondary)
                                .foregroundStyle(Theme.accentWarning.opacity(0.8))
                                .italic()
                        }
                        .padding(Spacing.lg)
                    }
                    .padding(.horizontal, Spacing.containerPadding)

                    // Rules hint
                    VStack(alignment: .leading, spacing: Spacing.sm) {
                        Text("游戏规则")
                            .font(Typography.headingSM)
                            .foregroundStyle(Theme.textPrimary)
                        RuleItem(icon: "bubble.left", text: "仔细阅读你的身份和秘密")
                        RuleItem(icon: "timer", text: "准备限时5分钟，超时自动开始")
                        RuleItem(icon: "hand.tap", text: "点击确认后进入第一幕")
                    }
                    .padding()
                    .background(Theme.bgCard)
                    .cornerRadius(Radius.md)
                    .overlay(
                        RoundedRectangle(cornerRadius: Radius.md)
                            .stroke(Theme.borderCard, lineWidth: 1)
                    )
                    .padding(.horizontal, Spacing.containerPadding)

                    Spacer(minLength: 100)
                }
            }

            // Confirm button bar
            VStack {
                Spacer()
                NeonButton(title: "已确认，进入第一幕", action: { isConfirmed = true }, isLoading: false)
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.bottom, 40)
            }
        }
        .sheet(isPresented: $showIdentityCard) {
            IdentityCardView(characterName: characterName, characterRole: characterRole, description: characterDescription)
        }
        .onReceive(Timer.publish(every: 1, on: .main, in: .common).autoconnect()) { _ in
            if timeRemaining > 0 && !isConfirmed {
                timeRemaining -= 1
            }
        }
    }
}

struct TimerBadge: View {
    let seconds: Int
    var minutes: Int { seconds / 60 }
    var secs: Int { seconds % 60 }

    var body: some View {
        Text(String(format: "%02d:%02d", minutes, secs))
            .font(.system(size: 32, weight: .bold, design: .monospaced))
            .foregroundStyle(seconds < 60 ? Theme.accentError : Theme.accentPrimary)
    }
}

struct RuleItem: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: Spacing.sm) {
            Image(systemName: icon)
                .foregroundStyle(Theme.accentPrimary)
                .frame(width: 24)
            Text(text)
                .font(Typography.body)
                .foregroundStyle(Theme.textSecondary)
            Spacer()
        }
    }
}

// MARK: - Identity Card View
struct IdentityCardView: View {
    let characterName: String
    let characterRole: String
    let description: String
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()
                VStack(spacing: Spacing.xl) {
                    AvatarView(text: String(characterName.prefix(1)), size: 80)
                    Text(characterName)
                        .font(Typography.headingLG)
                        .foregroundStyle(Theme.textPrimary)
                    Tag(text: characterRole, color: Theme.accentPrimary)
                    Text(description)
                        .font(Typography.body)
                        .foregroundStyle(Theme.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, Spacing.xl)
                    Spacer()
                }
            }
            .navigationTitle("身份卡")
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
