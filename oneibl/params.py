"""
Scenarios:
    - Load ONE with a cache dir: tries to load the Web client params from the dir
    - Load ONE with http address - gets cache dir from the address?

"""
import os
from ibllib.io import params as iopar
from getpass import getpass
from pathlib import Path
from ibllib.graphic import login


_PAR_ID_STR = 'one_params'
_CLIENT_ID_STR = 'web_client_params'


def default():
    par = {"ALYX_LOGIN": "test_user",
           "ALYX_PWD": "TapetesBloc18",
           "ALYX_URL": "https://test.alyx.internationalbrainlab.org",
           "CACHE_DIR": str(Path.home() / "Downloads" / "ONE"),  # TODO Remove
           "HTTP_DATA_SERVER": "https://ibl.flatironinstitute.org",
           "HTTP_DATA_SERVER_LOGIN": "iblmember",
           "HTTP_DATA_SERVER_PWD": None,
           }
    return iopar.from_dict(par)


def _get_current_par(k, par_current):
    cpar = getattr(par_current, k, None)
    if cpar is None:
        cpar = getattr(default(), k, None)
    return cpar


def setup_silent():
    par = iopar.read(_PAR_ID_STR, default())
    if par.CACHE_DIR:
        Path(par.CACHE_DIR).mkdir(parents=True, exist_ok=True)


def setup_alyx_params():
    setup_silent()
    par = iopar.read(_PAR_ID_STR).as_dict()
    [usr, pwd] = login(title='Alyx credentials')
    par['ALYX_LOGIN'] = usr
    par['ALYX_PWD'] = pwd
    iopar.write(_PAR_ID_STR, par)


# first get current and default parameters
def setup():
    par_default = default()
    par_current = iopar.read(_PAR_ID_STR, par_default)

    par = iopar.as_dict(par_default)
    for k in par.keys():
        cpar = _get_current_par(k, par_current)
        if "PWD" not in k:
            par[k] = input("Param " + k + ",  current value is [" + str(cpar) + "]:") or cpar

    cpar = _get_current_par("ALYX_PWD", par_current)
    prompt = "Enter the Alyx password for " + par["ALYX_LOGIN"] + '(leave empty to keep current):'
    par["ALYX_PWD"] = getpass(prompt) or cpar

    cpar = _get_current_par("HTTP_DATA_SERVER_PWD", par_current)
    prompt = "Enter the FlatIron HTTP password for " + par["HTTP_DATA_SERVER_LOGIN"] +\
             '(leave empty to keep current): '
    par["HTTP_DATA_SERVER_PWD"] = getpass(prompt) or cpar

    # default to home dir if empty dir somehow made it here
    if len(par['CACHE_DIR']) == 0:
        par['CACHE_DIR'] = str(Path.home() / "Downloads" / "FlatIron")

    par = iopar.from_dict(par)

    # create directory if needed
    if par.CACHE_DIR and not os.path.isdir(par.CACHE_DIR):
        os.mkdir(par.CACHE_DIR)
    iopar.write(_PAR_ID_STR, par)
    print('ONE Parameter file location: ' + iopar.getfile(_PAR_ID_STR))


def get(silent=False):
    par = iopar.read(_PAR_ID_STR, {})
    par = _patch_params(par)
    if not par and not silent:
        setup()
    elif not par and silent:
        setup_silent()
    return iopar.read(_PAR_ID_STR, default=default())


def _patch_params(old_par):
    """
    Copy over old parameters to the new cache dir based format
    :return: new parameters
    """
    if getattr(old_par, 'HTTP_DATA_SERVER_PWD', None):
        # Copy pars to cache dir
        assert old_par.CACHE_DIR
        cache_dir = Path(old_par.CACHE_DIR)
        if not cache_dir.exists():
            cache_dir.mkdir()
        new_web_client_pars = {k: v for k, v in old_par.as_dict().items() if k in default()}
        iopar.write(_CLIENT_ID_STR, new_web_client_pars)
        new_one_pars = {
            old_par.ALYX_URL: old_par.CACHE_DIR
        }
        iopar.write(_PAR_ID_STR, new_one_pars)
        return new_one_pars
    else:
        return old_par
