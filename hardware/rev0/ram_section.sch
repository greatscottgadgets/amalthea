EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 6 9
Title "Amalthea: RAM Section"
Date "2019-10-20"
Rev "r0"
Comp "Great Scott Gadgets"
Comment1 "Based on LUNA"
Comment2 ""
Comment3 "Licensed under CERN-OHL-P version 2"
Comment4 ""
$EndDescr
Wire Wire Line
	1800 1900 1800 1800
Wire Wire Line
	1800 1800 1850 1800
Wire Wire Line
	1900 1800 1900 1900
Wire Wire Line
	1850 1800 1850 1700
Connection ~ 1850 1800
Wire Wire Line
	1850 1800 1900 1800
$Comp
L fpgas_and_processors:ECP5-BGA256 IC1
U 3 1 5DE93650
P 1650 2100
F 0 "IC1" H 1620 308 50  0000 R CNN
F 1 "ECP5-BGA256" H 1620 218 50  0000 R CNN
F 2 "amalthea:lattice_cabga256" H -1550 5550 50  0001 L CNN
F 3 "" H -2000 6500 50  0001 L CNN
F 4 "FPGA - Field Programmable Gate Array ECP5; 12k LUTs; 1.1V" H -2000 6400 50  0001 L CNN "Description"
F 5 "1.7" H -2000 6750 50  0001 L CNN "Height"
F 6 "Lattice" H -1950 7350 50  0001 L CNN "Manufacturer_Name"
F 7 "LFE5U-12F-6BG256C" H -1950 7250 50  0001 L CNN "Manufacturer_Part_Number"
F 8 "842-LFE5U12F6BG256C" H -1300 5950 50  0001 L CNN "Mouser Part Number"
F 9 "https://www.mouser.com/Search/Refine.aspx?Keyword=842-LFE5U12F6BG256C" H -1650 5800 50  0001 L CNN "Mouser Price/Stock"
	3    1650 2100
	1    0    0    -1  
$EndComp
$Comp
L support_hardware:S27KS0641 U10
U 1 1 5DEA1FC4
P 5400 4850
F 0 "U10" H 5400 5772 50  0000 C CNN
F 1 "S27KL0641" H 5400 5682 50  0000 C CNN
F 2 "amalthea:BGA-24_5x5_6.0x8.0mm" H 6000 3950 50  0001 C CNN
F 3 "" H 5400 3950 50  0001 C CNN
F 4 "ANY" H 5400 4850 50  0001 C CNN "Source"
F 5 "S27KL0641" H 5400 4850 50  0001 C CNN "Manufacturer_Part_Number"
	1    5400 4850
	-1   0    0    -1  
$EndComp
Wire Wire Line
	6000 4150 6350 4150
Wire Wire Line
	6350 4150 6350 4250
Wire Wire Line
	6350 4350 6000 4350
Wire Wire Line
	6000 4250 6350 4250
Connection ~ 6350 4250
Wire Wire Line
	6350 4250 6350 4350
Wire Wire Line
	6350 4250 6550 4250
Wire Wire Line
	6550 4250 6550 4000
Wire Wire Line
	6000 5350 6350 5350
Wire Wire Line
	6350 5350 6350 5450
Wire Wire Line
	6350 5550 6000 5550
Wire Wire Line
	6000 5450 6350 5450
Connection ~ 6350 5450
Wire Wire Line
	6350 5450 6350 5550
Wire Wire Line
	6350 5450 6550 5450
Wire Wire Line
	6550 5450 6550 5600
$Comp
L power:GND #PWR085
U 1 1 5DEA82D8
P 6550 5600
F 0 "#PWR085" H 6550 5350 50  0001 C CNN
F 1 "GND" H 6554 5428 50  0000 C CNN
F 2 "" H 6550 5600 50  0001 C CNN
F 3 "" H 6550 5600 50  0001 C CNN
	1    6550 5600
	1    0    0    -1  
$EndComp
Wire Wire Line
	6000 4850 7100 4850
Entry Wire Line
	7100 4850 7200 4950
Wire Wire Line
	6000 4950 7100 4950
Entry Wire Line
	7100 4950 7200 5050
Text Label 6800 4850 0    50   ~ 0
CLK
Text Label 6800 4950 0    50   ~ 0
~CLK
Text Label 2900 5650 0    50   ~ 0
~CLK
Text Label 2900 5550 0    50   ~ 0
CLK
NoConn ~ 4800 5350
NoConn ~ 4800 5450
NoConn ~ 4800 5550
NoConn ~ 6000 5050
NoConn ~ 6000 5150
Text Label 2900 5450 0    50   ~ 0
~CS
Text Label 6950 4750 2    50   ~ 0
~CS
Text Label 2900 4950 0    50   ~ 0
~RESET
Text Label 6950 4550 2    50   ~ 0
~RESET
Text Label 4000 4350 0    50   ~ 0
RAM_DQ7
Text Label 4000 4450 0    50   ~ 0
RAM_DQ6
Text Label 4000 4550 0    50   ~ 0
RAM_DQ5
Text Label 4000 4650 0    50   ~ 0
RAM_DQ4
Text Label 4000 4750 0    50   ~ 0
RAM_DQ3
Text Label 4000 4850 0    50   ~ 0
RAM_DQ2
Text Label 4000 4950 0    50   ~ 0
RAM_DQ1
Text Label 4000 5050 0    50   ~ 0
RAM_DQ0
Text Label 4000 5150 0    50   ~ 0
RAM_RWDS
NoConn ~ 2700 2550
NoConn ~ 2700 2650
NoConn ~ 2700 2750
NoConn ~ 2700 2850
NoConn ~ 2700 3050
NoConn ~ 2700 3150
NoConn ~ 2700 3250
NoConn ~ 2700 3650
NoConn ~ 2700 3750
NoConn ~ 2700 3850
NoConn ~ 2700 4050
NoConn ~ 2700 4150
NoConn ~ 2700 4650
NoConn ~ 2700 4750
NoConn ~ 2700 4850
NoConn ~ 2700 5050
NoConn ~ 2700 5150
NoConn ~ 2700 5250
Wire Wire Line
	4800 4350 3950 4350
