"""Shared SPADE agent utilities for the local Prosody demo setup."""

from __future__ import annotations

from spade.agent import Agent as SpadeAgent
from spade.presence import PresenceManager
from spade.xmpp_client import XMPPClient


class LocalXMPPClient(XMPPClient):
    """SPADE XMPP client configured for localhost demo authentication."""

    def __init__(self, jid, password, verify_security, auto_register):
        super().__init__(jid, password, verify_security, auto_register)
        self["feature_mechanisms"].unencrypted_plain = True
        self["feature_mechanisms"].unencrypted_scram = True
        self["feature_mechanisms"].unencrypted_digest = True


class LocalAgent(SpadeAgent):
    """SPADE agent that uses the relaxed localhost XMPP client."""

    async def _async_start(self, auto_register: bool = True) -> None:
        await self._hook_plugin_before_connection()

        self.client = LocalXMPPClient(
            self.jid, self.password, self.verify_security, auto_register
        )
        self.presence = PresenceManager(agent=self, approve_all=False)

        await self._async_connect()
        await self._hook_plugin_after_connection()

        await self.setup()
        self._alive.set()
        for behaviour in self.behaviours:
            if not behaviour.is_running:
                behaviour.set_agent(self)
                behaviour.start()

