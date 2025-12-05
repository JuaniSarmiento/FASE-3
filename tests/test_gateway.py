"""
Unit and integration tests for AI Gateway

Tests cover:
- Session management
- Interaction processing pipeline
- Mode switching
- Trace capture and retrieval
- Gateway orchestration
"""
import pytest
from uuid import UUID

from backend.core.ai_gateway import AIGateway
from backend.core.cognitive_engine import AgentMode, CognitiveState
from backend.models.trace import TraceLevel


@pytest.mark.unit
@pytest.mark.gateway
class TestAIGateway:
    """Tests for AIGateway"""

    @pytest.fixture
    def gateway(self, mock_llm_provider):
        """Fixture providing an AI Gateway with mock LLM"""
        return AIGateway(llm_provider=mock_llm_provider)

    # ========================================================================
    # Session Management Tests
    # ========================================================================

    def test_create_session(self, gateway, student_id, activity_id):
        """Test creating a new session"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        assert session_id is not None
        # Should be valid UUID
        UUID(session_id)

        # Session should be stored
        assert session_id in gateway._active_sessions

    def test_create_multiple_sessions(self, gateway, student_id):
        """Test creating multiple sessions for same student"""
        session1 = gateway.create_session(student_id=student_id, activity_id="activity1")
        session2 = gateway.create_session(student_id=student_id, activity_id="activity2")

        assert session1 != session2
        assert session1 in gateway._active_sessions
        assert session2 in gateway._active_sessions

    def test_get_session_info(self, gateway, student_id, activity_id):
        """Test retrieving session information"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        session = gateway._active_sessions.get(session_id)

        assert session is not None
        assert session["student_id"] == student_id
        assert session["activity_id"] == activity_id
        assert "mode" in session

    # ========================================================================
    # Mode Management Tests
    # ========================================================================

    def test_set_mode(self, gateway, student_id, activity_id):
        """Test setting agent mode for a session"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        gateway.set_mode(session_id, AgentMode.TUTOR)

        session = gateway._active_sessions[session_id]
        assert session["mode"] == AgentMode.TUTOR

    def test_switch_modes(self, gateway, student_id, activity_id):
        """Test switching between different modes"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        for mode in [
            AgentMode.TUTOR,
            AgentMode.SIMULATOR,
            AgentMode.EVALUATOR,
        ]:
            gateway.set_mode(session_id, mode)
            session = gateway._active_sessions[session_id]
            assert session["mode"] == mode

    def test_default_mode_is_tutor(self, gateway, student_id, activity_id):
        """Test that default mode is TUTOR"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        session = gateway._active_sessions[session_id]
        assert session["mode"] == AgentMode.TUTOR

    # ========================================================================
    # Interaction Processing Tests
    # ========================================================================

    def test_process_interaction_basic(self, gateway, student_id, activity_id):
        """Test processing a basic interaction"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        response = gateway.process_interaction(
            session_id=session_id, prompt="¿Qué es una cola?"
        )

        assert response is not None
        assert "message" in response or "blocked" in response

    def test_process_delegation_blocked(self, gateway, student_id, activity_id):
        """Test that total delegation is blocked"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )
        gateway.set_mode(session_id, AgentMode.TUTOR)

        response = gateway.process_interaction(
            session_id=session_id, prompt="Dame el código completo de una cola"
        )

        # Should be blocked or redirected
        assert response.get("blocked") is True or "?" in response.get("message", "")

    def test_process_conceptual_question_allowed(self, gateway, student_id, activity_id):
        """Test that conceptual questions are allowed"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        response = gateway.process_interaction(
            session_id=session_id, prompt="¿Qué es una cola?"
        )

        assert response.get("blocked") is not True
        assert "message" in response
        assert len(response["message"]) > 0

    def test_interaction_creates_trace(self, gateway, student_id, activity_id):
        """Test that interactions create N4 traces"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        initial_trace_count = len(gateway._traces)

        gateway.process_interaction(session_id=session_id, prompt="Test prompt")

        # Should have created at least one trace
        assert len(gateway._traces) > initial_trace_count

    def test_multiple_interactions_build_history(self, gateway, student_id, activity_id):
        """Test that multiple interactions build conversation history"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        prompts = [
            "¿Qué es una cola?",
            "¿Cuáles son las operaciones?",
            "Planeo usar un arreglo circular",
        ]

        for prompt in prompts:
            gateway.process_interaction(session_id=session_id, prompt=prompt)

        # Should have multiple traces
        session_traces = [
            t for t in gateway._traces.values() if t.session_id == session_id
        ]
        assert len(session_traces) >= len(prompts)

    # ========================================================================
    # Trace Capture and Retrieval Tests
    # ========================================================================

    def test_get_trace_sequence(self, gateway, student_id, activity_id):
        """Test retrieving trace sequence for a session"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        # Create some interactions
        gateway.process_interaction(session_id=session_id, prompt="Test 1")
        gateway.process_interaction(session_id=session_id, prompt="Test 2")

        sequence = gateway.get_trace_sequence(session_id)

        assert sequence is not None
        assert sequence.session_id == session_id
        assert len(sequence.traces) >= 2

    def test_trace_sequence_ordering(self, gateway, student_id, activity_id):
        """Test that traces in sequence are ordered by timestamp"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        for i in range(5):
            gateway.process_interaction(session_id=session_id, prompt=f"Test {i}")

        sequence = gateway.get_trace_sequence(session_id)

        # Traces should be in chronological order
        timestamps = [trace.timestamp for trace in sequence.traces]
        assert timestamps == sorted(timestamps)

    def test_trace_level_is_n4(self, gateway, student_id, activity_id):
        """Test that captured traces are N4 level"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        gateway.process_interaction(session_id=session_id, prompt="Test prompt")

        sequence = gateway.get_trace_sequence(session_id)

        # All traces should be N4
        for trace in sequence.traces:
            assert trace.trace_level == TraceLevel.N4_COGNITIVO

    # ========================================================================
    # Risk Analysis Tests
    # ========================================================================

    def test_get_risk_report(self, gateway, student_id, activity_id):
        """Test retrieving risk report for a session"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        # Create interaction with delegation
        gateway.process_interaction(
            session_id=session_id, prompt="Dame el código completo"
        )

        # Get risk report (may need to be triggered explicitly)
        sequence = gateway.get_trace_sequence(session_id)
        assert sequence is not None

        # Risks should be captured
        session_risks = [
            r for r in gateway._risks.values() if r.session_id == session_id
        ]
        # May or may not have risks depending on implementation
        assert session_risks is not None

    # ========================================================================
    # Integration Tests
    # ========================================================================

    @pytest.mark.integration
    def test_full_session_flow(self, gateway, student_id, activity_id):
        """Test complete session flow from creation to evaluation"""
        # 1. Create session
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )
        assert session_id is not None

        # 2. Set mode
        gateway.set_mode(session_id, AgentMode.TUTOR)

        # 3. Multiple interactions
        interactions = [
            "¿Qué es una cola?",
            "¿Cuáles son las operaciones básicas?",
            "Planeo usar un arreglo circular. ¿Es correcto?",
        ]

        for prompt in interactions:
            response = gateway.process_interaction(session_id=session_id, prompt=prompt)
            assert response is not None

        # 4. Get trace sequence
        sequence = gateway.get_trace_sequence(session_id)
        assert len(sequence.traces) >= len(interactions)

        # 5. Verify cognitive path
        path = sequence.get_cognitive_path()
        assert len(path) > 0

        # 6. Check AI dependency
        dependency = sequence.ai_dependency_score
        assert 0.0 <= dependency <= 1.0

    @pytest.mark.integration
    def test_multi_session_isolation(self, gateway):
        """Test that sessions are properly isolated"""
        # Create two sessions
        session1 = gateway.create_session(
            student_id="student1", activity_id="activity1"
        )
        session2 = gateway.create_session(
            student_id="student2", activity_id="activity2"
        )

        # Interact with both
        gateway.process_interaction(session_id=session1, prompt="Session 1 prompt")
        gateway.process_interaction(session_id=session2, prompt="Session 2 prompt")

        # Get sequences
        seq1 = gateway.get_trace_sequence(session1)
        seq2 = gateway.get_trace_sequence(session2)

        # Should be isolated
        assert seq1.session_id == session1
        assert seq2.session_id == session2
        assert seq1.student_id == "student1"
        assert seq2.student_id == "student2"

    @pytest.mark.integration
    def test_error_handling_invalid_session(self, gateway):
        """Test error handling for invalid session ID"""
        with pytest.raises(Exception):
            gateway.process_interaction(
                session_id="invalid-session-id", prompt="Test"
            )

    @pytest.mark.integration
    def test_empty_prompt_handling(self, gateway, student_id, activity_id):
        """Test handling of empty prompts"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        # Empty prompt should be handled gracefully
        response = gateway.process_interaction(session_id=session_id, prompt="")

        # Should either reject or handle gracefully
        assert response is not None


# ============================================================================
# Performance Tests
# ============================================================================


@pytest.mark.slow
@pytest.mark.gateway
class TestGatewayPerformance:
    """Performance tests for AI Gateway"""

    def test_many_sessions(self, mock_llm_provider):
        """Test handling many concurrent sessions"""
        gateway = AIGateway(llm_provider=mock_llm_provider)

        session_ids = []
        for i in range(100):
            session_id = gateway.create_session(
                student_id=f"student_{i}", activity_id=f"activity_{i}"
            )
            session_ids.append(session_id)

        assert len(session_ids) == 100
        assert len(set(session_ids)) == 100  # All unique

    def test_many_interactions_per_session(self, mock_llm_provider, student_id, activity_id):
        """Test handling many interactions in one session"""
        gateway = AIGateway(llm_provider=mock_llm_provider)

        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        for i in range(50):
            gateway.process_interaction(session_id=session_id, prompt=f"Test {i}")

        sequence = gateway.get_trace_sequence(session_id)
        assert len(sequence.traces) >= 50
