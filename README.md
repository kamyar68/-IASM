# -IASM
Individualized Activity Space Modeller: A GIS toolbox

Requirements:
This toolbox needs ESRI ArcGIS 10.5  or above installed on the PC. ArcGIS needs advanced user license and include license for Spatial Analysis toolbox.
The toolbox (.tbx) may not be compatible with higher or lower versions of ArcGIS. However, using Arc CAtalog the Tbx file can be converted to match the applicable version of ArcGIS

Installation:
Clone the repository or download it as a zipfile to you local machine. Extract the zipfile to a desired location on your local hard disc and remember the path. Under the root  folder '-IASM-master', you can find two folders named 'My_toolboxes' and 'neighborhood_modeling_tools'. The first folder must include an ESRI toolbox file with '.tbx' extension. The second folder includes four python script files with '.py' extensions. The tools in the toolbox can be used in two ways:

  1. Using the scripts outside ArcGIS
  This method does not require any installation. You only need to open the python files from the folder 'neighborhood_modeling_tools', in your python IDE (Integrated Development Enviornment). In this method you can directly see/edit the script and directly provide parameteres using Python general guidelines. Please note, for the scripts to work you probably need to change your IDE's default Python shell to ArcGIS's Python package- python v.2.7 with pyside- (if you haven't done so before). This is the fastest method and it is recommended when intensive analyses on large datasets are performed.
Alternatively, if you do not have an IDE installed on your computer, you can open the Python files directly in ArcGIS or copy and Paste them into Arcmap's python window (Geoprocessing>Python).

  2. Using the Graphic User Interface (GUI)
  Using the GUI is a slower but easier way of using this toolbox. Using the ArcCatalog sidebar in ArcMap environment , navigate to the path where you have saved the software and open the 'My_toolboxes' folder. The folder includes an ESRI toolbox file named 'Modelin tools.tbx'. Once opened, four tools can be found in the toolbox. Double click on each of them to open and use the tool. You can also drag and drop the toolbox into Arc toolbox window for an easier future access. 
 
*Please note that the toolbox works with relative paths, so please make sure you do not rename any file or folder or move them from their relative path. 
*Please note that the toolbox is created with ArcGIS version 10.5 and it may not be compatible with some versions of ArcGIS. You can save the toolbox in a format matching your version of ArcGIS by right clicking the toolbox and clacking on save as.

Using the toolbox:
For detailed instructions on how to use each tool, please refer to the Instruction document found in Folder 'Instructions and Tutorial' on Github.
