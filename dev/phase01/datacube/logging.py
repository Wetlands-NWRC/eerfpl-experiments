import ee
from eelib import td
from pipelines import colors, logging


def benchmark_logger(s1_imgs, s2_imgs, training_data: td.TrainingData):
    logger = logging.eeLogger
    # s1 logger
    s1log = logger.Sentinel1_Logger(s1_imgs)
    # s2 logger
    s2log = logger.Sentinel2_logger(s2_imgs)
    # training-data logger
    td_log = logger.lookup(training_data.collection,
                           training_data.label_column,
                           colors.Colors.to_eeDict())
    pass


def datacube_logger():
    # s1 logger
    # Datacube logger
    # training-data logger
    pass
