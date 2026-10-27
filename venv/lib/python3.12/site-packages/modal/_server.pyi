import datetime
import modal._functions
import modal._logs_manager
import modal._metrics
import modal._partial_function
import modal._supports_logs
import modal.app
import modal.client
import modal.server
import modal.types
import modal_proto.api_pb2
import typing
import typing_extensions

def validate_http_server_config(
    port: int,
    proxy_regions: list[str],
    startup_timeout: int,
    exit_grace_period: typing.Optional[int],
    is_server: bool = False,
): ...

class _Server:
    """Server runs an HTTP server started in an `@modal.enter` method.

    See the [guide](https://modal.com/docs/guide/servers) for more information.

    Generally, you will not construct a Server directly.
    Instead, use the [`@app.server()`](https://modal.com/docs/sdk/py/latest/App#server) decorator.

    ```python notest
    @app.server(port=8080, routing_region="us-east")
    class MyServer:
        @modal.enter()
        def start_server(self):
            self.process = subprocess.Popen(["python3", "-m", "http.server", "8080"])
    ```
    """

    _user_cls: typing.Optional[type]
    _service_function: modal._functions._Function
    _app: typing.Optional[modal.app._App]
    _is_sessioned: typing.Optional[bool]

    def _get_user_cls(self) -> type: ...
    def _get_app(self) -> modal.app._App: ...
    def _get_service_function(self) -> modal._functions._Function: ...
    @property
    def object_id(self) -> str:
        """Modal's internal ID for this Server instance."""
        ...

    async def _get_log_query_data(self) -> modal._supports_logs._LogQueryData: ...
    @property
    def metrics(self) -> modal._metrics._ServerMetricsManager:
        """Access metric samples with `export()` and series definitions with `schema()`."""
        ...

    @property
    def logs(self) -> modal._logs_manager._ServerLogsManager:
        """Access logs for a `Server`.

        Use [`fetch()`](#logsfetch)
        to read logs from a UTC time range, [`tail()`](#logstail)
        to read the most recent logs, and [`stream()`](#logsstream)
        to follow new logs as they arrive.

        See also:
            - [`modal app logs`](https://modal.com/docs/cli/latest/app#modal-app-logs):
            CLI access to logs for an App.
        """
        ...

    @property
    def sessions(self) -> _ServerSessionsManager:
        """Start and terminate sticky sessions on a Server decorated with `@modal.sessioned()`."""
        ...

    @property
    def autoscaler(self) -> _ServerAutoscalerManager:
        """View and update Autoscaler settings on a Server."""
        ...

    async def info(self, *, refresh: bool = False) -> modal.types.ServerInfo:
        """Get an overview of a Server's resource requests, associated mounts, http config, etc.

        This method performs a network request to populate this information if the Server handle is
        a remote lookup whose information has not yet been fetched (e.g. from `Server.from_name(...)`),
        or if `refresh=True`.

        Args:
            refresh: Always perform a network request. Pass `refresh=True` to ensure that this method
                returns the most up to date information.

        Returns:
            This returns a [`modal.types.ServerInfo`](https://modal.com/docs/sdk/py/latest/types#ServerInfo)
            dataclass.
        """
        ...

    @staticmethod
    def _extract_user_cls(wrapped_user_cls: typing.Union[type, modal._partial_function._PartialFunction]) -> type: ...
    async def get_url(self) -> typing.Optional[str]:
        """The URL for making requests to this Server."""
        ...

    async def _experimental_list_containers(self) -> list[modal.types.ServerContainerInfo]:
        """List the containers currently registered to serve requests for this Server.

        This interface is experimental and may change or be removed without warning.
        """
        ...

    async def update_autoscaler(
        self,
        *,
        target_concurrency: typing.Optional[float] = None,
        min_containers: typing.Optional[int] = None,
        max_containers: typing.Optional[int] = None,
        buffer_containers: typing.Optional[int] = None,
        scaleup_window: typing.Optional[int] = None,
        scaledown_window: typing.Optional[int] = None,
    ) -> modal.types.ServerAutoscalerSettings:
        """Override the current autoscaler behavior for this Server.

        Unspecified parameters will retain their current value, i.e. either the static value
        from the `@app.server()` decorator, or an override value from a previous call to this method.

        Subsequent deployments of the App containing this Server will reset the autoscaler back to
        its static configuration.

        Args:
            target_concurrency:
                Target number of concurrent requests per container. May be fractional, e.g. 1.5 to
                target three concurrent requests per two containers.
            min_containers: Minimum number of containers to keep running regardless of demand.
            max_containers: Limit on the number of containers that can be concurrently running.
            buffer_containers: Extra containers to scale up beyond current demand.
            scaleup_window: Seconds of sustained demand required before scaling up new containers.
            scaledown_window: Maximum duration (in seconds) idle containers wait before scaling down.

        Returns:
            A `ServerAutoscalerSettings` dataclass which contains the current autoscaler settings of
            this Server after the call.

        Examples:
            ```python notest
            server = modal.Server.from_name("my-app", "Server")

            # Always have at least 2 containers running, with an extra buffer of 2 containers
            server.update_autoscaler(min_containers=2, buffer_containers=1)

            # Limit this Server to avoid spinning up more than 5 containers
            server.update_autoscaler(max_containers=5)

            # Require 30 seconds of sustained demand before scaling up
            server.update_autoscaler(scaleup_window=30)

            # Adjust Server autoscaling to target 20 concurrent requests per replica
            server.update_autoscaler(target_concurrency=20)

            # Target three concurrent requests for every two containers
            server.update_autoscaler(target_concurrency=1.5)

            # Disable the Server autoscaling by setting target_concurrency to 0
            server.update_autoscaler(target_concurrency=0)
            ```
        """
        ...

    async def hydrate(self, client: typing.Optional[modal.client._Client] = None) -> _Server:
        """Synchronize the local object with its identity on the Modal server.

        It is rarely necessary to call this method explicitly, as most operations will
        lazily hydrate when needed. The main use case is when you need to access object
        metadata, such as its ID.
        """
        ...

    @classmethod
    def _new_from_function(
        cls, object_id: str, client: modal.client._Client, metadata: modal_proto.api_pb2.FunctionHandleMetadata
    ) -> typing_extensions.Self:
        """mdmd:hidden

        Callers which already have handle metadata for a Server service function can use this method to
        create a hydrated handle without having to do an unnecessary RPC.
        """
        ...

    @staticmethod
    def _from_local(
        wrapped_user_cls: typing.Union[type, modal._partial_function._PartialFunction],
        app: modal.app._App,
        service_function: modal._functions._Function,
        is_sessioned: bool = False,
    ) -> _Server:
        """Create a Server from a local class definition."""
        ...

    @classmethod
    def from_name(
        cls: type[_Server],
        app_name: str,
        name: str,
        *,
        environment_name: typing.Optional[str] = None,
        client: typing.Optional[modal.client._Client] = None,
    ) -> _Server:
        """Reference a Server from a deployed App by its name.

        This is a lazy method that defers hydrating the local
        object with metadata from Modal servers until the first
        time it is actually used.

        Args:
            app_name: Name of the App containing the Server.
            name: Name of the Server within the App.
            environment_name: Name of the Environment where the App is deployed.
            client: Modal client instance for this session.

        ```python notest
        server = modal.Server.from_name("other-app", "Server")
        ```
        """
        ...

    @classmethod
    def from_id(cls: type[_Server], server_id: str, *, client: typing.Optional[modal.client._Client] = None):
        """Reference a Server from a deployed or running App by its ID.

        This is a lazy method that defers hydrating the local
        object with metadata from Modal servers until the first
        time it is actually used.

        Args:
            server_id: The ID of the server.
            client: Modal client instance for this session.

        Examples:
            ```python notest
            server = modal.Server.from_id("fu-456")
            ```
        """
        ...

    def _is_local(self) -> bool:
        """Returns True if this Server has local source code available."""
        ...

    @staticmethod
    def _validate_wrapped_user_cls_decorators(
        wrapped_user_cls: typing.Union[type, modal._partial_function._PartialFunction], enable_memory_snapshot: bool
    ): ...
    @staticmethod
    def _validate_construction_mechanism(
        wrapped_user_cls: typing.Union[type, modal._partial_function._PartialFunction],
    ):
        """Validate that the server class doesn't have a custom constructor."""
        ...

    async def stats(
        self,
        *,
        since: typing.Optional[datetime.datetime] = None,
        until: typing.Optional[datetime.datetime] = None,
        container: typing.Optional[str] = None,
    ) -> modal.types.ServerStats:
        """Return statistics for a modal Server.

        The default time range is the most recent hour. The maximum time range is 7 days.

        Args:
            since: The beginning of the time range, inclusive. If omitted, this defaults to an hour before `until`.
               Values without a timezone are interpeted as local time.
            until: The end of the time range, exclusive. If omitted, this defaults to current time.
                Values without a timezone are interpeted as local time.
            container: If passed in, the stats are computed for only this container. Default None.

        Returns:
            A `ServerStats` object
        """
        ...

