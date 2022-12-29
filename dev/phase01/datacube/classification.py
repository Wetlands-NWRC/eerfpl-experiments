from typing import Any, Dict

import ee
import factory
import yaml
from eelib import bands
from pipelines import eerfpl, logging


def datacube(config):

    def set_tileid(element):
        pass

    with open(config) as stream:
        CFG: Dict[str, Any] = yaml.safe_load(stream=stream)

    viewport_cfg = CFG.get('viewport', None)
    training_data_cfg = CFG.get('training_data', None)
    model_cfg = CFG.get('model_config', None)
    assets_cfg = CFG.get('assets').get('datacube')

    viewport = ee.FeatureCollection.from_file(
        filename=viewport_cfg.get('file_name'),
        driver=viewport_cfg.get('driver')
    ).geometry()

    s1_imgs = factory.s1_factory(assets_cfg.get('S1'))
    dc_imgs = factory.datacube_factory(
        asset_id=assets_cfg.get('S2').get('DC'),
        viewport=viewport
    )

    training_data = factory.training_data(
        file_name=training_data_cfg.get('file_name'),
        driver=training_data_cfg.get('driver', None),
        layer=training_data_cfg.get('layer', None)
    )

    pipe = eerfpl.eeRFPipeline(
        sar=s1_imgs,
        optical=dc_imgs,
        dem=None,
        training_data=training_data
    )

    pipe.optical_bands = [str(_.name) for _ in bands.S2SR]

    pipe.run()

    model = eerfpl.RandomForest(
        n_trees=1000
    )
    model.train(
        featues=training_data,
        class_label='land_cover_values',
        predictors=stack.bandNames()
    )

    classify = stack.classify(model.model)
    pass


def benchmark(arg):
    pass


def datacubeLSC():
    pass


def benchmarkLSC():
    pass
