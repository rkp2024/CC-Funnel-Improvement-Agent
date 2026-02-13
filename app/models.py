from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

class FunnelType(str, Enum):
    CREDIT_CARD = "credit_card"  # Focus on this as primary funnel

class CardType(str, Enum):
    EDGE_PLUS_RUPAY = "edge_plus_rupay"  # Edge+ CSB Bank RuPay credit card

class DropOffStep(str, Enum):
    PAN_CARD_CONFIRMATION = "pan_card_confirmation"
    ELIGIBILITY_CHECK = "eligibility_check"
    CARD_CVP = "card_cvp"
    PERSONAL_DETAILS_FORM = "personal_details_form"
    CARD_APPROVAL_LIMIT = "card_approval_limit"
    EKYC_PROCESS = "ekyc_process"
    VKYC_PROCESS = "vkyc_process"
    OTP_SCREEN = "otp_screen"

class ObjectionType(str, Enum):
    CASHBACK_CLARITY = "cashback_clarity"
    FEES_CONCERNS = "fees_concerns"
    ELIGIBILITY_DOUBTS = "eligibility_doubts"
    DOCUMENT_HASSLE = "document_hassle"
    TRUST_SECURITY = "trust_security"
    BETTER_OFFERS = "better_offers"
    CREDIT_IMPACT = "credit_impact"
    REWARD_VALUE = "reward_value"

class AgentState(str, Enum):
    INIT = "init"
    WAITING_FOR_REPLY = "waiting_for_reply"
    GUIDING = "guiding"
    OBJECTION_IDENTIFIED = "objection_identified"
    OBJECTION_ADDRESSED = "objection_addressed"
    COMPLETED = "completed"
    OPTED_OUT = "opted_out"
    ESCALATED = "escalated"

class Outcome(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    OPTED_OUT = "opted_out"
    ESCALATED = "escalated"

class Message(BaseModel):
    user_id: str
    sender: str  # "user" or "agent"
    content: str
    timestamp: datetime = datetime.now()

class Conversation(BaseModel):
    user_id: str
    conversation_id: str  # Unique conversation identifier for logging
    state: AgentState = AgentState.INIT
    outcome: Outcome = Outcome.PENDING
    messages: List[Message] = []
    user_info: Dict[str, Any] = {}
    start_time: datetime = datetime.now()
    end_time: Optional[datetime] = None
    metrics: Dict[str, Any] = {}
    fomo_offer_count: int = 0  # Track how many times FOMO offer has been shown