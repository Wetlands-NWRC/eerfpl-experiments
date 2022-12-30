from typing import List, Tuple

import ee
import eelib
from eelib import bands, eefuncs, sf
from pipelines import plcfgs


def s1_factory(imgs: List[str]) -> List[ee.Image]:
    # cast
    s1_imgs = [ee.Image(i) for i in imgs]
    s1_imgs = eefuncs.batch_despeckle(s1_imgs, sf.Boxcar(1))
    s1_imgs = eefuncs.batch_co_register(s1_imgs, 1)
    return s1_imgs


def s1_driv_factory(imgs: List[ee.Image]):
    ratios = eefuncs.batch_create_ratio(imgs, 'VV', 'VH')
    return ratios


def datacube_factory(asset_id: str, viewport: ee.Geometry) -> Tuple[List[ee.Image], ee.ImageCollection]:
    def set_tile_id(element: ee.Image):
        row = ee.Number(element.get('row')).format('%03d')
        col = ee.Number(element.get('col')).format('%03d')
        tile_id = row.cat(col)
        return element.set('tileID', tile_id)

    # remap bands to data cube descriptors
    CFG = plcfgs.DataCubeCfg()
    dc = ee.ImageCollection(asset_id).filterBounds(viewport).\
        map(set_tile_id).\
        select(
            selectors=CFG.src_bands,
            opt_names=CFG.dest_bands
    )

    # parse the image into spring summer fall
    s2_sr_bands = [str(_.name) for _ in bands.S2SR]
    # remap the parsed images to Sentinel - 2 SR band mappings
    dc_imgs = [dc.select(selector).mosaic()
               for selector in CFG.band_prefix.values()]
    dc_imgs = [dc_img.select(dc_img.bandNames(), s2_sr_bands) for dc_img in
               dc_imgs]
    return dc_imgs, dc


def s2_factory(imgs: List[str]) -> List[ee.Image]:
    s2_imgs = [ee.Image(img) for img in imgs]
    s2_imgs = [i.select('B.*') for i in s2_imgs]
    return s2_imgs


def s2_driv_factory(imgs: List[ee.Image]):
    savis = eefuncs.batch_create_savi(imgs)
    ndvis = eefuncs.batch_create_ndvi(imgs)
    tassels = eefuncs.batch_create_tassel_cap(imgs)
    return [*savis, *ndvis, *tassels]


def training_data(file_name, driver=None, layer=None):
    return ee.FeatureCollection.from_file(
        filename=file_name,
        driver=driver,
        layer=layer
    )


def stack():
    pass
