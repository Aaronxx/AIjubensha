//
//  Colors.swift
//  AI推理叙事游戏 - Design Tokens
//

import SwiftUI

// MARK: - Design Token Colors
enum Theme {
    // Background
    static let bgApp = Color(hex: "06080D")
    static let bgContainer = Color(hex: "0A0E17")
    static let bgCard = Color(hex: "0F1120")
    static let bgCardElevated = Color(hex: "1A1D35")
    static let bgCardHighlight = Color(hex: "1F1B3A")
    static let bgSearchBar = Color(hex: "12152A")
    static let bgBottomBar = Color(hex: "0D0F1A")
    static let bgBadge = Color(hex: "2A2520")
    static let bgAchievement = Color(hex: "1A1A2A")
    static let bgAvatar = Color(hex: "3D3B6B")

    // Accent
    static let accentPrimary = Color(hex: "00E5FF")
    static let accentSecondary = Color(hex: "00B4D8")
    static let accentPurple = Color(hex: "8B7AE0")
    static let accentPink = Color(hex: "FF6B6B")
    static let accentGold = Color(hex: "D4A853")
    static let accentBlue = Color(hex: "4A7DFF")
    static let accentGreen = Color(hex: "22C55E")
    static let accentTeal = Color(hex: "00BFA6")
    static let accentError = Color(hex: "EF4444")
    static let accentWarning = Color(hex: "C8652E")

    // Border
    static let borderContainer = Color(hex: "1A1A2E")
    static let borderDivider = Color(hex: "1A2040")
    static let borderCard = Color(hex: "1E2240")
    static let borderSubtle = Color(hex: "151830")

    // Text
    static let textPrimary = Color(hex: "FFFFFF")
    static let textSecondary = Color(hex: "B0B8D0")
    static let textTertiary = Color(hex: "6B7594")
    static let textCaption = Color(hex: "4A5578")
    static let textOnAccent = Color(hex: "06080D")

    // Gradient
    static let profileGradientStart = Color(hex: "4A3B7C")
    static let profileGradientEnd = Color(hex: "2D1B4E")
}

// MARK: - Color Extension
extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: .alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a: UInt64
        let r: UInt64
        let g: UInt64
        let b: UInt64
        switch hex.count {
        case 6:
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8:
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
