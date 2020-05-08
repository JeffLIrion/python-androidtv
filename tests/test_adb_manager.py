import asyncio
from contextlib import contextmanager
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, '..')

from aio_androidtv.adb_manager import _acquire, ADBPython
from aio_androidtv.exceptions import LockNotAcquiredException

from . import patchers
from .async_wrapper import awaiter


class Read(object):
    """Mock an opened file that can be read."""
    def read(self):
        return ''


class ReadFail(object):
    """Mock an opened file that cannot be read."""
    def read(self):
        raise FileNotFoundError


PNG_IMAGE = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08\x06\x00\x00\x00\x8d2\xcf\xbd\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\tpHYs\x00\x00\x0fa\x00\x00\x0fa\x01\xa8?\xa7i\x00\x00\x00\x0eIDAT\x18\x95c`\x18\x05\x83\x13\x00\x00\x01\x9a\x00\x01\x16\xca\xd3i\x00\x00\x00\x00IEND\xaeB`\x82'

PNG_IMAGE_NEEDS_REPLACING = PNG_IMAGE[:5] + b'\r' + PNG_IMAGE[5:]

@contextmanager
def open_priv(infile):
    """A patch that will read the private key but not the public key."""
    try:
        if infile == 'adbkey':
            yield Read()
        else:
            yield ReadFail()
    finally:
        pass


@contextmanager
def open_priv_pub(infile):
    try:
        yield Read()
    finally:
        pass


class AsyncFakeLock:
    def __init__(self):
        self._acquired = True

    async def acquire(self):
        if self._acquired:
            self._acquired = False
            return True
        return self._acquired

    def release(self):
        self._acquired = True


class AsyncLockedLock(AsyncFakeLock):
    def __init__(self):
        self._acquired = False


class AsyncTimedLock(AsyncFakeLock):
    async def acquire(self):
        await asyncio.sleep(1.0)
        return await super().acquire()


class TestLock(unittest.TestCase):
    """Test the async lock code."""

    @awaiter
    async def test_succeed(self):
        lock = AsyncFakeLock()
        async with _acquire(lock):
            self.assertTrue(True)
            return
        self.assertTrue(False)

    @awaiter
    async def test_fail(self):
        lock = AsyncLockedLock()
        with self.assertRaises(LockNotAcquiredException):
            async with _acquire(lock):
                pass # self.assertTrue(False)

    @awaiter
    async def test_fail_timeout(self):
        lock = AsyncTimedLock()
        with self.assertRaises(LockNotAcquiredException):
            async with _acquire(lock, 0.1):
                pass #self.assertTrue(False)


