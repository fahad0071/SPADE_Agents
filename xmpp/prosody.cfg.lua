pidfile = "prosody.pid"

admins = { "orchestrator@localhost" }

modules_enabled = {
    "roster";
    "saslauth";
    "disco";
    "private";
    "blocklist";
    "vcard4";
    "vcard_legacy";
    "version";
    "uptime";
    "time";
    "ping";
    "pep";
    "register";
    "admin_adhoc";
}

allow_registration = false
authentication = "internal_hashed"

storage = "internal"
data_path = "xmpp/data"

log = {
    info = "xmpp/logs/prosody.log";
    error = "xmpp/logs/prosody.err";
}

c2s_interfaces = { "127.0.0.1", "::1" }
c2s_ports = { 5222 }
s2s_interfaces = {}
s2s_ports = {}

c2s_require_encryption = false
s2s_require_encryption = false
allow_unencrypted_plain_auth = true

VirtualHost "localhost"
    enabled = true
