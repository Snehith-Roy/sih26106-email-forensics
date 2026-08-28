"""
Phase 6b — Campaign correlation (shared IP / domain / reply-to -> graph)
Owner: Member 4
"""
import networkx as nx


def build_campaign_graph(analyzed_emails: list[dict]) -> nx.Graph:
    """analyzed_emails: list of dicts each with keys
    'email_id', 'origin_ip', 'sender_domain', 'reply_to'."""
    G = nx.Graph()
    for e in analyzed_emails:
        G.add_node(e["email_id"], **e)

    by_ip, by_domain, by_reply_to = {}, {}, {}
    for e in analyzed_emails:
        by_ip.setdefault(e.get("origin_ip"), []).append(e["email_id"])
        by_domain.setdefault(e.get("sender_domain"), []).append(e["email_id"])
        by_reply_to.setdefault(e.get("reply_to"), []).append(e["email_id"])

    for grouping in (by_ip, by_domain, by_reply_to):
        for key, ids in grouping.items():
            if key and len(ids) > 1:
                for i in range(len(ids) - 1):
                    G.add_edge(ids[i], ids[i + 1], shared=key)
    return G


def get_campaigns(G: nx.Graph) -> list[list[str]]:
    """Each connected component with >1 email = a likely campaign."""
    return [list(c) for c in nx.connected_components(G) if len(c) > 1]
