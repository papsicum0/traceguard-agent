import asyncio.locks
import collections.abc
import google.protobuf.message
import modal._logs_manager
import modal._outbound_policy
import modal._supports_logs
import modal._tunnel
import modal.app
import modal.client
import modal.cloud_bucket_mount
import modal.container_process
import modal.image
import modal.io_streams
import modal.mount
import modal.network_file_system
import modal.object
import modal.proxy
import modal.sandbox._sandbox
import modal.sandbox._task_command_router_client
import modal.secret
import modal.stream_type
import modal.types
import modal.volume
import modal_proto.api_pb2
import modal_proto.task_command_router_pb2
import os
import pathlib
import typing
import typing_extensions

class SandboxFilesystem:
    """mdmd:namespace"""

    _container: typing.Union[Sandbox, SidecarContainer]

    def __init__(self, container: typing.Union[Sandbox, SidecarContainer]) -> None:
        """mdmd:hidden"""
        ...

    class __copy_from_local_spec(typing_extensions.Protocol):
        def __call__(self, /, local_path: typing.Union[str, os.PathLike], remote_path: str) -> None:
            """Copy a local file into the Sandbox.

            `remote_path` must be an absolute path to a file in the Sandbox.
            Parent directories for `remote_path` are created if needed.
            The remote file is overwritten if it already exists.

            Args:
                local_path: Path to the file on the local machine.
                remote_path: Absolute path to the file in the Sandbox.

            Raises:
                SandboxFilesystemNotADirectoryError: A parent path component of ``remote_path`` is not a directory.
                SandboxFilesystemIsADirectoryError: ``remote_path`` points to a directory.
                SandboxFilesystemPermissionError: Write permission is denied in the Sandbox.
                SandboxFilesystemError: The command fails for any other reason.
                FileNotFoundError: ``local_path`` does not exist.
                IsADirectoryError: ``local_path`` is a directory.
                PermissionError: Reading ``local_path`` is not permitted.

            Examples:
                ```python fixture:sandbox fixture:tmpdir
                import tempfile
                from pathlib import Path

                local_path = Path(tempfile.mktemp())
                local_path.write_text("Hello, world!\n")
                sandbox.filesystem.copy_from_local(local_path, "/tmp/hello.txt")
                ```
            """
            ...

        async def aio(self, /, local_path: typing.Union[str, os.PathLike], remote_path: str) -> None:
            """Copy a local file into the Sandbox.

            `remote_path` must be an absolute path to a file in the Sandbox.
            Parent directories for `remote_path` are created if needed.
            The remote file is overwritten if it already exists.

            Args:
                local_path: Path to the file on the local machine.
                remote_path: Absolute path to the file in the Sandbox.

            Raises:
                SandboxFilesystemNotADirectoryError: A parent path component of ``remote_path`` is not a directory.
                SandboxFilesystemIsADirectoryError: ``remote_path`` points to a directory.
                SandboxFilesystemPermissionError: Write permission is denied in the Sandbox.
                SandboxFilesystemError: The command fails for any other reason.
                FileNotFoundError: ``local_path`` does not exist.
                IsADirectoryError: ``local_path`` is a directory.
                PermissionError: Reading ``local_path`` is not permitted.

            Examples:
                ```python fixture:sandbox fixture:tmpdir
                import tempfile
                from pathlib import Path

                local_path = Path(tempfile.mktemp())
                local_path.write_text("Hello, world!\n")
                sandbox.filesystem.copy_from_local(local_path, "/tmp/hello.txt")
                ```
            """
            ...

    copy_from_local: __copy_from_local_spec

    class __copy_to_local_spec(typing_extensions.Protocol):
        def __call__(self, /, remote_path: str, local_path: typing.Union[str, os.PathLike]) -> None:
            """Copy a file from the Sandbox to a local path.

            `remote_path` must be an absolute path to a file in the Sandbox.
            Parent directories for `local_path` are created if needed.
            The local file is overwritten if it already exists.

            Args:
                remote_path: Absolute path to the file in the Sandbox.
                local_path: Path to the file on the local machine.

            Raises:
                SandboxFilesystemNotFoundError: The remote path does not exist.
                SandboxFilesystemIsADirectoryError: The remote path points to a directory.
                SandboxFilesystemFileTooLargeError: The file exceeds the read size limit.
                SandboxFilesystemPermissionError: Read permission is denied in the Sandbox.
                SandboxFilesystemError: The command fails for any other reason.
                IsADirectoryError: ``local_path`` points to a directory.
                NotADirectoryError: A component of the ``local_path`` parent is not a directory.
                PermissionError: Writing ``local_path`` is not permitted.

            Examples:
                ```python fixture:sandbox fixture:tmpdir
                sandbox.filesystem.write_text("Hello, world!\n", "/tmp/hello.txt")
                sandbox.filesystem.copy_to_local("/tmp/hello.txt", "/tmp/local-hello.txt")
                ```
            """
            ...

        async def aio(self, /, remote_path: str, local_path: typing.Union[str, os.PathLike]) -> None:
            """Copy a file from the Sandbox to a local path.

            `remote_path` must be an absolute path to a file in the Sandbox.
            Parent directories for `local_path` are created if needed.
            The local file is overwritten if it already exists.

            Args:
                remote_path: Absolute path to the file in the Sandbox.
                local_path: Path to the file on the local machine.

            Raises:
                SandboxFilesystemNotFoundError: The remote path does not exist.
                SandboxFilesystemIsADirectoryError: The remote path points to a directory.
                SandboxFilesystemFileTooLargeError: The file exceeds the read size limit.
                SandboxFilesystemPermissionError: Read permission is denied in the Sandbox.
                SandboxFilesystemError: The command fails for any other reason.
                IsADirectoryError: ``local_path`` points to a directory.
                NotADirectoryError: A component of the ``local_path`` parent is not a directory.
                PermissionError: Writing ``local_path`` is not permitted.

            Examples:
                ```python fixture:sandbox fixture:tmpdir
                sandbox.filesystem.write_text("Hello, world!\n", "/tmp/hello.txt")
                sandbox.filesystem.copy_to_local("/tmp/hello.txt", "/tmp/local-hello.txt")
                ```
            """
            ...

    copy_to_local: __copy_to_local_spec

    class __list_files_spec(typing_extensions.Protocol):
        def __call__(self, /, remote_path: str) -> list[modal.types.FileInfo]:
            """List files and directories in a Sandbox directory.

            Args:
                remote_path: Absolute path to the directory in the Sandbox.

            Returns:
                A list of `FileInfo` objects describing each entry.

            Raises:
                SandboxFilesystemNotFoundError: The path does not exist.
                SandboxFilesystemNotADirectoryError: The path is not a directory.
                SandboxFilesystemPermissionError: Read permission is denied.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                entries = sandbox.filesystem.list_files("/tmp")
                for entry in entries:
                    print(entry.name, entry.type, entry.size)
                ```
            """
            ...

        async def aio(self, /, remote_path: str) -> list[modal.types.FileInfo]:
            """List files and directories in a Sandbox directory.

            Args:
                remote_path: Absolute path to the directory in the Sandbox.

            Returns:
                A list of `FileInfo` objects describing each entry.

            Raises:
                SandboxFilesystemNotFoundError: The path does not exist.
                SandboxFilesystemNotADirectoryError: The path is not a directory.
                SandboxFilesystemPermissionError: Read permission is denied.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                entries = sandbox.filesystem.list_files("/tmp")
                for entry in entries:
                    print(entry.name, entry.type, entry.size)
                ```
            """
            ...

    list_files: __list_files_spec

    class __make_directory_spec(typing_extensions.Protocol):
        def __call__(self, /, remote_path: str, *, create_parents: bool = True) -> None:
            """Create a new directory in the Sandbox.

            `remote_path` must be an absolute path in the Sandbox.

            When `create_parents` is `True` (the default), any missing parent directories are created and the call is
            idempotent (succeeds silently if the directory already exists). When `create_parents` is `False`, the
            immediate parent directory must already exist and the path must not already exist.

            Args:
                remote_path: Absolute path of the directory to create in the Sandbox.
                create_parents: When ``True``, create missing parents and succeed if the directory already exists.

            Raises:
                SandboxFilesystemNotFoundError: The parent directory does not exist and ``create_parents`` is false.
                SandboxFilesystemPathAlreadyExistsError: The path already exists.
                SandboxFilesystemNotADirectoryError: A path component is not a directory.
                SandboxFilesystemPermissionError: Creation is not permitted.
                InvalidError: The operation is not supported by the mount.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.make_directory("/tmp/a/b/c")
                ```
            """
            ...

        async def aio(self, /, remote_path: str, *, create_parents: bool = True) -> None:
            """Create a new directory in the Sandbox.

            `remote_path` must be an absolute path in the Sandbox.

            When `create_parents` is `True` (the default), any missing parent directories are created and the call is
            idempotent (succeeds silently if the directory already exists). When `create_parents` is `False`, the
            immediate parent directory must already exist and the path must not already exist.

            Args:
                remote_path: Absolute path of the directory to create in the Sandbox.
                create_parents: When ``True``, create missing parents and succeed if the directory already exists.

            Raises:
                SandboxFilesystemNotFoundError: The parent directory does not exist and ``create_parents`` is false.
                SandboxFilesystemPathAlreadyExistsError: The path already exists.
                SandboxFilesystemNotADirectoryError: A path component is not a directory.
                SandboxFilesystemPermissionError: Creation is not permitted.
                InvalidError: The operation is not supported by the mount.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.make_directory("/tmp/a/b/c")
                ```
            """
            ...

    make_directory: __make_directory_spec

    class __read_bytes_spec(typing_extensions.Protocol):
        def __call__(self, /, remote_path: str) -> bytes:
            """Read a file from the Sandbox and return its contents as bytes.

            `remote_path` must be an absolute path to a file in the Sandbox.

            Args:
                remote_path: Absolute path to the file in the Sandbox.

            Returns:
                Raw bytes read from the file.

            Raises:
                SandboxFilesystemNotFoundError: The path does not exist.
                SandboxFilesystemIsADirectoryError: The path points to a directory.
                SandboxFilesystemFileTooLargeError: The file exceeds the read size limit.
                SandboxFilesystemPermissionError: Read permission is denied.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.write_bytes(b"Hello, world!\n", "/tmp/hello.bin")
                contents = sandbox.filesystem.read_bytes("/tmp/hello.bin")
                print(contents.decode("utf-8"))
                ```
            """
            ...

        async def aio(self, /, remote_path: str) -> bytes:
            """Read a file from the Sandbox and return its contents as bytes.

            `remote_path` must be an absolute path to a file in the Sandbox.

            Args:
                remote_path: Absolute path to the file in the Sandbox.

            Returns:
                Raw bytes read from the file.

            Raises:
                SandboxFilesystemNotFoundError: The path does not exist.
                SandboxFilesystemIsADirectoryError: The path points to a directory.
                SandboxFilesystemFileTooLargeError: The file exceeds the read size limit.
                SandboxFilesystemPermissionError: Read permission is denied.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.write_bytes(b"Hello, world!\n", "/tmp/hello.bin")
                contents = sandbox.filesystem.read_bytes("/tmp/hello.bin")
                print(contents.decode("utf-8"))
                ```
            """
            ...

    read_bytes: __read_bytes_spec

    class __read_text_spec(typing_extensions.Protocol):
        def __call__(self, /, remote_path: str) -> str:
            """Read a file from the Sandbox and return its contents as a UTF-8 string.

            `remote_path` must be an absolute path to a file in the Sandbox.

            Args:
                remote_path: Absolute path to the file in the Sandbox.

            Returns:
                File contents decoded as UTF-8.

            Raises:
                SandboxFilesystemNotFoundError: The path does not exist.
                SandboxFilesystemIsADirectoryError: The path points to a directory.
                SandboxFilesystemFileTooLargeError: The file exceeds the read size limit.
                SandboxFilesystemPermissionError: Read permission is denied.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.write_text("Hello, world!\n", "/tmp/hello.txt")
                contents = sandbox.filesystem.read_text("/tmp/hello.txt")
                print(contents)
                ```
            """
            ...

        async def aio(self, /, remote_path: str) -> str:
            """Read a file from the Sandbox and return its contents as a UTF-8 string.

            `remote_path` must be an absolute path to a file in the Sandbox.

            Args:
                remote_path: Absolute path to the file in the Sandbox.

            Returns:
                File contents decoded as UTF-8.

            Raises:
                SandboxFilesystemNotFoundError: The path does not exist.
                SandboxFilesystemIsADirectoryError: The path points to a directory.
                SandboxFilesystemFileTooLargeError: The file exceeds the read size limit.
                SandboxFilesystemPermissionError: Read permission is denied.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.write_text("Hello, world!\n", "/tmp/hello.txt")
                contents = sandbox.filesystem.read_text("/tmp/hello.txt")
                print(contents)
                ```
            """
            ...

    read_text: __read_text_spec

    class __remove_spec(typing_extensions.Protocol):
        def __call__(self, /, remote_path: str, *, recursive: bool = False) -> None:
            """Remove a file or directory in the Sandbox.

            When `remote_path` is a directory and `recursive` is `False` (the
            default), removes it only if it is empty. When `recursive` is `True`,
            removes the directory and all its contents.

            Recursive directory removal is not supported on all mounts.
            In particular, `CloudBucketMount` does not support it. An
            `InvalidError` is raised in that case.

            Args:
                remote_path: Absolute path to the file in the Sandbox.
                recursive: When ``True``, remove the directory and all its contents.

            Raises:
                SandboxFilesystemNotFoundError: The remote path does not exist.
                SandboxFilesystemDirectoryNotEmptyError: `recursive` is `False` and the directory is not empty.
                SandboxFilesystemPermissionError: Read permission is denied in the Sandbox.
                InvalidError: The operation is not supported by the mount.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                To remove a file:

                ```python fixture:sandbox
                sandbox.filesystem.write_bytes(b"Hello, world!\n", "/tmp/hello.bin")
                sandbox.filesystem.remove("/tmp/hello.bin")
                ```

                To remove a directory and all its contents:

                ```python fixture:sandbox
                sandbox.filesystem.make_directory("/tmp/mydir/subdir")
                sandbox.filesystem.remove("/tmp/mydir", recursive=True)
                ```
            """
            ...

        async def aio(self, /, remote_path: str, *, recursive: bool = False) -> None:
            """Remove a file or directory in the Sandbox.

            When `remote_path` is a directory and `recursive` is `False` (the
            default), removes it only if it is empty. When `recursive` is `True`,
            removes the directory and all its contents.

            Recursive directory removal is not supported on all mounts.
            In particular, `CloudBucketMount` does not support it. An
            `InvalidError` is raised in that case.

            Args:
                remote_path: Absolute path to the file in the Sandbox.
                recursive: When ``True``, remove the directory and all its contents.

            Raises:
                SandboxFilesystemNotFoundError: The remote path does not exist.
                SandboxFilesystemDirectoryNotEmptyError: `recursive` is `False` and the directory is not empty.
                SandboxFilesystemPermissionError: Read permission is denied in the Sandbox.
                InvalidError: The operation is not supported by the mount.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                To remove a file:

                ```python fixture:sandbox
                sandbox.filesystem.write_bytes(b"Hello, world!\n", "/tmp/hello.bin")
                sandbox.filesystem.remove("/tmp/hello.bin")
                ```

                To remove a directory and all its contents:

                ```python fixture:sandbox
                sandbox.filesystem.make_directory("/tmp/mydir/subdir")
                sandbox.filesystem.remove("/tmp/mydir", recursive=True)
                ```
            """
            ...

    remove: __remove_spec

    class __stat_spec(typing_extensions.Protocol):
        def __call__(self, /, remote_path: str) -> modal.types.FileInfo:
            """Return metadata for a single file, directory, or symlink in the Sandbox.

            `remote_path` must be an absolute path in the Sandbox. If `remote_path` is a symlink, the returned
            `FileInfo` object describes the symlink, not the target it points to.

            Args:
                remote_path: Absolute path in the Sandbox.

            Returns:
                A `FileInfo` object describing the path.

            Raises:
                SandboxFilesystemNotFoundError: The path does not exist.
                SandboxFilesystemNotADirectoryError: A non-leaf component of the path is not a directory.
                SandboxFilesystemPermissionError: A component of the path is not searchable.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.write_text("Hello, world!\n", "/tmp/hello.txt")
                info = sandbox.filesystem.stat("/tmp/hello.txt")
                print(info.size, info.permissions, info.modified_time)
                ```
            """
            ...

        async def aio(self, /, remote_path: str) -> modal.types.FileInfo:
            """Return metadata for a single file, directory, or symlink in the Sandbox.

            `remote_path` must be an absolute path in the Sandbox. If `remote_path` is a symlink, the returned
            `FileInfo` object describes the symlink, not the target it points to.

            Args:
                remote_path: Absolute path in the Sandbox.

            Returns:
                A `FileInfo` object describing the path.

            Raises:
                SandboxFilesystemNotFoundError: The path does not exist.
                SandboxFilesystemNotADirectoryError: A non-leaf component of the path is not a directory.
                SandboxFilesystemPermissionError: A component of the path is not searchable.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.write_text("Hello, world!\n", "/tmp/hello.txt")
                info = sandbox.filesystem.stat("/tmp/hello.txt")
                print(info.size, info.permissions, info.modified_time)
                ```
            """
            ...

    stat: __stat_spec

    class __watch_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            remote_path: str,
            *,
            filter: typing.Optional[list[modal.types.FileWatchEventType]] = None,
            recursive: bool = False,
            timeout: typing.Optional[int] = None,
        ) -> typing.Iterator[modal.types.FileWatchEvent]:
            """Watch a path in the Sandbox for filesystem changes.

            `remote_path` must be an absolute path in the Sandbox. If it points
            to a file, events for that file are reported. If it points to a
            directory, events for entries directly inside it are reported. Set
            `recursive=True` to also receive events for all nested subdirectories.
            If `remote_path` is a symlink, it is followed and events reference
            paths under the resolved target.

            Args:
                remote_path: Absolute path in the Sandbox to watch.
                filter: Restrict the kinds of events emitted to those included in the list.
                    The default ``None`` permits all event types.
                recursive: When ``True``, also report events for all nested subdirectories.
                timeout: Number of seconds to watch for. ``None`` means watch indefinitely.

            Yields:
                `FileWatchEvent` objects as changes occur, until either ``timeout`` seconds
                elapse, the iterator is closed, or the Sandbox is terminated. When ``timeout``
                elapses, the iterator stops without raising an exception.

            Raises:
                SandboxFilesystemNotFoundError: ``remote_path`` does not exist.
                SandboxFilesystemPermissionError: Watch access is denied.
                InvalidError: The filesystem at ``remote_path`` does not support watching.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python notest
                for event in sandbox.filesystem.watch(
                    "/tmp/foo",
                    recursive=True,
                    filter=[FileWatchEventType.Create],
                    timeout=60,
                ):
                    if any(p.endswith(".done") for p in event.paths):
                        break
                ```
            """
            ...

        def aio(
            self,
            /,
            remote_path: str,
            *,
            filter: typing.Optional[list[modal.types.FileWatchEventType]] = None,
            recursive: bool = False,
            timeout: typing.Optional[int] = None,
        ) -> typing.AsyncIterator[modal.types.FileWatchEvent]:
            """Watch a path in the Sandbox for filesystem changes.

            `remote_path` must be an absolute path in the Sandbox. If it points
            to a file, events for that file are reported. If it points to a
            directory, events for entries directly inside it are reported. Set
            `recursive=True` to also receive events for all nested subdirectories.
            If `remote_path` is a symlink, it is followed and events reference
            paths under the resolved target.

            Args:
                remote_path: Absolute path in the Sandbox to watch.
                filter: Restrict the kinds of events emitted to those included in the list.
                    The default ``None`` permits all event types.
                recursive: When ``True``, also report events for all nested subdirectories.
                timeout: Number of seconds to watch for. ``None`` means watch indefinitely.

            Yields:
                `FileWatchEvent` objects as changes occur, until either ``timeout`` seconds
                elapse, the iterator is closed, or the Sandbox is terminated. When ``timeout``
                elapses, the iterator stops without raising an exception.

            Raises:
                SandboxFilesystemNotFoundError: ``remote_path`` does not exist.
                SandboxFilesystemPermissionError: Watch access is denied.
                InvalidError: The filesystem at ``remote_path`` does not support watching.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python notest
                for event in sandbox.filesystem.watch(
                    "/tmp/foo",
                    recursive=True,
                    filter=[FileWatchEventType.Create],
                    timeout=60,
                ):
                    if any(p.endswith(".done") for p in event.paths):
                        break
                ```
            """
            ...

    watch: __watch_spec

    class __write_bytes_spec(typing_extensions.Protocol):
        def __call__(self, /, data: typing.Union[bytes, bytearray, memoryview], remote_path: str) -> None:
            """Write binary content to a file in the Sandbox.

            `remote_path` must be an absolute path to a file in the Sandbox.
            Parent directories for `remote_path` are created if needed.
            The remote file is overwritten if it already exists.

            Args:
                data: Bytes to write.
                remote_path: Absolute path to the file in the Sandbox.

            Raises:
                TypeError: ``data`` is not bytes-like.
                SandboxFilesystemNotADirectoryError: A parent path component is not a directory.
                SandboxFilesystemIsADirectoryError: ``remote_path`` points to a directory.
                SandboxFilesystemPermissionError: Write permission is denied.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.write_bytes(b"Hello, world!\n", "/tmp/hello.bin")
                ```
            """
            ...

        async def aio(self, /, data: typing.Union[bytes, bytearray, memoryview], remote_path: str) -> None:
            """Write binary content to a file in the Sandbox.

            `remote_path` must be an absolute path to a file in the Sandbox.
            Parent directories for `remote_path` are created if needed.
            The remote file is overwritten if it already exists.

            Args:
                data: Bytes to write.
                remote_path: Absolute path to the file in the Sandbox.

            Raises:
                TypeError: ``data`` is not bytes-like.
                SandboxFilesystemNotADirectoryError: A parent path component is not a directory.
                SandboxFilesystemIsADirectoryError: ``remote_path`` points to a directory.
                SandboxFilesystemPermissionError: Write permission is denied.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.write_bytes(b"Hello, world!\n", "/tmp/hello.bin")
                ```
            """
            ...

    write_bytes: __write_bytes_spec

    class __write_text_spec(typing_extensions.Protocol):
        def __call__(self, /, data: str, remote_path: str) -> None:
            """Write UTF-8 text to a file in the Sandbox.

            `remote_path` must be an absolute path to a file in the Sandbox.
            Parent directories for `remote_path` are created if needed.
            The remote file is overwritten if it already exists.

            Args:
                data: Text to write (encoded as UTF-8).
                remote_path: Absolute path to the file in the Sandbox.

            Raises:
                TypeError: ``data`` is not a string.
                SandboxFilesystemNotADirectoryError: A parent path component is not a directory.
                SandboxFilesystemIsADirectoryError: ``remote_path`` points to a directory.
                SandboxFilesystemPermissionError: Write permission is denied.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.write_text("Hello, world!\n", "/tmp/hello.txt")
                ```
            """
            ...

        async def aio(self, /, data: str, remote_path: str) -> None:
            """Write UTF-8 text to a file in the Sandbox.

            `remote_path` must be an absolute path to a file in the Sandbox.
            Parent directories for `remote_path` are created if needed.
            The remote file is overwritten if it already exists.

            Args:
                data: Text to write (encoded as UTF-8).
                remote_path: Absolute path to the file in the Sandbox.

            Raises:
                TypeError: ``data`` is not a string.
                SandboxFilesystemNotADirectoryError: A parent path component is not a directory.
                SandboxFilesystemIsADirectoryError: ``remote_path`` points to a directory.
                SandboxFilesystemPermissionError: Write permission is denied.
                SandboxFilesystemError: The command fails for any other reason.

            Examples:
                ```python fixture:sandbox
                sandbox.filesystem.write_text("Hello, world!\n", "/tmp/hello.txt")
                ```
            """
            ...

    write_text: __write_text_spec

    class ___exec_fs_tool_write_spec(typing_extensions.Protocol):
        def __call__(self, /, source: typing.BinaryIO, remote_path: str, op_name: str) -> int:
            """Exec the FS-tools write command and stream `source` into its stdin.

            Returns the number of bytes streamed.
            """
            ...

        async def aio(self, /, source: typing.BinaryIO, remote_path: str, op_name: str) -> int:
            """Exec the FS-tools write command and stream `source` into its stdin.

            Returns the number of bytes streamed.
            """
            ...

    _exec_fs_tool_write: ___exec_fs_tool_write_spec

