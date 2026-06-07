"""Room management tests."""
import pytest
import asyncio
import uuid
from datetime import datetime

from src.services.room_service import RoomService
from src.services.script_service import script_service
from src.models.room import RoomCreate, RoomUpdate, RoomSettings, RoomStatus, AISlotConfig
from src.models.script import ScriptCreate, ScriptType, DifficultyLevel


@pytest.fixture
def room_service():
    """Create a fresh room service for tests."""
    return RoomService()


@pytest.fixture
def script_id():
    """Create a test script and return its ID."""
    import uuid
    script_data = ScriptCreate(
        title=f"TestRoomScript_{uuid.uuid4().hex[:8]}",
        description="A test script for room management testing with sufficient length description",
        script_type=ScriptType.BENGGE,
        difficulty=DifficultyLevel.EASY,
        min_players=4,
        max_players=6,
        duration_minutes=60
    )
    result = asyncio.run(script_service.create_script(script_data))
    if not result.get("success"):
        raise RuntimeError(f"Failed to create test script: {result}")
    return result["script_id"]


class TestRoomCreation:
    """Test room creation functionality."""

    @pytest.mark.asyncio
    async def test_create_room_success(self, room_service, script_id):
        """Test successful room creation."""
        room_data = RoomCreate(
            name="Test Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="user_001",
            host_username="HostUser"
        )

        result = await room_service.create_room(room_data)

        assert result["success"] is True
        assert "room_id" in result
        assert result["room"]["name"] == "Test Room"
        assert result["room"]["host_id"] == "user_001"
        assert result["room"]["status"] == "waiting"
        assert len(result["room"]["players"]) == 1

    @pytest.mark.asyncio
    async def test_create_room_duplicate_host(self, room_service, script_id):
        """Test creating room when host is already in another room."""
        # First room
        await room_service.create_room(RoomCreate(
            name="First Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="user_dup",
            host_username="DupUser"
        ))

        # Second room with same host
        result = await room_service.create_room(RoomCreate(
            name="Second Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="user_dup",
            host_username="DupUser"
        ))

        assert result["success"] is False
        assert "already in another room" in result["error"]

    @pytest.mark.asyncio
    async def test_create_room_invalid_script(self, room_service):
        """Test creating room with non-existent script."""
        room_data = RoomCreate(
            name="Test Room",
            script_id="invalid_script_id",
            settings=RoomSettings(),
            host_id="user_002",
            host_username="TestUser"
        )

        result = await room_service.create_room(room_data)

        assert result["success"] is False
        assert "Script not found" in result["error"]


