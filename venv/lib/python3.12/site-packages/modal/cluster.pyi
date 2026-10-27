import google.protobuf.message
import modal.client
import modal.object
import modal_proto.api_pb2
import typing
import typing_extensions

class Cluster(modal.object.Object):
    """A group of containers scheduled together for a clustered Function or Server.

    Use `Cluster.from_context()` inside a cluster, or `Cluster.from_id()` to
    inspect a cluster remotely. Containers are ordered by cluster rank.
    """

    _metadata: typing.Optional[modal_proto.api_pb2.ClusterStats]

    def __init__(self, *args, **kwargs):
        """mdmd:hidden"""
        ...

    def _hydrate_metadata(self, metadata: typing.Optional[google.protobuf.message.Message]): ...
    def _get_metadata(self) -> modal_proto.api_pb2.ClusterStats: ...
    @staticmethod
    def from_context() -> Cluster:
        """Reference a Cluster from within one of its containers.

        Raises `InvalidError` outside an initialized clustered execution.
        """
        ...

    @staticmethod
    def from_id(cluster_id: str, *, client: typing.Optional[modal.client.Client] = None) -> Cluster:
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

    class __container_ids_spec(typing_extensions.Protocol):
        def __call__(self, /) -> list[str]:
            """Return container IDs ordered by cluster rank."""
            ...

        async def aio(self, /) -> list[str]:
            """Return container IDs ordered by cluster rank."""
            ...

    container_ids: __container_ids_spec

    class __container_ips_spec(typing_extensions.Protocol):
        def __call__(self, /, family: typing.Literal["ipv4", "ipv6"] = "ipv6") -> list[str]:
            """Return container IP addresses ordered by cluster rank.

            Returns IPv6 addresses by default; pass `family="ipv4"` for IPv4.
            These addresses are for intra-cluster communication.

            Must be called from a container in this cluster; otherwise raises `InvalidError`.
            """
            ...

        async def aio(self, /, family: typing.Literal["ipv4", "ipv6"] = "ipv6") -> list[str]:
            """Return container IP addresses ordered by cluster rank.

            Returns IPv6 addresses by default; pass `family="ipv4"` for IPv4.
            These addresses are for intra-cluster communication.

            Must be called from a container in this cluster; otherwise raises `InvalidError`.
            """
            ...

    container_ips: __container_ips_spec

    class __container_rank_spec(typing_extensions.Protocol):
        def __call__(self, /, container_id: typing.Optional[str] = None) -> int:
            """Return a container's rank within this cluster.

            With no argument, return the executing container's rank without a network
            request. Raises `InvalidError` if it is not a member of this cluster.

            With an explicit container ID, look up its rank in the cluster's membership.
            Raises `InvalidError` for nonmembers.
            """
            ...

        async def aio(self, /, container_id: typing.Optional[str] = None) -> int:
            """Return a container's rank within this cluster.

            With no argument, return the executing container's rank without a network
            request. Raises `InvalidError` if it is not a member of this cluster.

            With an explicit container ID, look up its rank in the cluster's membership.
            Raises `InvalidError` for nonmembers.
            """
            ...

    container_rank: __container_rank_spec
