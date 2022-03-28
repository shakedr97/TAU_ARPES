SESWrapper 2.7.7
----------------
SES version 1.9beta44 or newer is needed

Changes since version 2.7.6:
* Updated WRP Open Gui.vi to wait for dialog GDS_CalibrateVoltages and GDS_CalibrateDetector to close before proceeding.

Changes since version 2.7.5:
* Calls to get_property/set_property can be done to all SESInstrument.dll properties (i.e. element.MCP.CalibratedVoltage).
* New function: WRP_SaveLensTable("lenstable", "filepath"), where "lenstable" is the lens mode where the lens table should be loaded into and
  "filepath" is the path to a text file containing the element voltages. All voltages are for 1 eV pass energy, and scaled for all defined pass energies.
  Example file:
	Ek	Up	Left

	0	1	-0.025
	10	1	-0.025
  Note that the empty line is needed. Implemented in "WRP Save Lens Table.vi"
* New function: WRP_SaveInstrument(instrumentFilePath). If instrumentFilePath is empty, the loaded instrument file is updated. 
  Implemented in "WRP Save Instrument.vi"

Changes since version 2.7.4:
* Calls to get_property/set_property can be done to all SESInstrument.dll properties (i.e. element.MCP.CalibratedVoltage).
* New function: WRP_OpenGUI("name"), where "name" is in (GDS_InstallInstrument, GDS_InstallSupplies, 
	GDS_InstallElements, GDS_InstallLensModes, GDS_SetupSignals, GDS_CalibrateVoltages, GDS_CalibrateDetector, 
	GDS_ControlSupplies, GDS_SupplyInfo, GDS_DetectorInfo). Implemented in "WRP Open GUI.vi"
* New function: WRP_SetupDetector(detectorRegion). See example in sweep.vi. Implemented in "WRP Setup Detector.vi"


Changes since version 2.7.3:
* To ensure that the wrapper uses the same SESInstrument.dll, SES.ini file and instrument dat file as a specific SES installation, just set setLibWorkingDir to the SES.exe directory
  and call WRP_LoadInstrument with an empty string.

* The environmental variable SES_BASE_DIR is set when setting property setLibWorkingDir. If this property is set, there are no need to define the global environment parameter.

* WRP_LoadInstrument can be called with an empty string to open the last used instrument dat file in the SES_BASE_DIR folder.

* When intializing, an error is returned if Detector_Graph is used with the direct viewer enabled. This viewer is using QT and will crash LabView.

* The buffer size is verified when loading raw images.

* Unloads SESInstrument.dll on finalize 


Changes since version 2.7.2:

* SESWrapper now calls GDS_Start() instead of GDS_StartAcquisition() when WRP_StartAcquisition() is called.


Changes since version 2.7.1:

* Removed the use of SES_PATH_SET and setting of the PATH environment variable.

* The default value of the instrumentLibraryName_ variable has been changed to make use of
  SES_BASE_DIR if that variable is available. If SES_BASE_DIR is absent, the default value is
  now "dll\\SESInstrument.dll" which assumes that lib_working_dir has been set before
  WRP_Initialize() is called.


Changes since version 2.7.0:

* SESWrapper now makes use of the SES_PATH_SET variable to check whether SES_BASE_DIR has already been set by the user.


Changes since version 2.6.8:

* Removed the workingDir argument from WSESWrapperMain::instance() and the WSESWrapperMain and WSESWrapperBase constructors. If the working directory needs changing,
  use WRP_SetPropertyString("lib_working_dir", ...) instead. SESWrapper.dll still needs to be located in the same directory as SESInstrument.dll.


Changes since version 2.6.6:

* Now adds all subdirectories of the /dll directory to the PATH environment variable. The SES_BASE_DIR environment variable is also set at start.


Changes since version 2.6.5:

* Fixed bugs related to setting always_delay_region and allow_io_with_detector.


Changes since version 2.6.4:

* Fixed bug in WSESWrapperMain::getAcqImage()