class TestRoomJoining:
    """Test room joining functionality."""

    @pytest.mark.asyncio
    async def test_join_room_success(self, room_service, script_id):
        """Test successful room joining."""
        # Create room
        create_result = await room_service.create_room(RoomCreate(
            name="Join Test Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_001",
            host_username="HostUser"
        ))
        room_id = create_result["room_id"]

        # Join room
        result = await room_service.join_room(room_id, "user_003", "Joiner")

        assert result["success"] is True
        assert result["room"]["current_players"] == 2

    @pytest.mark.asyncio
    async def test_join_room_not_found(self, room_service):
        """Test joining non-existent room."""
        result = await room_service.join_room("invalid_room_id", "user_004", "Joiner")

        assert result["success"] is False
        assert "Room not found" in result["error"]

    @pytest.mark.asyncio
    async def test_join_room_already_in(self, room_service, script_id):
        """Test joining room when already in it."""
        create_result = await room_service.create_room(RoomCreate(
            name="Already In Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_002",
            host_username="HostUser"
        ))
        room_id = create_result["room_id"]

        # Join as new user
        await room_service.join_room(room_id, "user_005", "Joiner")

        # Try to join again
        result = await room_service.join_room(room_id, "user_005", "Joiner")

        assert result["success"] is False
        assert "already in this room" in result["error"]

    @pytest.mark.asyncio
    async def test_join_room_in_another(self, room_service, script_id):
        """Test joining room when in another room."""
        # Create first room and join
        room1 = await room_service.create_room(RoomCreate(
            name="Room One",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_003",
            host_username="Host3"
        ))
        await room_service.join_room(room1["room_id"], "user_006", "Player")

        # Create second room
        room2 = await room_service.create_room(RoomCreate(
            name="Room Two",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_004",
            host_username="Host4"
        ))

        # Try to join second room
        result = await room_service.join_room(room2["room_id"], "user_006", "Player")

        assert result["success"] is False
        assert "already in another room" in result["error"]

    @pytest.mark.asyncio
    async def test_join_room_wrong_password(self, room_service, script_id):
        """Test joining private room with wrong password."""
        # Create private room
        settings = RoomSettings(is_private=True, password="secret123")
        create_result = await room_service.create_room(RoomCreate(
            name="Private Room",
            script_id=script_id,
            settings=settings,
            host_id="host_005",
            host_username="Host5"
        ))
        room_id = create_result["room_id"]

        # Try to join with wrong password
        result = await room_service.join_room(room_id, "user_007", "Joiner", password="wrong")

        assert result["success"] is False
        assert "Invalid room password" in result["error"]

    @pytest.mark.asyncio
    async def test_join_room_full(self, room_service, script_id):
        """Test joining full room."""
        # First create a script with max 4 players using the singleton
        # Note: ScriptCreate requires min_players >= 4
        small_script = ScriptCreate(
            title=f"SmallScript_{uuid.uuid4().hex[:8]}",
            description="A small test script for testing full rooms with sufficient length here",
            script_type=ScriptType.BENGGE,
            difficulty=DifficultyLevel.EASY,
            min_players=4,
            max_players=4,
            duration_minutes=60
        )
        script_result = await script_service.create_script(small_script)
        small_script_id = script_result["script_id"]

        settings = RoomSettings(min_players=2)
        create_result = await room_service.create_room(RoomCreate(
            name="Small Room",
            script_id=small_script_id,
            settings=settings,
            host_id="host_full",
            host_username="HostFull"
        ))
        room_id = create_result["room_id"]

        # Fill the room (host + 3 more = 4 total, which is max_players=4)
        for i in range(3):
            await room_service.join_room(room_id, f"user_fill_{i}", f"Filler{i}")

        # Try to join full room
        result = await room_service.join_room(room_id, "user_overflow", "Overflow")

        assert result["success"] is False
        assert "Room is full" in result["error"]


class TestRoomLeaving:
    """Test room leaving functionality."""

    @pytest.mark.asyncio
    async def test_leave_room_success(self, room_service, script_id):
        """Test successful room leaving."""
        create_result = await room_service.create_room(RoomCreate(
            name="Leave Test Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_leave",
            host_username="HostLeave"
        ))
        room_id = create_result["room_id"]

        await room_service.join_room(room_id, "user_leave", "Leaver")

        result = await room_service.leave_room(room_id, "user_leave")

        assert result["success"] is True
        assert result["room"]["current_players"] == 1

    @pytest.mark.asyncio
    async def test_host_leave_closes_room(self, room_service, script_id):
        """Test that host leaving closes the room."""
        create_result = await room_service.create_room(RoomCreate(
            name="Host Leave Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_closer",
            host_username="HostCloser"
        ))
        room_id = create_result["room_id"]

        await room_service.join_room(room_id, "user_in_room", "Player")

        result = await room_service.leave_room(room_id, "host_closer")

        assert result["success"] is True
        assert "closed by host" in result["message"]

        # Verify room is deleted
        room = await room_service.get_room(room_id)
        assert room is None