async def _post_session_control(url: str, headers: dict[str, str]) -> tuple[int, str, str]:
    """POST to a sticky session control endpoint, raising on 5xx."""
    ...

async def _post_session_start(
    base_url: str, fn: modal._functions._Function, idle_timeout: int
) -> tuple[int, str, str]: ...
async def _post_session_terminate(base_url: str, headers: dict[str, str]) -> tuple[int, str, str]: ...

class _ServerSessionsManager:
    """mdmd:namespace"""
    def __init__(self, server: _Server):
        """mdmd:hidden"""
        ...

    def _validate(self) -> None: ...
    async def start(self, idle_timeout: int = 600) -> modal.types.ServerSessionCredentials:
        """Start a sticky session and return its ID and token.

        Requests to the server URL that carry the returned token are routed to the same container until the
        session has had no connections for `idle_timeout` seconds or is terminated. A container won't be scaled down
        for as long as it holds a live session.

        If no container has room for the session, the call waits for additional capacity. It will block for
        up to 25 minutes before giving up. To control the wait per call, use the HTTP API and apply your own retry
        policy.

        Args:
            idle_timeout: Seconds without an in-flight request before the session ends.

        Examples:

            ```python notest
            server = modal.Server.from_name("my-app", "MyServer")
            server_url = server.get_url()
            session = server.sessions.start(idle_timeout=600)
            headers = {"Modal-Authorization": f"Bearer {session.token}"}

            requests.get(server_url, headers=headers).raise_for_status()

            server.sessions.terminate(session.token)
            ```
        """
        ...

    async def terminate(self, token: str) -> None:
        """Terminate a sticky session.

        New requests to it will be rejected. The container continues serving other sessions.

        Args:
            token: The `token` of the `ServerSessionCredentials` to terminate.

        Examples:

            ```python notest
            server = modal.Server.from_name("my-app", "MyServer")
            session = server.sessions.start()

            server.sessions.terminate(session.token)
            ```
        """
        ...

