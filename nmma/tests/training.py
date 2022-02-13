import os
import glob
import numpy as np
from scipy.interpolate import interpolate as interp

from ..em import training, utils


def parse_data(data, tt, filts):

    data_out = {}

    # Note, for this example, all phi's and theta's are the same
    # so we remove them from the list

    magkeys = data.keys()
    for jj, key in enumerate(magkeys):
        keySplit = key.split("_")

        mejdyn = float(keySplit[2].replace("mejdyn", ""))
        mejwind = float(keySplit[3].replace("mejwind", ""))
        # phi0 = float(keySplit[4].replace("phi",""))
        # theta = float(keySplit[5])

        data_out[key] = {}
        data_out[key]["log10_mej_dyn"] = np.log10(mejdyn)
        data_out[key]["log10_mej_wind"] = np.log10(mejwind)
        # data_out[key]["phi"] = phi0
        # data_out[key]["theta"] = theta

        # Interpolate data onto grid
        data_out[key]["data"] = np.zeros((len(tt), len(filts)))
        for jj, filt in enumerate(filts):
            ii = np.where(np.isfinite(data[key][filt]))[0]
            f = interp.interp1d(
                data[key]["t"][ii], data[key][filt][ii], fill_value="extrapolate"
            )
            maginterp = f(tt)
            data_out[key]["data"][:, jj] = maginterp

    return data_out


def test_training():

    # The number of PCA components we'll use to represent each lightcurve
    n_coeff = 3
    model_name = "test_model"

    # The array of times we'll use to examine each lightcurve
    tini, tmax, dt = 0.1, 5.0, 0.2
    tt = np.arange(tini, tmax + dt, dt)  #

    # The filters we'll be focusing on
    filts = [
        "g",
        "r",
    ]  # We will focus on these two bands; all available: ["u","g","r","i","z","y","J","H","K"]

    dataDir = f"{os.path.dirname(__file__)}/data/bulla"
    ModelPath = "svdmodels"
    filenames = glob.glob("%s/*.dat" % dataDir)

    data = utils.read_files(filenames)
    # Loads the model data
    training_data = parse_data(data, tt, filts)

    interpolation_type = "sklearn_gp"
    training.SVDTrainingModel(
        model_name,
        training_data,
        tt,
        filts,
        n_coeff=n_coeff,
        svd_path=ModelPath,
        interpolation_type=interpolation_type,
    )

    interpolation_type = "tensorflow"
    training.SVDTrainingModel(
        model_name,
        training_data,
        tt,
        filts,
        n_coeff=n_coeff,
        svd_path=ModelPath,
        interpolation_type=interpolation_type,
    )
