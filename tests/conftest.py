"""conftest for whole testsuite"""
import os
from pathlib import Path
from unittest import mock
import pytest

INSTALLER_BINARY = "openshift-install"


def mocked_get_data(_tar_url, target: str, _processor) -> str:
    """make empty installer file in a installer path"""
    i = Path(target) / INSTALLER_BINARY
    with open(i, "x", encoding="utf-8"):
        pass
    os.chmod(i, 0o0744)
    return i.as_posix()


@pytest.fixture(scope="session", autouse=True)
def patch_install_get_data():
    """mock function that downloads and unpacks install binary"""
    with mock.patch("osia.installer.downloader.install.get_data") as patched:
        patched.side_effect = mocked_get_data
        yield patched


@pytest.fixture(scope="session", autouse=True)
def patch_image_get_data():
    """mock function that downloads and unpacks coreos image"""
    with mock.patch("osia.installer.downloader.image.get_data") as patched:
        patched.side_effect = mocked_get_data
        yield patched


@pytest.fixture
def installer_version():
    """get first ga for now"""
    return "4.19.0"


@pytest.fixture
def installer_arch():
    """test for amd64"""
    return "amd64"


@pytest.fixture
def create_dummy_installer(tmp_path, installer_version):
    """make empty file in a installer path"""
    d = tmp_path / "installers"
    d.mkdir()
    v = d / installer_version
    v.mkdir()
    i = v / INSTALLER_BINARY
    with open(i, "x", encoding="utf-8"):
        pass

    return d, v, i