class ServerSessionsManager:
    """mdmd:namespace"""
    def __init__(self, server: modal.server.Server):
        """mdmd:hidden"""
        ...

    def _validate(self) -> None: ...

    class __start_spec(typing_extensions.Protocol):
        def __call__(self, /, idle_timeout: int = 600) -> modal.types.ServerSessionCredentials:
            """Start a sticky session and return its ID and token.

            Requests to the server URL that carry the returned token are routed to the same container until the
            session has had no connections for `idle_timeout` seconds or is terminated. A container won't be scaled down
            for as long as it holds a live session.

            If no container has room for the session, the call waits for additional capacity. It will block for
            up to 25 minutes before giving up. To control the wait per call, use the HTTP API and apply your own retry
            policy.

            Args:
                idle_timeout: Seconds without an in-flight request before the session ends.

            Examples:

                ```python notest
                server = modal.Server.from_name("my-app", "MyServer")
                server_url = server.get_url()
                session = server.sessions.start(idle_timeout=600)
                headers = {"Modal-Authorization": f"Bearer {session.token}"}

                requests.get(server_url, headers=headers).raise_for_status()

                server.sessions.terminate(session.token)
                ```
            """
            ...

        async def aio(self, /, idle_timeout: int = 600) -> modal.types.ServerSessionCredentials:
            """Start a sticky session and return its ID and token.

            Requests to the server URL that carry the returned token are routed to the same container until the
            session has had no connections for `idle_timeout` seconds or is terminated. A container won't be scaled down
            for as long as it holds a live session.

            If no container has room for the session, the call waits for additional capacity. It will block for
            up to 25 minutes before giving up. To control the wait per call, use the HTTP API and apply your own retry
            policy.

            Args:
                idle_timeout: Seconds without an in-flight request before the session ends.

            Examples:

                ```python notest
                server = modal.Server.from_name("my-app", "MyServer")
                server_url = server.get_url()
                session = server.sessions.start(idle_timeout=600)
                headers = {"Modal-Authorization": f"Bearer {session.token}"}

                requests.get(server_url, headers=headers).raise_for_status()

                server.sessions.terminate(session.token)
                ```
            """
            ...

    start: __start_spec

    class __terminate_spec(typing_extensions.Protocol):
        def __call__(self, /, token: str) -> None:
            """Terminate a sticky session.

            New requests to it will be rejected. The container continues serving other sessions.

            Args:
                token: The `token` of the `ServerSessionCredentials` to terminate.

            Examples:

                ```python notest
                server = modal.Server.from_name("my-app", "MyServer")
                session = server.sessions.start()

                server.sessions.terminate(session.token)
                ```
            """
            ...

        async def aio(self, /, token: str) -> None:
            """Terminate a sticky session.

            New requests to it will be rejected. The container continues serving other sessions.

            Args:
                token: The `token` of the `ServerSessionCredentials` to terminate.

            Examples:

                ```python notest
                server = modal.Server.from_name("my-app", "MyServer")
                session = server.sessions.start()

                server.sessions.terminate(session.token)
                ```
            """
            ...

    terminate: __terminate_spec