Wire Wire Line
	3950 4450 4800 4450
Wire Wire Line
	4800 4550 3950 4550
Wire Wire Line
	4800 4650 3950 4650
Wire Wire Line
	4800 4750 3950 4750
Wire Wire Line
	4800 4850 3950 4850
Wire Wire Line
	4800 4950 3950 4950
Wire Wire Line
	4800 5050 3950 5050
Wire Wire Line
	4800 5150 3950 5150
Entry Wire Line
	3850 4250 3950 4350
Entry Wire Line
	3850 4350 3950 4450
Entry Wire Line
	3850 4450 3950 4550
Entry Wire Line
	3850 4550 3950 4650
Entry Wire Line
	3850 4650 3950 4750
Entry Wire Line
	3850 4750 3950 4850
Entry Wire Line
	3850 4850 3950 4950
Entry Wire Line
	3850 4950 3950 5050
Entry Wire Line
	3850 5050 3950 5150
Wire Bus Line
	3850 6050 7200 6050
Wire Wire Line
	2700 3350 3750 3350
Wire Wire Line
	2700 3450 3750 3450
Wire Wire Line
	2700 2950 3750 2950
Wire Wire Line
	2700 3550 3750 3550
Entry Wire Line
	3750 2950 3850 3050
Entry Wire Line
	3750 3350 3850 3450
Entry Wire Line
	3750 3450 3850 3550
Entry Wire Line
	3750 3550 3850 3650
Text Label 2900 3350 0    50   ~ 0
RAM_DQ7
Text Label 2900 2950 0    50   ~ 0
RAM_DQ6
Text Label 2900 3450 0    50   ~ 0
RAM_DQ5
Text Label 2900 3550 0    50   ~ 0
RAM_DQ1
Wire Wire Line
	2700 3950 3750 3950
Entry Wire Line
	3750 3950 3850 4050
Text Label 2900 4350 0    50   ~ 0
RAM_DQ0
Text Label 2900 3950 0    50   ~ 0
RAM_DQ4
Wire Wire Line
	2700 4450 3750 4450
Wire Wire Line
	2700 4350 3750 4350
Entry Wire Line
	3750 4350 3850 4450
Entry Wire Line
	3750 4450 3850 4550
Text Label 2900 4450 0    50   ~ 0
RAM_DQ3
Wire Wire Line
	2700 4550 3750 4550
Entry Wire Line
	3750 4550 3850 4650
Text Label 2900 4550 0    50   ~ 0
RAM_DQ2
Wire Wire Line
	2700 4950 3750 4950
Entry Wire Line
	3750 4950 3850 5050
Text Label 2900 5350 0    50   ~ 0
RAM_RWDS
Wire Wire Line
	2700 5350 3750 5350
Entry Wire Line
	3750 5350 3850 5450
Wire Wire Line
	6000 4550 7100 4550
Wire Wire Line
	6000 4750 7100 4750
Entry Wire Line
	7100 4750 7200 4850
Entry Wire Line
	7100 4550 7200 4650
Wire Wire Line
	2700 5450 3750 5450
Entry Wire Line
	3750 5450 3850 5550
Wire Wire Line
	2700 5550 3750 5550
Wire Wire Line
	2700 5650 3750 5650
Entry Wire Line
	3750 5550 3850 5650
Entry Wire Line
	3750 5650 3850 5750
$Comp
L power:+3V3 #PWR0106
U 1 1 5EA239A6
P 1850 1700
F 0 "#PWR0106" H 1850 1550 50  0001 C CNN
F 1 "+3V3" H 1865 1873 50  0000 C CNN
F 2 "" H 1850 1700 50  0001 C CNN
F 3 "" H 1850 1700 50  0001 C CNN
	1    1850 1700
	1    0    0    -1  
$EndComp
$Comp
L power:+3V3 #PWR0107
U 1 1 5EA2585C
P 6550 4000
F 0 "#PWR0107" H 6550 3850 50  0001 C CNN
F 1 "+3V3" H 6565 4173 50  0000 C CNN
F 2 "" H 6550 4000 50  0001 C CNN
F 3 "" H 6550 4000 50  0001 C CNN
	1    6550 4000
	1    0    0    -1  
$EndComp
NoConn ~ 2700 4250
Wire Bus Line
	7200 4450 7200 6050
Wire Bus Line
	3850 2800 3850 6050
$EndSCHEMATC
