# -*- coding: utf-8 -*-
"""
Using machine learning to predict coastal hydrographs

Timothy Tiggeloven and Anaïs Couasnon
"""
import os
import sys

from CHNN import ANN
from CHNN import to_learning
from CHNN import performance
from CHNN import model_run

# parameters and variables
station = 'cuxhaven-cuxhaven-germany-bsh'  # 'Cuxhaven' 'Hoek van Holland', Puerto Armuelles
resample = 'hourly' # 'hourly' 'daily'
resample_method = 'rolling_mean'  # 'max' 'res_max' 'rolling_mean' ## res_max for daily and rolling_mean for hourly
variables = ['msl', 'grad', 'u10', 'v10', 'rho']  # 'grad', 'rho', 'phi', 'u10', 'v10', 'uquad', 'vquad'
tt_value = 0.67  # train-test value
scaler = 'std_normal'  # std_normal, MinMax
n_ncells = 0
epochs = 50
batch = 100
batch_normalization = False
neurons = 48
filters = 8
n_layers = 1  # now only works for uniform layers with same settings
activation = 'relu'  # 'relu', 'swish', 'Leaky ReLu', 'sigmoid', 'tanh'
loss = 'mae'  # 'mae', 'mean_squared_logarithmic_error', 'mean_squared_error'
optimizer = 'adam'  # SGD(lr=0.01, momentum=0.9), 'adam'
dropout = True
drop_value = 0.2
l1, l2 = 0, 0.01
ML = 'ANN'  # 'LSTM', 'CNN', 'ConvLSTM', 'ANN', 'ALL'
model_dir = os.path.join(os.getcwd(), 'Models')
name_model = '{}_surge_ERA5'.format(ML)
input_dir = 'Input_nc'
output_dir = 'ML_model'
figures_dir = 'Figures'
year = 'last'
frac_ensemble = 0.5

loop = 2

logger, ch = model_run.set_logger(loop, n_ncells)
model_run.ensemble(station, variables, ML, tt_value, input_dir, resample, resample_method, scaler,
                   batch, n_layers, neurons, filters, dropout, drop_value, activation, optimizer,
                   batch_normalization, loss, epochs, loop=loop, n_ncells=n_ncells, l1=l1, l2=l2,
                   frac_ens=frac_ensemble, logger=logger, verbose=0)
sys.exit(0)
