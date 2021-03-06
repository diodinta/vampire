import processing.CHIRPSProcessor
import processing.MODISProcessor
import processing.RasterProcessor
import processing.ClimateAnalysis
import processing.ImpactAnalysis
import processing.raster_utils as raster_utils
import yaml

class ConfigFileError(ValueError):
    def __init__(self, message, e, *args):
        '''Raise when the config file contains an error'''
        self.message = message
        self.error = e
        super(ConfigFileError, self).__init__(message, e, *args)

class ConfigProcessor():

    def _process_CHIRPS(self, process, cfg, logger=None):
        try:
            output_dir = process['output_dir']
        except Exception, e:
            raise ConfigFileError("No ouput directory 'output_dir' specified.", e)
        cp = processing.CHIRPSProcessor.CHIRPSProcessor()
        if process['type'] == 'download':
            _dates = None
            _start_date = None
            _end_date = None
            _overwrite = False
            if 'dates' in process:
                _dates = process['dates']
            if 'start_date' in process:
                _start_date = process['start_date']
            if 'end_date' in process:
                _end_date = process['end_date']
            if 'overwrite' in process:
                _overwrite = True
            cp.download_data(output_dir, process['interval'], dates=_dates, start_date=_start_date,
                             end_date=_end_date, overwrite=_overwrite)
        elif process['type'] == 'longterm_average':
            if 'dates' in process:
                dates = process['dates']
            try:
                input_dir = process['input_dir']
            except Exception, e:
                raise ConfigFileError("No input directory 'input_dir' specified.", e)

            if 'functions' in process:
                funcs = process['functions']
            else:
                funcs = ['AVG']

            if 'file_pattern' in process:
                pattern = process['file_pattern']
            else:
                pattern = None

            cp.calculate_longterm_stats(process['interval'], input_dir, output_dir, pattern=pattern,
                                        function_list=funcs)
        else:
            raise ConfigFileError('Unknown CHIRPS process type {0}'.format(process['type']))
        return None

    def _process_MODIS(self, process, cfg, logger=None):
        mp = processing.MODISProcessor.MODISProcessor()
        if process['type'] == 'download':
            if logger: logger.debug("Downloading MODIS data")
            try:
                output_dir = process['output_dir']
            except Exception, e:
                raise ConfigFileError("No output directory specified. An 'output_dir' is required.")
            # default product is MOD13A3
            _product = 'MOD13A3.005'
            if 'product' in process:
                _product = process['product']
            # default to no tiles
            _tiles = None
            if 'tiles' in process:
                _tiles = process['tiles']
            _dates = None
            if 'dates' in process:
                _dates = process['dates']
            _mosaic_dir = None
            if 'mosaic_dir' in process:
                _mosaic_dir = process['mosaic_dir']
            _mrt_dir = None
            if 'MRT_dir' in process:
                _mrt_dir = process['MRT_dir']
            if 'overwrite' in process:
                _overwrite = True
            mp.download_data(output_dir=output_dir, product=_product, tiles=_tiles,
                             dates=_dates, mosaic_dir=_mosaic_dir)
        elif process['type'] == 'extract':
            if logger: logger.debug("Extract layer from MODIS data")
            try:
                _input_dir = process['input_dir']
            except Exception, e:
                raise ConfigFileError("No input directory 'input_dir' set.")
            try:
                _output_dir = process['output_dir']
            except Exception, e:
                raise ConfigFileError("No output directory 'output_dir' set.")
            if 'file_pattern' in process:
                _file_pattern = process['file_pattern']
            else:
                _file_pattern = None
            if 'output_pattern' in process:
                _output_pattern = process['output_pattern']
            else:
                _output_pattern = None
            if 'product' in process:
                _product = process['product']
            else:
                _product = None
            if process['layer'] == 'NDVI':
                mp.extract_NDVI(_input_dir, _output_dir, _file_pattern, _output_pattern, _product)
            elif process['layer'] == 'EVI':
                mp.extract_EVI(_input_dir, _output_dir, _file_pattern, _output_pattern, _product)
            elif process['layer'] == 'LST_Day' or process['layer'] == 'LST_Night':
                mp.extract_LST(_input_dir, _output_dir, _file_pattern, _output_pattern, process['layer'], _product)
        elif process['type'] == 'calc_average':
            if 'layer' in process:
                if process['layer'] == 'day_night_temp':
                    if logger: logger.debug("Calculate Average temperature from Day & Night for files matching pattern")
                    day_dir = process['lst_day_dir']
                    night_dir = process['lst_night_dir']
                    output_dir = process['output_dir']
                    if 'file_pattern' in process:
                        input_pattern = process['file_pattern']
                    else:
                        input_pattern = None
                    if 'output_pattern' in process:
                        output_pattern = process['output_pattern']
                    else:
                        output_pattern = None
                    patterns = (input_pattern, output_pattern)
                    mp.match_day_night_files(day_dir, night_dir, output_dir, patterns)
                elif process['layer'] == 'long_term_statistics':
                    if logger: logger.debug("Calculate long-term statistics for files matching pattern")
                    try:
                        _input_dir = process['input_dir']
                    except Exception, e:
                        raise ConfigFileError("No input directory 'input_dir' set.")
                    try:
                        _output_dir = process['output_dir']
                    except Exception, e:
                        raise ConfigFileError("No output directory 'output_dir' set.")
                    try:
                        _product = process['product']
                    except Exception, e:
                        raise ConfigFileError("No product 'product' set.")
                    try:
                        _input_pattern = process['file_pattern']
                    except Exception, e:
                        raise ConfigFileError("No input file pattern 'file_pattern' set.")
                    if 'country' in process:
                        _country = process['country']
                    else:
                        _country = None
                    if 'output_pattern' in process:
                        _output_pattern = process['output_pattern']
                    else:
                        _output_pattern = None
                    if 'start_date' in process:
                        _start_date = process['start_date']
                    else:
                        _start_date = None
                    if 'end_date' in process:
                        _end_date = process['end_date']
                    else:
                        _end_date = None
                    if 'functions' in process:
                        _function_list = process['functions']
                    else:
                        _function_list = None
                    if 'interval' in process:
                        _interval = process['interval']
                    else:
                        _interval = None
                    mp.calc_longterm_stats(input_dir=_input_dir, output_dir=_output_dir, product=_product,
                                           interval=_interval, country=_country,
                                           input_pattern=_input_pattern, output_pattern=_output_pattern,
                                           start_date=_start_date, end_date=_end_date, function_list=_function_list)

        return None

    def _process_analysis(self, process, cfg, logger=None):
        ca = processing.ClimateAnalysis.ClimateAnalysis()
        if process['type'] == 'rainfall_anomaly':
            if logger: logger.debug("Compute monthly rainfall anomaly")
            cur_file = None
            lta_file = None
            out_file = None
            cur_pattern = None
            lta_pattern = None
            output_pattern = None
            cur_dir = None
            lta_dir = None
            output_dir = None
            if 'current_file' in process:
                cur_file = process['current_file']
            else:
                if not 'current_file_pattern' in process:
                    raise ConfigFileError("No current file 'current_file' or pattern 'current_file_pattern' specified.", None)
                else:
                    if 'current_dir' in process:
                        cur_dir = process['current_dir']
                    else:
                        cur_dir = None

                    cur_pattern = process['current_file_pattern']

            # try:
            #     cur_file = process['current_file']
            # except Exception, e:
            #     raise ConfigFileError("No current file 'current_file' specified.", e)
            if 'longterm_avg_file' in process:
                lta_file = process['longterm_avg_file']
            else:
                if not 'longterm_avg_file_pattern' in process:
                    raise ConfigFileError("No long term average file 'longterm_avg_file' or pattern 'longterm_avg_file_pattern' specified.", None)
                else:
                    if 'longterm_avg_dir' in process:
                        lta_dir = process['longterm_avg_dir']
                    else:
                        lta_dir = None
                    lta_pattern = process['longterm_avg_file_pattern']
