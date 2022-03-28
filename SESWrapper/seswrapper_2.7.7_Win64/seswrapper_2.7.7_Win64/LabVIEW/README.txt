SesWrapper README
-----------------

This directory ("SesWrapper\LabVIEW") contains the LabVIEW specific files related to the SesWrapper library.
All files have been created for LabVIEW 8.5, which means that backward compatibility
to LabVIEW 7 and earlier is not guaranteed. It may be possible to import the SesWrapper.dll
functions manually under earlier versions, but the VIs available as examples (including
the SesWrapper VI library itself) will most likely not work.

There should not be any problem with the location of the VIs (LabVIEW usually asks the user
to specify locations of files not found). However, the SESInstrument.dll,
which SesWrapper wraps, expects a certain directory structure for the Scienta
SES software:

<base path>
  \data
  \dll
  \docs
  \ini

where the base path can be e.g. "D:\Ses-1.2.6". This path should be updated through
the lib_working_dir property (it is updated by the Initialize VI found in the
examples directory).
