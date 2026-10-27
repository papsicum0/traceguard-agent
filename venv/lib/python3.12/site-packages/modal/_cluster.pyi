import google.protobuf.message
import modal._object
import modal.client
import modal_proto.api_pb2
import types
import typing
import typing_extensions

class ClusterContext:
    """Cluster metadata and the executing container's rank, initialized at startup."""

    rank: int
    cluster_id: str
    container_ips: list[str]
    container_ipv4_ips: list[str]
    fabric_ids: list[str]

    def __init__(
        self, rank: int, cluster_id: str, container_ips: list[str], container_ipv4_ips: list[str], fabric_ids: list[str]
    ) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
        ...

    def __repr__(self):
        """Return repr(self)."""
        ...

    def __eq__(self, other):
        """Return self==value."""
        ...

def get_current_cluster_context() -> ClusterContext:
    """Return the executing container's initialized cluster context without an RPC."""
    ...

class _Cluster(modal._object._Object):
    """A group of containers scheduled together for a clustered Function or Server.

    Use `Cluster.from_context()` inside a cluster, or `Cluster.from_id()` to
    inspect a cluster remotely. Containers are ordered by cluster rank.
    """

    _metadata: typing.Optional[modal_proto.api_pb2.ClusterStats]

    def _hydrate_metadata(self, metadata: typing.Optional[google.protobuf.message.Message]): ...
    def _get_metadata(self) -> modal_proto.api_pb2.ClusterStats: ...
    @staticmethod
    def from_context() -> _Cluster:
        """Reference a Cluster from within one of its containers.

        Raises `InvalidError` outside an initialized clustered execution.
        """
        ...

    @staticmethod
    def from_id(cluster_id: str, *, client: typing.Optional[modal.client._Client] = None) -> _Cluster:
        """Reference a Cluster by its ID.

        Args:
            cluster_id: ID of the cluster.
            client: Modal client to use; defaults to `Client.from_env()` when omitted.

        Examples:
            ```python notest
            cluster = modal.Cluster.from_id("cu-123")
            ```
        """
        ...

    @property
    def object_id(self) -> str:
        """The cluster's unique `cu-` object ID."""
        ...

    async def container_ids(self) -> list[str]:
        """Return container IDs ordered by cluster rank."""
        ...

    async def container_ips(self, family: typing.Literal["ipv4", "ipv6"] = "ipv6") -> list[str]:
        """Return container IP addresses ordered by cluster rank.

        Returns IPv6 addresses by default; pass `family="ipv4"` for IPv4.
        These addresses are for intra-cluster communication.

        Must be called from a container in this cluster; otherwise raises `InvalidError`.
        """
        ...

    async def container_rank(self, container_id: typing.Optional[str] = None) -> int:
        """Return a container's rank within this cluster.

        With no argument, return the executing container's rank without a network
        request. Raises `InvalidError` if it is not a member of this cluster.

        With an explicit container ID, look up its rank in the cluster's membership.
        Raises `InvalidError` for nonmembers.
        """
        ...

async def _initialize_clustered_function(client: modal.client._Client, task_id: str): ...

class __initialize_clustered_function_spec(typing_extensions.Protocol):
    def __call__(self, /, client: modal.client.Client, task_id: str): ...
    async def aio(self, /, client: modal.client.Client, task_id: str): ...

initialize_clustered_function: __initialize_clustered_function_spec

current_cluster_context: ClusterContext | None
