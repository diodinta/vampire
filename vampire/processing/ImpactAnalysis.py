import os
import regex
import datetime
import dateutil
import functools
import vampire.VampireDefaults as VampireDefaults
import vampire.directory_utils as directory_utils
import vampire.filename_utils as filename_utils


try:
    import impact_analysis_arc as impact_analysis
    import calculate_statistics_arc as calculate_statistics
except ImportError:
    import impact_analysis_os as impact_analysis
    import calculate_statistics_os as calculate_statistics


class ImpactAnalysis():
    def __init__(self):
        # load default values from .ini file
        self.vampire = VampireDefaults.VampireDefaults()
        return

    def calculate_impact_popn(self, hazard_raster, hazard_dir, hazard_pattern, threshold,
                              population_raster, boundary, b_field, output_file,
                              output_dir, output_pattern, hazard_var='vhi'):
        if threshold is None:
            # get threshold from VampireDefaults
            _threshold = self.vampire.get('hazard_impact', '{0}_threshold'.format(hazard_var))
        else:
            _threshold = threshold

        if hazard_raster is None:
            if hazard_pattern is not None:
                _input_files = directory_utils.get_matching_files(hazard_dir, hazard_pattern)
                _hazard_raster = os.path.join(hazard_dir, _input_files[0])
            else:
                raise ValueError("Hazard raster is not specified")
        else:
            _hazard_raster = hazard_raster

        if output_file is None:
            if output_pattern is not None:
                _input_pattern = self.vampire.get('MODIS_VHI', 'vhi_pattern')
                _output_file = filename_utils.generate_output_filename(os.path.basename(_hazard_raster),
                                                                       _input_pattern, output_pattern)
                _output_file = os.path.join(output_dir, _output_file)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            else:
                raise ValueError("No output specified")
        else:
            _output_file = output_file

        # reclassify hazard raster to generate mask of all <= threshold
        _reclass_raster = os.path.join(os.path.dirname(_output_file), 'hazard_popn_reclass.tif')
        impact_analysis.reclassify_raster(raster=_hazard_raster, threshold=_threshold, output_raster=_reclass_raster)

        if population_raster is None:
            _hazard_raster = _reclass_raster
        else:
            # calculate population from hazard raster and population raster intersection
            _hazard_raster = os.path.join(os.path.dirname(_output_file), 'hazard_popn.tif')
            impact_analysis.multiply_by_mask(raster=population_raster, mask=_reclass_raster,
                                             output_raster=_hazard_raster)
        # calculate impact on boundary
        calculate_statistics.calc_zonal_statistics(raster_file=_hazard_raster, polygon_file=boundary,
                                                   zone_field=b_field, output_table=_output_file)

        # add field to table and calculate total for each area
        if population_raster is None:
            impact_analysis.calc_field(table_name=_output_file, new_field='pop_aff', cal_field='COUNT', type='LONG')
        else:
            impact_analysis.calc_field(table_name=_output_file, new_field='pop_aff', cal_field='SUM', type='LONG')

        return None

    def calculate_impact_area(self, hazard_raster, hazard_dir, hazard_pattern, threshold,
                              boundary, b_field, output_file, output_dir, output_pattern, hazard_var='vhi'):
        if threshold is None:
            # get threshold from VampireDefaults
            _threshold = self.vampire.get('hazard_impact', '{0}_threshold'.format(hazard_var))
        else:
            _threshold = threshold

        if hazard_raster is None:
            if hazard_pattern is not None:
                _input_files = directory_utils.get_matching_files(hazard_dir, hazard_pattern)
                _hazard_raster = os.path.join(hazard_dir, _input_files[0])
            else:
                raise ValueError("Hazard raster is not specified")
        else:
            _hazard_raster = hazard_raster

        if output_file is None:
            if output_pattern is not None:
                _input_pattern = self.vampire.get('MODIS_VHI', 'vhi_pattern')
                _output_file = filename_utils.generate_output_filename(os.path.basename(_hazard_raster),
                                                                       _input_pattern, output_pattern)
                _output_file = os.path.join(output_dir, _output_file)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
            else:
                raise ValueError("No output specified")
        else:
            _output_file = output_file

        # reclassify hazard raster to generate mask of all <= threshold
        _reclass_raster = os.path.join(os.path.dirname(_output_file), 'hazard_area_reclass.tif')
        impact_analysis.reclassify_raster(raster=_hazard_raster, threshold=_threshold, output_raster=_reclass_raster)

        # calculate impact on boundary
        stats = calculate_statistics.calc_zonal_statistics(raster_file=_reclass_raster, polygon_file=boundary,
                                                           zone_field=b_field, output_table=_output_file)
        # convert to hectares
        # TODO: get multiplier from defaults depending on resolution of hazard raster
        impact_analysis.calc_field(_output_file, 'area_aff', 'COUNT', 6.25)

        return None