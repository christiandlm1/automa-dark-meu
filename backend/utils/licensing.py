"""
AUTOMA Utils - Licensing Stubs.

Architectural shell and interfaces for licensing, activations, and machine IDs.
No operations, authentications, or payments are executed in this module.
"""

import uuid
import hashlib
import platform


class MachineID:
    """Calculates and represents hardware fingerprint hashes (Machine ID)."""

    @classmethod
    def get_hardware_uuid(cls) -> str:
        """Retrieve a stable hardware fingerprint identifier."""
        try:
            # Simple fallback using OS parameters and node
            node = platform.node()
            processor = platform.processor()
            system = platform.system()
            raw = f"{node}-{processor}-{system}"
            return hashlib.sha256(raw.encode("utf-8")).hexdigest()
        except Exception:
            return str(uuid.getnode())


class Licensing:
    """Interface to validate licenses."""

    def __init__(self, license_key: str | None = None) -> None:
        self.license_key = license_key

    def is_valid(self) -> bool:
        """Return license status (mocked to always True)."""
        return True

    def get_type(self) -> str:
        """Return tier type."""
        return "PRO"


class Subscription:
    """Mock structure representing active subscriptions."""

    def __init__(self, plan_name: str = "Enterprise") -> None:
        self.plan_name = plan_name
        self.is_active = True
        self.expires_at = "2099-12-31T23:59:59Z"


class Activation:
    """Registers activation keys locally."""

    def __init__(self, product_key: str) -> None:
        self.product_key = product_key

    def activate(self) -> bool:
        """Simulate activation key validation."""
        return True
