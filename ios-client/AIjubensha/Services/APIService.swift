//
//  APIService.swift
//  AI推理叙事游戏 - API服务层
//

import Foundation

// MARK: - API Error
enum APIError: LocalizedError {
    case networkError(Error)
    case unauthorized
    case serverError(String)
    case decodingError(Error)

    var errorDescription: String? {
        switch self {
        case .networkError(let error):
            return "网络错误: \(error.localizedDescription)"
        case .unauthorized:
            return "未授权，请重新登录"
        case .serverError(let message):
            return "服务器错误: \(message)"
        case .decodingError(let error):
            return "数据解析错误: \(error.localizedDescription)"
        }
    }
}

// MARK: - HTTP Method
enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case patch = "PATCH"
    case delete = "DELETE"
}

// MARK: - API Service
class APIService {
    static let shared = APIService()

    private let baseURL: String
    private var authToken: String?

    private init() {
        self.baseURL = ProcessInfo.processInfo.environment["API_BASE_URL"] ?? "http://localhost:8000/api"
    }

    // MARK: - Token Management
    func setToken(_ token: String) {
        authToken = token
        UserDefaults.standard.set(token, forKey: "authToken")
    }

    func getToken() -> String? {
        if authToken != nil {
            return authToken
        }
        return UserDefaults.standard.string(forKey: "authToken")
    }

    func clearToken() {
        authToken = nil
        UserDefaults.standard.removeObject(forKey: "authToken")
    }

    // MARK: - Request with response
    func request<T: Decodable>(
        _ method: HTTPMethod,
        path: String,
        body: Encodable? = nil,
        queryItems: [URLQueryItem]? = nil,
        responseType: T.Type
    ) async throws -> T {
        let url = try buildURL(path: path, queryItems: queryItems)
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        if let token = getToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }

        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse else {
                throw APIError.networkError(URLError(.cannotParseResponse))
            }

            switch httpResponse.statusCode {
            case 200...299:
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                return try decoder.decode(T.self, from: data)
            case 401:
                throw APIError.unauthorized
            case 400...499:
                let error = try? JSONDecoder().decode(APIErrorResponse.self, from: data)
                throw APIError.serverError(error?.detail ?? "客户端错误")
            default:
                throw APIError.serverError("服务器错误: \(httpResponse.statusCode)")
            }
        } catch let apiError as APIError {
            throw apiError
        } catch let urlError as URLError {
            throw APIError.networkError(urlError)
        } catch {
            throw APIError.decodingError(error)
        }
    }

    // MARK: - Request without response body
    func request(
        _ method: HTTPMethod,
        path: String,
        body: Encodable? = nil
    ) async throws {
        _ = try request(method, path: path, body: body, responseType: EmptyResponse.self)
    }

    // MARK: - URL Builder
    private func buildURL(path: String, queryItems: [URLQueryItem]? = nil) throws -> URL {
        let fullURL = baseURL + path
        guard var urlComponents = URLComponents(string: fullURL) else {
            throw URLError(.badURL)
        }
        if let queryItems = queryItems {
            urlComponents.queryItems = queryItems
        }
        guard let url = urlComponents.url else {
            throw URLError(.badURL)
        }
        return url
    }
}

// MARK: - Response Models
struct EmptyResponse: Decodable {}

struct APIErrorResponse: Decodable {
    let detail: String
}

// MARK: - Auth Endpoints
extension APIService {
    func login(username: String, password: String) async throws -> AuthResponse {
        try await request(.post, "/auth/login", body: LoginRequest(username: username, password: password), responseType: AuthResponse.self)
    }

    func register(username: String, email: String, password: String) async throws -> AuthResponse {
        try await request(.post, "/auth/register", body: RegisterRequest(username: username, email: email, password: password), responseType: AuthResponse.self)
    }

    func logout() async throws {
        try await request(.post, "/auth/logout")
    }

    func getProfile() async throws -> UserProfileResponse {
        try await request(.get, "/auth/me", responseType: UserProfileResponse.self)
    }
}

// MARK: - Script Endpoints
extension APIService {
    func fetchScripts() async throws -> [ScriptResponse] {
        try await request(.get, "/scripts", responseType: [ScriptResponse].self)
    }

