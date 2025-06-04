import os

import joblib
import lightgbm as lgb
from sklearn.pipeline import Pipeline


def load_model_pipline(modelDirPath) -> Pipeline:
    path = os.path.join(modelDirPath, 'strategy.joblib')
    mlModel: Pipeline = joblib.load(path)
    return mlModel


def load_model_lgbm(modelDirPath, fileName=None):
    fileName = fileName if fileName is not None else 'lgbmModel.txt'
    filePath = os.path.join(modelDirPath, fileName)
    mlModel_lgb = lgb.Booster(model_file=filePath)
    return mlModel_lgb
    # mlModel_lgb.feature_name()


def save_model_lgbm(modelLgbm, modelDirPath, fileName=None):
    fileName = fileName if fileName is not None else 'lgbmModel.txt'
    filePath_lgbmModel = os.path.join(modelDirPath, fileName)
    modelLgbm.booster_.save_model(filePath_lgbmModel)
