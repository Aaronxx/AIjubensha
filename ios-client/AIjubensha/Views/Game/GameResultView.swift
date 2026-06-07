//
//  GameResultView.swift
//  AI推理叙事游戏 - 结局短剧、结果公示、复盘
//

import SwiftUI

struct GameResultView: View {
    let gameResult: GameResultSummary
    @State private var showEnding = false
    @State private var showReview = false
    @State private var showStats = false
    @State private var currentStep: ResultStep = .announcement

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            ScrollView {
                VStack(spacing: Spacing.xl) {
                    // Result header
                    VStack(spacing: Spacing.md) {
                        Image(systemName: gameResult.murdererCaught ? "checkmark.seal.fill" : "xmark.seal.fill")
                            .font(.system(size: 64))
                            .foregroundStyle(gameResult.murdererCaught ? Theme.accentGreen : Theme.accentError)

                        Text(gameResult.murdererCaught ? "凶手被指认" : "凶手逃脱")
                            .font(Typography.headingLG)
                            .foregroundStyle(gameResult.murdererCaught ? Theme.accentGreen : Theme.accentError)

                        Text("剧本：\(gameResult.scriptName)")
                            .font(Typography.bodySecondary)
                            .foregroundStyle(Theme.textTertiary)
                    }
                    .padding(.top, Spacing.xxl)

                    // Vote results
                    CardContainer {
                        VStack(alignment: .leading, spacing: Spacing.md) {
                            Text("投票结果")
                                .font(Typography.headingMD)
                                .foregroundStyle(Theme.textPrimary)

                            ForEach(gameResult.voteResults) { vote in
                                HStack {
                                    Text(vote.playerName)
                                        .font(Typography.body)
                                        .foregroundStyle(Theme.textPrimary)
                                    Spacer()
                                    Image(systemName: "arrow.right")
                                        .foregroundStyle(Theme.textTertiary)
                                    Text(vote.targetName)
                                        .font(Typography.body)
                                        .foregroundStyle(vote.isCorrect ? Theme.accentGreen : Theme.accentError)
                                }
                            }

                            ThemeDivider()

                            HStack {
                                Text("真凶")
                                    .foregroundStyle(Theme.textTertiary)
                                Spacer()
                                Text(gameResult.murdererName)
                                    .font(Typography.headingSM)
                                    .foregroundStyle(Theme.accentWarning)
                                    .bold()
                            }
                        }
                        .padding(Spacing.lg)
                    }
                    .padding(.horizontal, Spacing.containerPadding)

                    // Player results
                    CardContainer {
                        VStack(alignment: .leading, spacing: Spacing.md) {
                            Text("玩家结果")
                                .font(Typography.headingMD)
                                .foregroundStyle(Theme.textPrimary)

                            ForEach(gameResult.playerResults) { result in
                                HStack {
                                    Text(result.playerName)
                                        .foregroundStyle(Theme.textPrimary)
                                    Text(result.role)
                                        .font(Typography.caption)
                                        .foregroundStyle(Theme.textTertiary)
                                    Spacer()
                                    Tag(
                                        text: result.isCorrect ? "✅ 正确" : "❌ 错误",
                                        color: result.isCorrect ? Theme.accentGreen : Theme.accentError
                                    )
                                }
                            }
                        }
                        .padding(Spacing.lg)
                    }
                    .padding(.horizontal, Spacing.containerPadding)

                    // Action buttons
                    VStack(spacing: Spacing.md) {
                        GhostButton(title: "🎬 观看结局短剧", action: { showEnding = true })
                            .padding(.horizontal, Spacing.containerPadding)
                        GhostButton(title: "📋 查看蝴蝶效应复盘", action: { showReview = true })
                            .padding(.horizontal, Spacing.containerPadding)
                        NeonButton(title: "查看当局战绩", action: { showStats = true }, isLoading: false)
                            .padding(.horizontal, Spacing.containerPadding)
                    }
                    .padding(.top, Spacing.lg)
                }
                .padding(.bottom, 100)
            }
        }
        .navigationTitle("结果公示")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showEnding) {
            EndingDramaView(scriptName: gameResult.scriptName, isCaught: gameResult.murdererCaught)
        }
        .sheet(isPresented: $showReview) {
            ButterflyReviewView(gameResult: gameResult)
        }
        .sheet(isPresented: $showStats) {
            GameStatsDetailView(gameResult: gameResult)
        }
    }
}

// MARK: - Models
struct GameResultSummary {
    let scriptName: String
    let murdererName: String
    let murdererCaught: Bool
    let voteResults: [VoteRecord]
    let playerResults: [PlayerResult]
}

struct VoteRecord: Identifiable {
    let id = UUID()
    let playerName: String
    let targetName: String
    let isCorrect: Bool
}

struct PlayerResult: Identifiable {
    let id = UUID()
    let playerName: String
    let role: String
    let isCorrect: Bool
}

