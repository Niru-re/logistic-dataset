Each box contains 14 mango fruits and weighs 5 kg.
There is a partition separating the fruits into 2 groups of 7 fruits.
In a Unit Load Device (ULD) containing 148 cartons, thirty-one instrumented cartons were placed at different positions to observe spatial and temporal temperature variations during 12 h cruising. 
In total, there are 342 files corresponding to the recorded data from 62 sensors (measuring mango temperature, air temperature, and relative humidity) across 11 steps in the supply chain. Specifically, there are 31 files corresponding to these boxes: 10 boxes at the top, 9 boxes at mid-height, 7 boxes at the bottom, and 5 boxes in intermediate positions, all containing the measurements. Additionally, there are 310 files for each step. It should be noted that some sensors recorded only temperature, while others recorded both temperature and relative humidity.
At the destination, mango quality attributes were assessed at different time-points during 15-day storage at 16.1 °C and 21.6 °C

Descriptive statistics for all instrumented boxes:
For temperature and humidity values:

iButtons: A dedicated software was used to read values, which were then saved in .txt files.
The raw data from these .txt files were segmented for analysis.
The raw values were processed to generate graphs, means, minimums, maximums, and standard deviations.
Measurement uncertainties and instruments (folder 14):
Temperature: Recorded at 5-minute intervals with a resolution of 0.5°C using iButtons (models "DS1922L" and "DS1923"). Data were read via OneWireViewer and saved as .txt files. The uncertainty was ±0.6°C (k = 2).
Relative humidity: Measured with the iButton model DS1923, with an uncertainty of ±5% RH (k = 2).
Mass (M): Measured with a KERN PRS 4200-2 balance, with an uncertainty of U(M)=0.008g + 4.19⋅* 10^−5⋅* R (k = 2, R = reading value).
Color: Measured using a spectrophotometer CM-700d at six positions per fruit (avec une moyenne sur 3 mesures, une par seconde), with an uncertainty of ±0.2 (k = 2).
Total Soluble Solid (TSS): Measured using a refractometer PAL-BrixAcid1 with an uncertainty of ±0.4% °Bx (k = 2).
pH value: Recorded with a digital meter Starter 300, with an uncertainty of ±0.03 pH (k = 2).
All data were stored as .txt files.

For the colorimeter values, the operator recorded the measurements directly into an .xls (Excel) file during the process. These raw measurements were later transferred to .txt files for further processing.
For the pH values, the raw measurements were first recorded in an Excel file and subsequently saved in .txt format.
For the TSS values, the raw measurements were similarly recorded in an Excel file and later converted to .txt format.
All summary statistical data tables were formatted as .html, .csv, or .txt files.
Graphs showing the averages for all boxes or mangoes, based on the phase of their journey, were created and stored in the "res" folders.

File name:

The file name of recorded temperature and relative humidity is formatted as "Step number"_"Step name"_"Box position"_Temp_Hum.txt. This format provides information of the step in the supply chain, the box position, and the type of recorded data i.e. temperature, relative humidity.

Example 1: The file "0_Packing_House_1_1_1_Temp_Hum.txt” denotes data from the step 0 called packing house for box (1, 1, 1) and the file contains the recorded temperature and relative humidity.

Example 2: The file "3_Storage_BKK_Platform_3_3_12_Temp” represents data from the step 3 called Storage BKK Platform for box (3, 3, 12), containing only temperature measurements without recorded relative humidity.

Example 3: The file "00_All_Recording_Packing_House_to_Arrival_At_INRAE_3_1_12_Temp” contains recorded temperature in all steps from the packing house to the arrival at INRAE for box (3, 1, 12).
The data in these files, considered raw values, are stored as .txt files in the folder named "01_src_subset_dataset_T_H."

The measured quality change in different storage days: D0 (April 18, 2023), D3, D6, D9, D12, and D15 (May 5, 2023) at 16°C and 21°C are also stored in txt files. These quality data (mass, color, TSS, pH, mango photo), considered as raw value, are in the folders named "03_src_subset_dataset_quality attribute" to "11_src_subset_dataset_quality attribute" (19 files in total). The min, max, average values, standard deviation and variance considered as processed data, are stored in folders named "04_res_subset_dataset_quality attribute" to "12_res_subset_dataset_quality attribute”. As for temperature and relative humidity presented above, the R scripts used.

This naming system allows differentiation of files based on several key attributes:

Configuration number: The configuration number (e.g., "1_" or "2_") at the beginning of the file name indicates which configuration the data belongs to. This makes it easy to identify the corresponding configuration for each file.

Attribute Measurement: The measured attribute is specified (e.g., "Weight" for weight). This indicates the type of data recorded in the file.

Storage Temperature: The storage temperature is mentioned in the file name (e.g., "21C" for 21 degrees Celsius).

Box Position: In some files, a box position is provided (e.g., "_1_1_1" or "_random"). This gives additional information about the location or arrangement of the mangoes measurements.