Changes since version 2.6.3:

* Fixed bugs that could cause the host process to crash when accessing measured data.


Changes since version 2.6.2:

* Fixed bug in WSESWrapperMain::instance().

* Added function WSESWrapperMain::references().


Changes since version 2.6.1:

* The global detector settings are now read as default settings for the detector region.

* Added C function WRP_GetAnalyzerRegion.

* No longer returns false if SESInstrument.dll is already loaded when load() is called.

* When calling WSESWrapperMain::setProperty(), the "reserved" argument should now contain the size (in bytes) of the value of the property being set.
  The corresponding WRP_SetPropertyBool(), WRP_SetPropertyInteger(), WRP_SetPropertyDouble() and WRP_SetPropertyString() automatically sets that argument
  to the appropriate values.

* The WSESWrapperMain class is now a singleton with access functions instance() and release(). The number of calls to release() must match the number of
  calls to instance() for the object to be correctly destroyed. For the DLL this should not be a problem since instance() and release() are both
  called by the global DllMain() function at the appropriate occations.


Changes since version 2.6.0:

* Fixed a bug that prevented SESWrapper from functioning properly when loading the SESInstrument DLL.


Changes since version 2.5.1:

* GDS_LoadRunVar and GDS_SaveRunVar have been removed from WSESInstrument. They were never exposed by the SESWrapper API so this change will not affect client applications.

* SC_SetProperty and SC_GetProperty have been added to WSESInstrument. If a property is not recognized when calling WSESWrapperMain::setProperty or WSESWrapperMain::getProperty,
  SESWrapper will call the corresponding SESInstrument functions. This enables us to access more of the internal properties available in SESInstrument. For example, if the user wants
  to enable/disable straight slit compensation, the 'slit_compensation' property can be set. It is a boolean property residing in SESInstrument.dll.
  
* A new property has been added: instrument_library. This property allows the calling application to switch between different instrument libraries (provided they are compatible with
  the SESInstrument.dll API). For example, a suggested function sequence could be

  WRP_SetPropertyString("lib_working_dir", "C:\\SES_1.3.1");
  WRP_SetPropertyString("instrument_library", "dll\\MySESInstrument.dll");
  WRP_Initialize(0);

  which would attach SESWrapper to MySESInstrument.dll instead of the normal SESInstrument.dll. The default setting for this property is "dll\SESInstrument.dll".

* SESWrapper no longer opens the SESInstrument.dll library when it is first loaded. This is only done through a call to WRP_Initialize(0) (or SESWRapperMain::initialize(0)). The reason for this
  is that the calling application has to be given the chance to set the instrument_library property before the correct library is loaded.

* The default value of acq_current_point is now -2147483648 (lowest value of 32-bit integer numbers) instead of the previous -999999 value.

* SESWrapper no longer checks the validity of the detector region when calling WRP_SetDetectorRegion() which means that the function no longer returns an error if the specified
  detector region is invalid. The reason for this is that there are a number of other settings that need to be set before a proper check can be made. The following function
  sequence shows a more appropriate way to accomplish this (the example assumes binding energies):

    bool useBindigEnergy = true;
    double excitationEnergy;
    char lensMode[32];
    double passEnergy;
    SESWrapperNS::WAnalyzerRegion region;
    SESWrapperNS::WDetectorRegion detector;
  
    // Initialize the variables here.
  
    WRP_SetPropertyBool("use_binding_energy", &useBindingEnergy);
    WRP_SetPropertyString("lens_mode", lensMode);
    WRP_SetPropertyDouble("pass_energy", &passEnergy);
    WRP_SetExcitationEnergy(excitationEnergy);
    WRP_SetAnalyzerRegion(&region);
    WRP_SetDetectorRegion(&detector);

    // Now we can verify the new region:
    SESWrapperNS::WAnalyzerRegion testRegion;
    int steps;
    double time_ms;
    double energyStep;
    int result = WRP_CheckAnalyzerRegion(&testRegion, int *steps, double *time_ms, double *energyStep);
    if (result != 0)
    {
      SESWrapperNS::WDetectorRegion testDetector;
      WRP_GetDetectorRegion(&testDetector);
    }


