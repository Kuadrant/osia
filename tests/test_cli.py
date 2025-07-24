""" test of the osia.cli.main_cli function """
import sys
from dataclasses import dataclass
from unittest import mock

import pytest

from osia import cli


@pytest.mark.parametrize("args", [[], ["-v"]])
def test_help(capsys, args):
    """ test that `osia -h` contains name of the program """
    testargs = ["osia", "-h"] + args
    with pytest.raises(SystemExit) as excinfo:
        with mock.patch.object(sys, 'argv', testargs):
            cli.main_cli()

    assert excinfo.value.code == 0

    out, err = capsys.readouterr()

    assert "osia" in out
    assert err == ""


def test_no_command(capsys):
    """ test if running `osia` will result with error no install/clean """
    testargs = ["osia"]
    with mock.patch.object(sys, 'argv', testargs):
        cli.main_cli()

    out, err = capsys.readouterr()

    assert "Operation not set, please specify either install or clean!" in out
    assert "" == err


def test_resolve_installer_no_args():
    """None as arguments should raise Exception"""
    @dataclass
    class C:
        """type for cli args"""
        installer: str | None
        installer_version: str | None

    from_args = {
        "installer": None,
        "installer_version": None,
    }

    with pytest.raises(Exception, match="Either installer or installer-version must be passed"):
        _ = cli._resolve_installer(C(**from_args))  # pylint: disable=protected-access


def test_resolve_installer(create_dummy_installer):
    """if executable is passed, resolve should return the path, and download get_data should not be called"""
    _, _, i = create_dummy_installer

    @dataclass
    class C:
        """type for cli args"""
        installer: str | None

    from_args = {
        "installer": i.as_posix(),
    }

    installer_path = cli._resolve_installer(C(**from_args))  # pylint: disable=protected-access

    assert installer_path == i.as_posix()
    # TODO: assert that get_data was not called


def test_resolve_installer_from_dest_dir(create_dummy_installer, installer_version, installer_arch):
    """resolve should return the path if executable is in epected place, and download get_data should not be called"""
    dest_directory, _, i = create_dummy_installer

    @dataclass
    class C:
        """type for cli args"""
        installer: str | None
        installer_version: str
        installer_arch: str
        installers_dir: str
        installer_source: str
        enable_fips: bool

    from_args = {
        "installer": None,
        "installer_version": installer_version,
        "installer_arch": installer_arch,
        "installers_dir": dest_directory,
        "installer_source": "prod",
        "enable_fips": False,
    }

    installer_path = cli._resolve_installer(C(**from_args))  # pylint: disable=protected-access

    assert installer_path == i.as_posix()
    # TODO: assert that get_data was not called
