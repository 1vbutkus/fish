import os.path

from anre.utils.modeling.model.concatModel.info import Info as ConcatModelInfo
from anre.utils.modeling.model.info import Info as InfoBase
from anre.utils.modeling.model.iPersistModel import IPersistModel
from anre.utils.modeling.model.leafModel.info import Info as LeafModelInfo
from anre.utils.modeling.model.modelHub.info import Info as ModelHubInfo
from anre.utils.modeling.model.partitionModel.info import Info as PartitionModelInfo


class ModelLoader:
    @staticmethod
    def load(dirPath: str, lazyLevel: int = -1) -> IPersistModel:
        assert os.path.exists(dirPath)
        infoDict = InfoBase.load_infoDict(dirPath=dirPath)

        classId = infoDict['classId']
        if classId == LeafModelInfo.get_expectedClassId():
            from anre.utils.modeling.model.leafModel.leafModel import LeafModel

            return LeafModel.load(dirPath=dirPath)

        elif classId == PartitionModelInfo.get_expectedClassId():
            from anre.utils.modeling.model.partitionModel.partitionModel import PartitionModel

            return PartitionModel.load(dirPath=dirPath, lazyLevel=lazyLevel)

        elif classId == ConcatModelInfo.get_expectedClassId():
            from anre.utils.modeling.model.concatModel.concatModel import ConcatModel

            return ConcatModel.load(dirPath=dirPath, lazyLevel=lazyLevel)

        elif classId == ModelHubInfo.get_expectedClassId():
            from anre.utils.modeling.model.modelHub.modelHub import ModelHub

            return ModelHub.load(dirPath=dirPath, lazyLevel=lazyLevel)

        else:
            msg = f'classId(`{classId}`) is not Implemented in ModelLoader'
            raise NotImplementedError(msg)