Changes since version 2.5.0:

* Fixed a bug that reset the use_binding_energy property whenever the analyzer region was set. The same bug also set the
  excitation energy to 0.


Changes since version 2.4.3:

* Added functions WRP_SetExcitationEnergy() and WRP_GetExcitationEnergy(), WRP_SetBindingEnergy() and WRP_GetBindingEnergy().

* Added property use_binding_energy. If set to true, the energies specified in the analyzer region struct are treated as binding energies.
  To use binding energies, you also need to set the excitation energy.
  
* Added properties element_name_count and element_name, which can be used to obtain a list of available voltage element names.


Changes since version 2.4.2:

* Updated the LabVIEW example VIs.


Changes since version 2.4.1:

* Added read-only variables acq_current_point, acq_point_intensity and acq_channel_intensity to obtain a single
  point from the acquired spectrum. This is useful during swept mode acquisitions to avoid unnecessary copying
  of data. The acq_current_point variable obtains the point index of the latest step taken and can then be used to
  request the corresponding intensity from the accumulated spectrum. This replaces the acq_current_step
  variable. acq_current_step still exists for backward compatibility.
  
  C Example:
  
  ...
  int point;
  int slices;
  WRP_WaitForPointReady(-1); // This is required to get a reliable value of p.
                             // Note that p is negative until the first channel has been completed
  WRP_GetAcquiredDataInteger("acq_current_point", 0, &point, 0);
  WRP_GetAcquiredDataInteger("acq_slices", 0, &slices, 0);
  double intensity = 0;
  double *channel = new double[slices];
  if (point >= 0)
  {
    WRP_GetAcquiredDataDouble("acq_point_intensity", point, &intensity, 0);
    WRP_GetAcquiredDataVectorDouble("acq_channel_intensity", point, channel, 0);
  }


Changes since version 2.4.0:

* Corrected a race condition between pointReady() and waitForPointReady().


Changes since version 2.3.2:

* A problem in SESInstrument has required the GDS_StartAcquisition() to be disabled and replaced by a call to the
  GDS_Start() function. This will be corrected in a future release.

* A new property has been introduced to allow SES support of spin detectors. The property (called 'use_spin')
  is a boolean value.

* Fixed a bug that caused SESWrapper to crash when calling the getters for "element_set" or "lens_mode" with string
  address 0.

Changes since version 2.3.1:

* The previous release did not ship with the correct SESWrapper DLL version. This has now been addressed.

* Added a Library Information box in the Sweep VI example to indicate the current version of SESWrapper DLL. This was done for
the obvious reason shown above.

Changes since version 2.2.1:

* Removed properties element_set_from_index, lend_mode_from_index and pass_energy_from_index. The element_set, lend_mode
  and pass_energy properties now make use of the index parameter. If index is -1, the current element_set, lens_mode
  or pass_energy is read/modified. If index is between 0 and element_set_count, lens_mode_count or pass_energy_count, the
  name or value for that index is read. For example, if you want to set the lens mode to Transmission, you could call
  
  WRP_SetProperty("lens_mode", -1, "Transmission");

  or, to find out which lens modes are available, this example shows how it can be done in C/C++:

  int count = 0;
  int size = 0;
  WRP_GetProperty("lens_mode_count", 0, &count, &size);
  for (int i = 0; i < count; i++)
  {
    char buffer[256];
    size = 256;
    WRP_GetProperty("lens_mode", i, buffer, &size);
    std::cout << buffer << std::endl;
  }
  WRP_GetProperty("lens_mode", -1, buffer, &size);
  std::cout << "Current lens mode: " << buffer << std::endl;

