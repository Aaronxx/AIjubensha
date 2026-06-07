//
//  Models.swift
//  AI推理叙事游戏 - 数据模型
//

import Foundation

// MARK: - User Profile
struct UserProfile: Decodable, Identifiable {
    let user_id: String
    let username: String
    let email: String
    var avatar_url: String?
    var member_level: Int = 0
    var stars_balance: Int = 0

    var id: String { user_id }
}

// MARK: - Script
struct Script: Decodable, Identifiable {
    let script_id: String
    let title: String
    let description: String
    let cover_url: String?
    let genre: String
    let difficulty: Int
    let min_players: Int
    let max_players: Int
    let duration_minutes: Int
    let price_stars: Int
    var is_free: Bool = false
    var is_unlocked: Bool = false

    var id: String { script_id }
    var difficultyLabel: String {
        String(repeating: "★", count: difficulty) + String(repeating: "☆", count: 5 - difficulty)
    }

    init(from dto: ScriptResponse) {
        self.script_id = dto.id
        self.title = dto.title
        self.description = dto.description
        self.cover_url = dto.cover_url
        self.genre = dto.genre
        self.difficulty = dto.difficulty
        self.min_players = dto.min_players
        self.max_players = dto.max_players
        self.duration_minutes = dto.duration_minutes
        self.price_stars = dto.price_stars
        self.is_free = dto.is_free
        self.is_unlocked = dto.is_unlocked
    }
}

// MARK: - Room
struct Room: Decodable, Identifiable {
    let room_id: String
    let script_id: String
    let script_name: String
    let host_id: String
    let host_name: String
    let status: RoomStatus
    let current_players: Int
    let max_players: Int
    let ai_fill: Bool

    var id: String { room_id }
    var canJoin: Bool { status == .waiting && current_players < max_players }

    init(from dto: RoomAPIResponse, scriptName: String? = nil) {
        self.room_id = dto.id
        self.script_id = dto.script_id
        self.script_name = scriptName ?? dto.script_id.prefix(8).uppercased()
        self.host_id = dto.host_id
        self.host_name = dto.host_username
        self.status = RoomStatus(rawValue: dto.status) ?? .finished
        self.current_players = dto.current_players
        self.max_players = dto.max_players
        self.ai_fill = dto.ai_fill
    }
}

enum RoomStatus: String, Decodable {
    case waiting = "waiting"
    case playing = "playing"
    case finished = "finished"
}

// MARK: - Character
struct Character: Decodable, Identifiable {
    let character_id: String
    let name: String
    let description: String
    let age: Int
    let occupation: String
    let personality: PersonalityMatrix
    let role_type: CharacterRole

    var id: String { character_id }
}

enum CharacterRole: String, Decodable {
    case civilian = "civilian"
    case murderer = "murderer"
    case detective = "detective"
}

struct PersonalityMatrix: Decodable {
    let extroversion: Float
    let aggressiveness: Float
    let honesty: Float
    let rationality: Float
}

// MARK: - Player Stats
struct PlayerStats: Decodable {
    let player_id: String
    var total_games: Int = 0
    var correct_votes: Int = 0
    var incorrect_votes: Int = 0
    var vote_accuracy: Double = 0
    var detective_games: Int = 0
    var detective_success: Int = 0
    var murderer_games: Int = 0
    var murderer_escapes: Int = 0
    var stars_earned: Int = 0
}

// MARK: - Achievement
struct Achievement: Decodable, Identifiable {
    let achievement_id: String
    let name: String
    let description: String
    let rarity: String
    var icon: String?
    var unlocked_at: String?
    var reward_stars: Int = 0

    var id: String { achievement_id }
}

// MARK: - Shop Product
struct ShopProduct: Decodable, Identifiable {
    let product_id: String
    let name: String
    let description: String
    let category: String
    let price_stars: Int
    var original_price: Int?
    var preview_images: [String] = []

    var id: String { product_id }

    init(from dto: ProductAPIResponse) {
        self.product_id = dto.product_id
        self.name = dto.name
        self.description = dto.description
        // Map backend enum to Chinese display category
        switch dto.category {
        case "script": self.category = "剧本"
        case "theme": self.category = "主题"
        case "chat_skin": self.category = "聊天皮肤"
        case "profile_skin": self.category = "主页皮肤"
        case "avatar_frame": self.category = "头像框"
        case "gift": self.category = "礼物"
        case "membership": self.category = "会员"
        default: self.category = dto.category
        }
        self.price_stars = dto.price_stars
        self.preview_images = dto.preview_images
    }
}

// MARK: - Chat Message
struct ChatMessage: Identifiable, Equatable {
    let id: String
    let sender_id: String
    let sender_name: String
    let content: String
    let timestamp: Date
    let is_system: Bool
    let is_ai: Bool

    init(id: String = UUID().uuidString, sender_id: String, sender_name: String, content: String, timestamp: Date = Date(), is_system: Bool = false, is_ai: Bool = false) {
        self.id = id
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.content = content
        self.timestamp = timestamp
        self.is_system = is_system
        self.is_ai = is_ai
    }
}

// MARK: - Settlement Record
struct SettlementRecord: Identifiable {
    let id = UUID()
    let scriptName: String
    let role: String
    let result: String
    let date: String
}