SUPERSELF = typing.TypeVar("SUPERSELF", covariant=True)

class SandboxSnapshot(modal.object.Object):
    """> Sandbox memory snapshots are in **early preview**.

    A `SandboxSnapshot` object lets you interact with a stored Sandbox snapshot that was created by calling
    `._experimental_snapshot()` on a Sandbox instance. This includes both the filesystem and memory state of
    the original Sandbox at the time the snapshot was taken.
    """

    _metadata: typing.Optional[modal_proto.api_pb2.SandboxSnapshotHandleMetadata]

    def __init__(self, *args, **kwargs):
        """mdmd:hidden"""
        ...

    def _hydrate_metadata(self, metadata: typing.Optional[google.protobuf.message.Message]): ...
    def _get_metadata(self) -> typing.Optional[modal_proto.api_pb2.SandboxSnapshotHandleMetadata]: ...
    @property
    def _is_v2(self) -> typing.Optional[bool]:
        """Whether the snapshot came from a V2 sandbox."""
        ...

    class __from_id_spec(typing_extensions.Protocol[SUPERSELF]):
        def __call__(
            self, /, sandbox_snapshot_id: str, client: typing.Optional[modal.client.Client] = None
        ) -> SUPERSELF:
            """Construct a `SandboxSnapshot` for an existing snapshot ID.

            Args:
                sandbox_snapshot_id: Snapshot ID returned when the snapshot was created.
                client: Modal client to use; defaults to `Client.from_env()` when omitted.

            Returns:
                A `SandboxSnapshot` handle (hydration validates the ID when used).
            """
            ...

        async def aio(self, /, sandbox_snapshot_id: str, client: typing.Optional[modal.client.Client] = None): ...

    from_id: typing.ClassVar[__from_id_spec[typing_extensions.Self]]

