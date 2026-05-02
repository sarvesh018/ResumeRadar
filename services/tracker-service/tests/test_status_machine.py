from app.core.status_machine import ApplicationStatus, is_valid_transition, get_allowed_transitions


class TestValidTransitions:
    def test_wishlist_to_applied(self):
        assert is_valid_transition(ApplicationStatus.WISHLIST, ApplicationStatus.APPLIED) is True

    def test_applied_to_screening(self):
        assert is_valid_transition(ApplicationStatus.APPLIED, ApplicationStatus.SCREENING) is True

    def test_applied_to_interviewing(self):
        assert is_valid_transition(ApplicationStatus.APPLIED, ApplicationStatus.INTERVIEWING) is True

    def test_screening_to_interviewing(self):
        assert is_valid_transition(ApplicationStatus.SCREENING, ApplicationStatus.INTERVIEWING) is True

    def test_interviewing_to_offer(self):
        assert is_valid_transition(ApplicationStatus.INTERVIEWING, ApplicationStatus.OFFER) is True

    def test_any_to_rejected(self):
        assert is_valid_transition(ApplicationStatus.APPLIED, ApplicationStatus.REJECTED) is True
        assert is_valid_transition(ApplicationStatus.SCREENING, ApplicationStatus.REJECTED) is True
        assert is_valid_transition(ApplicationStatus.INTERVIEWING, ApplicationStatus.REJECTED) is True

    def test_any_active_to_withdrawn(self):
        assert is_valid_transition(ApplicationStatus.WISHLIST, ApplicationStatus.WITHDRAWN) is True
        assert is_valid_transition(ApplicationStatus.APPLIED, ApplicationStatus.WITHDRAWN) is True
        assert is_valid_transition(ApplicationStatus.SCREENING, ApplicationStatus.WITHDRAWN) is True
        assert is_valid_transition(ApplicationStatus.INTERVIEWING, ApplicationStatus.WITHDRAWN) is True
        assert is_valid_transition(ApplicationStatus.OFFER, ApplicationStatus.WITHDRAWN) is True


class TestInvalidTransitions:
    def test_rejected_is_terminal(self):
        assert is_valid_transition(ApplicationStatus.REJECTED, ApplicationStatus.APPLIED) is False
        assert is_valid_transition(ApplicationStatus.REJECTED, ApplicationStatus.OFFER) is False

    def test_withdrawn_is_terminal(self):
        assert is_valid_transition(ApplicationStatus.WITHDRAWN, ApplicationStatus.APPLIED) is False

    def test_cannot_skip_backwards(self):
        assert is_valid_transition(ApplicationStatus.SCREENING, ApplicationStatus.APPLIED) is False
        assert is_valid_transition(ApplicationStatus.INTERVIEWING, ApplicationStatus.APPLIED) is False
        assert is_valid_transition(ApplicationStatus.OFFER, ApplicationStatus.INTERVIEWING) is False

    def test_rejected_to_offer_forbidden(self):
        assert is_valid_transition(ApplicationStatus.REJECTED, ApplicationStatus.OFFER) is False


class TestAllowedTransitions:
    def test_applied_shows_valid_next_steps(self):
        allowed = get_allowed_transitions(ApplicationStatus.APPLIED)
        assert "screening" in allowed
        assert "interviewing" in allowed
        assert "rejected" in allowed
        assert "withdrawn" in allowed
        assert "offer" not in allowed

    def test_rejected_has_no_transitions(self):
        assert get_allowed_transitions(ApplicationStatus.REJECTED) == []

    def test_offer_can_only_withdraw(self):
        assert get_allowed_transitions(ApplicationStatus.OFFER) == ["withdrawn"]