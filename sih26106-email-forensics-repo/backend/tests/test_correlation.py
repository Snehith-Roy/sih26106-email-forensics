"""
Unit tests for Phase 6b — correlation.py
Owner: Member 4

Tests campaign graph construction and connected-component clustering
with synthetic email dicts (no external deps).
"""

import pytest
from app.scoring.correlation import build_campaign_graph, get_campaigns


def _email(email_id, origin_ip=None, sender_domain=None, reply_to=None):
    return {
        "email_id": email_id,
        "origin_ip": origin_ip,
        "sender_domain": sender_domain,
        "reply_to": reply_to,
    }


# ---------------------------------------------------------------------------
# Graph building
# ---------------------------------------------------------------------------

class TestBuildCampaignGraph:
    def test_single_email_no_edges(self):
        emails = [_email("e1", origin_ip="1.2.3.4")]
        G = build_campaign_graph(emails)
        assert G.number_of_nodes() == 1
        assert G.number_of_edges() == 0

    def test_shared_ip_creates_edge(self):
        emails = [
            _email("e1", origin_ip="1.2.3.4"),
            _email("e2", origin_ip="1.2.3.4"),
        ]
        G = build_campaign_graph(emails)
        assert G.number_of_edges() == 1
        assert G.has_edge("e1", "e2")

    def test_shared_domain_creates_edge(self):
        emails = [
            _email("e1", sender_domain="evil.com"),
            _email("e2", sender_domain="evil.com"),
        ]
        G = build_campaign_graph(emails)
        assert G.has_edge("e1", "e2")

    def test_shared_reply_to_creates_edge(self):
        emails = [
            _email("e1", reply_to="attacker@evil.com"),
            _email("e2", reply_to="attacker@evil.com"),
        ]
        G = build_campaign_graph(emails)
        assert G.has_edge("e1", "e2")

    def test_nothing_shared_no_edges(self):
        emails = [
            _email("e1", origin_ip="1.1.1.1", sender_domain="a.com", reply_to="x@a.com"),
            _email("e2", origin_ip="2.2.2.2", sender_domain="b.com", reply_to="y@b.com"),
        ]
        G = build_campaign_graph(emails)
        assert G.number_of_edges() == 0

    def test_multiple_shared_signals_still_one_edge(self):
        """Two emails sharing IP + domain + reply-to should still be one edge."""
        emails = [
            _email("e1", origin_ip="1.2.3.4", sender_domain="evil.com", reply_to="a@evil.com"),
            _email("e2", origin_ip="1.2.3.4", sender_domain="evil.com", reply_to="a@evil.com"),
        ]
        G = build_campaign_graph(emails)
        assert G.number_of_edges() == 1  # simple graph, no multi-edges

    def test_chain_of_shared_ips(self):
        """e1-e2 share IP, e2-e3 share domain → 2 edges, 1 connected component."""
        emails = [
            _email("e1", origin_ip="1.2.3.4"),
            _email("e2", origin_ip="1.2.3.4", sender_domain="evil.com"),
            _email("e3", sender_domain="evil.com"),
        ]
        G = build_campaign_graph(emails)
        assert G.number_of_nodes() == 3
        assert G.number_of_edges() == 2

    def test_none_values_ignored(self):
        """None values for origin_ip/domain/reply_to should be silently skipped."""
        emails = [
            _email("e1", origin_ip=None, sender_domain=None, reply_to=None),
            _email("e2", origin_ip=None, sender_domain=None, reply_to=None),
        ]
        G = build_campaign_graph(emails)
        assert G.number_of_edges() == 0

    def test_empty_input(self):
        G = build_campaign_graph([])
        assert G.number_of_nodes() == 0
        assert G.number_of_edges() == 0

    def test_node_attributes_preserved(self):
        emails = [_email("e1", origin_ip="1.2.3.4", sender_domain="a.com")]
        G = build_campaign_graph(emails)
        assert G.nodes["e1"]["origin_ip"] == "1.2.3.4"
        assert G.nodes["e1"]["sender_domain"] == "a.com"


# ---------------------------------------------------------------------------
# Campaign clustering
# ---------------------------------------------------------------------------

class TestGetCampaigns:
    def test_no_emails(self):
        G = build_campaign_graph([])
        assert get_campaigns(G) == []

    def test_single_email_no_campaign(self):
        G = build_campaign_graph([_email("e1", origin_ip="1.2.3.4")])
        assert get_campaigns(G) == []

    def test_two_emails_same_ip_one_campaign(self):
        emails = [
            _email("e1", origin_ip="1.2.3.4"),
            _email("e2", origin_ip="1.2.3.4"),
        ]
        G = build_campaign_graph(emails)
        campaigns = get_campaigns(G)
        assert len(campaigns) == 1
        assert set(campaigns[0]) == {"e1", "e2"}

    def test_two_separate_campaigns(self):
        emails = [
            _email("e1", origin_ip="1.1.1.1"),
            _email("e2", origin_ip="1.1.1.1"),
            _email("e3", origin_ip="2.2.2.2"),
            _email("e4", origin_ip="2.2.2.2"),
        ]
        G = build_campaign_graph(emails)
        campaigns = get_campaigns(G)
        assert len(campaigns) == 2

    def test_three_email_chain_single_campaign(self):
        """e1→e2 share IP, e2→e3 share domain → all in one campaign."""
        emails = [
            _email("e1", origin_ip="1.2.3.4"),
            _email("e2", origin_ip="1.2.3.4", sender_domain="evil.com"),
            _email("e3", sender_domain="evil.com"),
        ]
        G = build_campaign_graph(emails)
        campaigns = get_campaigns(G)
        assert len(campaigns) == 1
        assert set(campaigns[0]) == {"e1", "e2", "e3"}

    def test_mixed_connected_and_isolated(self):
        """One campaign of 2, plus one isolated email → only one campaign returned."""
        emails = [
            _email("e1", origin_ip="1.2.3.4"),
            _email("e2", origin_ip="1.2.3.4"),
            _email("e3", origin_ip="9.9.9.9", sender_domain="solo.com"),
        ]
        G = build_campaign_graph(emails)
        campaigns = get_campaigns(G)
        assert len(campaigns) == 1
        assert set(campaigns[0]) == {"e1", "e2"}