class SidecarContainer:
    """Handle to an additional container running in a Sandbox."""

    _result: typing.Optional[modal_proto.api_pb2.GenericResult]
    _filesystem: typing.Optional[SandboxFilesystem]

    def __init__(
        self,
        sandbox: Sandbox,
        container_id: str,
        container_name: str,
        result: typing.Optional[modal_proto.api_pb2.GenericResult] = None,
    ) -> None: ...
    @property
    def object_id(self) -> str: ...
    @property
    def name(self) -> str: ...
    @staticmethod
    def _from_container_info(
        sandbox: Sandbox, container_info: modal_proto.task_command_router_pb2.TaskContainerInfo
    ) -> SidecarContainer: ...

    class ___get_command_router_spec(typing_extensions.Protocol):
        def __call__(self, /) -> tuple[str, modal.sandbox._task_command_router_client.TaskCommandRouterClient]:
            """Get task ID and command router client."""
            ...

        async def aio(self, /) -> tuple[str, modal.sandbox._task_command_router_client.TaskCommandRouterClient]:
            """Get task ID and command router client."""
            ...

    _get_command_router: ___get_command_router_spec

    class __snapshot_filesystem_spec(typing_extensions.Protocol):
        def __call__(self, /, timeout: int = 55, *, ttl: typing.Optional[int] = 2592000) -> modal.image.Image:
            """Snapshot this Sidecar container's filesystem.

            Args:
                timeout:
                    Maximum time in seconds to wait for the snapshot operation.
                ttl:
                    The resulting Image is retained for `ttl` seconds (default: 30 days). Pass `ttl=None` to retain
                    the image indefinitely.

            Returns:
                An [`Image`](https://modal.com/docs/sdk/py/latest/Image) containing a snapshot of this Sidecar's
                filesystem.
            """
            ...

        async def aio(self, /, timeout: int = 55, *, ttl: typing.Optional[int] = 2592000) -> modal.image.Image:
            """Snapshot this Sidecar container's filesystem.

            Args:
                timeout:
                    Maximum time in seconds to wait for the snapshot operation.
                ttl:
                    The resulting Image is retained for `ttl` seconds (default: 30 days). Pass `ttl=None` to retain
                    the image indefinitely.

            Returns:
                An [`Image`](https://modal.com/docs/sdk/py/latest/Image) containing a snapshot of this Sidecar's
                filesystem.
            """
            ...

    snapshot_filesystem: __snapshot_filesystem_spec

    class __exec_spec(typing_extensions.Protocol):
        @typing.overload
        def __call__(
            self,
            /,
            *args: str,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            text: typing.Literal[True] = True,
            bufsize: typing.Literal[-1, 1] = -1,
            pty: bool = False,
        ) -> modal.container_process.ContainerProcess[str]: ...
        @typing.overload
        def __call__(
            self,
            /,
            *args: str,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            text: typing.Literal[False],
            bufsize: typing.Literal[-1, 1] = -1,
            pty: bool = False,
        ) -> modal.container_process.ContainerProcess[bytes]: ...
        @typing.overload
        async def aio(
            self,
            /,
            *args: str,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            text: typing.Literal[True] = True,
            bufsize: typing.Literal[-1, 1] = -1,
            pty: bool = False,
        ) -> modal.container_process.ContainerProcess[str]: ...
        @typing.overload
        async def aio(
            self,
            /,
            *args: str,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            text: typing.Literal[False],
            bufsize: typing.Literal[-1, 1] = -1,
            pty: bool = False,
        ) -> modal.container_process.ContainerProcess[bytes]: ...

    exec: __exec_spec

    @property
    def filesystem(self) -> SandboxFilesystem:
        """Namespace for Sandbox filesystem APIs."""
        ...

    class __mount_image_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            path: typing.Union[pathlib.PurePosixPath, str],
            image: modal.image.Image,
            *,
            _experimental_encryption_key: typing.Optional[bytes] = None,
        ) -> None:
            """Mount an Image at a specified path in this Sidecar container.

            `path` should be a directory that is **not** the root path (`/`). If the path doesn't exist,
            it will be created. If it exists and contains data, the previous directory will be replaced
            by the mount.

            The `image` argument supports any Image that has an object ID, including:
            - Images built using `image.build()`
            - Images referenced by ID, e.g. `Image.from_id(...)`
            - Filesystem/directory snapshots, e.g. created by `.snapshot_directory()` or `.snapshot_filesystem()`
            - Empty images created with `Image.from_scratch()`

            Args:
                path: Absolute mount point directory inside the Sidecar container (not `/`).
                image: Image to mount at `path` (must be built, referenced by ID, or snapshot-based as described above).

            Examples:
                ```py notest
                sidecar_1.mount_image("/workspace", modal.Image.from_scratch())
                workspace_snapshot = sidecar_1.snapshot_directory("/workspace")

                # You can later mount this snapshot in another Sidecar:
                sidecar_2.mount_image("/workspace", workspace_snapshot)
                sidecar_2.filesystem.list_files("/workspace")
                ```
            """
            ...

        async def aio(
            self,
            /,
            path: typing.Union[pathlib.PurePosixPath, str],
            image: modal.image.Image,
            *,
            _experimental_encryption_key: typing.Optional[bytes] = None,
        ) -> None:
            """Mount an Image at a specified path in this Sidecar container.

            `path` should be a directory that is **not** the root path (`/`). If the path doesn't exist,
            it will be created. If it exists and contains data, the previous directory will be replaced
            by the mount.

            The `image` argument supports any Image that has an object ID, including:
            - Images built using `image.build()`
            - Images referenced by ID, e.g. `Image.from_id(...)`
            - Filesystem/directory snapshots, e.g. created by `.snapshot_directory()` or `.snapshot_filesystem()`
            - Empty images created with `Image.from_scratch()`

            Args:
                path: Absolute mount point directory inside the Sidecar container (not `/`).
                image: Image to mount at `path` (must be built, referenced by ID, or snapshot-based as described above).

            Examples:
                ```py notest
                sidecar_1.mount_image("/workspace", modal.Image.from_scratch())
                workspace_snapshot = sidecar_1.snapshot_directory("/workspace")

                # You can later mount this snapshot in another Sidecar:
                sidecar_2.mount_image("/workspace", workspace_snapshot)
                sidecar_2.filesystem.list_files("/workspace")
                ```
            """
            ...

    mount_image: __mount_image_spec

    class __unmount_image_spec(typing_extensions.Protocol):
        def __call__(self, /, path: typing.Union[pathlib.PurePosixPath, str]) -> None:
            """Unmount a previously mounted Image from this Sidecar container.

            `path` must be the exact mount point that was passed to `.mount_image()`.
            After unmounting, the underlying Sidecar filesystem at that path becomes
            visible again.

            Args:
                path: Absolute mount point directory to unmount.
            """
            ...

        async def aio(self, /, path: typing.Union[pathlib.PurePosixPath, str]) -> None:
            """Unmount a previously mounted Image from this Sidecar container.

            `path` must be the exact mount point that was passed to `.mount_image()`.
            After unmounting, the underlying Sidecar filesystem at that path becomes
            visible again.

            Args:
                path: Absolute mount point directory to unmount.
            """
            ...

    unmount_image: __unmount_image_spec

    class __snapshot_directory_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            path: typing.Union[pathlib.PurePosixPath, str],
            *,
            timeout: int = 55,
            ttl: typing.Optional[int] = 2592000,
            _experimental_encryption_key: typing.Optional[bytes] = None,
        ) -> modal.image.Image:
            """Snapshot a directory in this Sidecar container, creating a new Image with its content.

            `timeout` If the snapshot does not return within that window, the call is cancelled
            and `modal.exception.TimeoutError` is raised.

            `ttl` The resulting Image is retained for `ttl` seconds (default: 30 days).
            Pass `ttl=None` to retain the Image indefinitely.

            The returned Image can be used anywhere an Image is accepted, including
            as a mount or as the base filesystem for another container.

            Args:
                path: Absolute path of the directory inside the Sidecar container to snapshot.

            Returns:
                An `Image` containing the directory contents.

            Examples:
                ```py notest
                workspace_snapshot = sidecar_1.snapshot_directory("/workspace")

                # You can later mount this snapshot in another Sidecar:
                sidecar_2.mount_image("/workspace", workspace_snapshot)
                sidecar_2.filesystem.list_files("/workspace")
                ```
            """
            ...

        async def aio(
            self,
            /,
            path: typing.Union[pathlib.PurePosixPath, str],
            *,
            timeout: int = 55,
            ttl: typing.Optional[int] = 2592000,
            _experimental_encryption_key: typing.Optional[bytes] = None,
        ) -> modal.image.Image:
            """Snapshot a directory in this Sidecar container, creating a new Image with its content.

            `timeout` If the snapshot does not return within that window, the call is cancelled
            and `modal.exception.TimeoutError` is raised.

            `ttl` The resulting Image is retained for `ttl` seconds (default: 30 days).
            Pass `ttl=None` to retain the Image indefinitely.

            The returned Image can be used anywhere an Image is accepted, including
            as a mount or as the base filesystem for another container.

            Args:
                path: Absolute path of the directory inside the Sidecar container to snapshot.

            Returns:
                An `Image` containing the directory contents.

            Examples:
                ```py notest
                workspace_snapshot = sidecar_1.snapshot_directory("/workspace")

                # You can later mount this snapshot in another Sidecar:
                sidecar_2.mount_image("/workspace", workspace_snapshot)
                sidecar_2.filesystem.list_files("/workspace")
                ```
            """
            ...

    snapshot_directory: __snapshot_directory_spec

    class __wait_spec(typing_extensions.Protocol):
        def __call__(self, /, raise_on_termination: bool = True) -> None: ...
        async def aio(self, /, raise_on_termination: bool = True) -> None: ...

    wait: __wait_spec

    class __poll_spec(typing_extensions.Protocol):
        def __call__(self, /) -> typing.Optional[int]: ...
        async def aio(self, /) -> typing.Optional[int]: ...

    poll: __poll_spec

    class __terminate_spec(typing_extensions.Protocol):
        @typing.overload
        def __call__(self, /, *, wait: typing.Literal[True]) -> int: ...
        @typing.overload
        def __call__(self, /, *, wait: typing.Literal[False] = False) -> None: ...
        @typing.overload
        async def aio(self, /, *, wait: typing.Literal[True]) -> int: ...
        @typing.overload
        async def aio(self, /, *, wait: typing.Literal[False] = False) -> None: ...

    terminate: __terminate_spec

    class __reload_volumes_spec(typing_extensions.Protocol):
        def __call__(self, /, *, timeout: int = 55) -> None:
            """Reload all Volumes mounted in this sidecar container.

            EXPERIMENTAL: the API is subject to change.

            Blocks until the reload completes, or raises `modal.exception.TimeoutError` on timeout (the reload
            may still complete in the background).

            Args:
                timeout: Defaults to 55 seconds.
            """
            ...

        async def aio(self, /, *, timeout: int = 55) -> None:
            """Reload all Volumes mounted in this sidecar container.

            EXPERIMENTAL: the API is subject to change.

            Blocks until the reload completes, or raises `modal.exception.TimeoutError` on timeout (the reload
            may still complete in the background).

            Args:
                timeout: Defaults to 55 seconds.
            """
            ...

    reload_volumes: __reload_volumes_spec