    func fetchScript(_ scriptId: String) async throws -> ScriptDetailResponse {
        try await request(.get, "/scripts/\(scriptId)", responseType: ScriptDetailResponse.self)
    }
}

// MARK: - Room Endpoints
extension APIService {
    func fetchRooms(status: String? = nil, scriptId: String? = nil) async throws -> [RoomAPIResponse] {
        var items: [URLQueryItem] = []
        if let status { items.append(URLQueryItem(name: "status", value: status)) }
        if let scriptId { items.append(URLQueryItem(name: "script_id", value: scriptId)) }
        return try await request(.get, "/rooms", queryItems: items.isEmpty ? nil : items, responseType: [RoomAPIResponse].self)
    }

    func createRoom(name: String, scriptId: String, maxPlayers: Int = 6) async throws -> RoomCreateResponse {
        try await request(.post, "/rooms", body: CreateRoomRequest(name: name, script_id: scriptId, max_players: maxPlayers, host_id: "me", host_username: "me"), responseType: RoomCreateResponse.self)
    }

    func joinRoom(roomId: String, password: String? = nil) async throws -> JoinRoomResponse {
        try await request(.post, "/rooms/\(roomId)/join", body: JoinRoomBody(password: password), responseType: JoinRoomResponse.self)
    }

    func getRoom(_ roomId: String) async throws -> RoomAPIResponse {
        try await request(.get, "/rooms/\(roomId)", responseType: RoomAPIResponse.self)
    }
}

// MARK: - Game Endpoints
extension APIService {
    func getGameState(roomId: String) async throws -> GameStateResponse {
        try await request(.get, "/game/\(roomId)", responseType: GameStateResponse.self)
    }

    func playerConfirm(roomId: String, playerId: String) async throws {
        try await request(.post, "/game/\(roomId)/confirm", body: ConfirmBody(player_id: playerId))
    }

    func forceAdvance(roomId: String) async throws {
        try await request(.post, "/game/\(roomId)/force-advance")
    }

    func castVote(roomId: String, voterId: String, targetId: String) async throws {
        try await request(.post, "/game/\(roomId)/vote", body: VoteBody(voter_id: voterId, target_id: targetId))
    }
}

// MARK: - Profile Endpoints
extension APIService {
    func getPlayerStats(playerId: String) async throws -> PlayerStatsResponse {
        try await request(.get, "/players/\(playerId)/stats", responseType: PlayerStatsResponse.self)
    }

    func getAchievements(playerId: String) async throws -> [AchievementAPIResponse] {
        try await request(.get, "/players/\(playerId)/achievements", responseType: [AchievementAPIResponse].self)
    }

    func getSettlements(playerId: String) async throws -> [SettlementAPIResponse] {
        let raw = try await request(.get, "/players/\(playerId)/settlements", responseType: [SettlementBackendResponse].self)
        return raw.map { SettlementAPIResponse(from: $0) }
    }
}

// MARK: - Shop Endpoints
extension APIService {
    func fetchProducts(category: String? = nil) async throws -> [ProductAPIResponse] {
        var items: [URLQueryItem] = []
        if let category { items.append(URLQueryItem(name: "category", value: category)) }
        return try await request(.get, "/shop/products", queryItems: items.isEmpty ? nil : items, responseType: [ProductAPIResponse].self)
    }

    func purchaseProduct(productId: String) async throws {
        try await request(.post, "/shop/products/\(productId)/purchase")
    }

    func getStarsBalance() async throws -> StarsBalanceResponse {
        try await request(.get, "/shop/balance", responseType: StarsBalanceResponse.self)
    }
}

// MARK: - Request/Response DTOs
struct LoginRequest: Encodable {
    let username: String
    let password: String
}

struct RegisterRequest: Encodable {
    let username: String
    let email: String
    let password: String
}

struct AuthResponse: Decodable {
    let access_token: String
    let token_type: String
    let user_id: String
    let username: String
}

struct UserProfileResponse: Decodable {
    let user_id: String
    let username: String
    let email: String
    let avatar_url: String?
    let member_level: Int
    let stars_balance: Int
}

