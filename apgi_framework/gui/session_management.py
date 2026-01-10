"""
Session setup and participant management for parameter estimation experiments.

Provides classes for managing experimental sessions and participant information.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

from ..data.parameter_estimation_dao import ParameterEstimationDAO
from ..data.parameter_estimation_models import SessionData

logger = logging.getLogger(__name__)


class SessionSetupManager:
    """
    Manages session setup and configuration.

    Handles creation, loading, and configuration of experimental sessions.
    """

    def __init__(self, dao: ParameterEstimationDAO):
        """
        Initialize session setup manager.

        Args:
            dao: Data access object for persistence
        """
        self.dao = dao
        self.current_session: Optional[SessionData] = None

        logger.info("SessionSetupManager initialized")

    def create_session(
        self,
        participant_id: str,
        researcher: str = "",
        protocol_version: str = "1.0.0",
        notes: str = "",
    ) -> SessionData:
        """
        Create a new experimental session.

        Args:
            participant_id: Participant identifier
            researcher: Researcher name
            protocol_version: Protocol version string
            notes: Session notes

        Returns:
            SessionData: Created session
        """
        session = SessionData(
            session_id=str(uuid.uuid4()),
            participant_id=participant_id,
            session_date=datetime.now(),
            protocol_version=protocol_version,
            completion_status="in_progress",
            researcher=researcher,
            notes=notes,
        )

        # Save to database
        self.dao.create_session(session)
        self.current_session = session

        logger.info(
            f"Created session {session.session_id} for participant {participant_id}"
        )
        return session

    def load_session(self, session_id: str) -> Optional[SessionData]:
        """
        Load an existing session.

        Args:
            session_id: Session identifier

        Returns:
            SessionData or None if not found
        """
        session = self.dao.get_session(session_id)

        if session:
            self.current_session = session
            logger.info(f"Loaded session {session_id}")
        else:
            logger.warning(f"Session {session_id} not found")

        return session

    def update_session(self, session: SessionData) -> None:
        """
        Update session information.

        Args:
            session: Updated session data
        """
        self.dao.update_session(session)
        logger.info(f"Updated session {session.session_id}")

    def end_session(self, session: SessionData) -> None:
        """
        End a session and mark as completed.

        Args:
            session: Session to end
        """
        session.completion_status = "completed"
        session.total_duration_minutes = (
            datetime.now() - session.session_date
        ).total_seconds() / 60

        self.dao.update_session(session)
        logger.info(f"Ended session {session.session_id}")

    def get_session_summary(self, session: SessionData) -> Dict[str, Any]:
        """
        Get summary information for a session.

        Args:
            session: Session to summarize

        Returns:
            Dictionary with session summary
        """
        trial_counts = session.get_trial_count_by_task()

        return {
            "session_id": session.session_id,
            "participant_id": session.participant_id,
            "session_date": session.session_date.isoformat(),
            "completion_status": session.completion_status,
            "duration_minutes": session.total_duration_minutes,
            "trial_counts": trial_counts,
            "quality_score": session.session_quality_score,
            "researcher": session.researcher,
        }


class ParticipantManager:
    """
    Manages participant information and tracking.

    Handles participant registration, session history, and metadata.
    """

    def __init__(self, dao: ParameterEstimationDAO):
        """
        Initialize participant manager.

        Args:
            dao: Data access object for persistence
        """
        self.dao = dao
        self.participants: Dict[str, Dict[str, Any]] = {}

        logger.info("ParticipantManager initialized")

    def register_participant(
        self, participant_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a new participant.

        Args:
            participant_id: Participant identifier
            metadata: Optional participant metadata
        """
        if participant_id in self.participants:
            logger.warning(f"Participant {participant_id} already registered")
            return

        self.participants[participant_id] = {
            "participant_id": participant_id,
            "registration_date": datetime.now(),
            "metadata": metadata or {},
            "sessions": [],
        }

        logger.info(f"Registered participant {participant_id}")

    def get_participant_sessions(self, participant_id: str) -> List[str]:
        """
        Get all sessions for a participant.

        Args:
            participant_id: Participant identifier

        Returns:
            List of session IDs
        """
        return self.dao.list_sessions(participant_id=participant_id)

    def get_participant_info(self, participant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get participant information.

        Args:
            participant_id: Participant identifier

        Returns:
            Participant information dictionary or None
        """
        return self.participants.get(participant_id)

    def update_participant_metadata(
        self, participant_id: str, metadata: Dict[str, Any]
    ) -> None:
        """
        Update participant metadata.

        Args:
            participant_id: Participant identifier
            metadata: Updated metadata
        """
        if participant_id not in self.participants:
            logger.warning(f"Participant {participant_id} not found")
            return

        self.participants[participant_id]["metadata"].update(metadata)
        logger.info(f"Updated metadata for participant {participant_id}")

    def get_participant_summary(self, participant_id: str) -> Dict[str, Any]:
        """
        Get summary information for a participant.

        Args:
            participant_id: Participant identifier

        Returns:
            Dictionary with participant summary
        """
        sessions = self.get_participant_sessions(participant_id)
        participant_info = self.get_participant_info(participant_id)

        return {
            "participant_id": participant_id,
            "n_sessions": len(sessions),
            "session_ids": sessions,
            "metadata": (
                participant_info.get("metadata", {}) if participant_info else {}
            ),
        }
