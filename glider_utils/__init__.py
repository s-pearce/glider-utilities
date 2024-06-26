import sys as _sys
from distutils.version import LooseVersion as __LV

import numpy as np

#from . import conv
from .geo import *
from .analysis import *
#import geo
from .parsers.dvl_parser import DVLparser
from .parsers.dbd_parsers import DbaDataParser
from .parsers.gliderstate_parser import GSxml
#from .parsers.dbd_parsers import DataVizDataParser

# seawater 3 uses the GSW package that only works for version 3.5 and higher
_ver = "%d.%d" % (_sys.version_info.major, _sys.version_info.minor)
if __LV(_ver) >= __LV("3.5"):
    from . import seawater3 as sw
else:
    try:
        from . import seawater2 as sw
    except ImportError:
        pass

def fwd_fill(x, init_nan_fill=None):
    """ Forward fills an array with nans, i.e. fill each nan or nan cluster with
    the preceding finite value.

    :param x: array with nan clusters to forward fill
    :param init_nan_fill: value to fill with if there are initial nans,
        defaults to back filling with the first finite value.
    :return: array x with nans forward filled
    """

    # This function assumes that the first value in the array is finite.
    # That should be accounted for.  This can be accounted for by identifying
    # nan category number 0. if there is a zero, it means it is at the start
    # of the array.
    y = x.copy()

    # first get indexes of nans
    nan_index = np.where(np.isnan(y))[0]  # assuming 1d, so take [0] index

    # create an ordinal set vector the same length as nan_index
    # i.e. (0,1,2,3,4,...)
    nanrange = range(len(nan_index))

    # subtraction basically makes a numerical category for each consecutive
    # index value

    # subtraction creates a "category" vector where each unique value
    # represents a specific sequence of nans in y, and, the number of
    # occurrences of a particular value gives the number of NaNs in that
    # particular sequence.

    # E.g.
    # x = [19.8, nan, nan, nan, 11.3, 9.3, nan, nan, nan, 7.4, nan, nan, 4.5])
    # nan_index = [1, 2, 3, 6, 7, 8, 10, 11]
    # nanrange =  [0, 1, 2, 3, 4, 5,  6,  7]; subtract nanrange from nan_index
    # nan_cats =  [1, 1, 1, 3, 3, 3,  4,  4];
    # categorical numbers represent a group of consecutive nans
    nan_cats = nan_index - nanrange

    # using np.unique creates the unique category groups, and also returns an
    # index where the first occurrence of the category group number occurs (
    # firstidx), and an array of indexes that can reproduce nan_cats from
    # uniques (restoreidx)
    uniques, firstidx, restoreidx = np.unique(nan_cats, True, True)

    # using firstidx on nan_index instead, gives the indexes of the first nan
    # in each cluster.  Subtracting those indexs by 1 gives the indexes for
    # the finite value preceeding each nan cluster.  Then simply use the
    # restoring index to repeat the preceeding finite values into an index
    # array (good_index) that is the same shape as nan_index.
    good_index = (nan_index[firstidx] - 1)[restoreidx]

    # So using x[good_index] makes an array of the preceeding good values with
    # the same repititions as the nan clusters.  Then you can reinsert that
    # repeating finite value array into where the nans were in the original
    # array using ...

    if not init_nan_fill:
        init_nan_fill = y[np.isfinite(y)][0]
    if 0 in uniques:
        y = np.append(y, init_nan_fill)

    y[nan_index] = y[good_index]

    if 0 in uniques:
        y = np.delete(y, -1)

    return y


def fwd_fill_to_new_x(oldx, newx, y):
    """forward fill y values to new x/timestamp values"""
    temp_x = list(oldx)
    temp_x.extend(list(newx))
    all_x, unique_ii, inverse_ii = np.unique(temp_x, return_index=True, return_inverse=True)
    
    temp_y = np.full_like(temp_x, np.nan)
    temp_y[0:len(oldx)] = y
    all_y = temp_y[unique_ii]
    all_y_ff = fwd_fill(all_y)
    
    temp_y_ff = all_y_ff[inverse_ii]
    y_at_new_x = temp_y_ff[len(oldx):]
    return y_at_new_x


def cluster_index(indices, ids=False):
    ordinals = np.arange(0, len(indices))
    index = indices - ordinals
    if ids:
        index_ids = np.unique(index)
        return index, index_ids
    return index


def nan_array_equal(arr1, arr2):
    finites1 = np.isfinite(arr1)
    finites2 = np.isfinite(arr2)
    aa = np.array_equal(finites1, finites2)

    nans1 = np.isnan(arr1)
    nans2 = np.isnan(arr2)
    bb = np.array_equal(nans1, nans2)

    cc = np.array_equal(arr1[finites1], arr2[finites2])

    if aa and bb and cc:
        return True
    else:
        return False


def all_sci_indices(gldata):
    """

    :param gldata: A GliderData instance
    :return:
    """
    sci_indices = np.array([], dtype=np.int64)
    for sci_sensor in DATA_CONFIG_LIST:
        sci_data = gldata.getdata(sci_sensor)
        sci_ii = np.flatnonzero(np.isfinite(sci_data))
        sci_indices = np.union1d(sci_indices, sci_ii)
    return sci_indices

# This came from Kerfoot's gncutils package.  I don't think its worth much
# without having indices that tell you which columns have been removed, but
# worth keeping as an example. I also think this should have been .all?
def clean_dataset(dataset):
    """Remove any row in dataset for which one or more columns is np.nan
    """
    # Get rid of NaNs
    dataset = dataset[~np.isnan(dataset[:, 1:]).any(axis=1), :]

    return dataset


