import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import precision_score, recall_score, fbeta_score
import performance

class Station():
    
    def __init__(self, station_name, train_test, train_X, train_Y, test_X, test_Y, val_X, val_Y, scaler, df, reframed_df, n_train_final, test_dates, test_year):
        self.train_X = train_X
        self.name = station_name
        self.train_y = train_Y
        self.test_X = test_X
        self.test_y = test_Y
        self.val_X = val_X
        self.val_y = val_Y
        self.scaler = scaler
        self.df = df
        self.reframed_df = reframed_df
        self.n_train_final = n_train_final
        self.test_dates = test_dates
        self.test_year = test_year
        self.train_test = train_test
        
        # Initialize Storage of results
        self.result_all = dict()
        self.result_all['data'] = dict()
        self.result_all['train_loss'] = dict()
        self.result_all['test_loss'] = dict()
        self.result_all['rmse'] = dict()
        self.result_all['rel_rmse'] = dict()
        self.result_all['rmse_ext'] = dict()
        self.result_all['rel_rmse_ext'] = dict()
        self.result_all['precision_ext'] = dict()
        self.result_all['recall_ext'] = dict()
        self.result_all['fbeta_ext'] = dict()
        
    def predict(self, model, ensemble_loop, mask_val):
        """Make predictions for a given station
        """
        
        # Replace masking values
        temp_df = self.test_year.replace(to_replace=mask_val, value=np.nan)[self.n_train_final:].copy()

        # make a prediction
        self.test_preds = model.predict(self.test_X)
        
        # invert scaling for observed surge
        self.inv_test_y = self.scaler.inverse_transform(temp_df.values)[:,-1]

        # invert scaling for modelled surge
        temp_df.loc[:,'values(t)'] = self.test_preds
        self.inv_test_preds = self.scaler.inverse_transform(temp_df.values)[:,-1]
        
         # Get evaluation metrics
        self.evaluate_model(ensemble_loop)
        
    def evaluate_model(self, ensemble_loop):
        """Get evaluation metrics for model predictions. RMSE, Rel_RMSE, Precision, Recall, FBeta.
        """
        # RMSE
        self.rmse = np.sqrt(mse(self.inv_test_y, self.inv_test_preds))
        self.rel_rmse = self.rmse/np.mean(self.inv_test_y)
        
        # Get the values that are deemed as extremes
        extremes = (pd.DataFrame(self.inv_test_y)
                    .nlargest(round(.10*len(self.inv_test_y)), 0) # Largest 10%
                    .sort_index())
        min_ext = extremes.iloc[:,0].min() # Minimum of Largest 10% to use as threshold lower bound
        extremes_indices = extremes.index.values
                            
        self.inv_test_y_ext = self.inv_test_y[extremes_indices]
        self.inv_test_preds_ext = self.inv_test_preds[extremes_indices]
        
        # RMSE for Extremes
        self.rmse_ext = np.sqrt(mse(self.inv_test_y_ext, self.inv_test_preds_ext))
        self.rel_rmse_ext = self.rmse_ext / self.inv_test_y.mean()
        
        # Precision and recall and fbeta score for extremes
        
        # Turn into binary classification
        ext_df = pd.DataFrame([self.inv_test_y, self.inv_test_preds], index = ['Obs', 'Pred']).T
        ext_df['Extreme_obs'] = ext_df['Obs'] >= min_ext
        ext_df['Extreme_pred'] = ext_df['Pred'] >= min_ext
        
        self.precision_ext = precision_score(ext_df['Extreme_obs'], ext_df['Extreme_pred'])
        self.recall_ext = recall_score(ext_df['Extreme_obs'], ext_df['Extreme_pred'])
        self.fbeta_ext = fbeta_score(ext_df['Extreme_obs'], ext_df['Extreme_pred'], beta=2)
        
        # Store Results
        df_all = performance.store_result(self.inv_test_preds, self.inv_test_y)
        df_all = df_all.set_index(self.df.iloc[self.test_dates,:].index, drop = True)                                                                    
        
        self.result_all['rmse'][ensemble_loop] = self.rmse
        self.result_all['rel_rmse'][ensemble_loop] = self.rel_rmse
        self.result_all['rmse_ext'][ensemble_loop] = self.rmse_ext
        self.result_all['rel_rmse_ext'][ensemble_loop] = self.rel_rmse_ext
        
        self.result_all['precision_ext'][ensemble_loop] = self.precision_ext
        self.result_all['recall_ext'][ensemble_loop] = self.recall_ext
        self.result_all['fbeta_ext'][ensemble_loop] = self.fbeta_ext
        
        self.result_all['data'][ensemble_loop] = df_all.copy()
    