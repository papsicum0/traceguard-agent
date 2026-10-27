import datetime
import modal._object
import modal.object
import modal.types
import modal_proto.api_pb2
import typing
import typing_extensions

def _metrics_request(
    since: typing.Optional[datetime.datetime],
    until: typing.Optional[datetime.datetime],
    bucket_size: typing.Optional[datetime.timedelta],
    groups: typing.Optional[list[str]],
) -> modal_proto.api_pb2.FunctionGetMetricsRequest: ...
def _object_metrics(
    object_id: str,
    response: typing.Union[
        modal_proto.api_pb2.FunctionGetMetricsResponse, modal_proto.api_pb2.ServerGetMetricsResponse
    ],
) -> modal.types.ObjectMetrics: ...

class _MetricsManager:
    """mdmd:namespace"""
    def __init__(self, function: modal._object._Object, *, is_server: bool):
        """mdmd:hidden"""
        ...

    async def schema(self, groups: typing.Optional[list[str]] = None) -> dict[str, modal.types.MetricsSchema]:
        """Return metric definitions keyed by group name without fetching samples.

        Omit `groups` to list all groups. Each group contains its exact individual
        series definitions.
        """
        ...

    async def _schema(
        self,
        *,
        since: typing.Optional[datetime.datetime] = None,
        until: typing.Optional[datetime.datetime] = None,
        bucket_size: typing.Optional[datetime.timedelta] = None,
        groups: typing.Optional[list[str]] = None,
    ) -> modal_proto.api_pb2.MetricsGetInfoResponse:
        """Fetch schema rows and resolved bucket metadata for a preview window."""
        ...

    async def _export(
        self,
        since: typing.Optional[datetime.datetime],
        until: typing.Optional[datetime.datetime],
        bucket_size: typing.Optional[datetime.timedelta],
        groups: typing.Optional[list[str]],
        all_variants: bool = False,
    ) -> modal.types.ObjectMetrics: ...

class _FunctionMetricsManager(_MetricsManager):
    """mdmd:namespace"""
    def __init__(self, function: modal._object._Object):
        """mdmd:hidden"""
        ...

    async def export(
        self,
        *,
        since: typing.Optional[datetime.datetime] = None,
        until: typing.Optional[datetime.datetime] = None,
        bucket_size: typing.Optional[datetime.timedelta] = None,
        groups: typing.Optional[list[str]] = None,
        all_variants: bool = False,
    ) -> modal.types.ObjectMetrics:
        """Fetch metric samples for a Function.

        Defaults to all groups over the last hour. `since` defaults to one hour
        before `until`; naive datetimes use local time. The maximum range is 31
        days, with at most 500 points per series. If `bucket_size` is omitted,
        Modal selects a supported width targeting approximately 100 buckets.
        Bounds round down to UTC bucket boundaries, so data before `since` may
        be included and the partial bucket at `until` is excluded.

        Set `all_variants=True` to include the root Function and its variants.
        Missing observations have value None. Use `schema()` to discover
        group names and series definitions without fetching samples.

        ```python notest
        metrics = function.metrics.export(bucket_size=timedelta(minutes=5), groups=["calls"])
        for point in metrics["successful_calls_count"].points:
            print(point.time, point.value)
        ```
        """
        ...

class _ServerMetricsManager(_MetricsManager):
    """mdmd:namespace"""
    def __init__(self, function: modal._object._Object):
        """mdmd:hidden"""
        ...

    async def export(
        self,
        *,
        since: typing.Optional[datetime.datetime] = None,
        until: typing.Optional[datetime.datetime] = None,
        bucket_size: typing.Optional[datetime.timedelta] = None,
        groups: typing.Optional[list[str]] = None,
    ) -> modal.types.ObjectMetrics:
        """Fetch metric samples for a Server.

        Defaults to all groups over the last hour. `since` defaults to one hour
        before `until`; naive datetimes use local time. The maximum range is 31
        days, with at most 500 points per series. Omit `bucket_size` for automatic
        sizing. Bounds round down to UTC bucket boundaries; the partial bucket
        at `until` is excluded. Missing observations have value None.

        Use `schema()` to discover groups and series without fetching samples.
        """
        ...

