import modal.secret
import modal_proto.api_pb2
import typing

def _header_value_has_invalid_chars(value: str) -> bool: ...
def _template_references_key(template: str) -> bool:
    """Whether a header value template references a `$KEY`."""
    ...

class _HeaderReplacement:
    """_HeaderReplacement(domain: 'str', headers: 'dict[str, str]', secret: '_Secret | None')"""

    domain: str
    headers: dict[str, str]
    secret: typing.Optional[modal.secret._Secret]

    def __init__(self, domain: str, headers: dict[str, str], secret: typing.Optional[modal.secret._Secret]) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
        ...

    def __repr__(self):
        """Return repr(self)."""
        ...

    def __eq__(self, other):
        """Return self==value."""
        ...

    def __setattr__(self, name, value):
        """Implement setattr(self, name, value)."""
        ...

    def __delattr__(self, name):
        """Implement delattr(self, name)."""
        ...

    def __hash__(self):
        """Return hash(self)."""
        ...

class _OutboundPolicy:
    """Immutable configuration for replacing headers in outbound HTTPS requests
    from a Sandbox.

    This API is experimental and may change in the future.

    Header values support templating with keys in a replacement's secret: a
    `$`-prefixed key name in the secret is replaced with the secret value.
    Literal `$` characters are written `$$`.

    Secret values never enter the Sandbox: they are resolved and injected into
    matching requests outside the container.

    Examples:
        ```python
        import modal
        import modal.experimental

        secret = modal.Secret.from_name("api-token")

        outbound_policy = (
            modal.experimental.OutboundPolicy()
            # Inject a secret-backed Authorization header.
            .with_header_replacement(
                domain="example.com",
                secret=secret,
                headers={"Authorization": "Bearer $API_TOKEN"},
            )
            # Inject a static header into requests to another domain.
            .with_header_replacement(
                domain="modal.com",
                headers={"X-Trace-Token": "trace_abcd"},
            )
        )

        sb = modal.Sandbox.create(_experimental_outbound_policy=outbound_policy)
        ```
    """

    _replacements: tuple[_HeaderReplacement, ...]

    def __init__(self, _replacements: tuple[_HeaderReplacement, ...] = ()):
        """Initialize self.  See help(type(self)) for accurate signature."""
        ...

    def with_header_replacement(
        self, *, domain: str, headers: typing.Mapping[str, str], secret: typing.Optional[modal.secret._Secret] = None
    ) -> _OutboundPolicy:
        """Return a new `OutboundPolicy` with an added header replacement.

        Args:
            domain: Domain the replacements are scoped to. Supports `*.` wildcard
                prefixes (matching the apex domain and subdomains) and a bare `"*"`.
            headers: Header name -> header value. Values support `$KEY` templates
                referencing keys in the replacement's `secret`.
            secret: Named Secret (e.g. from `Secret.from_name`) whose keys may be
                referenced in the header value templates. Static replacements pass no
                secret.
        """
        ...

    def _validate(self) -> None:
        """Check all replacements, raising `InvalidError` on the first violation found."""
        ...

    def _secrets(self) -> list[modal.secret._Secret]:
        """Deduplicated list of secrets referenced by the policy's replacements."""
        ...

    def _to_proto(self) -> modal_proto.api_pb2.ExperimentalOutboundPolicy:
        """Convert to the wire format. Referenced secrets must be hydrated first."""
        ...

def _validate_compatible_network_access(
    outbound_policy: typing.Optional[_OutboundPolicy],
    block_network: bool,
    outbound_domain_allowlist: typing.Optional[typing.Sequence[str]],
) -> None:
    """Reject combinations of network configuration and outbound policy that the server does not support."""
    ...

class OutboundPolicy:
    """Immutable configuration for replacing headers in outbound HTTPS requests
    from a Sandbox.

    This API is experimental and may change in the future.

    Header values support templating with keys in a replacement's secret: a
    `$`-prefixed key name in the secret is replaced with the secret value.
    Literal `$` characters are written `$$`.

    Secret values never enter the Sandbox: they are resolved and injected into
    matching requests outside the container.

    Examples:
        ```python
        import modal
        import modal.experimental

        secret = modal.Secret.from_name("api-token")

        outbound_policy = (
            modal.experimental.OutboundPolicy()
            # Inject a secret-backed Authorization header.
            .with_header_replacement(
                domain="example.com",
                secret=secret,
                headers={"Authorization": "Bearer $API_TOKEN"},
            )
            # Inject a static header into requests to another domain.
            .with_header_replacement(
                domain="modal.com",
                headers={"X-Trace-Token": "trace_abcd"},
            )
        )

        sb = modal.Sandbox.create(_experimental_outbound_policy=outbound_policy)
        ```
    """

    _replacements: tuple[_HeaderReplacement, ...]

    def __init__(self, _replacements: tuple[_HeaderReplacement, ...] = ()): ...
    def with_header_replacement(
        self, *, domain: str, headers: typing.Mapping[str, str], secret: typing.Optional[modal.secret.Secret] = None
    ) -> OutboundPolicy:
        """Return a new `OutboundPolicy` with an added header replacement.

        Args:
            domain: Domain the replacements are scoped to. Supports `*.` wildcard
                prefixes (matching the apex domain and subdomains) and a bare `"*"`.
            headers: Header name -> header value. Values support `$KEY` templates
                referencing keys in the replacement's `secret`.
            secret: Named Secret (e.g. from `Secret.from_name`) whose keys may be
                referenced in the header value templates. Static replacements pass no
                secret.
        """
        ...

    def _validate(self) -> None:
        """Check all replacements, raising `InvalidError` on the first violation found."""
        ...

    def _secrets(self) -> list[modal.secret.Secret]:
        """Deduplicated list of secrets referenced by the policy's replacements."""
        ...

    def _to_proto(self) -> modal_proto.api_pb2.ExperimentalOutboundPolicy:
        """Convert to the wire format. Referenced secrets must be hydrated first."""
        ...
