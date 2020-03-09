# nba_stats
Contains functions used to import and manipulate a database of weather statistics.

The weather data used is GHCN-daily.

Note that the GHCN-Daily dataset itself now has a DOI (Digital Object Identifier)
so it may be relevant to cite both the methods/overview journal article as well 
as the specific version of the dataset used.

The journal article describing GHCN-Daily is:
Menne, M.J., I. Durre, R.S. Vose, B.E. Gleason, and T.G. Houston, 2012:  An overview 
of the Global Historical Climatology Network-Daily Database.  Journal of Atmospheric 
and Oceanic Technology, 29, 897-910, doi:10.1175/JTECH-D-11-00103.1.

To acknowledge the specific version of the dataset used, please cite:
Menne, M.J., I. Durre, B. Korzeniewski, S. McNeal, K. Thomas, X. Yin, S. Anthony, R. Ray, 
R.S. Vose, B.E.Gleason, and T.G. Houston, 2012: Global Historical Climatology Network - 
Daily (GHCN-Daily), Version 3. [indicate subset used following decimal, 
e.g. Version 3.12]. 
NOAA National Climatic Data Center. http://doi.org/10.7289/V5D21VHZ [access date].

Download files in the following structure from https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/
 - all/
 - ghcnd-countries.txt
 - ghcnd-inventory.txt
 - ghcnd-states.txt
 - ghcnd-stations.txt
 - ghcnd-version.txt
 - ghcnd-stations.csv

The path of the directory where the data was downloaded to must be set.
To do this use function set_path function. (To import use "from weather.functions.config import set_path").
This function requires only the desired path as input.
Only needs to be set once, will be maintained on new sessions.