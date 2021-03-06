$python = "C:\Python27\python.exe"
$processing_script = "c:\PRISM\scripts\vampire\prism_process.py"

$ref_date = (Get-Date).AddDays(-16)
#$ref_date = [DateTime]'2017-07-29'
#get year from last month
$YEARNOW = ($ref_date).Year
echo $YEARNOW

#get month from last month
$MONTHNOW = (($ref_date).Month).ToString("00")
echo $MONTHNOW

$start_year = "$YEARNOW-01-01"
$time_span = ($ref_date) - [DateTime]($start_year)
$16days = ($time_span.Days)/16
$remainder = ($time_span.Days)%16
if ($remainder -ne 0) {
  $16day_date = ($ref_date).AddDays(-$remainder)
} else {
  $16day_date = $ref_date
}
$YEARNOW = $16day_date.Year
$MONTHNOW = ($16day_date.Month).ToString("00")
$DAYNOW = ($16day_date.Day).ToString("00")
echo $time_span
echo "ref_date:" $ref_date
echo "remainder:" $remainder
echo "16Day Date:" $16day_date
$16day_end = ($16day_date).AddDays(15)
$YEAREND = $16day_end.Year
$MONTHEND = ($16day_end.Month).ToString("00")
$DAYEND = ($16day_end.Day).ToString("00")

$valid_from = ($16day_date).AddDays(-15)
$valid_YEAR = $valid_from.Year
$valid_MONTH = ($valid_from.Month).ToString("00")
$valid_DAY = ($valid_from.Day).ToString("00")
echo $valid_from

#check if the final tif (lka_phy_MOD13Q1.$YEARNOW$MONTHNOW$DAYNOW.250m_16_days_EVI_EVI_VCI_VHI.tif) already exist
$vhi_geoserver_path = "C:\PRISM\data\Geoserver\data_dir\data\vhi\lka_phy_MOD13Q1.$YEARNOW$MONTHNOW$DAYNOW.250m_16_days_EVI_EVI_VCI_VHI.tif"
echo $vhi_geoserver_path
if (Test-Path $vhi_geoserver_path) {
  echo "File exists"
}
Else {
  echo "VHI for $YEARNOW-$MONTHNOW-$DAYNOW does not exist yet. Try processing."
  & $python $processing_script -c "Sri Lanka" -p vhi -o c:\PRISM\configs\config_vhi_current.yml -d $YEARNOW-$MONTHNOW-$DAYNOW -t $valid_YEAR-$valid_MONTH-$valid_DAY
#  & $python $processing_script -c "Sri Lanka" -p vhi -o c:\PRISM\configs\config_vhi_current.yml -d $YEARNOW-$MONTHNOW-$DAYNOW -t $YEAREND-$MONTHEND-$DAYEND
}
