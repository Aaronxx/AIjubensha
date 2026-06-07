//
//  AIJubenshaApp.swift
//  AI推理叙事游戏 - iOS客户端
//

import SwiftUI

@main
struct AIJubenshaApp: App {
    @StateObject private var authManager = AuthManager.shared
    @StateObject private var appState = AppState.shared

    var body: some Scene {
        WindowGroup {
            Group {
                if authManager.isAuthenticated {
                    MainTabView()
                } else {
                    AuthView()
                }
            }
            .environmentObject(authManager)
            .environmentObject(appState)
        }
    }
}

// MARK: - App State
@MainActor
class AppState: ObservableObject {
    static let shared = AppState()

    @Published var currentGameSessionId: String?
    @Published var gamePhase: GamePhase = .idle
    @Published var showGameOverlay: Bool = false

    func enterGame(sessionId: String) {
        currentGameSessionId = sessionId
        showGameOverlay = true
    }

    func exitGame() {
        currentGameSessionId = nil
        gamePhase = .idle
        showGameOverlay = false
    }
}

// MARK: - Game Phase
enum GamePhase: String, Codable {
    case idle
    case preparation
    case act1Speaking
    case act1Free
    case investigation1
    case act2Discussion
    case detectiveVote
    case investigation2
    case act3Discussion
    case finalVote
    case voteResult
    case settlement
}