class _ServerAutoscalerManager:
    def __init__(self, server: _Server):
        """mdmd:hidden"""
        ...

    async def settings(self) -> modal.types.ServerAutoscalerSettings:
        """View the current Autoscaler settings for this Server.

        Returns:
            A `ServerAutoscalerSettings` dataclass.

        Examples:

            ```python notest
            server = modal.Server.from_name("my-app", "MyServer")
            settings = server.autoscaler.settings()
            ```
        """
        ...

    async def update(
        self,
        *,
        target_concurrency: typing.Optional[float] = -1,
        min_containers: typing.Optional[int] = -1,
        max_containers: typing.Optional[int] = -1,
        buffer_containers: typing.Optional[int] = -1,
        scaledown_window: int = -1,
        scaleup_window: int = -1,
    ) -> modal.types.ServerAutoscalerSettings:
        """Override the current Autoscaler settings for this Server.

        All parameters to this function are optional; not passing an argument for a given parameter
        will not update its value.

        Note that re-deploying the App containing this Server will wipe any overrides and revert
        its Autoscaler settings back to those defined on the Server at creation time.

        Args:
            target_concurrency: Target number of concurrent requests per container. Must either be a
                positive float (e.g. 1.5 to target 3 requests for every 2 containers), or `None`.
                Passing `None` will disable autoscaling of this Server (effectively setting target
                concurrency to infinity).
            min_containers: Minimum number of containers to keep running. Must be a nonnegative
                integer, or `None`. Passing `None` is equivalent to setting the minimum to 0.
            max_containers: Maximum concurrent containers. Must be a positive integer, or `None`.
                Passing `None` is equivalent to disabling the upper bound on container concurrency at
                the Server level (note that Environment and Workspace level container upper limits
                still apply.)
            buffer_containers: Extra containers to keep warm beyond current demand. Must be a
                nonnegative integer, or `None`. Passing `None` is equivalent to setting the buffer to
                0.
            scaledown_window: Maximum duration (in seconds) idle containers wait before scaling down.
                Must be a positive integer between 2 and 3600, inclusive.
            scaleup_window: Seconds of sustained demand required before scaling up new containers.
                Must be a positive integer.

        Returns:
            A `ServerAutoscalerSettings` dataclass.

        Examples:

            Update `MyServer` so that 2 containers are always active.

            ```python notest
            MyServer = modal.Server.from_name("my-app", "MyServer")
            MyServer.autoscaler.update(min_containers=2)
            ```

            Update `MyServer` so that there is no Server-level limit on `max_containers`:

            ```python notest
            MyServer = modal.Server.from_name("my-app", "MyServer")
            MyServer.autoscaler.update(max_containers=None)
            ```
        """
        ...
