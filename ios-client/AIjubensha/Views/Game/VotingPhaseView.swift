//
//  VotingPhaseView.swift
//  AI推理叙事游戏 - 投票阶段
//

import SwiftUI

struct VotingPhaseView: View {
    let phase: VotingPhase  // .detective or .final
    let suspects: [SuspectCard]
    let timeLimit: Int
    @State private var selectedSuspect: String?
    @State private var isVoted = false
    @State private var timeRemaining: Int
    @State private var showResult = false

    init(phase: VotingPhase, suspects: [SuspectCard], timeLimit: Int) {
        self.phase = phase
        self.suspects = suspects
        self.timeLimit = timeLimit
        self._timeRemaining = State(initialValue: timeLimit)
    }

    var body: some View {
        ZStack {
            Theme.bgApp.ignoresSafeArea()

            ScrollView {
                VStack(spacing: Spacing.xl) {
                    // Header
                    VStack(spacing: Spacing.xs) {
                        Text(phase == .detective ? "侦探投票" : "最终投票")
                            .font(Typography.headingLG)
                            .foregroundStyle(Theme.textPrimary)
                        Text(phase == .detective ? "仅侦探可见，结果不公开" : "所有人参与投票，决定最终结果")
                            .font(Typography.bodySecondary)
                            .foregroundStyle(Theme.textTertiary)
                        TimerBadge(seconds: timeRemaining)
                    }
                    .padding(.top, Spacing.xxl)

                    // Suspects list
                    ForEach(suspects) { suspect in
                        SuspectVoteCard(
                            suspect: suspect,
                            isSelected: selectedSuspect == suspect.id,
                            phase: phase
                        ) {
                            selectedSuspect = suspect.id
                        }
                        .padding(.horizontal, Spacing.containerPadding)
                    }

                    // Vote reasoning
                    CardContainer {
                        VStack(alignment: .leading, spacing: Spacing.md) {
                            Text("投票理由")
                                .font(Typography.headingSM)
                                .foregroundStyle(Theme.textPrimary)
                            Text("基于已发现的线索和对话内容，综合分析后做出判断")
                                .font(Typography.bodySecondary)
                                .foregroundStyle(Theme.textTertiary)
                        }
                        .padding(Spacing.lg)
                    }
                    .padding(.horizontal, Spacing.containerPadding)
                }
                .padding(.bottom, 120)
            }

            // Submit button
            VStack {
                Spacer()
                if selectedSuspect != nil {
                    NeonButton(title: phase == .detective ? "确认投票" : "提交最终投票", action: {
                        isVoted = true
                        showResult = true
                    }, isLoading: false)
                    .padding(.horizontal, Spacing.containerPadding)
                    .padding(.bottom, 40)
                } else {
                    Text("选择嫌疑人后投票")
                        .font(Typography.caption)
                        .foregroundStyle(Theme.textTertiary)
                        .padding(.bottom, 40)
                }
            }
        }
        .navigationTitle(phase == .detective ? "侦探投票" : "最终投票")
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showResult) {
            VoteResultView(phase: phase, selectedSuspectId: selectedSuspect ?? "")
        }
        .onReceive(Timer.publish(every: 1, on: .main, in: .common).autoconnect()) { _ in
            if timeRemaining > 0 && !isVoted {
                timeRemaining -= 1
            }
        }
    }
}

// MARK: - Models
enum VotingPhase {
    case detective
    case final
}

struct SuspectCard: Identifiable {
    let id: String
    let name: String
    let role: String
    let suspicionLevel: Int  // 1-5
    let cluesAgainst: [String]
}

// MARK: - Suspect Vote Card
struct SuspectVoteCard: View {
    let suspect: SuspectCard
    let isSelected: Bool
    let phase: VotingPhase
    let onSelect: () -> Void

    var body: some View {
        Button(action: onSelect) {
            HStack(spacing: Spacing.md) {
                AvatarView(text: String(suspect.name.prefix(1)), size: 48)
                    .overlay(
                        RoundedRectangle(cornerRadius: 24)
                            .stroke(isSelected ? Theme.accentPrimary : Color.clear, lineWidth: 2)
                    )

                VStack(alignment: .leading, spacing: Spacing.xs) {
                    HStack {
                        Text(suspect.name)
                            .font(Typography.headingMD)
                            .foregroundStyle(isSelected ? Theme.accentPrimary : Theme.textPrimary)
                        Text(suspect.role)
                            .font(Typography.caption)
                            .foregroundStyle(Theme.textTertiary)
                    }

                    // Suspicion meter
                    HStack(spacing: Spacing.xs) {
                        ForEach(0..<5) { i in
                            Image(systemName: i < suspect.suspicionLevel ? "star.fill" : "star")
                                .font(.system(size: 12))
                                .foregroundStyle(i < suspect.suspicionLevel ? Theme.accentWarning : Theme.textTertiary)
                        }
                        Text("可疑度")
                            .font(Typography.captionTiny)
                            .foregroundStyle(Theme.textTertiary)
                            .padding(.leading, Spacing.sm)
                    }

                    if !suspect.cluesAgainst.isEmpty {
                        Text(suspect.cluesAgainst[0])
                            .font(Typography.caption)
                            .foregroundStyle(Theme.accentError.opacity(0.8))
                            .lineLimit(1)
                    }
                }

                Spacer()

                Image(systemName: isSelected ? "checkmark.circle.fill" : "circle")
                    .foregroundStyle(isSelected ? Theme.accentPrimary : Theme.textTertiary)
                    .font(.system(size: 24))
            }
            .padding()
            .background(isSelected ? Theme.accentPrimary.opacity(0.1) : Theme.bgCard)
            .cornerRadius(Radius.md)
            .overlay(
                RoundedRectangle(cornerRadius: Radius.md)
                    .stroke(isSelected ? Theme.accentPrimary : Theme.borderCard, lineWidth: isSelected ? 2 : 1)
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Vote Result View
struct VoteResultView: View {
    let phase: VotingPhase
    let selectedSuspectId: String
    @Environment(\.dismiss) var dismiss

    var body: some View {
        NavigationView {
            ZStack {
                Theme.bgApp.ignoresSafeArea()
                VStack(spacing: Spacing.xl) {
                    Image(systemName: phase == .detective ? "eye.fill" : "checkmark.seal.fill")
                        .font(.system(size: 64))
                        .foregroundStyle(phase == .detective ? Theme.accentBlue : Theme.accentPrimary)

                    Text(phase == .detective ? "侦探投票完成" : "最终投票已提交")
                        .font(Typography.headingLG)
                        .foregroundStyle(Theme.textPrimary)

                    Text("投票结果将在结果公示阶段公布")
                        .font(Typography.bodySecondary)
                        .foregroundStyle(Theme.textTertiary)

                    Spacer()
                }
                .padding(.horizontal, Spacing.containerPadding)
            }
            .navigationTitle("投票结果")
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
