# TESS LIGHT CURVE READER
# (TRANSITING EXOPLANET SURVEY SATELLITE)

import astropy.io.fits as pyfits
import matplotlib.pyplot as plt
import math

def display_light_curve():
    fits_filename = input("FITS file:")
    error_bars = input("Error bars? (y/N):")

    if error_bars.lower() == "y":
        error_bars = True
    else:
        error_bars = False

    if not fits_filename[-4:0] == ".fits":
        fits_filename = fits_filename + ".fits"

    try:
        hdu_list = pyfits.open(fits_filename)
    except FileNotFoundError or OSError:
        print("Check FITS file name!")
        return
    
    light_curve_hdu = None

    for hdu in hdu_list:
        if hdu.name == "LIGHTCURVE":
            light_curve_hdu = hdu
            break

    # Print some basic data, not everyone needs to see all
    # the stuff in the header
    try:
        print("\nOBJECT:", hdu.header["OBJECT"])
    except KeyError:
        pass
        
    print("Celestial reference frame:", hdu.header["RADESYS"])
    print("Right ascension:", hdu.header["RA_OBJ"])
    print("Declination:", hdu.header["DEC_OBJ"])
    print("Equinox of celestial coordinate system:", hdu.header["EQUINOX"])

    date_start = hdu.header["DATE-OBS"].replace("T", " T")
    date_end = hdu.header["DATE-END"].replace("T", " T")
    print("Observation start date:", date_start)
    print("Observation end date:", date_end)

    try:
        print("\nTelescope:", hdu.header["TELESCOP"])
        print("Instrument:", hdu.header["INSTRUME"])
    except KeyError:
        pass

    light_curve_data = hdu.data

    # use better variable names
    time_list = []
    time_corr_list = []
    cadence_list = []
    sap_flux_list = []
    sap_flux_err_list = []
    sap_bkg_list = []
    sap_bkg_err_list = []

    for data_point in light_curve_data:
        time_list.append(data_point[0])
        time_corr_list.append(data_point[1])
        cadence_list.append(data_point[2])
        sap_flux_list.append(data_point[3])
        sap_flux_err_list.append(data_point[4])
        sap_bkg_list.append(data_point[5])
        sap_bkg_err_list.append(data_point[6])

    # smooth the data so we can draw an aiding curve
    
    # it's sort of data binning but uses averages and
    # not the median values
    
    smooth_factor = int(len(time_list)/250)
    rst = 0
    flux_smooth_list = []
    time_reduced_list = []
    skip_flag = False

    for i in range(0, len(time_list)-smooth_factor, smooth_factor):
        rst = 0
        for i2 in range(smooth_factor):
            divider = 0
            if not math.isnan(sap_flux_list[i+i2]):
                rst += sap_flux_list[i+i2]/smooth_factor
                divider += 1
            else:
                skip_flag = True
                break

        if not divider == 0 and not skip_flag:
            rst = rst/divider
            flux_smooth_list.append(rst)
            time_reduced_list.append(time_list[i])
        elif skip_flag:
            skip_flag = False

    if error_bars:
        plt.errorbar(time_list, sap_flux_list,\
                     yerr=sap_flux_err_list, fmt="b.")
    else:
        plt.plot(time_list, sap_flux_list, "b.")

    plt.plot(time_reduced_list, flux_smooth_list, "r-")

    plt.title(fits_filename + " Light Curve")
    plt.xlabel("Time (" + str(hdu.header["TIMEUNIT"]) + ")")
    plt.ylabel("Flux")
    plt.show()

print("TESS LIGHT CURVE READER")
display_light_curve()
