//
//  AuthService.swift
//  AI推理叙事游戏 - 认证服务
//

import Foundation

class AuthService {
    private let api = APIService.shared

    func login(username: String, password: String) async throws -> AuthResponse {
        let response = try await api.login(username: username, password: password)
        api.setToken(response.access_token)
        return response
    }

    func register(username: String, email: String, password: String) async throws -> AuthResponse {
        let response = try await api.register(username: username, email: email, password: password)
        api.setToken(response.access_token)
        return response
    }

    func logout() async throws {
        do { try await api.logout() } catch {}
        api.clearToken()
    }

    func getProfile() async throws -> UserProfile {
        let response = try await api.getProfile()
        return UserProfile(
            user_id: response.user_id,
            username: response.username,
            email: response.email,
            avatar_url: response.avatar_url,
            member_level: response.member_level,
            stars_balance: response.stars_balance
        )
    }
}