class TestADBPython(unittest.TestCase):
    """Test the `ADBPython` class."""

    PATCH_KEY = 'python'

    def setUp(self):
        """Create an `ADBPython` instance.

        """
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY]:
            self.adb = ADBPython('HOST', 5555)

    '''@awaiter
    async def test_locked_lock(self):
        """Test that the ``FakeLock`` class works as expected.

        """
        with patch.object(self.adb, '_adb_lock', AsyncFakeLock()):
            with _acquire(self.adb._adb_lock):
                with self.assertRaises(LockNotAcquiredException):
                    with _acquire(self.adb._adb_lock):
                        pass

            with _acquire(self.adb._adb_lock) as acquired:
                self.assertTrue(acquired)'''

    @awaiter
    async def test_connect_success(self):
        """Test when the connect attempt is successful.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(await self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

    @awaiter
    async def test_connect_fail(self):
        """Test when the connect attempt fails.

        """
        with patchers.patch_connect(False)[self.PATCH_KEY]:
            self.assertFalse(await self.adb.connect())
            self.assertFalse(self.adb.available)
            self.assertFalse(self.adb._available)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(await self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

        with patchers.PATCH_CONNECT_FAIL_CUSTOM_EXCEPTION[self.PATCH_KEY]:
            self.assertFalse(await self.adb.connect())
            self.assertFalse(self.adb.available)
            self.assertFalse(self.adb._available)

    @awaiter
    async def test_connect_fail_lock(self):
        """Test when the connect attempt fails due to the lock.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patch.object(self.adb, '_adb_lock', AsyncLockedLock()):
                self.assertFalse(await self.adb.connect())
                self.assertFalse(self.adb.available)
                self.assertFalse(self.adb._available)

    @awaiter
    async def test_adb_shell_fail(self):
        """Test when an ADB shell command is not sent because the device is unavailable.

        """
        self.assertFalse(self.adb.available)
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(None)[self.PATCH_KEY]:
            self.assertIsNone(await self.adb.shell("TEST"))

        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(await self.adb.connect())
            with patch.object(self.adb, '_adb_lock', AsyncLockedLock()):
                with self.assertRaises(LockNotAcquiredException):
                    await self.adb.shell("TEST")

                with self.assertRaises(LockNotAcquiredException):
                    await self.adb.shell("TEST2")

    @awaiter
    async def test_adb_shell_success(self):
        """Test when an ADB shell command is successfully sent.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(await self.adb.connect())
            self.assertEqual(await self.adb.shell("TEST"), "TEST")

    @awaiter
    async def test_adb_shell_fail_lock_released(self):
        """Test that the ADB lock gets released when an exception is raised.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(await self.adb.connect())

        with patchers.patch_shell("TEST", error=True)[self.PATCH_KEY], patch.object(self.adb, '_adb_lock', AsyncFakeLock()):
            with patch('{}.AsyncFakeLock.release'.format(__name__)) as release:
                with self.assertRaises(Exception):
                    await self.adb.shell("TEST")
                assert release.called

    @awaiter
    async def test_adb_shell_lock_not_acquired_not_released(self):
        """Test that the lock does not get released if it is not acquired.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(await self.adb.connect())
            self.assertEqual(await self.adb.shell("TEST"), "TEST")

        with patchers.patch_shell("TEST")[self.PATCH_KEY], patch.object(self.adb, '_adb_lock', AsyncLockedLock()):
            with patch('{}.AsyncLockedLock.release'.format(__name__)) as release:
                with self.assertRaises(LockNotAcquiredException):
                    await self.adb.shell("TEST")

                release.assert_not_called()

    @awaiter
    async def test_adb_push_fail(self):
        """Test when an ADB push command is not executed because the device is unavailable.

        """
        self.assertFalse(self.adb.available)
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PUSH[self.PATCH_KEY] as patch_push:
                await self.adb.push("TEST_LOCAL_PATCH", "TEST_DEVICE_PATH")
                patch_push.assert_not_called()

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PUSH[self.PATCH_KEY] as patch_push:
                self.assertTrue(await self.adb.connect())
                with patch.object(self.adb, '_adb_lock', AsyncLockedLock()):
                    with self.assertRaises(LockNotAcquiredException):
                        await self.adb.push("TEST_LOCAL_PATH", "TEST_DEVICE_PATH")

                    patch_push.assert_not_called()

    @awaiter
    async def test_adb_push_success(self):
        """Test when an ADB push command is successfully executed.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PUSH[self.PATCH_KEY] as patch_push:
                self.assertTrue(await self.adb.connect())
                await self.adb.push("TEST_LOCAL_PATH", "TEST_DEVICE_PATH")
                self.assertEqual(patch_push.call_count, 1)

    @awaiter
    async def test_adb_pull_fail(self):
        """Test when an ADB pull command is not executed because the device is unavailable.

        """
        self.assertFalse(self.adb.available)
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PULL[self.PATCH_KEY] as patch_pull:
                await self.adb.pull("TEST_LOCAL_PATCH", "TEST_DEVICE_PATH")
                patch_pull.assert_not_called()

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PULL[self.PATCH_KEY] as patch_pull:
                self.assertTrue(await self.adb.connect())
                with patch.object(self.adb, '_adb_lock', AsyncLockedLock()):
                    with self.assertRaises(LockNotAcquiredException):
                        await self.adb.pull("TEST_LOCAL_PATH", "TEST_DEVICE_PATH")
                    patch_pull.assert_not_called()

    @awaiter
    async def test_adb_pull_success(self):
        """Test when an ADB pull command is successfully executed.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY]:
            with patchers.PATCH_PULL[self.PATCH_KEY] as patch_pull:
                self.assertTrue(await self.adb.connect())
                await self.adb.pull("TEST_LOCAL_PATH", "TEST_DEVICE_PATH")
                self.assertEqual(patch_pull.call_count, 1)

    @awaiter
    async def test_adb_screencap_fail_unavailable(self):
        """Test when an ADB screencap command fails because the connection is unavailable.

        """        
        self.assertFalse(self.adb.available)
        self.assertIsNone(await self.adb.screencap())

    @awaiter
    async def test_adb_screencap_lock_not_acquired(self):
        """Test when an ADB screencap command fails because the ADB lock could not be acquired.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell("TEST")[self.PATCH_KEY]:
            self.assertTrue(await self.adb.connect())
            self.assertEqual(await self.adb.shell("TEST"), "TEST")

        with patchers.patch_shell(PNG_IMAGE)[self.PATCH_KEY], patch.object(self.adb, '_adb_lock', AsyncLockedLock()):
            with patch('{}.AsyncLockedLock.release'.format(__name__)) as release:
                with self.assertRaises(LockNotAcquiredException):
                    await self.adb.screencap()

                release.assert_not_called()

    @awaiter
    async def test_adb_screencap_success(self):
        """Test the `screencap` method.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patchers.patch_shell(PNG_IMAGE)[self.PATCH_KEY]:
            self.assertTrue(await self.adb.connect())

            if isinstance(self.adb, ADBPython):
                self.assertEqual(await self.adb.screencap(), PNG_IMAGE)

                with patchers.patch_shell(PNG_IMAGE_NEEDS_REPLACING)[self.PATCH_KEY]:
                    self.assertEqual(await self.adb.screencap(), PNG_IMAGE)


class TestADBPythonWithAuthentication(unittest.TestCase):
    """Test the `ADBPython` class."""

    PATCH_KEY = 'python'

    def setUp(self):
        """Create an `ADBPython` instance.

        """
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY]:
            self.adb = ADBPython('HOST', 5555, 'adbkey')

    @awaiter
    async def test_connect_success_with_priv_key(self):
        """Test when the connect attempt is successful when using a private key.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patch('aio_androidtv.adb_manager.open', open_priv), patch('aio_androidtv.adb_manager.PythonRSASigner', return_value=None):
            self.assertTrue(await self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

    @awaiter
    async def test_connect_success_with_priv_pub_key(self):
        """Test when the connect attempt is successful when using private and public keys.

        """
        with patchers.patch_connect(True)[self.PATCH_KEY], patch('aio_androidtv.adb_manager.open', open_priv_pub), patch('aio_androidtv.adb_manager.PythonRSASigner', return_value=None):
            self.assertTrue(await self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)


class TestADBPythonClose(unittest.TestCase):
    """Test the `ADBPython.close` method."""

    PATCH_KEY = 'python'

    @awaiter
    async def test_close(self):
        """Test the `ADBPython.close` method.

        """
        with patchers.PATCH_ADB_DEVICE_TCP, patchers.patch_connect(True)[self.PATCH_KEY]:
            self.adb = ADBPython('HOST', 5555)

        with patchers.patch_connect(True)[self.PATCH_KEY]:
            self.assertTrue(await self.adb.connect())
            self.assertTrue(self.adb.available)
            self.assertTrue(self.adb._available)

            await self.adb.close()
            self.assertFalse(self.adb.available)