#            try:
#                lta_file = process['longterm_avg_file']
#            except Exception, e:
#                raise ConfigFileError("No long term average file 'longterm_avg_file' specified.", e)
            if 'output_file' in process:
                out_file = process['output_file']
            else:
                if not 'output_file_pattern':
                    raise  ConfigFileError("No output file 'output_file' or output pattern 'output_file_pattern' specified.", None)
                else:
                    if 'output_dir' in process:
                        output_dir = process['output_dir']
                    else:
                        output_dir = None
                    output_pattern = process['output_file_pattern']
#            try:
#                out_file = process['output_file']
#            except Exception, e:
#                raise ConfigFileError("No output file 'output_file' specified.", e)

            ca.calc_rainfall_anomaly(cur_filename=cur_file, lta_filename=lta_file,
                                     cur_dir=cur_dir, lta_dir=lta_dir,
                                     cur_pattern=cur_pattern, lta_pattern=lta_pattern,
                                     dst_filename=out_file, dst_pattern=output_pattern, dst_dir=output_dir )
        elif process['type'] == 'SPI':
            if logger: logger.debug("Compute standardized precipitation index")
            cur_file = None
            lta_file = None
            ltsd_file = None
            out_file = None
            cur_pattern = None
            lta_pattern = None
            ltsd_pattern = None
            output_pattern = None
            cur_dir = None
            lta_dir = None
            ltsd_dir = None
            output_dir = None
            if 'current_file' in process:
                cur_file = process['current_file']
            else:
                if not 'current_file_pattern' in process:
                    raise ConfigFileError("No current file 'current_file' or pattern 'current_file_pattern' specified.", None)
                else:
                    if 'current_dir' in process:
                        cur_dir = process['current_dir']
                    else:
                        cur_dir = None

                    cur_pattern = process['current_file_pattern']

            if 'longterm_avg_file' in process:
                lta_file = process['longterm_avg_file']
            else:
                if not 'longterm_avg_file_pattern' in process:
                    raise ConfigFileError("No long term average file 'longterm_avg_file' or pattern 'longterm_avg_file_pattern' specified.", None)
                else:
                    if 'longterm_avg_dir' in process:
                        lta_dir = process['longterm_avg_dir']
                    else:
                        lta_dir = None
                    lta_pattern = process['longterm_avg_file_pattern']

            if 'longterm_sd_file' in process:
                ltsd_file = process['longterm_sd_file']
            else:
                if not 'longterm_sd_file_pattern' in process:
                    raise ConfigFileError("No long term standard deviation file 'longterm_sd_file' or pattern 'longterm_sd_file_pattern' specified.", None)
                else:
                    if 'longterm_sd_dir' in process:
                        ltsd_dir = process['longterm_sd_dir']
                    else:
                        ltsd_dir = None
                    ltsd_pattern = process['longterm_sd_file_pattern']

            if 'output_file' in process:
                out_file = process['output_file']
            else:
                if not 'output_file_pattern':
                    raise  ConfigFileError("No output file 'output_file' or output pattern 'output_file_pattern' specified.", None)
                else:
                    if 'output_dir' in process:
                        output_dir = process['output_dir']
                    else:
                        output_dir = None
                    output_pattern = process['output_file_pattern']

            ca.calc_standardized_precipitation_index(cur_filename=cur_file, lta_filename=lta_file,
                                                     ltsd_filename=ltsd_file,
                                                     cur_dir=cur_dir, lta_dir=lta_dir, ltsd_dir=ltsd_dir,
                                                     cur_pattern=cur_pattern, lta_pattern=lta_pattern,
                                                     ltsd_pattern=ltsd_pattern,
                                                     dst_filename=out_file, dst_pattern=output_pattern,
                                                     dst_dir=output_dir )

        elif process['type'] == 'days_since_last_rain':
            if logger: logger.debug("Compute Days Since Last Rain")
            if 'input_dir' in process:
                _input_dir = process['input_dir']
            else:
                _input_dir = None
            if 'output_dir' in process:
                _output_dir = process['output_dir']
            else:
                _output_dir = None
            if 'file_pattern' in process:
                _file_pattern = process['file_pattern']
            else:
                _file_pattern = None
            if 'threshold' in process:
                _threshold = process['threshold']
            else:
                _threshold = None
            if 'max_days' in process:
                _max_days = process['max_days']
            else:
                _max_days = None
            if 'start_date' in process:
                _start_date = process['start_date']
            ca.calc_days_since_last_rainfall(data_dir=_input_dir, data_pattern=_file_pattern,
                                             dst_dir=_output_dir, start_date=_start_date,
                                             threshold=_threshold, max_days=_max_days)

        elif process['type'] == 'VCI':
            _cur_file = None
            _cur_dir = None
            _cur_pattern = None
            _evi_max_file = None
            _evi_min_file = None
            _evi_max_dir = None
            _evi_min_dir = None
            _evi_max_pattern = None
            _evi_min_pattern = None
            _output_file = None
            _output_dir = None
            _output_pattern = None

            if logger: logger.debug("Compute Vegetation Condition Index")
            if 'current_file' in process:
                _cur_file = process['current_file']
            else:
                if not 'current_file_pattern' in process:
                    raise ConfigFileError("No current file 'current_file' or pattern 'current_file_pattern' specified.", None)
                else:
                    if 'current_dir' in process:
                        _cur_dir = process['current_dir']
                    else:
                        _cur_dir = None

                    _cur_pattern = process['current_file_pattern']
            if 'EVI_max_file' in process:
                _evi_max_file = process['EVI_max_file']
            else:
                if not 'EVI_max_pattern' in process:
                    raise ConfigFileError("No EVI long-term maximum file 'EVI_max_file' or pattern 'EVI_max_pattern' specified.", None)
                else:
                    if 'EVI_max_dir' in process:
                        _evi_max_dir = process['EVI_max_dir']
                    else:
                        _evi_max_dir = None
                    _evi_max_pattern = process['EVI_max_pattern']

            if 'EVI_min_file' in process:
                _evi_min_file = process['EVI_min_file']
            else:
                if not 'EVI_min_pattern' in process:
                    raise ConfigFileError("No EVI long-term minimum file 'EVI_min_file' or pattern 'EVI_min_pattern' specified.", None)
                else:
                    if 'EVI_min_dir' in process:
                        _evi_min_dir = process['EVI_min_dir']
                    else:
                        _evi_min_dir = None
                    _evi_min_pattern = process['EVI_min_pattern']
            if 'output_file' in process:
                _output_file = process['output_file']
            else:
                if not 'output_file_pattern':
                    raise  ConfigFileError("No output file 'output_file' or output pattern 'output_file_pattern' specified.", None)
                else:
                    if 'output_dir' in process:
                        _output_dir = process['output_dir']
                    else:
                        _output_dir = None
                    _output_pattern = process['output_file_pattern']
            ca.calc_vci(cur_filename=_cur_file, cur_dir=_cur_dir, cur_pattern=_cur_pattern,
                        evi_max_filename=_evi_max_file, evi_max_dir=_evi_max_dir, evi_max_pattern=_evi_max_pattern,
                        evi_min_filename=_evi_min_file, evi_min_dir=_evi_min_dir, evi_min_pattern=_evi_min_pattern,
                        dst_filename=_output_file, dst_dir=_output_dir, dst_pattern=_output_pattern)

        elif process['type'] == 'TCI':
            if logger: logger.debug("Compute Temperature Condition Index")
            _cur_file = None
            _cur_dir = None
            _cur_pattern = None
            _lst_max_file = None
            _lst_min_file = None
            _lst_max_dir = None
            _lst_min_dir = None
            _lst_max_pattern = None
            _lst_min_pattern = None
            _output_file = None
            _output_dir = None
            _output_pattern = None
            _interval = None

            if logger: logger.debug("Compute Temperature Condition Index")
            if 'current_file' in process:
                _cur_file = process['current_file']
            else:
                if not 'current_file_pattern' in process:
                    raise ConfigFileError("No current file 'current_file' or pattern 'current_file_pattern' specified.", None)
                else:
                    if 'current_dir' in process:
                        _cur_dir = process['current_dir']
                    else:
                        _cur_dir = None

                    _cur_pattern = process['current_file_pattern']
            if 'LST_max_file' in process:
                _lst_max_file = process['LST_max_file']
            else:
                if not 'LST_max_pattern' in process:
                    raise ConfigFileError("No LST long-term maximum file 'LST_max_file' or pattern 'LST_max_pattern' specified.", None)
                else:
                    if 'LST_max_dir' in process:
                        _lst_max_dir = process['LST_max_dir']
                    else:
                        _lst_max_dir = None
                    _lst_max_pattern = process['LST_max_pattern']

            if 'LST_min_file' in process:
                _lst_min_file = process['LST_min_file']
            else:
                if not 'LST_min_pattern' in process:
                    raise ConfigFileError("No LST long-term minimum file 'LST_min_file' or pattern 'LST_min_pattern' specified.", None)
                else:
                    if 'LST_min_dir' in process:
                        _lst_min_dir = process['LST_min_dir']
                    else:
                        _lst_min_dir = None
                    _lst_min_pattern = process['LST_min_pattern']
            if 'output_file' in process:
                _output_file = process['output_file']
            else:
                if not 'output_file_pattern':
                    raise  ConfigFileError("No output file 'output_file' or output pattern 'output_file_pattern' specified.", None)
                else:
                    if 'output_dir' in process:
                        _output_dir = process['output_dir']
                    else:
                        _output_dir = None
                    _output_pattern = process['output_file_pattern']
            if 'interval' in process:
                _interval = process['interval']

            ca.calc_tci(cur_filename=_cur_file, cur_dir=_cur_dir, cur_pattern=_cur_pattern,
                        lst_max_filename=_lst_max_file, lst_max_dir=_lst_max_dir, lst_max_pattern=_lst_max_pattern,
                        lst_min_filename=_lst_min_file, lst_min_dir=_lst_min_dir, lst_min_pattern=_lst_min_pattern,
                        dst_filename=_output_file, dst_dir=_output_dir, dst_pattern=_output_pattern, interval=_interval
                        )

        elif process['type'] == 'VHI':
            if logger: logger.debug("Compute Vegetation Health Index")
            _vci_file = None
            _vci_dir = None
            _vci_pattern = None
            _tci_file = None
            _tci_dir = None
            _tci_pattern = None
            _out_file = None
            _output_dir = None
            _output_pattern = None

            if 'VCI_file' in process:
                _vci_file = process['VCI_file']
            else:
                if not 'VCI_pattern' in process:
                    raise ConfigFileError("No VCI file 'VCI_file' or pattern 'VCI_pattern' specified.", None)
                else:
                    if 'VCI_dir' in process:
                        _vci_dir = process['VCI_dir']
                    else:
                        _vci_dir = None
                    _vci_pattern = process['VCI_pattern']
            if 'TCI_file' in process:
                _tci_file = process['TCI_file']
            else:
                if not 'TCI_pattern' in process:
                    raise ConfigFileError("No TCI file 'TCI_file' or pattern 'TCI_pattern' specified.", None)
                else:
                    if 'TCI_dir' in process:
                        _tci_dir = process['TCI_dir']
                    else:
                        _tci_dir = None
                    _tci_pattern = process['TCI_pattern']
            if 'output_file' in process:
                _out_file = process['output_file']
            else:
                if not 'output_pattern' in process:
                    raise ConfigFileError("No output file 'output_file' or pattern 'output_pattern' specified.", None)
                else:
                    if 'output_dir' in process:
                        _output_dir = process['output_dir']
                    else:
                        _output_dir = None
                    _output_pattern = process['output_pattern']

            ca.calc_vhi(vci_filename=_vci_file, vci_dir=_vci_dir, vci_pattern=_vci_pattern,
                        tci_filename=_tci_file, tci_dir=_tci_dir, tci_pattern=_tci_pattern,
                        dst_filename=_out_file, dst_dir=_output_dir, dst_pattern=_output_pattern)

        return None

    def _process_raster(self, process, cfg, logger=None):
        rp = processing.RasterProcessor.RasterProcessor()
        if process['type'] == 'crop':
            if logger: logger.debug("Crop raster data to boundary")

            if 'file_pattern' in process:
                _pattern = process['file_pattern']
            else:
                _pattern = None
            if 'output_pattern' in process:
                _out_pattern = process['output_pattern']
            else:
                _out_pattern = None
            if 'overwrite' in process:
                _overwrite = True
            else:
                _overwrite = False
            if 'no_data' in process:
                _no_data = True
            else:
                _no_data = False

            try:
                _input_dir = process['input_dir']
            except Exception, e:
                raise ConfigFileError("No input directory 'input_dir' set.", e)
            try:
                _output_dir = process['output_dir']
            except Exception, e:
                raise ConfigFileError("No output directory 'output_dir' set.", e)
            try:
                _boundary_file = process['boundary_file']
            except Exception, e:
                raise ConfigFileError("No boundary file specified." ,e)
            rp.crop_files(input_dir=_input_dir, output_dir=_output_dir, boundary_file=_boundary_file,
                          file_pattern=_pattern, output_pattern=_out_pattern, overwrite=_overwrite,
                          nodata=_no_data, logger=logger)
        elif process['type'] == 'match_projection':
            if logger: logger.debug("Reproject file to same extent and resolution as master")
            _master_filename = None
            _slave_filename = None
            _master_dir = None
            _master_pattern = None
            _slave_dir = None
            _slave_pattern = None
            _output_file = None
            _output_dir = None
            _output_pattern = None

            if 'master_file' in process:
                _master_filename = process['master_file']
            else:
                if not 'master_dir' in process:
                    raise ConfigFileError("No master file 'master_file' or pattern 'master_pattern'/directory 'master_dir' specified.", None)
                else:
                    _master_dir = process['master_dir']
                    _master_pattern = process['master_pattern']
            if 'slave_file' in process:
                _slave_filename = process['slave_file']
            else:
                if not 'slave_dir' in process:
                    raise ConfigFileError("No slave file 'slave_file' or pattern 'slave_pattern'/directory 'slave_dir' specified.", None)
                else:
                    _slave_dir = process['slave_dir']
                    _slave_pattern = process['slave_pattern']

            if 'output_file' in process:
                _output_file = process['output_file']
            else:
                if not 'output_pattern' in process:
                    raise ConfigFileError("No output filename 'output_file' or output pattern 'output_pattern' specified.", None)
                else:
                    _output_pattern = process['output_pattern']
                    _output_dir = process['output_dir']

            rp.match_projection(master_file=_master_filename, master_dir=_master_dir, master_pattern=_master_pattern,
                                slave_file=_slave_filename, slave_dir=_slave_dir, slave_pattern=_slave_pattern,
                                output_file=_output_file, output_dir=_output_dir, output_pattern=_output_pattern)

        elif process['type'] == 'zonal_statistics':
            if logger: logger.debug("Calculate zonal statistics as a table from raster and polygon")
            _raster_filename = None
            _polygon_filename = None
            _raster_dir = None
            _raster_pattern = None
            _polygon_dir = None
            _polygon_pattern = None
            _output_file = None
            _output_dir = None
            _output_pattern = None
            _zone_field = None

            if 'raster_file' in process:
                _raster_filename = process['raster_file']
            else:
                if not 'raster_dir' in process:
                    raise ConfigFileError("No raster file 'raster_file' or pattern 'raster_pattern'/directory 'raster_dir' specified.", None)
                else:
                    _raster_dir = process['raster_dir']
                    _raster_pattern = process['raster_pattern']
            if 'polygon_file' in process:
                _polygon_filename = process['polygon_file']
            else:
                if not 'polygon_dir' in process:
                    raise ConfigFileError("No polygon file 'polygon_file' or pattern 'polygon_pattern'/directory 'polygon_dir' specified.", None)
                else:
                    _polygon_dir = process['polygon_dir']
                    _polygon_pattern = process['polygon_pattern']

            if 'output_file' in process:
                _output_file = process['output_file']
            else:
                if not 'output_pattern' in process:
                    raise ConfigFileError("No output filename 'output_file' or output pattern 'output_pattern' specified.", None)
                else:
                    _output_pattern = process['output_pattern']
                    _output_dir = process['output_dir']

            if 'zone_field' in process:
                _zone_field = process['zone_field']
            else:
                raise ConfigFileError("No zone field specified", None)

            rp.calc_zonal_statistics(raster_file=_raster_filename, raster_dir=_raster_dir, raster_pattern=_raster_pattern,
                                polygon_file=_polygon_filename, polygon_dir=_polygon_dir, polygon_pattern=_polygon_pattern,
                                output_file=_output_file, output_dir=_output_dir, output_pattern=_output_pattern,
                                zone_field=_zone_field)
        elif process['type'] == 'apply_mask':
            if logger: logger.debug("Apply shapefile mask to raster")
            _raster_filename = None
            _polygon_filename = None
            _raster_dir = None
            _raster_pattern = None
            _polygon_dir = None
            _polygon_pattern = None
            _output_file = None
            _output_dir = None
            _output_pattern = None

            if 'raster_file' in process:
                _raster_filename = process['raster_file']
            else:
                if not 'raster_dir' in process:
                    raise ConfigFileError("No raster file 'raster_file' or pattern 'raster_pattern'/directory 'raster_dir' specified.", None)
                else:
                    _raster_dir = process['raster_dir']
                    _raster_pattern = process['raster_pattern']
            if 'polygon_file' in process:
                _polygon_filename = process['polygon_file']
            else:
                if not 'polygon_dir' in process:
                    raise ConfigFileError("No polygon file 'polygon_file' or pattern 'polygon_pattern'/directory 'polygon_dir' specified.", None)
                else:
                    _polygon_dir = process['polygon_dir']
                    _polygon_pattern = process['polygon_pattern']

            if 'output_file' in process:
                _output_file = process['output_file']
            else:
                if not 'output_pattern' in process:
                    raise ConfigFileError("No output filename 'output_file' or output pattern 'output_pattern' specified.", None)
                else:
                    _output_pattern = process['output_pattern']
                    _output_dir = process['output_dir']
            if 'no_data' in process:
                _no_data = True
            else:
                _no_data = False

            rp.mask_by_shapefile(raster_file=_raster_filename, raster_dir=_raster_dir, raster_pattern=_raster_pattern,
                                 polygon_file=_polygon_filename, polygon_dir=_polygon_dir, polygon_pattern=_polygon_pattern,
                                 output_file=_output_file, output_dir=_output_dir, output_pattern=_output_pattern,
                                 nodata=_no_data, logger=logger)

        # elif process['type'] == 'average_files':
        #     if logger: logger.debug("Compute average of raster files")
        #
        #     if 'file_pattern' in process:
        #         _pattern = process['file_pattern']
        #     else:
        #         _pattern = None
        #     if 'output_pattern' in process:
        #         _out_pattern = process['output_pattern']
        #     else:
        #         _out_pattern = None
        #     try:
        #         _input_dir = process['input_dir']
        #     except Exception, e:
        #         raise ConfigFileError("No input directory 'input_dir' set.", e)
        #     try:
        #         _output_dir = process['output_dir']
        #     except Exception, e:
        #         raise ConfigFileError("No output directory 'output_dir' set.", e)
        #     rp.average_files(input_dir=_input_dir, input_pattern=_pattern,
        #                      output_dir=_output_dir, output_pattern=_out_pattern)
        return None
    #

    def _process_impact(self, process, cfg, logger=None):
        ia = processing.ImpactAnalysis.ImpactAnalysis()
        if 'start_date' in process:
            _start_date = process['start_date']
        else:
            _start_date = None

        if 'end_date' in process:
            _end_date = process['end_date']
        else:
            _end_date = None

        if process['type'] == 'area':
            if logger: logger.debug("Compute area of event impact")

            _hazard_pattern = None
            _hazard_dir = None
            _hazard_file = None
            _output_file = None
            _output_dir = None
            _output_pattern = None
            if 'hazard_file' in process:
                _hazard_file = process['hazard_file']
            elif 'hazard_pattern' in process:
                _hazard_dir = process['hazard_dir']
                _hazard_pattern = process['hazard_pattern']
            else:
                raise ConfigFileError('No hazard filename "hazard_file" or hazard dir/pattern "hazard_dir / hazard_pattern" set', None)

            if 'boundary_file' in process:
                _boundary_file = process['boundary_file']
            else:
                raise ConfigFileError('No boundary file "boundary_file" provided', None)

            if 'boundary_field' in process:
                _boundary_field = process['boundary_field']
            else:
                _boundary_field = None

            if 'output_file' in process:
                _output_file = process['output_file']
            elif 'output_pattern' in process:
                _output_dir = process['output_dir']
                _output_pattern = process['output_pattern']
            else:
                raise ConfigFileError('No output file "output_file" or output directory/pattern "output_dir/output_pattern" specified', None)

            if 'hazard_threshold' in process:
                _threshold = process['hazard_threshold']
            else:
                _threshold = None

            ia.calculate_impact_area(hazard_raster=_hazard_file, hazard_dir=_hazard_dir, hazard_pattern=_hazard_pattern,
                                     boundary=_boundary_file, b_field=_boundary_field, threshold=_threshold,
                                     output_file=_output_file, output_dir=_output_dir, output_pattern=_output_pattern,
                                     start_date=_start_date, end_date=_end_date)
        elif process['type'] == 'crops':
            if logger: logger.debug("Compute area of affected crops")

            _hazard_pattern = None
            _hazard_dir = None
            _hazard_file = None
            _output_file = None
            _output_dir = None
            _output_pattern = None
            _crop_pattern = None
            _crop_dir = None
            _crop_file = None
            if 'hazard_file' in process:
                _hazard_file = process['hazard_file']
            elif 'hazard_pattern' in process:
                _hazard_dir = process['hazard_dir']
                _hazard_pattern = process['hazard_pattern']
            else:
                raise ConfigFileError('No hazard filename "hazard_file" or hazard dir/pattern "hazard_dir / hazard_pattern" set', None)

            if 'boundary_file' in process:
                _boundary_file = process['boundary_file']
            else:
                raise ConfigFileError('No boundary file "boundary_file" provided', None)

            if 'boundary_field' in process:
                _boundary_field = process['boundary_field']
            else:
                _boundary_field = None

            if 'output_file' in process:
                _output_file = process['output_file']
            elif 'output_pattern' in process:
                _output_dir = process['output_dir']
                _output_pattern = process['output_pattern']
            else:
                raise ConfigFileError('No output file "output_file" or output directory/pattern "output_dir/output_pattern" specified', None)

            if 'hazard_threshold' in process:
                _threshold = process['hazard_threshold']
            else:
                _threshold = None

            if 'crop_boundary' in process:
                _crop_file = process['crop_boundary']
            elif 'crop_pattern' in process:
                _crop_dir = process['crop_dir']
                _crop_pattern = process['crop_pattern']
            else:
                raise ConfigFileError('No crop boundary file "crop_boundary" or crop directory/pattern "crop_dir/crop_pattern" specified', None)

            if 'crop_field' in process:
                _crop_field = process['crop_field']
            else:
                _crop_field = None


            ia.calculate_impact_crops(hazard_raster=_hazard_file, hazard_dir=_hazard_dir, hazard_pattern=_hazard_pattern,
                                     crop_boundary=_crop_file, crop_dir=_crop_dir, crop_pattern=_crop_pattern,
                                     crop_field=_crop_field, threshold=_threshold,
                                     admin_boundary=_boundary_file, admin_boundary_field=_boundary_field,
                                     output_file=_output_file, output_dir=_output_dir, output_pattern=_output_pattern,
                                     start_date=_start_date, end_date=_end_date)
        elif process['type'] == 'population':
            if logger: logger.debug("Compute population affected by event")

            _hazard_pattern = None
            _hazard_dir = None
            _hazard_file = None
            if 'hazard_file' in process:
                _hazard_file = process['hazard_file']
            elif 'hazard_pattern' in process:
                _hazard_dir = process['hazard_dir']
                _hazard_pattern = process['hazard_pattern']
            else:
                raise ConfigFileError('No hazard filename "hazard_file" or hazard dir/pattern "hazard_dir / hazard_pattern" set', None)

            _population_pattern = None
            _population_dir = None
            _population_file = None
            if 'population_file' in process:
                _population_file = process['population_file']
            elif 'population_pattern' in process:
                _population_dir = process['population_dir']
                _population_pattern = process['population_pattern']
            else:
                raise ConfigFileError('No population filename "population_file" or population dir/pattern "population_dir / population_pattern" set', None)

            if 'boundary_file' in process:
                _boundary_file = process['boundary_file']
            else:
                raise ConfigFileError('No boundary file "boundary_file" provided', None)

            if 'boundary_field' in process:
                _boundary_field = process['boundary_field']
            else:
                _boundary_field = None

            _output_file = None
            _output_dir = None
            _output_pattern = None
            if 'output_file' in process:
                _output_file = process['output_file']
            elif 'output_pattern' in process:
                _output_dir = process['output_dir']
                _output_pattern = process['output_pattern']
            else:
                raise ConfigFileError('No output file "output_file" specified', None)

            if 'hazard_threshold' in process:
                _threshold = process['hazard_threshold']
            else:
                _threshold = None

            ia.calculate_impact_popn(hazard_raster=_hazard_file, hazard_dir=_hazard_dir, hazard_pattern=_hazard_pattern,
                                     population_raster=_population_file,
                                     boundary=_boundary_file, b_field=_boundary_field, threshold=_threshold,
                                     output_file=_output_file, output_dir=_output_dir, output_pattern=_output_pattern,
                                     start_date=_start_date, end_date=_end_date)
        elif process['type'] == 'poverty':
            if logger: logger.debug("Compute poor population affected by event")
            _hazard_pattern = None
            _hazard_dir = None
            _hazard_file = None
            if 'hazard_file' in process:
                _hazard_file = process['hazard_file']
            elif 'hazard_pattern' in process:
                _hazard_dir = process['hazard_dir']
                _hazard_pattern = process['hazard_pattern']
            else:
                raise ConfigFileError('No hazard filename "hazard_file" or hazard dir/pattern "hazard_dir / hazard_pattern" set', None)
            _hazard_field = None
            if 'hazard_field' in process:
                _hazard_field = process['hazard_field']
            if 'hazard_area_code' in process:
                _hazard_match_field = process['hazard_area_code']
            else:
                _hazard_match_field = None
            _poverty_pattern = None
            _poverty_dir = None
            _poverty_file = None
            if 'poverty_file' in process:
                _poverty_file = process['poverty_file']
            elif 'poverty_pattern' in process:
                _poverty_dir = process['poverty_dir']
                _poverty_pattern = process['poverty_pattern']
            else:
                raise ConfigFileError('No poverty filename "poverty_file" or poverty dir/pattern "poverty_dir / poverty_pattern" set', None)
            if 'poverty_field' in process:
                _poverty_field = process['poverty_field']
            else:
                _poverty_field = None
            if 'poverty_area_code' in process:
                _poverty_match_field = process['poverty_area_code']
            else:
                _poverty_match_field = None
            if 'poverty_multiplier' in process:
                _poverty_multiplier = process['poverty_multiplier']
            else:
                _poverty_multiplier = None

            _output_file = None
            _output_dir = None
            _output_pattern = None
            if 'output_file' in process:
                _output_file = process['output_file']
            elif 'output_pattern' in process:
                _output_dir = process['output_dir']
                _output_pattern = process['output_pattern']
            else:
                raise ConfigFileError('No output file "output_file" specified', None)
            if 'output_field' in process:
                _output_field = process['output_field']
            else:
                _output_field = None


            ia.calculate_impact_poverty(impact_file=_hazard_file, impact_dir=_hazard_dir,
                                        impact_pattern=_hazard_pattern, impact_field=_hazard_field,
                                        impact_match_field=_hazard_match_field,
                                        poor_file=_poverty_file, poor_field=_poverty_field,
                                        poor_match_field=_poverty_match_field, poor_multiplier=_poverty_multiplier,
                                        output_file=_output_file, output_dir=_output_dir,
                                        output_pattern=_output_pattern, output_field=_output_field,
                                        start_date=_start_date, end_date=_end_date)

        return None


    def process_config(self, config, logger=None):

        global options, args
        try:
            if config:
                # parse config file
                with open(config, 'r') as ymlfile:
                    cfg = yaml.load(ymlfile)
            else:
                print "no config"
                if logger:
                    logger.error("A config file is required. Please specify a config file on the command line.")
                return -1
        except Exception, e:
            if logger:
                logger.error("Cannot load config file.")
            raise ConfigFileError('no run in cfg',e)

        if not 'run' in cfg:
            print "Error in cfg!!"
        _process_list = cfg['run']
        if logger:
            logger.debug(_process_list)

        for i,p in enumerate(_process_list):
            try:
                if p['process'].upper() == 'CHIRPS':
                    print "Processing CHIRPS data"
                    self._process_CHIRPS(p, cfg, logger)
            except Exception, e:
                ConfigFileError("running process CHIRPS", e)
                raise
            try:
                if p['process'].upper() == 'MODIS':
                    print "Processing MODIS data"
                    self._process_MODIS(p, cfg, logger)
            except Exception, e:
                ConfigFileError("running process MODIS", e)
                raise
            try:
                if p['process'].lower() == 'analysis':
                    print "Performing data analysis"
                    self._process_analysis(p, cfg, logger)
            except Exception, e:
                ConfigFileError("performing data analysis", e)
                raise
            try:
                if p['process'].lower() == 'raster':
                    print "Performing raster analysis"
                    self._process_raster(p, cfg, logger)
            except Exception, e:
                ConfigFileError("performing raster analysis", e)
                raise
            try:
                if p['process'].lower() == 'impact':
                    print "Performing impact analysis"
                    self._process_impact(p, cfg, logger)
            except Exception, e:
                ConfigFileError('performing impact analysis', e)

        return None