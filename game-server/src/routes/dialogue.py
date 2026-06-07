"""Dialogue system routes."""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query

from ..models.dialogue import (
    PrivateChatRequest, DialogueFilterParams, MessageType
)
from ..services.dialogue_service import dialogue_service

router = APIRouter(prefix="/dialogue", tags=["dialogue"])


@router.post("/sessions/{session_id}/message", response_model=dict)
async def send_player_message(
    session_id: str,
    room_id: str,
    player_id: str,
    player_name: str,
    content: str,
    target_id: Optional[str] = None
):
    """Send a player message to the dialogue."""
    msg_type = MessageType.PRIVATE if target_id else MessageType.PLAYER

    message = await dialogue_service.store_message(
        session_id=session_id,
        room_id=room_id,
        sender_id=player_id,
        sender_name=player_name,
        sender_type=msg_type,
        content=content,
        metadata={"target_id": target_id} if target_id else {}
    )

    return {
        "success": True,
        "message_id": message.message_id,
        "timestamp": message.timestamp.isoformat()
    }


@router.post("/sessions/{session_id}/npc-response", response_model=dict)
async def get_npc_response(
    session_id: str,
    room_id: str,
    character_id: str,
    player_id: str,
    player_message: str,
    current_act: str = "act_2",
    game_state: Optional[dict] = None
):
    """Get NPC response to player message."""
    try:
        # Build context
        context = await dialogue_service.build_dialogue_context(
            character_id=character_id,
            player_id=player_id,
            player_message=player_message,
            session_id=session_id,
            current_act=current_act,
            game_state=game_state or {}
        )

        # Build prompt
        system_prompt = dialogue_service.build_npc_prompt(context, player_message)

        # Call API (simulated)
        api_response = await dialogue_service.call_npc_api(system_prompt, player_message)

        # Parse response
        parsed = dialogue_service.parse_npc_response(api_response)

        # Update state
        state_update = await dialogue_service.update_dialogue_state(
            session_id=session_id,
            character_id=character_id,
            parsed_output=parsed,
            player_id=player_id
        )

        # Store NPC message
        from ..services.character_service import character_service
        char = await character_service.get_character(character_id)
        char_name = char["name"] if char else "NPC"

        message = await dialogue_service.store_message(
            session_id=session_id,
            room_id=room_id,
            sender_id=character_id,
            sender_name=char_name,
            sender_type=MessageType.NPC,
            content=parsed.reply,
            metadata={
                "emotional_tag": parsed.emotional_tag,
                "info_revealed": parsed.info_revealed,
                "attitude_shift": parsed.attitude_shift
            }
        )

        return {
            "success": True,
            "message_id": message.message_id,
            "reply": parsed.reply,
            "emotional_tag": parsed.emotional_tag,
            "info_revealed": parsed.info_revealed,
            "state_update": {
                "new_emotional_tag": state_update.new_emotional_tag,
                "info_released": state_update.info_released,
                "attitude_changes": state_update.attitude_changes,
                "arc_transition": state_update.arc_transition
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/sessions/{session_id}/messages", response_model=list)
async def get_session_messages(
    session_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """Get messages for a session."""
    messages = await dialogue_service.get_messages_for_session(
        session_id=session_id,
        skip=skip,
        limit=limit
    )

    return [
        {
            "message_id": msg.message_id,
            "sender_id": msg.sender_id,
            "sender_name": msg.sender_name,
            "sender_type": msg.sender_type.value,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
            "metadata": msg.metadata
        }
        for msg in messages
    ]


@router.post("/private-chat", response_model=dict)
async def create_private_chat(request: PrivateChatRequest):
    """Create a private chat session with NPC."""
    session = await dialogue_service.create_private_chat(
        player_id=request.player_id,
        npc_id=request.npc_id
    )

    return {
        "success": True,
        "session_id": session.session_id,
        "started_at": session.started_at.isoformat()
    }


@router.post("/private-chat/{session_id}/end", response_model=dict)
async def end_private_chat(session_id: str):
    """End a private chat session."""
    result = await dialogue_service.end_private_chat(session_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Private chat session not found"
        )

    return {"success": True}


@router.get("/quota/{character_id}", response_model=dict)
async def get_speech_quota(character_id: str, act: str):
    """Get remaining speech quota for NPC."""
    quota_key = f"{character_id}_{act}"

    # Initialize if not exists
    from ..services.dialogue_service import dialogue_service as ds
    if quota_key not in ds._speech_quotas:
        await ds.init_speech_quota(character_id, act)

    quota = ds._speech_quotas.get(quota_key)

    if not quota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quota not found"
        )

    return {
        "character_id": quota.character_id,
        "act": quota.act,
        "max_speeches": quota.max_speeches,
        "used_speeches": quota.used_speeches,
        "remaining_speeches": quota.remaining_speeches
    }
