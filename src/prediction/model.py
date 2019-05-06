"""
A Model to contain classifiers, regressors, etc
"""
import os
import sys
import pandas as pd
from pdb import set_trace
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import LinearSVC
from sklearn.decomposition import PCA
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from pathlib import Path
from typing import Tuple
from sklearn.base import clone
from imblearn.under_sampling import EditedNearestNeighbours

root = Path(os.path.abspath(os.path.join(os.getcwd().split("src")[0], 'src')))
if root not in sys.path:
    sys.path.append(str(root))

from metrics.abcd import ABCD


class PredictionModel:
    def __init__(self, classifier: str = "XGBoost") -> None:
        self._set_classifier(classifier)

    def _set_classifier(self, classifier: str) -> None:
        if classifier == "SVC":
            self.clf = LinearSVC(C=0.01, penalty="l1", dual=False)
        elif classifier == "RF":
            self.clf = RandomForestClassifier()
        elif classifier == "XGBoost":
            self.clf = XGBClassifier()

    @staticmethod
    def _binarize(dframe: pd.DataFrame) -> pd.DataFrame:
        """
        Turn the dependent variable column to a binary class

        Parameters
        ----------
        dframe: pandas.core.frame.DataFrame
            A pandas dataframe with independent and dependent variable columns

        Return
        ------
        dframe: pandas.core.frame.DataFrame
            The orignal dataframe with binary dependent variable columns
        """
        dframe.loc[dframe[dframe.columns[-1]] > 0, dframe.columns[-1]] = 1
        dframe.loc[dframe[dframe.columns[-1]] == 0, dframe.columns[-1]] = 0
        return dframe

    def predict_defects(self,
                        train: pd.DataFrame,
                        test: pd.DataFrame,
                        oversample: bool = True,
                        binarize: bool = True) -> Tuple[list, list]:
        """
        Predict for Defects

        Parameters
        ----------
        train: numpy.ndarray or pandas.core.frame.DataFrame
            Training dataset as a pandas dataframe
        test: pandas.core.frame.DataFrame
            Test dataset as a pandas dataframe
        oversample: Bool
            Oversample with SMOTE
        binarize: Bool
            A boolean variable to

        Return
        ------
        actual: numpy.ndarray
            Actual defect counts
        predicted: numpy.ndarray
            Predictied defect counts
        """

        if binarize:
            train = self._binarize(train)
            test = self._binarize(test)

        x_train = train[train.columns[:-1]].values
        y_train = train[train.columns[-1]].values
        
        # pca = PCA(n_components=3)
        # pca.fit(x_train)
        # x_train = pca.transform(x_train)
        # x_train = model.transform(x_train)
        
        if oversample:
            k = min(2, sum(y_train) - 1)
            # sm = SMOTE(kind='regular', k_neighbors=k)
            sm = EditedNearestNeighbours()
            x_train, y_train = sm.fit_sample(x_train, y_train)
        
        lsvc = clone(self.clf, safe=True)
        lsvc.fit(x_train, y_train)
        model = SelectFromModel(lsvc, prefit=True)
        x_train = model.transform(x_train)
        # set_trace()
        # pca = PCA(n_components=3)
        # pca.fit(x_train)
        # x_train = pca.transform(x_train)
        self.clf.fit(x_train, y_train)
        actual = test[test.columns[-1]].values.astype(int)
        x_test = test[test.columns[:-1]]
        x_test = model.transform(x_test)
        # x_test = pca.transform(x_test)
        predicted = self.clf.predict(x_test).astype(int)
        return actual, predicted