The boxes were selected across four configurations, the configurations are indicated by the numbers at the beginning of the file names:

"1_" Corresponds to boxes chosen from extreme positions within the container at 21°C.
"2_" Corresponds to boxes selected randomly from non-extreme positions within the container at 21°C.
"3_" Corresponds to randomly selected mangoes from any box in the storage, without regard to the position of the box in the container, at 21°C.
"4_" Corresponds to randomly selected mangoes from any box in the storage, without regard to the position of the box in the container, at 16°C.
We remind you of the storage temperature values for each case: "1_" (21°C), "2_"  (21°C), "3_" (21°C), and "4_" (16°C), as these are part of the researchers' experimental design.

In the folder 03_src_subset_dataset_W:
The file name of recorded weight is formatted as "Configuration number”_"Attribute Measurement”_"storage temperature”_"Box position”.txt.

Example 1: the file "1_Weight_21C_1_1_1" corresponds to configuration 1, contains weight measurements taken at a storage temperature of 21°C, and specifies a box position of (1, 1, 1).

Example 2: the file "2_Weight_21C_random" : corresponds to configuration 2, contains weight measurements taken at a storage temperature of 21°C, and specifies the boxes selected randomly.
This numbering system is consistent across all files to specify the corresponding configuration.

In the folder 03_src_subset_dataset_W:
The file name of recorded weight is formatted as "Configuration number"_"Quality attribute"_"storage temperature"_"Box position".txt.

Example 1: In the files 1_Weight_21C_1_1_1:
M_1_1_1/1: Refers to the mango (M) at position (1, 1, 1) and the first (/1) mango selected from the box.

Example 2: In the folder 04_res_subset_dataset_W:
M_1_1_1.1: Refers to the mango (M) at position (1, 1, 1) and the first (.1) mango selected from the box.
The difference in notation arises from processing in R, which uses .1, whereas the initial processing was done via Excel before formatting into .txt files.

In the folder 05_src_subset_dataset_C:
3_Color_21C_storage_random: Refers to configuration 3 (random mango selection at 21°C).
4_Color_16C_storage_random: Refers to configuration 4 (random mango selection at 16°C).

For color, pH and TSS folders:
File names conventions follow a similar structure.

The file names of photos are formatted as "Box position"_"Storage temperature"_"Relative date".

Example: 1_1_1_21C_D3 corresponds to the box at position (1, 1, 1), stored at 21°C, and captured on relative date D3.

The images of several mangoes in different storage days are stored as .jpeg files in the folder named "13_src_extra_subset_dataset_Photo".

To resume, the file names for mass, color, pH, and TSS are formatted as "Experimental number_Quality attribute_Storage Temperature_Box Number.txt”. These filenames provide information about the experimental condition, the measured parameter, the storage temperature, and the selected box number. The experimental number refers to experimental choices, distinguishing between mangoes that were monitored regularly (number 1) and those selected randomly (number 2, 3 and 4).

Abbreviations:
"T" or "temp": Temperature
"H" or "Hum": Relative humidity
"W": Weight
"M": Mango or mangoes
"C": Color
"TSS": Total soluble solids
"SR": Storage room

Key Phases:
0_Packing_House_: The phase when sensors are placed on the mangoes.
1_Cold_Storage_: Cold storage of mangoes in a chamber.
2_Transport_BKK_Airport_: Transportation phase to Bangkok Airport (BKK).
3_Storage_BKK_Platform_: Storage phase at Bangkok Airport (BKK).
4_Mango_Box_Arrange_: Arrangement of boxes in the ULD (Unit Load Device).
5_Tarmac_: Waiting phase for the ULD with mangoes on the tarmac.
6_Loading_: Loading phase of the ULD onto the airplane.
7_Inflight_: In-flight phase.
8_Storage_CDG_PARIS_Airport_: Storage of the ULD after arrival at Paris Charles de Gaulle Airport (CDG).
9_10_Transport_And_Storage_At_INRAE_: Transportation and storage phase between the airport and INRAE FRISE.
Storage Temperatures:
21C: Average temperature of 21°C in the mango storage chamber (stage 10 and onward).
16C: Average temperature of 16°C in the mango storage chamber (stage 10 and onward).

Code R: 4.4.0 in 00_script was developed by Yvanne Paviet-Salomon.
The following scripts are used to process files between directories:
01to02_script_temp_hum.R: Generates processed files for folder 02 from folder 01 (1388 lines).
03to04_script_temp_hum.R: Generates processed files for folder 04 from folder 03 (211 lines).
05to06_script_temp_hum.R: Generates processed files for folder 06 from folder 05 (226 lines).
07to08_script_temp_hum.R: Generates processed files for folder 08 from folder 07 (213 lines).
09to10_script_temp_hum.R: Generates processed files for folder 10 from folder 09 (203 lines).
11to12_script_temp_hum.R: Generates processed files for folder 12 from folder 11 (139 lines).