struct ScriptResponse: Decodable {
    let id: String
    let title: String
    let description: String
    let cover_url: String?
    let genre: String
    let difficulty: Int
    let min_players: Int
    let max_players: Int
    let duration_minutes: Int
    let price_stars: Int
    let is_free: Bool
    let is_unlocked: Bool
}

struct ScriptDetailResponse: Decodable {
    let id: String
    let title: String
    let description: String
    let cover_url: String?
    let genre: String
    let difficulty: Int
    let min_players: Int
    let max_players: Int
    let duration_minutes: Int
    let price_stars: Int
    let is_free: Bool
    let is_unlocked: Bool
    let characters: [String]
}

struct RoomAPIResponse: Decodable {
    let id: String
    let name: String
    let script_id: String
    let host_id: String
    let host_username: String
    let status: String
    let current_players: Int
    let max_players: Int
    let ai_fill: Bool
    let can_join: Bool?
}

struct RoomCreateResponse: Decodable {
    let success: Bool
    let room_id: String
    let room: RoomAPIResponse
}

struct JoinRoomBody: Encodable {
    let password: String?
}

struct JoinRoomResponse: Decodable {
    let success: Bool
    let room: RoomAPIResponse
}

struct CreateRoomRequest: Encodable {
    let name: String
    let script_id: String
    let max_players: Int
    let host_id: String
    let host_username: String
}

struct GameStateResponse: Decodable {
    let session_id: String
    let script_id: String
    let current_phase: String
    let players: [GamePlayerResponse]
}

struct GamePlayerResponse: Decodable {
    let player_id: String
    let character_id: String
    let role: String
    let is_ai: Bool
    let ap_remaining: Int
}

struct ConfirmBody: Encodable {
    let player_id: String
}

struct VoteBody: Encodable {
    let voter_id: String
    let target_id: String
}

struct PlayerStatsResponse: Decodable {
    let player_id: String
    let total_games: Int
    let correct_votes: Int
    let detective_games: Int
    let detective_success: Int
    let murderer_games: Int
    let murderer_escapes: Int
    let stars_earned: Int
}

struct AchievementAPIResponse: Decodable, Identifiable {
    let achievement_id: String
    let name: String
    let description: String
    let rarity: String  // Backend returns enum as string: "common", "rare", etc.
    let icon: String?
    let unlocked_at: String?  // Backend ISO datetime or null
    let reward_stars: Int

    var id: String { achievement_id }
}

struct SettlementAPIResponse: Decodable, Identifiable {
    let settlement_id: String
    let script_name: String
    let role: String       // Backend returns enum: "detective", "murderer", "civilian"
    let result: String     // Backend returns enum: "victory", "defeat", "escape", "caught"
    let date: String       // ISO datetime from backend

    var id: String { settlement_id }

    init(from backend: SettlementBackendResponse) {
        self.settlement_id = backend.settlement_id
        self.script_name = backend.script_name
        self.role = backend.role.capitalized
        // Convert backend result enum to display string
        switch backend.result {
        case "victory": self.result = "✅ 胜利"
        case "caught": self.result = "✅ 凶手被抓"
        case "defeat": self.result = "❌ 失败"
        case "escape": self.result = "❌ 凶手逃脱"
        default: self.result = backend.result
        }
        // Format date from ISO to short string
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
        formatter.locale = Locale(identifier: "en_US_POSIX")
        if let date = formatter.date(from: backend.date) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateFormat = "MM-dd"
            self.date = displayFormatter.string(from: date)
        } else {
            self.date = backend.date.prefix(10).description
        }
    }
}

/// Raw backend response model for settlements — matches backend SettlementRecord exactly
struct SettlementBackendResponse: Decodable {
    let settlement_id: String
    let script_name: String
    let role: String
    let result: String
    let created_at: String

    var date: String { created_at }
}

struct ProductAPIResponse: Decodable, Identifiable {
    let product_id: String
    let name: String
    let description: String
    let category: String       // Backend enum: "script", "theme", etc.
    let price_stars: Int
    let icon: String?          // Backend product icon
    let preview_images: [String]
    let original_price: Int?   // Optional original price for discounts

    var id: String { product_id }
}

struct StarsBalanceResponse: Decodable {
    let balance: Int
}
