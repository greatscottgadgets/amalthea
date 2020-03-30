EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 5 9
Title "Amalthea: Downstream / Target / Analysis Section"
Date "2019-10-20"
Rev "r0"
Comp "Great Scott Gadgets"
Comment1 "Based on LUNA"
Comment2 ""
Comment3 "Licensed under CERN-OHL-P version 2"
Comment4 ""
$EndDescr
$Comp
L fpgas_and_processors:ECP5-BGA256 IC1
U 4 1 5DDE3D5A
P 1650 2100
F 0 "IC1" H 1620 283 50  0000 R CNN
F 1 "ECP5-BGA256" H 1620 193 50  0000 R CNN
F 2 "amalthea:lattice_cabga256" H -1550 5550 50  0001 L CNN
F 3 "" H -2000 6500 50  0001 L CNN
F 4 "FPGA - Field Programmable Gate Array ECP5; 12k LUTs; 1.1V" H -2000 6400 50  0001 L CNN "Description"
F 5 "1.7" H -2000 6750 50  0001 L CNN "Height"
F 6 "Lattice" H -1950 7350 50  0001 L CNN "Manufacturer_Name"
F 7 "LFE5U-12F-6BG256C" H -1950 7250 50  0001 L CNN "Manufacturer_Part_Number"
F 8 "842-LFE5U12F6BG256C" H -1300 5950 50  0001 L CNN "Mouser Part Number"
F 9 "https://www.mouser.com/Search/Refine.aspx?Keyword=842-LFE5U12F6BG256C" H -1650 5800 50  0001 L CNN "Mouser Price/Stock"
	4    1650 2100
	1    0    0    -1  
$EndComp
NoConn ~ 2600 3550
NoConn ~ 2600 3150
NoConn ~ 2600 3250
NoConn ~ 2600 3650
NoConn ~ 2600 3750
NoConn ~ 2600 3850
NoConn ~ 2600 4350
NoConn ~ 2600 4450
NoConn ~ 2600 4550
NoConn ~ 2600 4650
NoConn ~ 2600 4750
NoConn ~ 2600 4850
NoConn ~ 2600 5050
NoConn ~ 2600 5150
NoConn ~ 2600 5250
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
L power:+3V3 #PWR069
U 1 1 5DE347EF
P 1850 1700
F 0 "#PWR069" H 1850 1550 50  0001 C CNN
F 1 "+3V3" H 1864 1873 50  0000 C CNN
F 2 "" H 1850 1700 50  0001 C CNN
F 3 "" H 1850 1700 50  0001 C CNN
	1    1850 1700
	1    0    0    -1  
$EndComp
$EndSCHEMATC