// MARK: - Ending Drama View
struct EndingDramaView: View {
    let scriptName: String
    let isCaught: Bool
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()
                VStack(spacing: Spacing.xl) {
                    // Video placeholder
                    Theme.bgCardElevated
                        .frame(height: 240)
                        .cornerRadius(Radius.md)
                        .overlay(
                            VStack {
                                Image(systemName: "play.circle.fill")
                                    .font(.system(size: 48))
                                    .foregroundStyle(Theme.accentPrimary.opacity(0.6))
                                Text("结局短剧")
                                    .font(Typography.headingMD)
                                    .foregroundStyle(Theme.textPrimary)
                                    .padding(.top, Spacing.md)
                                Text(isCaught ? "凶手被指认 - 结局A" : "凶手逃脱 - 结局D")
                                    .font(Typography.bodySecondary)
                                    .foregroundStyle(Theme.textTertiary)
                            }
                        )
                        .padding(.horizontal, Spacing.containerPadding)

                    Text("AI 真人短剧将根据你的选择播放对应结局")
                        .font(Typography.bodySecondary)
                        .foregroundStyle(Theme.textTertiary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, Spacing.xl)

                    Spacer()
                }
            }
            .navigationTitle("结局短剧")
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

// MARK: - Butterfly Review View
struct ButterflyReviewView: View {
    let gameResult: GameResultSummary
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()
                ScrollView {
                    VStack(spacing: Spacing.xl) {
                        Text("蝴蝶效应复盘")
                            .font(Typography.headingLG)
                            .foregroundStyle(Theme.textPrimary)

                        CardContainer {
                            VStack(alignment: .leading, spacing: Spacing.md) {
                                Text("你的关键选择")
                                    .font(Typography.headingSM)
                                    .foregroundStyle(Theme.accentPrimary)
                                ChoiceItem(text: "第一轮搜证选择了调查死者房间", impact: "发现了指纹线索")
                                ChoiceItem(text: "第二幕质问了苏晚晴关于当晚的行踪", impact: "解锁了深层线索")
                                ChoiceItem(text: "最终投票投给了\(gameResult.murdererName)", impact: gameResult.murdererCaught ? "正确指认凶手" : "指认错误")
                            }
                            .padding(Spacing.lg)
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                    }
                    .padding(.bottom, 100)
                }
            }
            .navigationTitle("蝴蝶效应复盘")
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

struct ChoiceItem: View {
    let text: String
    let impact: String

    var body: some View {
        VStack(alignment: .leading, spacing: Spacing.xs) {
            HStack {
                Image(systemName: "arrowshape.turn.up.right.fill")
                    .foregroundStyle(Theme.accentPrimary)
                Text(text)
                    .font(Typography.body)
                    .foregroundStyle(Theme.textPrimary)
            }
            HStack(spacing: Spacing.sm) {
                Image(systemName: "arrow.right")
                    .foregroundStyle(Theme.accentGold)
                Text("→ \(impact)")
                    .font(Typography.caption)
                    .foregroundStyle(Theme.accentGold)
            }
        }
        .padding(.vertical, Spacing.sm)
    }
}

// MARK: - Game Stats Detail View
struct GameStatsDetailView: View {
    let gameResult: GameResultSummary
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()
                ScrollView {
                    VStack(spacing: Spacing.lg) {
                        // Stats cards
                        HStack(spacing: 0) {
                            StatCardView(value: "78", label: "分钟", valueColor: Theme.accentPrimary)
                            ThemeDivider()
                            StatCardView(value: "7", label: "线索", valueColor: Theme.accentGold)
                            ThemeDivider()
                            StatCardView(value: "23", label: "发言", valueColor: Theme.accentBlue)
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                        .padding(.vertical, Spacing.lg)
                        .background(Theme.bgCard)

                        CardContainer {
                            VStack(alignment: .leading, spacing: Spacing.md) {
                                Text("详细数据")
                                    .font(Typography.headingMD)
                                    .foregroundStyle(Theme.textPrimary)
                                StatRow(label: "搜证AP使用", value: "5/5")
                                StatRow(label: "发现线索", value: "7条")
                                StatRow(label: "公开线索", value: "5条")
                                StatRow(label: "保留线索", value: "2条")
                                StatRow(label: "发言次数", value: "23次")
                                StatRow(label: "私聊次数", value: "4次")
                                StatRow(label: "最终投票", value: gameResult.murdererName)
                            }
                            .padding(Spacing.lg)
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                    }
                    .padding(.bottom, 100)
                }
            }
            .navigationTitle("当局战绩")
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

struct StatRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label)
                .foregroundStyle(Theme.textSecondary)
            Spacer()
            Text(value)
                .foregroundStyle(Theme.textPrimary)
                .bold()
        }
        .padding(.vertical, Spacing.xs)
    }
}
