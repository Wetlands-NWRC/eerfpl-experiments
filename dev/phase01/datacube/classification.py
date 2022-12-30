from typing import Any, Dict

import ee
import factory
import yaml
from eelib import bands
from pipelines import colors, eerfpl, logging


def datacube(config):

    with open(config) as stream:
        CFG: Dict[str, Any] = yaml.safe_load(stream=stream)

    viewport_cfg = CFG.get('viewport', None)
    training_data_cfg = CFG.get('training_data', None)
    model_cfg = CFG.get('model_config', None)
    assets_cfg = CFG.get('assets')
    dc_cfg = assets_cfg.get('datacube')
    dem_cfg = assets_cfg.get('dem')

    viewport = ee.FeatureCollection.from_file(
        filename=viewport_cfg.get('file_name'),
        driver=viewport_cfg.get('driver')
    ).geometry()

    s1_imgs = factory.s1_factory(dc_cfg.get('S1'))
    dc_imgs = factory.datacube_factory(
        asset_id=dc_cfg.get('S2').get('DC'),
        viewport=viewport
    )

    dem = ee.Image(dem_cfg)

    training_data = factory.training_data(
        file_name=training_data_cfg.get('file_name'),
        driver=training_data_cfg.get('driver', None),
        layer=training_data_cfg.get('layer', None)
    )

    pipe = eerfpl.eeRFPipeline(
        sar=s1_imgs,
        optical=dc_imgs[0],
        dem=dem,
        training_data=training_data
    )

    pipe.optical_bands = [str(_.name) for _ in bands.S2SR]

    output = pipe.run()

    ############################################################################
    # Logging
    ############################################################################
    logger = logging.eeLogger

    # logging
    # Data Cube logging
    dc_tiles = logger.dct_logger(
        tileIDs=dc_imgs[1].aggregate_array('tileID'),
        system_index=dc_imgs[1].aggregate_array('system:index')
    )
    dc_dates = logger.datacube_dates()

    # Sentiel - 1 Logging
    s1_log = logger.Sentinel1_Logger(s1_imgs)

    # Training Data logging
    training_data = output.get('training_data')

    lookup = logger.lookup(
        collection=training_data.collection,
        label_col=training_data.class_labels,
        value_col=training_data.class_values,
        colors=colors.Colors.to_eeDict()
    )

    log_predictors = logger.predictors(pipe.predictors)
    b = ' '

    #

    pass


def benchmark(arg):
    pass


def datacubeLSC():
    pass


def benchmarkLSC():
    pass