class TestRoomKicking:
    """Test room kicking functionality."""

    @pytest.mark.asyncio
    async def test_kick_player_success(self, room_service, script_id):
        """Test successful player kicking."""
        create_result = await room_service.create_room(RoomCreate(
            name="Kick Test Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_kicker",
            host_username="HostKicker"
        ))
        room_id = create_result["room_id"]

        await room_service.join_room(room_id, "user_kicked", "KickedUser")

        result = await room_service.kick_player(room_id, "host_kicker", "user_kicked")

        assert result["success"] is True
        assert result["room"]["current_players"] == 1

    @pytest.mark.asyncio
    async def test_kick_not_host(self, room_service, script_id):
        """Test that non-host cannot kick."""
        create_result = await room_service.create_room(RoomCreate(
            name="No Kick Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_real",
            host_username="RealHost"
        ))
        room_id = create_result["room_id"]

        await room_service.join_room(room_id, "user_normal", "NormalUser")
        await room_service.join_room(room_id, "user_target", "TargetUser")

        result = await room_service.kick_player(room_id, "user_normal", "user_target")

        assert result["success"] is False
        assert "Only host can kick" in result["error"]


class TestRoomReady:
    """Test room ready functionality."""

    @pytest.mark.asyncio
    async def test_set_ready_success(self, room_service, script_id):
        """Test setting player as ready."""
        create_result = await room_service.create_room(RoomCreate(
            name="Ready Test Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_ready",
            host_username="HostReady"
        ))
        room_id = create_result["room_id"]

        await room_service.join_room(room_id, "user_ready", "ReadyUser")

        result = await room_service.set_player_ready(room_id, "user_ready", ready=True)

        assert result["success"] is True
        player = next(p for p in result["room"]["players"] if p["user_id"] == "user_ready")
        assert player["is_ready"] is True

    @pytest.mark.asyncio
    async def test_all_ready_changes_status(self, room_service, script_id):
        """Test that room status changes when all players are ready."""
        create_result = await room_service.create_room(RoomCreate(
            name="All Ready Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_all",
            host_username="HostAll"
        ))
        room_id = create_result["room_id"]

        # Host is already ready, add one more player
        await room_service.join_room(room_id, "user_last", "LastUser")

        # Set last player ready
        result = await room_service.set_player_ready(room_id, "user_last", ready=True)

        assert result["success"] is True
        assert result["room"]["status"] == "ready"


class TestRoomAI:
    """Test AI player management."""

    @pytest.mark.asyncio
    async def test_add_ai_success(self, room_service, script_id):
        """Test adding AI player."""
        create_result = await room_service.create_room(RoomCreate(
            name="AI Test Room",
            script_id=script_id,
            settings=RoomSettings(ai_fill=True),
            host_id="host_ai",
            host_username="HostAI"
        ))
        room_id = create_result["room_id"]

        config = AISlotConfig(
            seat_number=2,
            ai_character_id="npc_001",
            ai_character_name="AI Character"
        )

        result = await room_service.add_ai_slot(room_id, "host_ai", config)

        assert result["success"] is True
        assert result["room"]["current_players"] == 2
        ai_player = next(p for p in result["room"]["players"] if p["is_ai"])
        assert ai_player["username"] == "AI Character"

    @pytest.mark.asyncio
    async def test_remove_ai_success(self, room_service, script_id):
        """Test removing AI player."""
        create_result = await room_service.create_room(RoomCreate(
            name="Remove AI Room",
            script_id=script_id,
            settings=RoomSettings(ai_fill=True),
            host_id="host_rmai",
            host_username="HostRMAI"
        ))
        room_id = create_result["room_id"]

        # Add AI
        config = AISlotConfig(
            seat_number=2,
            ai_character_id="npc_002",
            ai_character_name="AI To Remove"
        )
        await room_service.add_ai_slot(room_id, "host_rmai", config)

        # Remove AI
        result = await room_service.remove_ai_slot(room_id, "host_rmai", 2)

        assert result["success"] is True
        assert result["room"]["current_players"] == 1

    @pytest.mark.asyncio
    async def test_add_ai_not_host(self, room_service, script_id):
        """Test that non-host cannot add AI."""
        create_result = await room_service.create_room(RoomCreate(
            name="No AI Room",
            script_id=script_id,
            settings=RoomSettings(ai_fill=True),
            host_id="host_only",
            host_username="HostOnly"
        ))
        room_id = create_result["room_id"]

        await room_service.join_room(room_id, "user_not_host", "NotHost")

        config = AISlotConfig(
            seat_number=2,
            ai_character_id="npc_003",
            ai_character_name="AI"
        )

        result = await room_service.add_ai_slot(room_id, "user_not_host", config)

        assert result["success"] is False
        assert "Only host can add AI" in result["error"]