* Added function validate() (exported as WRP_Validate), which should be used to validate the combination of the given
  element set, lens mode and pass energy. The function also includes a kinetic energy argument, which is currently ignored.
  Use this function to check whether a certain pass energy is available for a given lens mode.

* Modified the LabVIEW Sweep.vi example to make use of the new index syntax for element sets, lens modes
  and pass energies (described above).


Changes since version 2.1.1:

* Updated the documentation by adding a page ("Coding Examples") that gives an example of how to create a C/C++
  application that converts SESWrapper.dll into an executable.

* Added two functions for setting/retrieving properties with the void* argument type. These functions are not
  included in the LabVIEW parts of the package.

* Updated the appearance of the Sweep VI and related VIs.


Changes since version 2.1.0:

* A new property has been added: reset_data_between_iterations. If this is set to 1, the data is automatically
  cleared between each call to WRP_StartAcquisition. This minimizes the need to call WRP_InitAcquisition to set
  up a new acquisition.

* The energy scale shown in the image in the Sweep.vi example has been removed. The scale was erroneously showing
  Kinetic energy, but that information could not be imported to that sub-VI.

Changes since version 2.0.1:

* SESWrapper now tries to load and initialize the SESInstrument library automatically on startup. On
  exit, the library then also makes finalization automatically. This removes the need to call WRP_Initialize
  and WRP_Finalize, and allows the owning application to select any working directory during execution.
  This requires SESWrapper.dll to be in the same directory as SESInstrument.dll, and the libraries must also
  be in the dll\ directory of the SES software.

* The Sweep.vi example has been modified according to the above change to the library.

* A bug has been corrected that made it impossible to set the temp_file_name property. This property has no
  direct impact on the general operation of the library, but can be used to gain access to the temporary file
  generated during acquisitions.
  
* Each time an error occurs in the SESInstrument library, an error string is logged in the seswrapper.log file.
  This has now been improved by also adding the date and time of the error. The file is never cleared, and can be
  used for trouble reporting. Normal operation does not generate any text in the file, and if it is deleted, a new
  file is created when necessary. The file is normally saved in the current working directory.

Changes since version 1.0.2:

* SESWrapper now requires version 1.2.5 of the SES software. A number of problems have been corrected
  which has required the removal of legacy support (SES 1.2.2).

* The WRP_LoadConfig() and WRP_SaveConfig() functions were never used and have been removed.

* The properties and data parameters have been completely redesigned to improve performance
  and the readability of the source code. Internally they now use individual callbacks ("setters"
  and "getters"). This in turn has resulted in a major overhaul of the SESWrapper Developer's
  Guide.

* The index parameter found in the WRP_SetProperty were sometimes used inconsitently. This
  parameter has now been renamed to "reserved" and should not be used in the current version of
  SESWrapper WRP_SetProperty... functions. Properties "element_set_from_index", "lens_mode_from_index"
  and "pass_energy_from_index" now correctly uses the "value" parameter to set the corresponding
  value. The value in this case would be an index from the available values in the element set,
  lens mode or pass energy lists. To set an element set, lens mode or pass energy directly by its
  name/value (e.g. "Transmission" for the lens mode), use the "lens_mode" property instead,
  with the WRP_SetPropertyString function.

* A number of small bugs have been fixed, including a problem with the WRP_CheckAnalyzerRegion function
  which resulted in the loss of correct lens mode and pass energy at certain points of execution.

* The Sweep.vi example VI has been redesigned to improve performance and usability. However, it is
  important to remember that this is only an example, and should not be assumed to be a complete
  application.

* A new property has been added: "temp_file_name". This property is set through the WRP_SetPropertyString
  function, and should contain the name of the temporary file used during acquisition of one spectrum. It is possible to use this string (which can contain an absolute path) later on to convert the temporary file to e.g. an Igor file by using one of our file interface DLLs.

* A new property has been added: "region_name". This property is optional and will not affect much of the
  operation of SESWrapper, but adds to the internal structure used to communicate with the SESInstrument library.