class SidecarManager:
    """Creates and manages sidecar containers in a Sandbox."""
    def __init__(self, sandbox: Sandbox) -> None: ...

    class ___get_command_router_spec(typing_extensions.Protocol):
        def __call__(self, /) -> tuple[str, modal.sandbox._task_command_router_client.TaskCommandRouterClient]:
            """Get task ID and command router client."""
            ...

        async def aio(self, /) -> tuple[str, modal.sandbox._task_command_router_client.TaskCommandRouterClient]:
            """Get task ID and command router client."""
            ...

    _get_command_router: ___get_command_router_spec

    class __create_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *args: str,
            name: str,
            image: modal.image.Image,
            env: typing.Optional[dict[str, str]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            workdir: typing.Optional[str] = None,
            volumes: typing.Optional[
                dict[
                    typing.Union[str, os.PathLike],
                    typing.Union[modal.volume.Volume, modal.cloud_bucket_mount.CloudBucketMount],
                ]
            ] = None,
            outbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            outbound_domain_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            include_oidc_identity_token: bool = False,
            proxy: typing.Optional[modal.proxy.Proxy] = None,
            pty: bool = False,
            experimental_memory_reserve_consume_mib: typing.Optional[int] = None,
        ) -> SidecarContainer:
            """Create a sidecar container running alongside the Sandbox's main container.

            Sidecar containers share the Sandbox's lifecycle but run their own Image and command. They
            can be used to run auxiliary processes, such as a database or a service the main container
            depends on.

            The sidecar's outbound network policy is independent of the main container's and defaults to
            open network access. To restrict it, pass `outbound_cidr_allowlist` and/or
            `outbound_domain_allowlist`. To block all external egress while keeping connectivity to the
            main container, pass an empty allowlist (`outbound_cidr_allowlist=[]`); a fully network-blocked
            sidecar is not supported because it would have no IP and could not reach the main container.

            Args:
                *args: Command and arguments to run inside the sidecar container.
                name: Unique name for the sidecar container. The name ``"main"`` is reserved.
                image: Image to run the sidecar container with. Must be a pre-built or referenced Image.
                env: Environment variables to set in the sidecar container.
                secrets: Secrets to inject as environment variables in the sidecar container.
                workdir: Working directory for the command; must be absolute if set.
                volumes: Mapping of mount paths to `Volume` or `CloudBucketMount` objects to mount in the
                    sidecar container. Cloud bucket mounts are not supported for GPU Sandboxes.
                outbound_cidr_allowlist: If set, restrict the sidecar's outbound traffic to these CIDR
                    blocks. An empty list blocks all external egress while preserving connectivity to the
                    main container.
                outbound_domain_allowlist: If set, restrict the sidecar's outbound TLS connections (port
                    443) to these SNI domains. Supports wildcards like ``*.example.com``.
                include_oidc_identity_token: If True, the sidecar receives a MODAL_IDENTITY_TOKEN env var for
                    OIDC-based auth (e.g. to AWS, GCP). The token identifies the sidecar container itself,
                    not the main container. Not supported for GPU Sandboxes.
                proxy: Reference to a Modal Proxy to use in front of this sidecar. Not supported for GPU
                    Sandboxes.
                pty: Whether to enable PTY for the sidecar container.
                experimental_memory_reserve_consume_mib: Memory, in MiB, this sidecar consumes from the Sandbox's
                    sidecar memory reserve (the experimental `vm_sidecar_memory_reserve_mib` option).
                    Unset consumes whatever is left of the reserve; creation fails if the request exceeds
                    what is left. Ignored by Sandboxes without a reserve.

            Returns:
                A `SidecarContainer` handle for the running container.
            """
            ...

        async def aio(
            self,
            /,
            *args: str,
            name: str,
            image: modal.image.Image,
            env: typing.Optional[dict[str, str]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            workdir: typing.Optional[str] = None,
            volumes: typing.Optional[
                dict[
                    typing.Union[str, os.PathLike],
                    typing.Union[modal.volume.Volume, modal.cloud_bucket_mount.CloudBucketMount],
                ]
            ] = None,
            outbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            outbound_domain_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            include_oidc_identity_token: bool = False,
            proxy: typing.Optional[modal.proxy.Proxy] = None,
            pty: bool = False,
            experimental_memory_reserve_consume_mib: typing.Optional[int] = None,
        ) -> SidecarContainer:
            """Create a sidecar container running alongside the Sandbox's main container.

            Sidecar containers share the Sandbox's lifecycle but run their own Image and command. They
            can be used to run auxiliary processes, such as a database or a service the main container
            depends on.

            The sidecar's outbound network policy is independent of the main container's and defaults to
            open network access. To restrict it, pass `outbound_cidr_allowlist` and/or
            `outbound_domain_allowlist`. To block all external egress while keeping connectivity to the
            main container, pass an empty allowlist (`outbound_cidr_allowlist=[]`); a fully network-blocked
            sidecar is not supported because it would have no IP and could not reach the main container.

            Args:
                *args: Command and arguments to run inside the sidecar container.
                name: Unique name for the sidecar container. The name ``"main"`` is reserved.
                image: Image to run the sidecar container with. Must be a pre-built or referenced Image.
                env: Environment variables to set in the sidecar container.
                secrets: Secrets to inject as environment variables in the sidecar container.
                workdir: Working directory for the command; must be absolute if set.
                volumes: Mapping of mount paths to `Volume` or `CloudBucketMount` objects to mount in the
                    sidecar container. Cloud bucket mounts are not supported for GPU Sandboxes.
                outbound_cidr_allowlist: If set, restrict the sidecar's outbound traffic to these CIDR
                    blocks. An empty list blocks all external egress while preserving connectivity to the
                    main container.
                outbound_domain_allowlist: If set, restrict the sidecar's outbound TLS connections (port
                    443) to these SNI domains. Supports wildcards like ``*.example.com``.
                include_oidc_identity_token: If True, the sidecar receives a MODAL_IDENTITY_TOKEN env var for
                    OIDC-based auth (e.g. to AWS, GCP). The token identifies the sidecar container itself,
                    not the main container. Not supported for GPU Sandboxes.
                proxy: Reference to a Modal Proxy to use in front of this sidecar. Not supported for GPU
                    Sandboxes.
                pty: Whether to enable PTY for the sidecar container.
                experimental_memory_reserve_consume_mib: Memory, in MiB, this sidecar consumes from the Sandbox's
                    sidecar memory reserve (the experimental `vm_sidecar_memory_reserve_mib` option).
                    Unset consumes whatever is left of the reserve; creation fails if the request exceeds
                    what is left. Ignored by Sandboxes without a reserve.

            Returns:
                A `SidecarContainer` handle for the running container.
            """
            ...

    create: __create_spec

    class __get_spec(typing_extensions.Protocol):
        def __call__(self, /, *, name: str, include_terminated: bool = False) -> SidecarContainer: ...
        async def aio(self, /, *, name: str, include_terminated: bool = False) -> SidecarContainer: ...

    get: __get_spec

    class __list_spec(typing_extensions.Protocol):
        def __call__(self, /, include_terminated: bool = False) -> list[SidecarContainer]: ...
        async def aio(self, /, include_terminated: bool = False) -> list[SidecarContainer]: ...

    list: __list_spec

class Sandbox(modal.object.Object):
    """A `Sandbox` object lets you interact with a running sandbox. This API is similar to Python's
    [asyncio.subprocess.Process](https://docs.python.org/3/library/asyncio-subprocess.html#asyncio.subprocess.Process).

    Refer to the [guide](https://modal.com/docs/guide/sandbox) on how to spawn and use sandboxes.
    """

    _result: typing.Optional[modal_proto.api_pb2.GenericResult]
    _stdout: modal.io_streams.StreamReader[str]
    _stderr: modal.io_streams.StreamReader[str]
    _stdin: modal.io_streams.StreamWriter
    _task_id: typing.Optional[str]
    _tunnels: typing.Optional[dict[int, modal._tunnel.Tunnel]]
    _enable_snapshot: bool
    _command_router_client: typing.Optional[modal.sandbox._task_command_router_client.TaskCommandRouterClient]
    _command_router_lock: typing.Optional[asyncio.locks.Lock]
    _init_command_router_access: typing.Optional[modal_proto.api_pb2.CommandRouterAccess]
    _attached: bool
    _filesystem: typing.Optional[SandboxFilesystem]
    _is_v2: bool
    _app_id: typing.Optional[str]

    def __init__(self, *args, **kwargs):
        """mdmd:hidden"""
        ...

    @staticmethod
    def _default_pty_info() -> modal_proto.api_pb2.PTYInfo: ...
    @staticmethod
    def _new(
        args: collections.abc.Sequence[str],
        image: modal.image.Image,
        secrets: collections.abc.Collection[modal.secret.Secret],
        name: typing.Optional[str] = None,
        timeout: int = 300,
        idle_timeout: typing.Optional[int] = None,
        workdir: typing.Optional[str] = None,
        gpu: typing.Optional[str] = None,
        cloud: typing.Optional[str] = None,
        region: typing.Union[str, collections.abc.Sequence[str], None] = None,
        cpu: typing.Union[float, tuple[float, float], None] = None,
        memory: typing.Union[int, tuple[int, int], None] = None,
        mounts: collections.abc.Sequence[modal.mount.Mount] = (),
        network_file_systems: dict[typing.Union[str, os.PathLike], modal.network_file_system.NetworkFileSystem] = {},
        block_network: bool = False,
        outbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
        outbound_domain_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
        outbound_policy: typing.Optional[modal._outbound_policy.OutboundPolicy] = None,
        inbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
        volumes: dict[
            typing.Union[str, os.PathLike], typing.Union[modal.volume.Volume, modal.cloud_bucket_mount.CloudBucketMount]
        ] = {},
        pty: bool = False,
        pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
        encrypted_ports: collections.abc.Sequence[int] = [],
        h2_ports: collections.abc.Sequence[int] = [],
        unencrypted_ports: collections.abc.Sequence[int] = [],
        proxy: typing.Optional[modal.proxy.Proxy] = None,
        readiness_probe: typing.Optional[modal.sandbox._sandbox.Probe] = None,
        experimental_options: typing.Optional[dict[str, typing.Any]] = None,
        tags: typing.Optional[dict[str, str]] = None,
        enable_snapshot: bool = False,
        verbose: bool = False,
        custom_domain: typing.Optional[str] = None,
        include_oidc_identity_token: bool = False,
        runtime: typing.Optional[typing.Literal["gvisor", "vm"]] = None,
    ) -> Sandbox:
        """mdmd:hidden"""
        ...

    class __create_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *args: str,
            app: typing.Optional[modal.app.App] = None,
            name: typing.Optional[str] = None,
            tags: typing.Optional[dict[str, str]] = None,
            image: typing.Optional[modal.image.Image] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            network_file_systems: dict[
                typing.Union[str, os.PathLike], modal.network_file_system.NetworkFileSystem
            ] = {},
            timeout: int = 300,
            idle_timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            gpu: typing.Optional[str] = None,
            cloud: typing.Optional[str] = None,
            region: typing.Union[str, collections.abc.Sequence[str], None] = None,
            cpu: typing.Union[float, tuple[float, float], None] = None,
            memory: typing.Union[int, tuple[int, int], None] = None,
            runtime: typing.Optional[typing.Literal["gvisor", "vm"]] = None,
            block_network: bool = False,
            outbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            outbound_domain_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            _experimental_outbound_policy: typing.Optional[modal._outbound_policy.OutboundPolicy] = None,
            inbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            volumes: dict[
                typing.Union[str, os.PathLike],
                typing.Union[modal.volume.Volume, modal.cloud_bucket_mount.CloudBucketMount],
            ] = {},
            pty: bool = False,
            encrypted_ports: collections.abc.Sequence[int] = [],
            h2_ports: collections.abc.Sequence[int] = [],
            unencrypted_ports: collections.abc.Sequence[int] = [],
            custom_domain: typing.Optional[str] = None,
            proxy: typing.Optional[modal.proxy.Proxy] = None,
            include_oidc_identity_token: bool = False,
            readiness_probe: typing.Optional[modal.sandbox._sandbox.Probe] = None,
            verbose: bool = False,
            experimental_options: typing.Optional[dict[str, typing.Any]] = None,
            _experimental_enable_snapshot: bool = False,
            client: typing.Optional[modal.client.Client] = None,
            environment_name: typing.Optional[str] = None,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
        ) -> Sandbox:
            """Create a new Sandbox to run untrusted, arbitrary code.

            The Sandbox's corresponding container will be created asynchronously.

            Args:
                *args: Set the CMD of the Sandbox, overriding any CMD of the container image.
                app: Associate the sandbox with an app. Required unless creating from a container.
                name: Optionally give the sandbox a name. Unique within an app.
                tags: Tags to assign to the Sandbox.
                image: The image to run as the container for the sandbox.
                env: Environment variables to set in the Sandbox.
                secrets: Secrets to inject into the Sandbox as environment variables.
                network_file_systems: Network file systems to mount into the sandbox.
                timeout: Maximum lifetime of the sandbox in seconds.
                idle_timeout: The amount of time in seconds that a sandbox can be idle before being terminated.
                workdir: Working directory of the sandbox.
                gpu: GPU reservation for the sandbox.
                cloud: Cloud provider for the sandbox.
                region: Region or regions to run the sandbox on.
                cpu:
                    Specify, in fractional CPU cores, how many CPU cores to request. Or, pass (request, limit) to
                    additionally specify a hard limit in fractional CPU cores. CPU throttling will prevent a container
                    from exceeding its specified limit.
                memory:
                    Specify, in MiB, a memory request which is the minimum memory required. Or, pass (request, limit) to
                    additionally specify a hard limit in MiB.
                runtime:
                    Runtime under which the Sandbox executes, or None to let Modal pick.
                block_network: Whether to block network access.
                outbound_cidr_allowlist: List of CIDRs the sandbox is allowed to access. If None, all CIDRs are allowed.
                outbound_domain_allowlist: List of domain names the sandbox is allowed to access. Supports
                    wildcard prefixes (``*.``); a bare ``"*"`` allows all domains. The outbound policy
                    can be replaced later via `Sandbox._experimental_set_outbound_network_policy`.
                inbound_cidr_allowlist:
                    List of CIDRs allowed to connect inbound to the sandbox (tunnels and connection tokens). If None,
                    all CIDRs are allowed.
                _experimental_outbound_policy: Configuration for replacing headers in outbound HTTPS requests from
                    the Sandbox. Secrets referenced by the policy are resolved outside the Sandbox and are never
                    visible to the workload. See `modal.experimental.OutboundPolicy`. This API is experimental and
                    may change in the future.
                volumes: Mount points for Modal Volumes and CloudBucketMounts.
                pty:
                    Enable a PTY for the Sandbox entrypoint command. When enabled, all output (stdout and stderr from the
                    process) is multiplexed into stdout, and the stderr stream is effectively empty.
                encrypted_ports: List of ports to tunnel into the sandbox. Encrypted ports are tunneled with TLS.
                h2_ports: List of encrypted ports to tunnel into the sandbox, using HTTP/2.
                unencrypted_ports: List of ports to tunnel into the sandbox without encryption.
                custom_domain:
                    Allow connections to the Sandbox via a subdomain of this parent rather than a default Modal domain.
                proxy: Reference to a Modal Proxy to use in front of this Sandbox.
                include_oidc_identity_token:
                    If True, the sandbox will receive a MODAL_IDENTITY_TOKEN env var for OIDC-based auth.
                readiness_probe: Probe used to determine when the sandbox has become ready.
                verbose: Enable verbose logging for sandbox operations.
                experimental_options: Experimental options to pass to the sandbox.
                _experimental_enable_snapshot: Enable memory snapshots.
                client: Modal Client to use for the sandbox.
                environment_name: *DEPRECATED* Optionally override the default environment
                pty_info: *DEPRECATED* Use `pty` instead. `pty` will override `pty_info`.
                cidr_allowlist: *DEPRECATED* Use outbound_cidr_allowlist instead.

            Returns:
                A `Sandbox` object representing the created sandbox which can be used to interact with the sandbox.

            Raises:
                AlreadyExistsError: If a sandbox with the same name already exists.

            Examples:
                ```python
                app = modal.App.lookup('sandbox-hello-world', create_if_missing=True)
                sandbox = modal.Sandbox.create("echo", "hello world", app=app)
                print(sandbox.stdout.read())
                sandbox.wait()
                ```
            """
            ...

        async def aio(
            self,
            /,
            *args: str,
            app: typing.Optional[modal.app.App] = None,
            name: typing.Optional[str] = None,
            tags: typing.Optional[dict[str, str]] = None,
            image: typing.Optional[modal.image.Image] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            network_file_systems: dict[
                typing.Union[str, os.PathLike], modal.network_file_system.NetworkFileSystem
            ] = {},
            timeout: int = 300,
            idle_timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            gpu: typing.Optional[str] = None,
            cloud: typing.Optional[str] = None,
            region: typing.Union[str, collections.abc.Sequence[str], None] = None,
            cpu: typing.Union[float, tuple[float, float], None] = None,
            memory: typing.Union[int, tuple[int, int], None] = None,
            runtime: typing.Optional[typing.Literal["gvisor", "vm"]] = None,
            block_network: bool = False,
            outbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            outbound_domain_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            _experimental_outbound_policy: typing.Optional[modal._outbound_policy.OutboundPolicy] = None,
            inbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            volumes: dict[
                typing.Union[str, os.PathLike],
                typing.Union[modal.volume.Volume, modal.cloud_bucket_mount.CloudBucketMount],
            ] = {},
            pty: bool = False,
            encrypted_ports: collections.abc.Sequence[int] = [],
            h2_ports: collections.abc.Sequence[int] = [],
            unencrypted_ports: collections.abc.Sequence[int] = [],
            custom_domain: typing.Optional[str] = None,
            proxy: typing.Optional[modal.proxy.Proxy] = None,
            include_oidc_identity_token: bool = False,
            readiness_probe: typing.Optional[modal.sandbox._sandbox.Probe] = None,
            verbose: bool = False,
            experimental_options: typing.Optional[dict[str, typing.Any]] = None,
            _experimental_enable_snapshot: bool = False,
            client: typing.Optional[modal.client.Client] = None,
            environment_name: typing.Optional[str] = None,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
        ) -> Sandbox:
            """Create a new Sandbox to run untrusted, arbitrary code.

            The Sandbox's corresponding container will be created asynchronously.

            Args:
                *args: Set the CMD of the Sandbox, overriding any CMD of the container image.
                app: Associate the sandbox with an app. Required unless creating from a container.
                name: Optionally give the sandbox a name. Unique within an app.
                tags: Tags to assign to the Sandbox.
                image: The image to run as the container for the sandbox.
                env: Environment variables to set in the Sandbox.
                secrets: Secrets to inject into the Sandbox as environment variables.
                network_file_systems: Network file systems to mount into the sandbox.
                timeout: Maximum lifetime of the sandbox in seconds.
                idle_timeout: The amount of time in seconds that a sandbox can be idle before being terminated.
                workdir: Working directory of the sandbox.
                gpu: GPU reservation for the sandbox.
                cloud: Cloud provider for the sandbox.
                region: Region or regions to run the sandbox on.
                cpu:
                    Specify, in fractional CPU cores, how many CPU cores to request. Or, pass (request, limit) to
                    additionally specify a hard limit in fractional CPU cores. CPU throttling will prevent a container
                    from exceeding its specified limit.
                memory:
                    Specify, in MiB, a memory request which is the minimum memory required. Or, pass (request, limit) to
                    additionally specify a hard limit in MiB.
                runtime:
                    Runtime under which the Sandbox executes, or None to let Modal pick.
                block_network: Whether to block network access.
                outbound_cidr_allowlist: List of CIDRs the sandbox is allowed to access. If None, all CIDRs are allowed.
                outbound_domain_allowlist: List of domain names the sandbox is allowed to access. Supports
                    wildcard prefixes (``*.``); a bare ``"*"`` allows all domains. The outbound policy
                    can be replaced later via `Sandbox._experimental_set_outbound_network_policy`.
                inbound_cidr_allowlist:
                    List of CIDRs allowed to connect inbound to the sandbox (tunnels and connection tokens). If None,
                    all CIDRs are allowed.
                _experimental_outbound_policy: Configuration for replacing headers in outbound HTTPS requests from
                    the Sandbox. Secrets referenced by the policy are resolved outside the Sandbox and are never
                    visible to the workload. See `modal.experimental.OutboundPolicy`. This API is experimental and
                    may change in the future.
                volumes: Mount points for Modal Volumes and CloudBucketMounts.
                pty:
                    Enable a PTY for the Sandbox entrypoint command. When enabled, all output (stdout and stderr from the
                    process) is multiplexed into stdout, and the stderr stream is effectively empty.
                encrypted_ports: List of ports to tunnel into the sandbox. Encrypted ports are tunneled with TLS.
                h2_ports: List of encrypted ports to tunnel into the sandbox, using HTTP/2.
                unencrypted_ports: List of ports to tunnel into the sandbox without encryption.
                custom_domain:
                    Allow connections to the Sandbox via a subdomain of this parent rather than a default Modal domain.
                proxy: Reference to a Modal Proxy to use in front of this Sandbox.
                include_oidc_identity_token:
                    If True, the sandbox will receive a MODAL_IDENTITY_TOKEN env var for OIDC-based auth.
                readiness_probe: Probe used to determine when the sandbox has become ready.
                verbose: Enable verbose logging for sandbox operations.
                experimental_options: Experimental options to pass to the sandbox.
                _experimental_enable_snapshot: Enable memory snapshots.
                client: Modal Client to use for the sandbox.
                environment_name: *DEPRECATED* Optionally override the default environment
                pty_info: *DEPRECATED* Use `pty` instead. `pty` will override `pty_info`.
                cidr_allowlist: *DEPRECATED* Use outbound_cidr_allowlist instead.

            Returns:
                A `Sandbox` object representing the created sandbox which can be used to interact with the sandbox.

            Raises:
                AlreadyExistsError: If a sandbox with the same name already exists.

            Examples:
                ```python
                app = modal.App.lookup('sandbox-hello-world', create_if_missing=True)
                sandbox = modal.Sandbox.create("echo", "hello world", app=app)
                print(sandbox.stdout.read())
                sandbox.wait()
                ```
            """
            ...

    create: typing.ClassVar[__create_spec]

    class ___create_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *args: str,
            app: typing.Optional[modal.app.App] = None,
            name: typing.Optional[str] = None,
            tags: typing.Optional[dict[str, str]] = None,
            image: typing.Optional[modal.image.Image] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            mounts: collections.abc.Sequence[modal.mount.Mount] = (),
            network_file_systems: dict[
                typing.Union[str, os.PathLike], modal.network_file_system.NetworkFileSystem
            ] = {},
            timeout: int = 300,
            idle_timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            gpu: typing.Optional[str] = None,
            cloud: typing.Optional[str] = None,
            region: typing.Union[str, collections.abc.Sequence[str], None] = None,
            cpu: typing.Union[float, tuple[float, float], None] = None,
            memory: typing.Union[int, tuple[int, int], None] = None,
            runtime: typing.Optional[typing.Literal["gvisor", "vm"]] = None,
            block_network: bool = False,
            outbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            outbound_domain_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            _experimental_outbound_policy: typing.Optional[modal._outbound_policy.OutboundPolicy] = None,
            inbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            volumes: dict[
                typing.Union[str, os.PathLike],
                typing.Union[modal.volume.Volume, modal.cloud_bucket_mount.CloudBucketMount],
            ] = {},
            pty: bool = False,
            encrypted_ports: collections.abc.Sequence[int] = [],
            h2_ports: collections.abc.Sequence[int] = [],
            unencrypted_ports: collections.abc.Sequence[int] = [],
            proxy: typing.Optional[modal.proxy.Proxy] = None,
            include_oidc_identity_token: bool = False,
            readiness_probe: typing.Optional[modal.sandbox._sandbox.Probe] = None,
            experimental_options: typing.Optional[dict[str, typing.Any]] = None,
            _experimental_enable_snapshot: bool = False,
            client: typing.Optional[modal.client.Client] = None,
            verbose: bool = False,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            custom_domain: typing.Optional[str] = None,
        ):
            """Private method used internally.

            This method exposes some internal arguments (currently `mounts`) which are not in the public API.
            `mounts` is currently only used by modal shell (cli) to provide a function's mounts to the
            sandbox that runs the shell session.
            """
            ...

        async def aio(
            self,
            /,
            *args: str,
            app: typing.Optional[modal.app.App] = None,
            name: typing.Optional[str] = None,
            tags: typing.Optional[dict[str, str]] = None,
            image: typing.Optional[modal.image.Image] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            mounts: collections.abc.Sequence[modal.mount.Mount] = (),
            network_file_systems: dict[
                typing.Union[str, os.PathLike], modal.network_file_system.NetworkFileSystem
            ] = {},
            timeout: int = 300,
            idle_timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            gpu: typing.Optional[str] = None,
            cloud: typing.Optional[str] = None,
            region: typing.Union[str, collections.abc.Sequence[str], None] = None,
            cpu: typing.Union[float, tuple[float, float], None] = None,
            memory: typing.Union[int, tuple[int, int], None] = None,
            runtime: typing.Optional[typing.Literal["gvisor", "vm"]] = None,
            block_network: bool = False,
            outbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            outbound_domain_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            _experimental_outbound_policy: typing.Optional[modal._outbound_policy.OutboundPolicy] = None,
            inbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            volumes: dict[
                typing.Union[str, os.PathLike],
                typing.Union[modal.volume.Volume, modal.cloud_bucket_mount.CloudBucketMount],
            ] = {},
            pty: bool = False,
            encrypted_ports: collections.abc.Sequence[int] = [],
            h2_ports: collections.abc.Sequence[int] = [],
            unencrypted_ports: collections.abc.Sequence[int] = [],
            proxy: typing.Optional[modal.proxy.Proxy] = None,
            include_oidc_identity_token: bool = False,
            readiness_probe: typing.Optional[modal.sandbox._sandbox.Probe] = None,
            experimental_options: typing.Optional[dict[str, typing.Any]] = None,
            _experimental_enable_snapshot: bool = False,
            client: typing.Optional[modal.client.Client] = None,
            verbose: bool = False,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            custom_domain: typing.Optional[str] = None,
        ):
            """Private method used internally.

            This method exposes some internal arguments (currently `mounts`) which are not in the public API.
            `mounts` is currently only used by modal shell (cli) to provide a function's mounts to the
            sandbox that runs the shell session.
            """
            ...

    _create: typing.ClassVar[___create_spec]

    class ___experimental_create_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *args: str,
            app: typing.Optional[modal.app.App] = None,
            name: typing.Optional[str] = None,
            tags: typing.Optional[dict[str, str]] = None,
            image: typing.Optional[modal.image.Image] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            mounts: collections.abc.Sequence[modal.mount.Mount] = (),
            timeout: int = 300,
            idle_timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            cpu: typing.Union[float, tuple[float, float], None] = None,
            memory: typing.Union[int, tuple[int, int], None] = None,
            runtime: typing.Optional[typing.Literal["gvisor", "vm"]] = None,
            cloud: typing.Optional[str] = None,
            region: typing.Union[str, collections.abc.Sequence[str], None] = None,
            block_network: bool = False,
            outbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            outbound_domain_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            _experimental_outbound_policy: typing.Optional[modal._outbound_policy.OutboundPolicy] = None,
            inbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            i6pn: bool = False,
            volumes: dict[
                typing.Union[str, os.PathLike],
                typing.Union[modal.volume.Volume, modal.cloud_bucket_mount.CloudBucketMount],
            ] = {},
            pty: bool = False,
            encrypted_ports: collections.abc.Sequence[int] = [],
            h2_ports: collections.abc.Sequence[int] = [],
            unencrypted_ports: collections.abc.Sequence[int] = [],
            proxy: typing.Optional[modal.proxy.Proxy] = None,
            readiness_probe: typing.Optional[modal.sandbox._sandbox.Probe] = None,
            experimental_options: typing.Optional[dict[str, typing.Any]] = None,
            include_oidc_identity_token: bool = False,
            verbose: bool = False,
            custom_domain: typing.Optional[str] = None,
            client: typing.Optional[modal.client.Client] = None,
            _experimental_enable_snapshot: bool = False,
        ) -> Sandbox:
            """Create a sandbox using the V2 backend.

            Supported features include exec, encrypted tunnels, wait/poll/terminate,
            CPU and memory configuration, region placement, private IPv6 networking
            (i6pn), volumes, cloud bucket mounts (with static credentials via
            `secret=...` or `oidc_auth_role_arn`), OIDC identity tokens, proxies,
            filesystem snapshots, and custom domains (`custom_domain=...` allows
            connections to the sandbox via a subdomain of that parent domain rather
            than a default Modal domain; requires prior setup by Modal).

            `cpu` and `memory` accept either a scalar request or a `(request, limit)`
            tuple that additionally sets a hard limit (fractional CPU cores; memory
            in MiB), matching `Sandbox.create()`.

            Pass `_experimental_enable_snapshot=True` to create a sandbox that can be
            snapshotted with `._experimental_snapshot()`. Features like network
            file systems and GPUs are not supported.

            Set `i6pn=True` to enable private IPv6 networking so sandboxes in the same
            workspace can address each other directly at their `i6pn.modal.local`
            address. i6pn only connects sandboxes co-located on the same routable
            network, so pin every sandbox in the group to the same specific region
            (e.g. `region="us-east-1"`).

            V2 sandboxes created with this method are not currently returned by
            `Sandbox.list()`. A named sandbox can be looked up with
            `Sandbox._experimental_from_name(app_name, name)`; otherwise store
            `sandbox.object_id` and use `Sandbox.from_id(sandbox.object_id)` to
            reattach.
            """
            ...

        async def aio(
            self,
            /,
            *args: str,
            app: typing.Optional[modal.app.App] = None,
            name: typing.Optional[str] = None,
            tags: typing.Optional[dict[str, str]] = None,
            image: typing.Optional[modal.image.Image] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            mounts: collections.abc.Sequence[modal.mount.Mount] = (),
            timeout: int = 300,
            idle_timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            cpu: typing.Union[float, tuple[float, float], None] = None,
            memory: typing.Union[int, tuple[int, int], None] = None,
            runtime: typing.Optional[typing.Literal["gvisor", "vm"]] = None,
            cloud: typing.Optional[str] = None,
            region: typing.Union[str, collections.abc.Sequence[str], None] = None,
            block_network: bool = False,
            outbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            outbound_domain_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            _experimental_outbound_policy: typing.Optional[modal._outbound_policy.OutboundPolicy] = None,
            inbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            i6pn: bool = False,
            volumes: dict[
                typing.Union[str, os.PathLike],
                typing.Union[modal.volume.Volume, modal.cloud_bucket_mount.CloudBucketMount],
            ] = {},
            pty: bool = False,
            encrypted_ports: collections.abc.Sequence[int] = [],
            h2_ports: collections.abc.Sequence[int] = [],
            unencrypted_ports: collections.abc.Sequence[int] = [],
            proxy: typing.Optional[modal.proxy.Proxy] = None,
            readiness_probe: typing.Optional[modal.sandbox._sandbox.Probe] = None,
            experimental_options: typing.Optional[dict[str, typing.Any]] = None,
            include_oidc_identity_token: bool = False,
            verbose: bool = False,
            custom_domain: typing.Optional[str] = None,
            client: typing.Optional[modal.client.Client] = None,
            _experimental_enable_snapshot: bool = False,
        ) -> Sandbox:
            """Create a sandbox using the V2 backend.

            Supported features include exec, encrypted tunnels, wait/poll/terminate,
            CPU and memory configuration, region placement, private IPv6 networking
            (i6pn), volumes, cloud bucket mounts (with static credentials via
            `secret=...` or `oidc_auth_role_arn`), OIDC identity tokens, proxies,
            filesystem snapshots, and custom domains (`custom_domain=...` allows
            connections to the sandbox via a subdomain of that parent domain rather
            than a default Modal domain; requires prior setup by Modal).

            `cpu` and `memory` accept either a scalar request or a `(request, limit)`
            tuple that additionally sets a hard limit (fractional CPU cores; memory
            in MiB), matching `Sandbox.create()`.

            Pass `_experimental_enable_snapshot=True` to create a sandbox that can be
            snapshotted with `._experimental_snapshot()`. Features like network
            file systems and GPUs are not supported.

            Set `i6pn=True` to enable private IPv6 networking so sandboxes in the same
            workspace can address each other directly at their `i6pn.modal.local`
            address. i6pn only connects sandboxes co-located on the same routable
            network, so pin every sandbox in the group to the same specific region
            (e.g. `region="us-east-1"`).

            V2 sandboxes created with this method are not currently returned by
            `Sandbox.list()`. A named sandbox can be looked up with
            `Sandbox._experimental_from_name(app_name, name)`; otherwise store
            `sandbox.object_id` and use `Sandbox.from_id(sandbox.object_id)` to
            reattach.
            """
            ...

    _experimental_create: typing.ClassVar[___experimental_create_spec]

    class ___v2_metadata_spec(typing_extensions.Protocol):
        def __call__(self, /, client: typing.Optional[modal.client.Client] = None) -> list[tuple[str, str]]: ...
        async def aio(self, /, client: typing.Optional[modal.client.Client] = None) -> list[tuple[str, str]]: ...

    _v2_metadata: ___v2_metadata_spec

    def _get_metadata(self) -> modal_proto.api_pb2.SandboxHandleMetadata: ...
    def _hydrate_metadata(self, handle_metadata: typing.Optional[google.protobuf.message.Message]) -> None: ...
    def _hydrate_metadata_v2(self) -> None:
        """Wire up V2 stdio readers that read directly from the worker. Cheap
        to call eagerly: the router connection is opened lazily on first read.
        """
        ...

    def _initialize_from_other(self, other): ...
    def _initialize_from_empty(self): ...

    class __detach_spec(typing_extensions.Protocol):
        def __call__(self, /):
            """Disconnects your client from the sandbox and cleans up resources associated with the connection.

            Be sure to only call `detach` when you are done interacting with the sandbox. After calling `detach`,
            any operation using the Sandbox object is not guaranteed to work anymore. If you want to continue interacting
            with a running sandbox, use `Sandbox.from_id` to get a new Sandbox object.

            This method does not interrupt or wait for running concurrent operations on the sandbox. Resources are
            promptly closed once those operations complete.
            """
            ...

        async def aio(self, /):
            """Disconnects your client from the sandbox and cleans up resources associated with the connection.

            Be sure to only call `detach` when you are done interacting with the sandbox. After calling `detach`,
            any operation using the Sandbox object is not guaranteed to work anymore. If you want to continue interacting
            with a running sandbox, use `Sandbox.from_id` to get a new Sandbox object.

            This method does not interrupt or wait for running concurrent operations on the sandbox. Resources are
            promptly closed once those operations complete.
            """
            ...

    detach: __detach_spec

    @property
    def _client(self) -> modal.client.Client: ...
    @_client.setter
    def _client(self, value): ...
    def _ensure_attached(self): ...
    def _ensure_v1(self, method_name: str): ...

    class __from_name_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            app_name: str,
            name: str,
            *,
            environment_name: typing.Optional[str] = None,
            include_terminated: bool = False,
            client: typing.Optional[modal.client.Client] = None,
        ) -> Sandbox:
            """Get a running Sandbox by name from a deployed App.

            A Sandbox's name is the `name` argument passed to `Sandbox.create`.

            Args:
                app_name: Name of the deployed app to look up the sandbox under.
                name: Sandbox name to resolve.
                environment_name: Optional environment name for the lookup; defaults to the configured environment.
                include_terminated: If set to `True` and no Sandbox with the name is currently running, the most
                    recent terminated Sandbox will be returned instead.
                client: Modal client to use for the RPC; defaults to `Client.from_env()` when omitted.

            Returns:
                A `Sandbox` handle for the running Sandbox, or the most recent terminated one when
                `include_terminated=True`.

            Raises:
                NotFoundError: If no matching sandbox exists with the given name.
            """
            ...

        async def aio(
            self,
            /,
            app_name: str,
            name: str,
            *,
            environment_name: typing.Optional[str] = None,
            include_terminated: bool = False,
            client: typing.Optional[modal.client.Client] = None,
        ) -> Sandbox:
            """Get a running Sandbox by name from a deployed App.

            A Sandbox's name is the `name` argument passed to `Sandbox.create`.

            Args:
                app_name: Name of the deployed app to look up the sandbox under.
                name: Sandbox name to resolve.
                environment_name: Optional environment name for the lookup; defaults to the configured environment.
                include_terminated: If set to `True` and no Sandbox with the name is currently running, the most
                    recent terminated Sandbox will be returned instead.
                client: Modal client to use for the RPC; defaults to `Client.from_env()` when omitted.

            Returns:
                A `Sandbox` handle for the running Sandbox, or the most recent terminated one when
                `include_terminated=True`.

            Raises:
                NotFoundError: If no matching sandbox exists with the given name.
            """
            ...

    from_name: typing.ClassVar[__from_name_spec]

    class ___experimental_from_name_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            app_name: str,
            name: str,
            *,
            environment_name: typing.Optional[str] = None,
            include_terminated: bool = False,
            client: typing.Optional[modal.client.Client] = None,
        ) -> Sandbox:
            """Get a running V2 Sandbox by name from a deployed App.

            This looks up V2 sandboxes, ie sandboxes created via `modal.Sandbox._experimental_create`.

            Args:
                app_name: Name of the deployed app to look up the sandbox under.
                name: Sandbox name to resolve.
                environment_name: Optional environment name for the lookup; defaults to the configured environment.
                include_terminated: If set to `True` and no Sandbox with the name is currently running, the most
                    recent terminated Sandbox will be returned instead.
                client: Modal client to use for the RPC; defaults to `Client.from_env()` when omitted.

            Returns:
                A `Sandbox` handle for the running Sandbox, or the most recent terminated one when
                `include_terminated=True`.

            Raises:
                NotFoundError: If no matching sandbox exists with the given name.
            """
            ...

        async def aio(
            self,
            /,
            app_name: str,
            name: str,
            *,
            environment_name: typing.Optional[str] = None,
            include_terminated: bool = False,
            client: typing.Optional[modal.client.Client] = None,
        ) -> Sandbox:
            """Get a running V2 Sandbox by name from a deployed App.

            This looks up V2 sandboxes, ie sandboxes created via `modal.Sandbox._experimental_create`.

            Args:
                app_name: Name of the deployed app to look up the sandbox under.
                name: Sandbox name to resolve.
                environment_name: Optional environment name for the lookup; defaults to the configured environment.
                include_terminated: If set to `True` and no Sandbox with the name is currently running, the most
                    recent terminated Sandbox will be returned instead.
                client: Modal client to use for the RPC; defaults to `Client.from_env()` when omitted.

            Returns:
                A `Sandbox` handle for the running Sandbox, or the most recent terminated one when
                `include_terminated=True`.

            Raises:
                NotFoundError: If no matching sandbox exists with the given name.
            """
            ...

    _experimental_from_name: typing.ClassVar[___experimental_from_name_spec]

    class __from_id_spec(typing_extensions.Protocol):
        def __call__(self, /, sandbox_id: str, client: typing.Optional[modal.client.Client] = None) -> Sandbox:
            """Construct a Sandbox from an id and look up the Sandbox result.

            The ID of a Sandbox object can be accessed using `.object_id`.

            Args:
                sandbox_id: Sandbox object ID to attach to.
                client: Modal client to use for the lookup; defaults to the environment client when omitted.

            Returns:
                A `Sandbox` handle with any available result metadata populated from the server.
            """
            ...

        async def aio(self, /, sandbox_id: str, client: typing.Optional[modal.client.Client] = None) -> Sandbox:
            """Construct a Sandbox from an id and look up the Sandbox result.

            The ID of a Sandbox object can be accessed using `.object_id`.

            Args:
                sandbox_id: Sandbox object ID to attach to.
                client: Modal client to use for the lookup; defaults to the environment client when omitted.

            Returns:
                A `Sandbox` handle with any available result metadata populated from the server.
            """
            ...

    from_id: typing.ClassVar[__from_id_spec]

    class __get_tags_spec(typing_extensions.Protocol):
        def __call__(self, /) -> dict[str, str]:
            """Fetches any tags (key-value pairs) currently attached to this Sandbox from the server.

            Returns:
                Tags as a map from tag name to tag value.
            """
            ...

        async def aio(self, /) -> dict[str, str]:
            """Fetches any tags (key-value pairs) currently attached to this Sandbox from the server.

            Returns:
                Tags as a map from tag name to tag value.
            """
            ...

    get_tags: __get_tags_spec

    class __set_tags_spec(typing_extensions.Protocol):
        def __call__(self, /, tags: dict[str, str], *, client: typing.Optional[modal.client.Client] = None) -> None:
            """Set tags (key-value pairs) on the Sandbox. Tags can be used to filter results in `Sandbox.list`.

            Setting tags replaces the Sandbox's entire tag set; passing an empty dict clears all tags.

            Args:
                tags: Tag names and values to set on this sandbox.
                client: Deprecated. Prefer setting the client when creating or re-attaching to the sandbox.
            """
            ...

        async def aio(self, /, tags: dict[str, str], *, client: typing.Optional[modal.client.Client] = None) -> None:
            """Set tags (key-value pairs) on the Sandbox. Tags can be used to filter results in `Sandbox.list`.

            Setting tags replaces the Sandbox's entire tag set; passing an empty dict clears all tags.

            Args:
                tags: Tag names and values to set on this sandbox.
                client: Deprecated. Prefer setting the client when creating or re-attaching to the sandbox.
            """
            ...

    set_tags: __set_tags_spec

    class ___experimental_set_name_spec(typing_extensions.Protocol):
        def __call__(self, /, name: str) -> None:
            """Assign a name to a running V2 Sandbox that was created without one.

            This is only supported for V2 sandboxes, ie sandboxes created via
            `modal.Sandbox._experimental_create`. A name may only be set once and
            only on a Sandbox that has never had one; afterwards the Sandbox can
            be looked up with `Sandbox._experimental_from_name(app_name, name)`.
            Repeating the Sandbox's current name is idempotent and succeeds, so
            the call is safe to retry.

            Args:
                name: Name to assign to the Sandbox. Must be unique within the App.

            Raises:
                AlreadyExistsError: If another running Sandbox in the App already holds the name.
                ConflictError: If the Sandbox already has a different name or is no longer running.
            """
            ...

        async def aio(self, /, name: str) -> None:
            """Assign a name to a running V2 Sandbox that was created without one.

            This is only supported for V2 sandboxes, ie sandboxes created via
            `modal.Sandbox._experimental_create`. A name may only be set once and
            only on a Sandbox that has never had one; afterwards the Sandbox can
            be looked up with `Sandbox._experimental_from_name(app_name, name)`.
            Repeating the Sandbox's current name is idempotent and succeeds, so
            the call is safe to retry.

            Args:
                name: Name to assign to the Sandbox. Must be unique within the App.

            Raises:
                AlreadyExistsError: If another running Sandbox in the App already holds the name.
                ConflictError: If the Sandbox already has a different name or is no longer running.
            """
            ...

    _experimental_set_name: ___experimental_set_name_spec

    class ___experimental_set_outbound_network_policy_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *,
            outbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            outbound_domain_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
        ) -> None:
            """Replace the outbound network policy of a running Sandbox.

            Established connections that the new policy no longer permits are
            terminated.

            Args:
                outbound_cidr_allowlist: List of CIDRs the Sandbox is allowed to access. If None, all CIDRs are allowed.
                outbound_domain_allowlist: List of domain names the Sandbox is allowed to access. Supports
                    wildcard prefixes (``*.``); a bare ``"*"`` allows all domains.
            """
            ...

        async def aio(
            self,
            /,
            *,
            outbound_cidr_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
            outbound_domain_allowlist: typing.Optional[collections.abc.Sequence[str]] = None,
        ) -> None:
            """Replace the outbound network policy of a running Sandbox.

            Established connections that the new policy no longer permits are
            terminated.

            Args:
                outbound_cidr_allowlist: List of CIDRs the Sandbox is allowed to access. If None, all CIDRs are allowed.
                outbound_domain_allowlist: List of domain names the Sandbox is allowed to access. Supports
                    wildcard prefixes (``*.``); a bare ``"*"`` allows all domains.
            """
            ...

    _experimental_set_outbound_network_policy: ___experimental_set_outbound_network_policy_spec

    class ___experimental_update_outbound_policy_spec(typing_extensions.Protocol):
        def __call__(self, /, outbound_policy: modal._outbound_policy.OutboundPolicy) -> None:
            """Replace the outbound policy of a running Sandbox.

            This API is experimental and may change in the future.

            The new policy replaces all existing policy configuration on the
            Sandbox; build a policy including any existing rules you want to keep.

            Only Sandboxes created with an `_experimental_outbound_policy` can be
            updated this way; for Sandboxes created without one this fails, since
            header replacement is only set up at creation time.

            Args:
                outbound_policy: The new policy to apply.
            """
            ...

        async def aio(self, /, outbound_policy: modal._outbound_policy.OutboundPolicy) -> None:
            """Replace the outbound policy of a running Sandbox.

            This API is experimental and may change in the future.

            The new policy replaces all existing policy configuration on the
            Sandbox; build a policy including any existing rules you want to keep.

            Only Sandboxes created with an `_experimental_outbound_policy` can be
            updated this way; for Sandboxes created without one this fails, since
            header replacement is only set up at creation time.

            Args:
                outbound_policy: The new policy to apply.
            """
            ...

    _experimental_update_outbound_policy: ___experimental_update_outbound_policy_spec

    class ___experimental_get_exit_snapshot_spec(typing_extensions.Protocol):
        def __call__(self, /, timeout: typing.Optional[float] = None) -> modal.image.Image:
            """Get the exit filesystem snapshot image.

            An exit snapshot captures the Sandbox filesystem when the Sandbox exits,
            whether its entrypoint finishes gracefully, abruptly, or it is stopped with
            `terminate()`. Exit snapshots are opt-in: the Sandbox must have been
            created with `experimental_options={"enable_exit_snapshot": True}`.

            Args:
                timeout: Total time to wait in seconds, spread across repeated long
                    polls of at most `_EXIT_SNAPSHOT_LONG_POLL_TIMEOUT` seconds each.
                    `None` (the default) waits until the snapshot reaches a terminal
                    state; `0` performs an immediate check without waiting.

            Returns:
                The exit snapshot Image.

            Raises:
                InvalidError: If `timeout` is negative, or if exit snapshot is not
                    enabled for the sandbox.
                TimeoutError: If `timeout` elapses before the snapshot reaches a
                    terminal state. This includes `timeout=0` when the snapshot is
                    still pending.
                SnapshotCreationError: Snapshot operation is done and failed.
                    Polling again will not produce an Image; filesystem state is gone.
                NotFoundError: If the sandbox does not exist.
                PermissionDeniedError: If the caller cannot access the sandbox.
            """
            ...

        async def aio(self, /, timeout: typing.Optional[float] = None) -> modal.image.Image:
            """Get the exit filesystem snapshot image.

            An exit snapshot captures the Sandbox filesystem when the Sandbox exits,
            whether its entrypoint finishes gracefully, abruptly, or it is stopped with
            `terminate()`. Exit snapshots are opt-in: the Sandbox must have been
            created with `experimental_options={"enable_exit_snapshot": True}`.

            Args:
                timeout: Total time to wait in seconds, spread across repeated long
                    polls of at most `_EXIT_SNAPSHOT_LONG_POLL_TIMEOUT` seconds each.
                    `None` (the default) waits until the snapshot reaches a terminal
                    state; `0` performs an immediate check without waiting.

            Returns:
                The exit snapshot Image.

            Raises:
                InvalidError: If `timeout` is negative, or if exit snapshot is not
                    enabled for the sandbox.
                TimeoutError: If `timeout` elapses before the snapshot reaches a
                    terminal state. This includes `timeout=0` when the snapshot is
                    still pending.
                SnapshotCreationError: Snapshot operation is done and failed.
                    Polling again will not produce an Image; filesystem state is gone.
                NotFoundError: If the sandbox does not exist.
                PermissionDeniedError: If the caller cannot access the sandbox.
            """
            ...

    _experimental_get_exit_snapshot: ___experimental_get_exit_snapshot_spec

    class __snapshot_filesystem_spec(typing_extensions.Protocol):
        def __call__(self, /, timeout: int = 55, *, ttl: typing.Optional[int] = 2592000) -> modal.image.Image:
            """Snapshot the filesystem of the Sandbox.

            Args:
                timeout:
                    Maximum time in seconds to wait for the snapshot operation. If the snapshot does not return within
                    that window, the call is cancelled and `modal.exception.TimeoutError` is raised.
                ttl:
                    The resulting Image is retained for `ttl` seconds (default: 30 days). Pass `ttl=None` to retain
                    the image indefinitely.

            Returns:
                An [`Image`](https://modal.com/docs/sdk/py/latest/Image) object which can be used to spawn a new
                Sandbox with the same filesystem.
            """
            ...

        async def aio(self, /, timeout: int = 55, *, ttl: typing.Optional[int] = 2592000) -> modal.image.Image:
            """Snapshot the filesystem of the Sandbox.

            Args:
                timeout:
                    Maximum time in seconds to wait for the snapshot operation. If the snapshot does not return within
                    that window, the call is cancelled and `modal.exception.TimeoutError` is raised.
                ttl:
                    The resulting Image is retained for `ttl` seconds (default: 30 days). Pass `ttl=None` to retain
                    the image indefinitely.

            Returns:
                An [`Image`](https://modal.com/docs/sdk/py/latest/Image) object which can be used to spawn a new
                Sandbox with the same filesystem.
            """
            ...

    snapshot_filesystem: __snapshot_filesystem_spec

    class ___snapshot_filesystem_spec(typing_extensions.Protocol):
        def __call__(
            self, /, timeout: int, *, ttl: typing.Optional[int], container_id: str = ""
        ) -> modal.image.Image: ...
        async def aio(
            self, /, timeout: int, *, ttl: typing.Optional[int], container_id: str = ""
        ) -> modal.image.Image: ...

    _snapshot_filesystem: ___snapshot_filesystem_spec

    class ___legacy_snapshot_filesystem_spec(typing_extensions.Protocol):
        def __call__(self, /, timeout: int = 55) -> modal.image.Image: ...
        async def aio(self, /, timeout: int = 55) -> modal.image.Image: ...

    _legacy_snapshot_filesystem: ___legacy_snapshot_filesystem_spec

    class __mount_image_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            path: typing.Union[pathlib.PurePosixPath, str],
            image: modal.image.Image,
            *,
            _experimental_encryption_key: typing.Optional[bytes] = None,
        ):
            """Mount an Image at a specified path in a running Sandbox.

            `path` should be a directory that is **not** the root path (`/`). If the path doesn't exist
            it will be created. If it exists and contains data, the previous directory will be replaced
            by the mount.

            The `image` argument supports any Image that has an object ID, including:
            - Images built using `image.build()`
            - Images referenced by ID, e.g. `Image.from_id(...)`
            - Filesystem/directory snapshots, e.g. created by `.snapshot_directory()` or `.snapshot_filesystem()`
            - Empty images created with `Image.from_scratch()`

            Args:
                path: Absolute mount point directory inside the sandbox (not `/`).
                image: Image to mount at `path` (must be built, referenced by ID, or snapshot-based as described above).


            Examples:
                ```py notest
                user_project_snapshot: Image = sandbox_session_1.snapshot_directory("/user_project")

                # You can later mount this snapshot to another Sandbox:
                sandbox_session_2 = modal.Sandbox.create(...)
                sandbox_session_2.mount_image("/user_project", user_project_snapshot)
                sandbox_session_2.filesystem.list_files("/user_project")
                ```
            """
            ...

        async def aio(
            self,
            /,
            path: typing.Union[pathlib.PurePosixPath, str],
            image: modal.image.Image,
            *,
            _experimental_encryption_key: typing.Optional[bytes] = None,
        ):
            """Mount an Image at a specified path in a running Sandbox.

            `path` should be a directory that is **not** the root path (`/`). If the path doesn't exist
            it will be created. If it exists and contains data, the previous directory will be replaced
            by the mount.

            The `image` argument supports any Image that has an object ID, including:
            - Images built using `image.build()`
            - Images referenced by ID, e.g. `Image.from_id(...)`
            - Filesystem/directory snapshots, e.g. created by `.snapshot_directory()` or `.snapshot_filesystem()`
            - Empty images created with `Image.from_scratch()`

            Args:
                path: Absolute mount point directory inside the sandbox (not `/`).
                image: Image to mount at `path` (must be built, referenced by ID, or snapshot-based as described above).


            Examples:
                ```py notest
                user_project_snapshot: Image = sandbox_session_1.snapshot_directory("/user_project")

                # You can later mount this snapshot to another Sandbox:
                sandbox_session_2 = modal.Sandbox.create(...)
                sandbox_session_2.mount_image("/user_project", user_project_snapshot)
                sandbox_session_2.filesystem.list_files("/user_project")
                ```
            """
            ...

    mount_image: __mount_image_spec

    class __unmount_image_spec(typing_extensions.Protocol):
        def __call__(self, /, path: typing.Union[pathlib.PurePosixPath, str]):
            """Unmount a previously mounted Image from a running Sandbox.

            `path` must be the exact mount point that was passed to `.mount_image()`.
            After unmounting, the underlying Sandbox filesystem at that path becomes
            visible again.

            Args:
                path: Absolute mount point directory to unmount.
            """
            ...

        async def aio(self, /, path: typing.Union[pathlib.PurePosixPath, str]):
            """Unmount a previously mounted Image from a running Sandbox.

            `path` must be the exact mount point that was passed to `.mount_image()`.
            After unmounting, the underlying Sandbox filesystem at that path becomes
            visible again.

            Args:
                path: Absolute mount point directory to unmount.
            """
            ...

    unmount_image: __unmount_image_spec

    class __snapshot_directory_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            path: typing.Union[pathlib.PurePosixPath, str],
            *,
            timeout: int = 55,
            ttl: typing.Optional[int] = 2592000,
            _experimental_encryption_key: typing.Optional[bytes] = None,
        ) -> modal.image.Image:
            """Snapshot a directory in a running Sandbox, creating a new Image with its content.

            `timeout` If the snapshot does not return within that window, the call is cancelled
            and `modal.exception.TimeoutError` is raised.

            `ttl` The resulting Image is retained for `ttl` seconds (default: 30 days)
            Pass `ttl=None` to retain the image indefinitely.

            Args:
                path: Absolute path of the directory inside the sandbox to snapshot.

            Returns:
                An `Image` containing the directory contents.

            Examples:
                ```py notest
                user_project_snapshot: Image = sandbox_session_1.snapshot_directory("/user_project")

                # You can later mount this snapshot to another Sandbox:
                sandbox_session_2 = modal.Sandbox.create(...)
                sandbox_session_2.mount_image("/user_project", user_project_snapshot)
                sandbox_session_2.filesystem.list_files("/user_project")
                ```
            """
            ...

        async def aio(
            self,
            /,
            path: typing.Union[pathlib.PurePosixPath, str],
            *,
            timeout: int = 55,
            ttl: typing.Optional[int] = 2592000,
            _experimental_encryption_key: typing.Optional[bytes] = None,
        ) -> modal.image.Image:
            """Snapshot a directory in a running Sandbox, creating a new Image with its content.

            `timeout` If the snapshot does not return within that window, the call is cancelled
            and `modal.exception.TimeoutError` is raised.

            `ttl` The resulting Image is retained for `ttl` seconds (default: 30 days)
            Pass `ttl=None` to retain the image indefinitely.

            Args:
                path: Absolute path of the directory inside the sandbox to snapshot.

            Returns:
                An `Image` containing the directory contents.

            Examples:
                ```py notest
                user_project_snapshot: Image = sandbox_session_1.snapshot_directory("/user_project")

                # You can later mount this snapshot to another Sandbox:
                sandbox_session_2 = modal.Sandbox.create(...)
                sandbox_session_2.mount_image("/user_project", user_project_snapshot)
                sandbox_session_2.filesystem.list_files("/user_project")
                ```
            """
            ...

    snapshot_directory: __snapshot_directory_spec

    class __wait_spec(typing_extensions.Protocol):
        def __call__(self, /, raise_on_termination: bool = True):
            """Wait for the Sandbox to finish running.

            Args:
                raise_on_termination: If True, raise when the sandbox is terminated externally.
            """
            ...

        async def aio(self, /, raise_on_termination: bool = True):
            """Wait for the Sandbox to finish running.

            Args:
                raise_on_termination: If True, raise when the sandbox is terminated externally.
            """
            ...

    wait: __wait_spec

    class __wait_until_ready_spec(typing_extensions.Protocol):
        def __call__(self, /, *, timeout: int = 300) -> None:
            """Wait for the Sandbox readiness probe to report that the Sandbox is ready.

            The Sandbox must be configured with a `readiness_probe` in order to use this method.

            Args:
                timeout: Maximum time in seconds to wait for readiness.


            Examples:
                ```py notest
                app = modal.App.lookup('sandbox-wait-until-ready', create_if_missing=True)
                sandbox = modal.Sandbox.create(
                    "python3", "-m", "http.server", "8080",
                    readiness_probe=modal.Probe.with_tcp(8080),
                    app=app,
                )
                sandbox.wait_until_ready()
                ```
            """
            ...

        async def aio(self, /, *, timeout: int = 300) -> None:
            """Wait for the Sandbox readiness probe to report that the Sandbox is ready.

            The Sandbox must be configured with a `readiness_probe` in order to use this method.

            Args:
                timeout: Maximum time in seconds to wait for readiness.


            Examples:
                ```py notest
                app = modal.App.lookup('sandbox-wait-until-ready', create_if_missing=True)
                sandbox = modal.Sandbox.create(
                    "python3", "-m", "http.server", "8080",
                    readiness_probe=modal.Probe.with_tcp(8080),
                    app=app,
                )
                sandbox.wait_until_ready()
                ```
            """
            ...

    wait_until_ready: __wait_until_ready_spec

    class __tunnels_spec(typing_extensions.Protocol):
        def __call__(self, /, timeout: int = 50) -> dict[int, modal._tunnel.Tunnel]:
            """Get Tunnel metadata for the sandbox.

            NOTE: Previous to client [v0.64.153](https://modal.com/docs/sdk/py/changelog#064153-2024-09-30), this
            returned a list of `TunnelData` objects.

            Args:
                timeout: Maximum time in seconds to wait for tunnel metadata when not already cached.

            Returns:
                A dictionary mapping container port to `Tunnel` metadata.

            Raises:
                SandboxTimeoutError: If the tunnels are not available after the timeout.
            """
            ...

        async def aio(self, /, timeout: int = 50) -> dict[int, modal._tunnel.Tunnel]:
            """Get Tunnel metadata for the sandbox.

            NOTE: Previous to client [v0.64.153](https://modal.com/docs/sdk/py/changelog#064153-2024-09-30), this
            returned a list of `TunnelData` objects.

            Args:
                timeout: Maximum time in seconds to wait for tunnel metadata when not already cached.

            Returns:
                A dictionary mapping container port to `Tunnel` metadata.

            Raises:
                SandboxTimeoutError: If the tunnels are not available after the timeout.
            """
            ...

    tunnels: __tunnels_spec

    class __create_connect_token_spec(typing_extensions.Protocol):
        def __call__(
            self, /, user_metadata: typing.Union[str, dict[str, typing.Any], None] = None, port: int = 8080
        ) -> modal.types.SandboxConnectCredentials:
            """Create a token for making HTTP connections to the Sandbox.

            Accepts an optional user_metadata string or dict to associate with the token. This metadata
            will be added to the headers by the proxy when forwarding requests to the Sandbox.
            Also accepts a port that requests will be routed to.

            Args:
                user_metadata: Optional JSON-serializable metadata or string stored with the connect token.
                port: Optional container port that requests are routed to when using this token.

            Returns:
                URL and token credentials for connecting to the sandbox over HTTP.
            """
            ...

        async def aio(
            self, /, user_metadata: typing.Union[str, dict[str, typing.Any], None] = None, port: int = 8080
        ) -> modal.types.SandboxConnectCredentials:
            """Create a token for making HTTP connections to the Sandbox.

            Accepts an optional user_metadata string or dict to associate with the token. This metadata
            will be added to the headers by the proxy when forwarding requests to the Sandbox.
            Also accepts a port that requests will be routed to.

            Args:
                user_metadata: Optional JSON-serializable metadata or string stored with the connect token.
                port: Optional container port that requests are routed to when using this token.

            Returns:
                URL and token credentials for connecting to the sandbox over HTTP.
            """
            ...

    create_connect_token: __create_connect_token_spec

    class __reload_volumes_spec(typing_extensions.Protocol):
        def __call__(self, /, *, timeout: int = 55) -> None:
            """Reload all Volumes mounted in the Sandbox.

            Added in v1.1.0.

            Blocks until the reload completes, or raises `modal.exception.TimeoutError` on timeout (the reload
            may still complete in the background).

            Args:
                timeout: Defaults to 55 seconds.
            """
            ...

        async def aio(self, /, *, timeout: int = 55) -> None:
            """Reload all Volumes mounted in the Sandbox.

            Added in v1.1.0.

            Blocks until the reload completes, or raises `modal.exception.TimeoutError` on timeout (the reload
            may still complete in the background).

            Args:
                timeout: Defaults to 55 seconds.
            """
            ...

    reload_volumes: __reload_volumes_spec

    class ___reload_volumes_spec(typing_extensions.Protocol):
        def __call__(self, /, *, timeout: int, container_id: str = "") -> None: ...
        async def aio(self, /, *, timeout: int, container_id: str = "") -> None: ...

    _reload_volumes: ___reload_volumes_spec

    class __terminate_spec(typing_extensions.Protocol):
        @typing.overload
        def __call__(self, /, *, wait: typing.Literal[True]) -> int: ...
        @typing.overload
        def __call__(self, /, *, wait: typing.Literal[False] = False) -> None: ...
        @typing.overload
        async def aio(self, /, *, wait: typing.Literal[True]) -> int: ...
        @typing.overload
        async def aio(self, /, *, wait: typing.Literal[False] = False) -> None: ...

    terminate: __terminate_spec

    class __poll_spec(typing_extensions.Protocol):
        def __call__(self, /) -> typing.Optional[int]:
            """Check if the Sandbox has finished running.

            Returns:
                `None` if the Sandbox is still running, otherwise the exit code.
            """
            ...

        async def aio(self, /) -> typing.Optional[int]:
            """Check if the Sandbox has finished running.

            Returns:
                `None` if the Sandbox is still running, otherwise the exit code.
            """
            ...

    poll: __poll_spec

    class ___get_task_id_spec(typing_extensions.Protocol):
        def __call__(
            self, /, raise_if_task_complete=False, timeout: typing.Optional[float] = None, retry_transient: bool = False
        ) -> str: ...
        async def aio(
            self, /, raise_if_task_complete=False, timeout: typing.Optional[float] = None, retry_transient: bool = False
        ) -> str: ...

    _get_task_id: ___get_task_id_spec

    class ___resolve_task_id_for_logs_spec(typing_extensions.Protocol):
        def __call__(self, /) -> str:
            """Try to resolve the task ID in one shot for historical log fetches.

            For a historical log api, we should not wait for the task to be created.
            If the Sandbox created logs worth fetching, the task ID should be available.
            """
            ...

        async def aio(self, /) -> str:
            """Try to resolve the task ID in one shot for historical log fetches.

            For a historical log api, we should not wait for the task to be created.
            If the Sandbox created logs worth fetching, the task ID should be available.
            """
            ...

    _resolve_task_id_for_logs: ___resolve_task_id_for_logs_spec

    class ___get_command_router_client_spec(typing_extensions.Protocol):
        def __call__(self, /, task_id: str) -> modal.sandbox._task_command_router_client.TaskCommandRouterClient: ...
        async def aio(self, /, task_id: str) -> modal.sandbox._task_command_router_client.TaskCommandRouterClient: ...

    _get_command_router_client: ___get_command_router_client_spec

    @property
    def _experimental_sidecars(self) -> SidecarManager:
        """Manage sidecar containers running in this Sandbox."""
        ...

    class __exec_spec(typing_extensions.Protocol):
        @typing.overload
        def __call__(
            self,
            /,
            *args: str,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            text: typing.Literal[True] = True,
            bufsize: typing.Literal[-1, 1] = -1,
            pty: bool = False,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            _pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
        ) -> modal.container_process.ContainerProcess[str]: ...
        @typing.overload
        def __call__(
            self,
            /,
            *args: str,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            text: typing.Literal[False] = False,
            bufsize: typing.Literal[-1, 1] = -1,
            pty: bool = False,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            _pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
        ) -> modal.container_process.ContainerProcess[bytes]: ...
        @typing.overload
        async def aio(
            self,
            /,
            *args: str,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            text: typing.Literal[True] = True,
            bufsize: typing.Literal[-1, 1] = -1,
            pty: bool = False,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            _pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
        ) -> modal.container_process.ContainerProcess[str]: ...
        @typing.overload
        async def aio(
            self,
            /,
            *args: str,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            text: typing.Literal[False] = False,
            bufsize: typing.Literal[-1, 1] = -1,
            pty: bool = False,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            _pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
        ) -> modal.container_process.ContainerProcess[bytes]: ...

    exec: __exec_spec

    class ___exec_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *args: str,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            text: bool = True,
            bufsize: typing.Literal[-1, 1] = -1,
            container_id: typing.Optional[str] = None,
        ) -> typing.Union[
            modal.container_process.ContainerProcess[bytes], modal.container_process.ContainerProcess[str]
        ]:
            """Private method used internally.

            This method exposes some internal arguments (currently `pty_info`) which are not in the public API.
            """
            ...

        async def aio(
            self,
            /,
            *args: str,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            env: typing.Optional[dict[str, typing.Optional[str]]] = None,
            secrets: typing.Optional[collections.abc.Collection[modal.secret.Secret]] = None,
            text: bool = True,
            bufsize: typing.Literal[-1, 1] = -1,
            container_id: typing.Optional[str] = None,
        ) -> typing.Union[
            modal.container_process.ContainerProcess[bytes], modal.container_process.ContainerProcess[str]
        ]:
            """Private method used internally.

            This method exposes some internal arguments (currently `pty_info`) which are not in the public API.
            """
            ...

    _exec: ___exec_spec

    class ___exec_through_command_router_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *args: str,
            task_id: str,
            command_router_client: modal.sandbox._task_command_router_client.TaskCommandRouterClient,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            secret_sources: typing.Optional[collections.abc.Collection[modal_proto.api_pb2.SecretSource]] = None,
            text: bool = True,
            bufsize: typing.Literal[-1, 1] = -1,
            runtime_debug: bool = False,
            container_id: typing.Optional[str] = None,
        ) -> typing.Union[
            modal.container_process.ContainerProcess[bytes], modal.container_process.ContainerProcess[str]
        ]:
            """Execute a command through a task command router running on the Modal worker."""
            ...

        async def aio(
            self,
            /,
            *args: str,
            task_id: str,
            command_router_client: modal.sandbox._task_command_router_client.TaskCommandRouterClient,
            pty_info: typing.Optional[modal_proto.api_pb2.PTYInfo] = None,
            stdout: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            stderr: modal.stream_type.StreamType = modal.stream_type.StreamType.PIPE,
            timeout: typing.Optional[int] = None,
            workdir: typing.Optional[str] = None,
            secret_sources: typing.Optional[collections.abc.Collection[modal_proto.api_pb2.SecretSource]] = None,
            text: bool = True,
            bufsize: typing.Literal[-1, 1] = -1,
            runtime_debug: bool = False,
            container_id: typing.Optional[str] = None,
        ) -> typing.Union[
            modal.container_process.ContainerProcess[bytes], modal.container_process.ContainerProcess[str]
        ]:
            """Execute a command through a task command router running on the Modal worker."""
            ...

    _exec_through_command_router: ___exec_through_command_router_spec

    class ___experimental_snapshot_spec(typing_extensions.Protocol):
        def __call__(self, /) -> SandboxSnapshot: ...
        async def aio(self, /) -> SandboxSnapshot: ...

    _experimental_snapshot: ___experimental_snapshot_spec

    class ___experimental_from_snapshot_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            snapshot: SandboxSnapshot,
            client: typing.Optional[modal.client.Client] = None,
            *,
            name: typing.Optional[str] = modal.sandbox._sandbox._DEFAULT_SANDBOX_NAME_OVERRIDE,
        ):
            """Restore a Sandbox from a memory snapshot.

            The restore targets the same backend the snapshot was taken from. A V1
            snapshot restores as a V1 sandbox, a V2 snapshot as a V2 sandbox.
            """
            ...

        async def aio(
            self,
            /,
            snapshot: SandboxSnapshot,
            client: typing.Optional[modal.client.Client] = None,
            *,
            name: typing.Optional[str] = modal.sandbox._sandbox._DEFAULT_SANDBOX_NAME_OVERRIDE,
        ):
            """Restore a Sandbox from a memory snapshot.

            The restore targets the same backend the snapshot was taken from. A V1
            snapshot restores as a V1 sandbox, a V2 snapshot as a V2 sandbox.
            """
            ...

    _experimental_from_snapshot: typing.ClassVar[___experimental_from_snapshot_spec]

    class ___experimental_from_snapshot_v2_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            snapshot: SandboxSnapshot,
            client: modal.client.Client,
            *,
            override_type: int,
            name_override: typing.Optional[str],
        ) -> Sandbox: ...
        async def aio(
            self,
            /,
            snapshot: SandboxSnapshot,
            client: modal.client.Client,
            *,
            override_type: int,
            name_override: typing.Optional[str],
        ) -> Sandbox: ...

    _experimental_from_snapshot_v2: typing.ClassVar[___experimental_from_snapshot_v2_spec]

    @property
    def filesystem(self) -> SandboxFilesystem:
        """Namespace for Sandbox filesystem APIs."""
        ...

    @property
    def stdout(self) -> modal.io_streams.StreamReader[str]:
        """[`StreamReader`](https://modal.com/docs/sdk/py/latest/io_streams#streamreader)
        for the sandbox's stdout stream.

        Returns:
            Stream reader for sandbox stdout.
        """
        ...

    @property
    def stderr(self) -> modal.io_streams.StreamReader[str]:
        """[`StreamReader`](https://modal.com/docs/sdk/py/latest/io_streams#streamreader)
        for the Sandbox's stderr stream.

        Returns:
            Stream reader for sandbox stderr.
        """
        ...

    @property
    def stdin(self) -> modal.io_streams.StreamWriter:
        """[`StreamWriter`](https://modal.com/docs/sdk/py/latest/io_streams#streamwriter)
        for the Sandbox's stdin stream.

        Returns:
            Stream writer for sandbox stdin.
        """
        ...

    @property
    def returncode(self) -> typing.Optional[int]:
        """Return code of the Sandbox process if it has finished running, else `None`.

        Returns:
            Exit code when the sandbox process has completed, otherwise None.
        """
        ...

    class __list_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *,
            app_id: typing.Optional[str] = None,
            tags: typing.Optional[dict[str, str]] = None,
            client: typing.Optional[modal.client.Client] = None,
        ) -> typing.Generator[Sandbox, None, None]:
            """List all Sandboxes for the current Environment or App ID (if specified). If tags are specified, only
            Sandboxes that have at least those tags are returned.

            Args:
                app_id: If set, restrict results to sandboxes under this app ID.
                tags: If set, only sandboxes containing at least these tags are returned.
                client: Modal client to use for listing; defaults to `Client.from_env()` when omitted.

            Returns:
                An async generator yielding `Sandbox` objects.
            """
            ...

        def aio(
            self,
            /,
            *,
            app_id: typing.Optional[str] = None,
            tags: typing.Optional[dict[str, str]] = None,
            client: typing.Optional[modal.client.Client] = None,
        ) -> collections.abc.AsyncGenerator[Sandbox, None]:
            """List all Sandboxes for the current Environment or App ID (if specified). If tags are specified, only
            Sandboxes that have at least those tags are returned.

            Args:
                app_id: If set, restrict results to sandboxes under this app ID.
                tags: If set, only sandboxes containing at least these tags are returned.
                client: Modal client to use for listing; defaults to `Client.from_env()` when omitted.

            Returns:
                An async generator yielding `Sandbox` objects.
            """
            ...

    list: typing.ClassVar[__list_spec]

    class ___experimental_list_spec(typing_extensions.Protocol):
        def __call__(
            self,
            /,
            *,
            app_id: typing.Optional[str] = None,
            tags: typing.Optional[dict[str, str]] = None,
            client: typing.Optional[modal.client.Client] = None,
        ) -> typing.Generator[Sandbox, None, None]:
            """List all sandboxes (both v1 and v2).

            Pass `app_id` to scope to an App; without it, Sandboxes across the current
            Environment are listed (deprecated — prefer scoping by `app_id`).

            Args:
                app_id: If set, restrict results to Sandboxes under this App.
                tags: If set, only sandboxes containing at least these tags are returned.
                client: Optional client to use for the session.

            Yields:
                `Sandbox` objects that are currently running.
            """
            ...

        def aio(
            self,
            /,
            *,
            app_id: typing.Optional[str] = None,
            tags: typing.Optional[dict[str, str]] = None,
            client: typing.Optional[modal.client.Client] = None,
        ) -> collections.abc.AsyncGenerator[Sandbox, None]:
            """List all sandboxes (both v1 and v2).

            Pass `app_id` to scope to an App; without it, Sandboxes across the current
            Environment are listed (deprecated — prefer scoping by `app_id`).

            Args:
                app_id: If set, restrict results to Sandboxes under this App.
                tags: If set, only sandboxes containing at least these tags are returned.
                client: Optional client to use for the session.

            Yields:
                `Sandbox` objects that are currently running.
            """
            ...

    _experimental_list: typing.ClassVar[___experimental_list_spec]

    class ___get_log_query_data_spec(typing_extensions.Protocol):
        def __call__(self, /) -> modal._supports_logs._LogQueryData: ...
        async def aio(self, /) -> modal._supports_logs._LogQueryData: ...

    _get_log_query_data: ___get_log_query_data_spec

    @property
    def logs(self) -> modal._logs_manager.SandboxLogsManager:
        """Access logs for a `Sandbox` entrypoint.

        Useful for inspecting logs after a Sandbox terminates.
        Use [`fetch()`](#logsfetch)
        to read logs from a UTC time range, [`tail()`](#logstail)
        to read the most recent logs.

        Note that the logs from executed commands in the sandbox (via `exec()`) are not included in the
        entrypoint logs.

        See also:
            - [`modal app logs`](https://modal.com/docs/cli/latest/app#modal-app-logs):
              CLI access to logs for an App.
        """
        ...

class ___container_exec_spec(typing_extensions.Protocol):
    def __call__(
        self,
        /,
        pty: bool,
        container_id: str = "",
        command: tuple[str, ...] = (),
        sandbox_id_v2: typing.Optional[str] = None,
    ):
        """Execute a command in a container.

        For tasks belonging to V2 sandboxes, `sandbox_id_v2` may be set to the
        sandbox ID; otherwise the V2 backend is used whenever the task ID itself
        marks a V2 sandbox task.
        """
        ...

    async def aio(
        self,
        /,
        pty: bool,
        container_id: str = "",
        command: tuple[str, ...] = (),
        sandbox_id_v2: typing.Optional[str] = None,
    ):
        """Execute a command in a container.

        For tasks belonging to V2 sandboxes, `sandbox_id_v2` may be set to the
        sandbox ID; otherwise the V2 backend is used whenever the task ID itself
        marks a V2 sandbox task.
        """
        ...

_container_exec: ___container_exec_spec