class TestRoomGameStart:
    """Test game starting functionality."""

    @pytest.mark.asyncio
    async def test_start_game_success(self, room_service, script_id):
        """Test successful game start."""
        create_result = await room_service.create_room(RoomCreate(
            name="Start Game Room",
            script_id=script_id,
            settings=RoomSettings(min_players=2),
            host_id="host_start",
            host_username="HostStart"
        ))
        room_id = create_result["room_id"]

        await room_service.join_room(room_id, "user_join", "Joiner")
        await room_service.set_player_ready(room_id, "user_join", ready=True)

        result = await room_service.start_game(room_id, "host_start")

        assert result["success"] is True
        assert result["room"]["status"] == "playing"

    @pytest.mark.asyncio
    async def test_start_game_not_ready(self, room_service, script_id):
        """Test starting game when not all ready."""
        create_result = await room_service.create_room(RoomCreate(
            name="Not Ready Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_nr",
            host_username="HostNR"
        ))
        room_id = create_result["room_id"]

        # Don't set anyone as ready
        result = await room_service.start_game(room_id, "host_nr")

        assert result["success"] is False
        error_msg = result["error"].lower()
        assert "not ready" in error_msg or "need at least" in error_msg


class TestRoomListing:
    """Test room listing functionality."""

    @pytest.mark.asyncio
    async def test_list_rooms(self, room_service, script_id):
        """Test listing rooms."""
        # Create multiple rooms
        for i in range(3):
            await room_service.create_room(RoomCreate(
                name=f"Listed Room {i}",
                script_id=script_id,
                settings=RoomSettings(),
                host_id=f"host_list_{i}",
                host_username=f"HostList{i}"
            ))

        rooms = await room_service.list_rooms()

        assert len(rooms) >= 3

    @pytest.mark.asyncio
    async def test_filter_by_status(self, room_service, script_id):
        """Test filtering rooms by status."""
        # Create room with another player and set ready to make status = READY
        create_result = await room_service.create_room(RoomCreate(
            name="Playing Room",
            script_id=script_id,
            settings=RoomSettings(min_players=2),
            host_id="host_play",
            host_username="HostPlay"
        ))
        room_id = create_result["room_id"]

        # Add another player and set both ready to make room status = READY
        await room_service.join_room(room_id, "player2", "Player2")
        await room_service.set_player_ready(room_id, "player2", ready=True)

        # Now start the game
        await room_service.start_game(room_id, "host_play")

        playing_rooms = await room_service.list_rooms(status=RoomStatus.PLAYING)

        assert len(playing_rooms) >= 1
        assert all(r["status"] == "playing" for r in playing_rooms)


class TestRoomUpdate:
    """Test room update functionality."""

    @pytest.mark.asyncio
    async def test_update_room_name(self, room_service, script_id):
        """Test updating room name."""
        create_result = await room_service.create_room(RoomCreate(
            name="Old Name",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_update",
            host_username="HostUpdate"
        ))
        room_id = create_result["room_id"]

        update_data = RoomUpdate(name="New Name")
        result = await room_service.update_room(room_id, "host_update", update_data)

        assert result["success"] is True
        assert result["room"]["name"] == "New Name"

    @pytest.mark.asyncio
    async def test_update_not_host(self, room_service, script_id):
        """Test that non-host cannot update room."""
        create_result = await room_service.create_room(RoomCreate(
            name="Protected Room",
            script_id=script_id,
            settings=RoomSettings(),
            host_id="host_prot",
            host_username="HostProt"
        ))
        room_id = create_result["room_id"]

        await room_service.join_room(room_id, "user_no_update", "NoUpdate")

        update_data = RoomUpdate(name="Hacked Name")
        result = await room_service.update_room(room_id, "user_no_update", update_data)

        assert result["success"] is False
        assert "Only host can update" in result["error"]
