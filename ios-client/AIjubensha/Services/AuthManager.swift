//
//  AuthManager.swift
//  AI推理叙事游戏 - 认证状态管理
//

import Foundation

@MainActor
class AuthManager: ObservableObject {
    static let shared = AuthManager()

    @Published var isAuthenticated = false
    @Published var currentUser: UserProfile?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let authService = AuthService()

    init() {
        // Check for existing token
        if APIService.shared.getToken() != nil {
            isAuthenticated = true
        }
    }

    // MARK: - Login
    func login(username: String, password: String) async {
        isLoading = true
        errorMessage = nil

        do {
            let response = try await authService.login(username: username, password: password)
            isAuthenticated = true
            currentUser = UserProfile(
                user_id: response.user_id,
                username: response.username,
                email: ""
            )
        } catch let error as APIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "登录失败: \(error.localizedDescription)"
        }

        isLoading = false
    }

    // MARK: - Register
    func register(username: String, email: String, password: String) async {
        isLoading = true
        errorMessage = nil

        do {
            let response = try await authService.register(username: username, email: email, password: password)
            isAuthenticated = true
            currentUser = UserProfile(
                user_id: response.user_id,
                username: response.username,
                email: email
            )
        } catch let error as APIError {
            errorMessage = error.errorDescription
        } catch {
            errorMessage = "注册失败: \(error.localizedDescription)"
        }

        isLoading = false
    }

    // MARK: - Logout
    func logout() {
        Task {
            try? await authService.logout()
        }
        isAuthenticated = false
        currentUser = nil
        APIService.shared.clearToken()
    }
}