class MetricsManager:
    """mdmd:namespace"""
    def __init__(self, function: modal.object.Object, *, is_server: bool):
        """mdmd:hidden"""
        ...

    class __schema_spec(typing_extensions.Protocol):
        def __call__(self, /, groups: typing.Optional[list[str]] = None) -> dict[str, modal.types.MetricsSchema]:
            """Return metric definitions keyed by group name without fetching samples.

            Omit `groups` to list all groups. Each group contains its exact individual
            series definitions.
            """
            ...

        async def aio(self, /, groups: typing.Optional[list[str]] = None) -> dict[str, modal.types.MetricsSchema]:
            """Return metric definitions keyed by group name without fetching samples.

            Omit `groups` to list all groups. Each group contains its exact individual
            series definitions.
            """
            ...

    schema: __schema_spec

    class ___schema_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *,
            since: typing.Optional[datetime.datetime] = None,
            until: typing.Optional[datetime.datetime] = None,
            bucket_size: typing.Optional[datetime.timedelta] = None,
            groups: typing.Optional[list[str]] = None,
        ) -> modal_proto.api_pb2.MetricsGetInfoResponse:
            """Fetch schema rows and resolved bucket metadata for a preview window."""
            ...

        async def aio(
            self,
            /,
            *,
            since: typing.Optional[datetime.datetime] = None,
            until: typing.Optional[datetime.datetime] = None,
            bucket_size: typing.Optional[datetime.timedelta] = None,
            groups: typing.Optional[list[str]] = None,
        ) -> modal_proto.api_pb2.MetricsGetInfoResponse:
            """Fetch schema rows and resolved bucket metadata for a preview window."""
            ...

    _schema: ___schema_spec

    class ___export_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            since: typing.Optional[datetime.datetime],
            until: typing.Optional[datetime.datetime],
            bucket_size: typing.Optional[datetime.timedelta],
            groups: typing.Optional[list[str]],
            all_variants: bool = False,
        ) -> modal.types.ObjectMetrics: ...
        async def aio(
            self,
            /,
            since: typing.Optional[datetime.datetime],
            until: typing.Optional[datetime.datetime],
            bucket_size: typing.Optional[datetime.timedelta],
            groups: typing.Optional[list[str]],
            all_variants: bool = False,
        ) -> modal.types.ObjectMetrics: ...

    _export: ___export_spec

class FunctionMetricsManager(MetricsManager):
    """mdmd:namespace"""
    def __init__(self, function: modal.object.Object):
        """mdmd:hidden"""
        ...

    class __export_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *,
            since: typing.Optional[datetime.datetime] = None,
            until: typing.Optional[datetime.datetime] = None,
            bucket_size: typing.Optional[datetime.timedelta] = None,
            groups: typing.Optional[list[str]] = None,
            all_variants: bool = False,
        ) -> modal.types.ObjectMetrics:
            """Fetch metric samples for a Function.

            Defaults to all groups over the last hour. `since` defaults to one hour
            before `until`; naive datetimes use local time. The maximum range is 31
            days, with at most 500 points per series. If `bucket_size` is omitted,
            Modal selects a supported width targeting approximately 100 buckets.
            Bounds round down to UTC bucket boundaries, so data before `since` may
            be included and the partial bucket at `until` is excluded.

            Set `all_variants=True` to include the root Function and its variants.
            Missing observations have value None. Use `schema()` to discover
            group names and series definitions without fetching samples.

            ```python notest
            metrics = function.metrics.export(bucket_size=timedelta(minutes=5), groups=["calls"])
            for point in metrics["successful_calls_count"].points:
                print(point.time, point.value)
            ```
            """
            ...

        async def aio(
            self,
            /,
            *,
            since: typing.Optional[datetime.datetime] = None,
            until: typing.Optional[datetime.datetime] = None,
            bucket_size: typing.Optional[datetime.timedelta] = None,
            groups: typing.Optional[list[str]] = None,
            all_variants: bool = False,
        ) -> modal.types.ObjectMetrics:
            """Fetch metric samples for a Function.

            Defaults to all groups over the last hour. `since` defaults to one hour
            before `until`; naive datetimes use local time. The maximum range is 31
            days, with at most 500 points per series. If `bucket_size` is omitted,
            Modal selects a supported width targeting approximately 100 buckets.
            Bounds round down to UTC bucket boundaries, so data before `since` may
            be included and the partial bucket at `until` is excluded.

            Set `all_variants=True` to include the root Function and its variants.
            Missing observations have value None. Use `schema()` to discover
            group names and series definitions without fetching samples.

            ```python notest
            metrics = function.metrics.export(bucket_size=timedelta(minutes=5), groups=["calls"])
            for point in metrics["successful_calls_count"].points:
                print(point.time, point.value)
            ```
            """
            ...

    export: __export_spec

class ServerMetricsManager(MetricsManager):
    """mdmd:namespace"""
    def __init__(self, function: modal.object.Object):
        """mdmd:hidden"""
        ...

    class __export_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *,
            since: typing.Optional[datetime.datetime] = None,
            until: typing.Optional[datetime.datetime] = None,
            bucket_size: typing.Optional[datetime.timedelta] = None,
            groups: typing.Optional[list[str]] = None,
        ) -> modal.types.ObjectMetrics:
            """Fetch metric samples for a Server.

            Defaults to all groups over the last hour. `since` defaults to one hour
            before `until`; naive datetimes use local time. The maximum range is 31
            days, with at most 500 points per series. Omit `bucket_size` for automatic
            sizing. Bounds round down to UTC bucket boundaries; the partial bucket
            at `until` is excluded. Missing observations have value None.

            Use `schema()` to discover groups and series without fetching samples.
            """
            ...

        async def aio(
            self,
            /,
            *,
            since: typing.Optional[datetime.datetime] = None,
            until: typing.Optional[datetime.datetime] = None,
            bucket_size: typing.Optional[datetime.timedelta] = None,
            groups: typing.Optional[list[str]] = None,
        ) -> modal.types.ObjectMetrics:
            """Fetch metric samples for a Server.

            Defaults to all groups over the last hour. `since` defaults to one hour
            before `until`; naive datetimes use local time. The maximum range is 31
            days, with at most 500 points per series. Omit `bucket_size` for automatic
            sizing. Bounds round down to UTC bucket boundaries; the partial bucket
            at `until` is excluded. Missing observations have value None.

            Use `schema()` to discover groups and series without fetching samples.
            """
            ...

    export: __export_spec
