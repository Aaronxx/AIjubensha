//
//  Components.swift
//  AI推理叙事游戏 - Shared UI Components
//

import SwiftUI

// MARK: - Neon Button
struct NeonButton: View {
    let title: String
    let action: () -> Void
    var isLoading: Bool = false
    var isFullWidth: Bool = true

    var body: some View {
        Button(action: action) {
            Group {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(.circular)
                        .tint(Theme.textOnAccent)
                } else {
                    Text(title)
                        .font(Typography.button)
                        .foregroundStyle(Theme.textOnAccent)
                }
            }
            .frame(maxWidth: isFullWidth ? .infinity : nil)
            .padding(.vertical, Spacing.lg)
            .background(Theme.accentPrimary)
            .cornerRadius(Radius.md)
        }
        .disabled(isLoading)
    }
}

// MARK: - Ghost Button
struct GhostButton: View {
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(Typography.link)
                .foregroundStyle(Theme.accentPrimary)
                .padding(.vertical, Spacing.md)
                .padding(.horizontal, Spacing.xl)
                .overlay(
                    RoundedRectangle(cornerRadius: Radius.md)
                        .stroke(Theme.accentPrimary, lineWidth: 1)
                )
        }
    }
}

// MARK: - Status Badge
struct StatusBadgeView: View {
    let text: String
    let color: Color

    var body: some View {
        Text(text)
            .font(Typography.captionTiny)
            .foregroundStyle(.white)
            .padding(.horizontal, Spacing.sm)
            .padding(.vertical, Spacing.xs)
            .background(color)
            .cornerRadius(Radius.sm)
    }
}

// MARK: - Card Container
struct CardContainer<Content: View>: View {
    let content: Content
    var isElevated: Bool = false

    init(isElevated: Bool = false, @ViewBuilder content: () -> Content) {
        self.isElevated = isElevated
        self.content = content()
    }

    var body: some View {
        content
            .padding(Spacing.cardPadding)
            .background(isElevated ? Theme.bgCardElevated : Theme.bgCard)
            .cornerRadius(Radius.md)
            .overlay(
                RoundedRectangle(cornerRadius: Radius.md)
                    .stroke(Theme.borderCard, lineWidth: 1)
            )
    }
}

// MARK: - Section Header
struct SectionHeader: View {
    let title: String
    var showMore: Bool = false
    var onMore: (() -> Void)? = nil

    var body: some View {
        HStack {
            Text(title)
                .font(Typography.headingMD)
                .foregroundStyle(Theme.textPrimary)
            Spacer()
            if showMore, let onMore {
                Button("更多", action: onMore)
                    .font(Typography.link)
                    .foregroundStyle(Theme.accentPrimary)
            }
        }
        .padding(.horizontal, Spacing.containerPadding)
    }
}

// MARK: - Tag
struct Tag: View {
    let text: String
    var color: Color = Theme.accentSecondary

    var body: some View {
        Text(text)
            .font(Typography.tag)
            .foregroundStyle(color)
            .padding(.horizontal, Spacing.md)
            .padding(.vertical, Spacing.xs)
            .background(color.opacity(0.15))
            .cornerRadius(Radius.sm)
    }
}

// MARK: - Divider
struct ThemeDivider: View {
    var body: some View {
        Rectangle()
            .fill(Theme.borderDivider)
            .frame(height: 1)
    }
}

// MARK: - Avatar
struct AvatarView: View {
    let text: String
    var size: CGFloat = 40
    var borderColor: Color = Theme.accentPurple

    var body: some View {
        ZStack {
            Circle()
                .fill(Theme.bgAvatar)
                .frame(width: size, height: size)
            Text(text.prefix(1).uppercased())
                .font(.system(size: size * 0.4, weight: .bold))
                .foregroundStyle(Theme.accentPrimary)
        }
        .overlay(
            Circle()
                .stroke(borderColor, lineWidth: 2)
        )
    }
}

// MARK: - Search Bar
struct ThemeSearchField: View {
    @Binding var text: String

    var body: some View {
        HStack(spacing: Spacing.md) {
            Image(systemName: "magnifyingglass")
                .foregroundStyle(Theme.textTertiary)
            TextField("搜索", text: $text)
                .font(Typography.body)
                .foregroundStyle(Theme.textPrimary)
        }
        .padding(.vertical, Spacing.md)
        .padding(.horizontal, Spacing.lg)
        .background(Theme.bgSearchBar)
        .cornerRadius(Radius.md)
    }
}

// MARK: - Stat Card
struct StatCardView: View {
    let value: String
    let label: String
    var valueColor: Color = Theme.accentGold

    var body: some View {
        VStack(spacing: Spacing.xs) {
            Text(value)
                .font(Typography.statNumber)
                .foregroundStyle(valueColor)
            Text(label)
                .font(Typography.statLabel)
                .foregroundStyle(Theme.textTertiary)
        }
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Achievement Badge
struct AchievementBadgeView: View {
    let name: String
    let icon: String
    let rarityColor: Color

    var body: some View {
        VStack(spacing: Spacing.xs) {
            Image(systemName: icon)
                .font(.system(size: 28))
                .foregroundStyle(rarityColor)
            Text(name)
                .font(Typography.caption)
                .foregroundStyle(Theme.textTertiary)
                .lineLimit(1)
        }
        .frame(width: 80)
        .padding(Spacing.lg)
        .background(Theme.bgAchievement)
        .cornerRadius(Radius.md)
        .overlay(
            RoundedRectangle(cornerRadius: Radius.md)
                .stroke(Theme.borderCard, lineWidth: 1)
        )
    }
}
