EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 9
Title "Amalthea"
Date "2019-10-20"
Rev "r0"
Comp "Great Scott Gadgets"
Comment1 "Based on LUNA"
Comment2 ""
Comment3 "Licensed under CERN-OHL-P version 2"
Comment4 ""
$EndDescr
$Sheet
S 800  6600 1150 800 
U 5DA7B3F4
F0 "Power Supplies" 50
F1 "power_supplies.sch" 50
$EndSheet
$Sheet
S 4000 4900 1700 1500
U 5DCAA6D2
F0 "FPGA Configuration and Dev Features" 39
F1 "fpga_configuration.sch" 39
F2 "SIDEBAND_D-" B R 5700 5150 50 
F3 "SIDEBAND_D+" B R 5700 5050 50 
F4 "DEBUG_SPI_UC_OUT" O R 5700 5750 50 
F5 "DEBUG_SPI_CLK" O R 5700 5850 50 
F6 "DEBUG_SPI_UC_IN" I R 5700 5950 50 
F7 "SIDEBAND_PHY_1V8" I L 4000 6000 50 
F8 "HOST_PHY_1V8" I L 4000 5300 50 
F9 "TARGET_PHY_1V8" I L 4000 5200 50 
F10 "FORCE_RECOVERY" I L 4000 5450 50 
F11 "FORCE_DFU" I L 4000 5550 50 
F12 "INHIBIT_UC_USB" B L 4000 5900 50 
F13 "RESET" I L 4000 5650 50 
F14 "UC_TX_FPGA_RX" O R 5700 6200 50 
F15 "UC_RX_FPGA_TX" I R 5700 6300 50 
F16 "DEBUG_SPI_CS" O R 5700 6050 50 
$EndSheet
Text Label 5950 5050 0    50   ~ 0
SIDEBAND_D+
Text Label 5950 5150 0    50   ~ 0
SIDEBAND_D-
Wire Wire Line
	7100 5550 7100 5450
Wire Wire Line
	7100 5550 7150 5550
Wire Wire Line
	7200 5550 7200 5450
$Comp
L power:GND #PWR06
U 1 1 5DCD7B6D
P 7150 5600
F 0 "#PWR06" H 7150 5350 50  0001 C CNN
F 1 "GND" H 7300 5600 50  0000 C CNN
F 2 "" H 7150 5600 50  0001 C CNN
F 3 "" H 7150 5600 50  0001 C CNN
	1    7150 5600
	1    0    0    -1  
$EndComp
Wire Wire Line
	7150 5600 7150 5550
Connection ~ 7150 5550
Wire Wire Line
	7150 5550 7200 5550
$Comp
L Device:D_Schottky D8
U 1 1 5DCD8026
P 6300 4850
F 0 "D8" H 6300 4950 50  0000 C CNN
F 1 "PMEG3050EP,115" H 6200 5000 50  0001 C CNN
F 2 "amalthea:SOD128" H 6300 4850 50  0001 C CNN
F 3 "~" H 6300 4850 50  0001 C CNN
	1    6300 4850
	1    0    0    -1  
$EndComp
Wire Wire Line
	6450 4850 6500 4850
$Comp
L power:+5V #PWR05
U 1 1 5DCD8771
P 5950 4850
F 0 "#PWR05" H 5950 4700 50  0001 C CNN
F 1 "+5V" V 5965 4978 50  0000 L CNN
F 2 "" H 5950 4850 50  0001 C CNN
F 3 "" H 5950 4850 50  0001 C CNN
	1    5950 4850
	0    -1   -1   0   
$EndComp
Wire Wire Line
	5950 4850 6150 4850
$Comp
L Connector:USB_B_Micro J2
U 1 1 5DCD559E
P 7100 5050
F 0 "J2" H 6870 5039 50  0000 R CNN
F 1 "USB_B_Micro" H 6870 4949 50  0000 R CNN
F 2 "Connector_USB:USB_Micro-B_Amphenol_10103594-0001LF_Horizontal" H 7250 5000 50  0001 C CNN
F 3 "~" H 7250 5000 50  0001 C CNN
	1    7100 5050
	-1   0    0    -1  
$EndComp
$Sheet
S 4000 6600 1700 800 
U 5DCD9772
F0 "Sideband Section" 50
F1 "sideband_side.sch" 50
F2 "SIDEBAND_PHY_1V8" O L 4000 6900 50 
F3 "SIDEBAND_VBUS" I L 4000 7300 50 
F4 "SIDEBAND_D-" B R 5700 6850 50 
F5 "SIDEBAND_D+" B R 5700 6750 50 
F6 "SIDEBAND_ID" B R 5700 7050 50 
F7 "UC_USB_INHIBIT" B L 4000 7000 50 
$EndSheet
Wire Wire Line
	4000 6900 3200 6900
Wire Wire Line
	6500 4850 6500 4600
Wire Wire Line
	6500 4600 6900 4600
Connection ~ 6500 4850
Text Label 6900 4600 0    50   ~ 0
SIDEBAND_VBUS
Wire Wire Line
	4000 7300 3750 7300
Text Label 3750 7300 2    50   ~ 0
SIDEBAND_VBUS
Wire Wire Line
	5700 5050 6550 5050
Wire Wire Line
	5700 5150 6650 5150
Wire Wire Line
	6500 4850 6800 4850
Wire Wire Line
	6550 6750 6550 5050
Wire Wire Line
	5700 6750 6550 6750
Connection ~ 6550 5050
Wire Wire Line
	6550 5050 6800 5050
Wire Wire Line
	6650 6850 6650 5150
Wire Wire Line
	5700 6850 6650 6850
Connection ~ 6650 5150
Wire Wire Line
	6650 5150 6800 5150
Wire Wire Line
	6800 5250 6750 5250
Wire Wire Line
	6750 5250 6750 7050
Wire Wire Line
	6750 7050 5700 7050
$Comp
L Connector:USB_B_Micro J1
U 1 1 5DD67FA9
P 900 3900
F 0 "J1" H 956 4365 50  0000 C CNN
F 1 "USB_B_Micro" H 956 4275 50  0000 C CNN
F 2 "Connector_USB:USB_Micro-B_Amphenol_10103594-0001LF_Horizontal" H 1050 3850 50  0001 C CNN
F 3 "~" H 1050 3850 50  0001 C CNN
	1    900  3900
	1    0    0    -1  
$EndComp
Wire Wire Line
	800  4300 800  4350
Wire Wire Line
	800  4350 850  4350
Wire Wire Line
	900  4350 900  4300
$Comp
L power:GND #PWR01
U 1 1 5DD6A23B
P 850 4400
F 0 "#PWR01" H 850 4150 50  0001 C CNN
F 1 "GND" H 854 4228 50  0000 C CNN
F 2 "" H 850 4400 50  0001 C CNN
F 3 "" H 850 4400 50  0001 C CNN
	1    850  4400
	1    0    0    -1  
$EndComp
Wire Wire Line
	850  4400 850  4350
Connection ~ 850  4350
Wire Wire Line
	850  4350 900  4350
Wire Wire Line
	1850 3700 1300 3700
Wire Wire Line
	1200 3900 1850 3900
Wire Wire Line
	1850 4000 1200 4000
Wire Wire Line
	1200 4100 1850 4100
$Comp
L Device:D_Schottky D1
U 1 1 5DDCCE15
P 1500 3550
F 0 "D1" H 1500 3650 50  0000 C CNN
F 1 "PMEG3050EP,115" H 1400 3700 50  0001 C CNN
F 2 "amalthea:SOD128" H 1500 3550 50  0001 C CNN
F 3 "~" H 1500 3550 50  0001 C CNN
	1    1500 3550
	-1   0    0    1   
$EndComp
Wire Wire Line
	1350 3550 1300 3550
Wire Wire Line
	1300 3550 1300 3700
Connection ~ 1300 3700
Wire Wire Line
	1300 3700 1200 3700
Wire Wire Line
	9000 2900 9050 2900
Connection ~ 9000 2900
Wire Wire Line
	9000 3000 9000 2900
$Comp
L power:GND #PWR08
U 1 1 5DD6FDBE
P 9000 3000
F 0 "#PWR08" H 9000 2750 50  0001 C CNN
F 1 "GND" H 9004 2828 50  0000 C CNN
F 2 "" H 9000 3000 50  0001 C CNN
F 3 "" H 9000 3000 50  0001 C CNN
	1    9000 3000
	1    0    0    -1  
$EndComp
Wire Wire Line
	9050 2900 9050 2850
Wire Wire Line
	8950 2900 9000 2900
Wire Wire Line
	8950 2850 8950 2900
$Comp
L Connector:USB_A J3
U 1 1 5DD6DEF2
P 8950 2450
F 0 "J3" H 8721 2439 50  0000 R CNN
F 1 "USB_A" H 8721 2349 50  0000 R CNN
F 2 "amalthea:CONN-Amphenol-UE27AC54100" H 9100 2400 50  0001 C CNN
F 3 " ~" H 9100 2400 50  0001 C CNN
	1    8950 2450
	-1   0    0    -1  
$EndComp
Wire Wire Line
	4000 3500 3600 3500
$Sheet
S 4000 3350 1700 1250
U 5DDDB747
F0 "Target Section" 50
F1 "target_side.sch" 50
F2 "TARGET_ID" B R 5700 3950 50 
F3 "TARGET_D+" B R 5700 3750 50 
F4 "TARGET_D-" B R 5700 3850 50 
F5 "TARGET_VBUS" I R 5700 3550 50 
F6 "TARGET_PHY_1V8" O L 4000 3500 50 
F7 "TARGET_FAULT" I R 5700 4150 50 
F8 "A_PORT_POWER_ENABLE" O R 5700 4350 50 
F9 "ALLOW_POWER_VIA_TARGET_PORT" O R 5700 4450 50 
$EndSheet
Wire Wire Line
	9050 4200 9000 4200
Connection ~ 9050 4200
Wire Wire Line
	9050 4250 9050 4200
$Comp
L power:GND #PWR09
U 1 1 5DD6B00F
P 9050 4250
F 0 "#PWR09" H 9050 4000 50  0001 C CNN
F 1 "GND" H 9054 4078 50  0000 C CNN
F 2 "" H 9050 4250 50  0001 C CNN
F 3 "" H 9050 4250 50  0001 C CNN
	1    9050 4250
	-1   0    0    -1  
$EndComp
Wire Wire Line
	9000 4200 9000 4150
Wire Wire Line
	9100 4200 9050 4200
Wire Wire Line
	9100 4150 9100 4200
$Comp
L Connector:USB_B_Micro J4
U 1 1 5DD6B002
P 9000 3750
F 0 "J4" H 9056 4215 50  0000 C CNN
F 1 "USB_B_Micro" H 9056 4125 50  0000 C CNN
F 2 "Connector_USB:USB_Micro-B_Amphenol_10103594-0001LF_Horizontal" H 9150 3700 50  0001 C CNN
F 3 "~" H 9150 3700 50  0001 C CNN
	1    9000 3750
	-1   0    0    -1  
$EndComp
Wire Wire Line
	8550 1600 8700 1600
Text Label 10000 1350 0    50   ~ 0
TARGET_FAULT
Text Label 8100 1200 2    50   ~ 0
PROVIDE_A_PORT_VBUS
Text Label 8100 1850 2    50   ~ 0
VBUS_PASSTHROUGH_EN
$Sheet
S 4000 1900 1700 950 
U 5DE77FE3
F0 "RAM / 1V8 Section" 50
F1 "ram_section.sch" 50
$EndSheet
Text Notes 4250 2400 0    100  ~ 0
64Mib HyperRAM
Wire Wire Line
	5700 3550 6200 3550
Wire Wire Line
	5700 3750 6300 3750
Wire Wire Line
	5700 3850 6400 3850
Wire Wire Line
	10700 2050 8450 2050
Wire Wire Line
	8450 2050 8450 2250
Wire Wire Line
	8450 2250 8650 2250
Wire Wire Line
	6200 1500 6200 3550
Connection ~ 6200 3550
Wire Wire Line
	6200 3550 8700 3550
Wire Wire Line
	6300 2450 6300 3750
Wire Wire Line
	6300 2450 8650 2450
Connection ~ 6300 3750
Wire Wire Line
	6300 3750 8700 3750
Wire Wire Line
	6400 3850 6400 2550
Wire Wire Line
	6400 2550 8650 2550
Connection ~ 6400 3850
Wire Wire Line
	6400 3850 8700 3850
$Comp
L Device:R R2
U 1 1 5DFA3A73
P 7950 1700
F 0 "R2" V 8050 1700 50  0000 C CNN
F 1 "10K" V 7950 1700 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 7880 1700 50  0001 C CNN
F 3 "~" H 7950 1700 50  0001 C CNN
	1    7950 1700
	0    1    -1   0   
$EndComp
Wire Wire Line
	3200 6900 3200 6000
Wire Wire Line
	3500 5300 4000 5300
Wire Wire Line
	4000 5200 3600 5200
Wire Wire Line
	3600 5200 3600 3500
Text Label 5850 6750 0    50   ~ 0
SIDEBAND_D+
Text Label 5850 6850 0    50   ~ 0
SIDEBAND_D-
Text Label 5850 7050 0    50   ~ 0
SIDEBAND_ID
Wire Wire Line
	5700 5750 5850 5750
Text Label 5850 5750 0    50   ~ 0
DEBUG_SPI_MOSI
Wire Wire Line
	5700 5850 5850 5850
Wire Wire Line
	5700 5950 5850 5950
Text Label 5850 5950 0    50   ~ 0
DEBUG_SPI_MISO
Text Label 5850 5850 0    50   ~ 0
DEBUG_SPI_CLK
$Comp
L support_hardware:DSC60xx Y1
U 1 1 5E0711AF
P 1050 2400
F 0 "Y1" H 900 2000 50  0000 L CNN
F 1 "DSC60xx" H 1450 2450 50  0000 L CNN
F 2 "Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm" H 1050 2400 50  0001 C CNN
F 3 "" H 1050 2400 50  0001 C CNN
	1    1050 2400
	1    0    0    -1  
$EndComp
Wire Wire Line
	950  2600 800  2600
Wire Wire Line
	800  2600 800  2200
Wire Wire Line
	1300 2200 1300 2300
$Comp
L power:+3V3 #PWR011
U 1 1 5E07C6A8
P 1300 2200
F 0 "#PWR011" H 1300 2050 50  0001 C CNN
F 1 "+3V3" H 1314 2373 50  0000 C CNN
F 2 "" H 1300 2200 50  0001 C CNN
F 3 "" H 1300 2200 50  0001 C CNN
	1    1300 2200
	1    0    0    -1  
$EndComp
Wire Wire Line
	1700 2600 2150 2600
Text Label 5950 4450 0    50   ~ 0
VBUS_PASSTHROUGH_EN
Text Label 5950 4350 0    50   ~ 0
PROVIDE_A_PORT_VBUS
Text Label 7200 2450 0    50   ~ 0
TARGET_D+
Text Label 7200 2550 0    50   ~ 0
TARGET_D-
Text Label 7200 3750 0    50   ~ 0
TARGET_D+
Text Label 7200 3850 0    50   ~ 0
TARGET_D-
Text Label 7200 3950 0    50   ~ 0
TARGET_ID
Text Label 7200 3550 0    50   ~ 0
TARGET_VBUS_IN
Text Label 8750 2050 0    50   ~ 0
TARGET_VBUS_OUT
Text Label 1300 3900 0    50   ~ 0
HOST_D+
Text Label 1300 4000 0    50   ~ 0
HOST_D-
Text Label 1300 4100 0    50   ~ 0
HOST_ID
Wire Wire Line
	4000 6000 3200 6000
$Comp
L Switch:SW_SPST SW1
U 1 1 5E0E58AB
P 2250 5350
F 0 "SW1" H 2000 5400 50  0000 C CNN
F 1 "BTN_RECOVERY" H 2250 5250 50  0000 C CNN
F 2 "amalthea:SWITCH-FSMRA" H 2250 5350 50  0001 C CNN
F 3 "~" H 2250 5350 50  0001 C CNN
	1    2250 5350
	1    0    0    -1  
$EndComp
$Comp
L Switch:SW_SPST SW2
U 1 1 5E0E6B65
P 2250 5650
F 0 "SW2" H 2000 5700 50  0000 C CNN
F 1 "BTN_DFU" H 2250 5500 50  0000 C CNN
F 2 "amalthea:SWITCH-FSMRA" H 2250 5650 50  0001 C CNN
F 3 "~" H 2250 5650 50  0001 C CNN
	1    2250 5650
	1    0    0    -1  
$EndComp
Wire Wire Line
	4000 5450 2550 5450
Wire Wire Line
	2450 5650 2550 5650
Wire Wire Line
	2550 5650 2550 5550
Wire Wire Line
	2550 5550 4000 5550
Wire Wire Line
	1900 5650 2050 5650
Wire Wire Line
	2450 5350 2550 5350
Wire Wire Line
	2550 5350 2550 5450
Wire Wire Line
	2050 5350 1900 5350
Text Label 2800 5450 0    50   ~ 0
FORCE_RECOVERY
Text Label 2800 5550 0    50   ~ 0
FORCE_DFU
Wire Wire Line
	2950 4800 3500 4800
$Sheet
S 1850 3500 1100 1500
U 5DD754D4
F0 "Host Section" 50
F1 "host_side.sch" 50
F2 "HOST_ID" B L 1850 4100 50 
F3 "HOST_D+" B L 1850 3900 50 
F4 "HOST_D-" B L 1850 4000 50 
F5 "HOST_VBUS" I L 1850 3700 50 
F6 "HOST_PHY_1V8" O R 2950 4800 50 
$EndSheet
Wire Wire Line
	4000 7000 3100 7000
Wire Wire Line
	3100 7000 3100 5900
Wire Wire Line
	3100 5900 4000 5900
Text Label 3950 7000 2    50   ~ 0
USB_INHIBIT
Text Label 3950 6900 2    50   ~ 0
SIDEBAND_PHY_1V8
Text Label 3000 4800 0    50   ~ 0
HOST_PHY_1V8
Text Label 3600 4150 1    50   ~ 0
TARGET_PHY_1V8
$Comp
L Switch:SW_SPST SW3
U 1 1 5E2B35A7
P 2250 6000
F 0 "SW3" H 2000 6050 50  0000 C CNN
F 1 "BTN_RESET" H 2250 5900 50  0000 C CNN
F 2 "amalthea:SWITCH-FSMRA" H 2250 6000 50  0001 C CNN
F 3 "~" H 2250 6000 50  0001 C CNN
	1    2250 6000
	1    0    0    -1  
$EndComp
Text Label 2800 5650 0    50   ~ 0
FULL_RESET
Wire Wire Line
	1900 5650 1900 6000
Wire Wire Line
	1900 6000 2050 6000
Connection ~ 1900 5650
Wire Wire Line
	2600 5650 2600 6000
Wire Wire Line
	2600 5650 4000 5650
Wire Wire Line
	2450 6000 2600 6000
Wire Wire Line
	1900 5350 1900 5650
$Comp
L power:GND #PWR0102
U 1 1 5E2DCA26
P 1700 5650
F 0 "#PWR0102" H 1700 5400 50  0001 C CNN
F 1 "GND" V 1704 5522 50  0000 R CNN
F 2 "" H 1700 5650 50  0001 C CNN
F 3 "" H 1700 5650 50  0001 C CNN
	1    1700 5650
	0    1    1    0   
$EndComp
Wire Wire Line
	1700 5650 1900 5650
$Comp
L power:GND #PWR0104
U 1 1 5E35A664
P 1300 3050
F 0 "#PWR0104" H 1300 2800 50  0001 C CNN
F 1 "GND" H 1450 3000 50  0000 C CNN
F 2 "" H 1300 3050 50  0001 C CNN
F 3 "" H 1300 3050 50  0001 C CNN
	1    1300 3050
	1    0    0    -1  
$EndComp
Wire Wire Line
	1300 3050 1300 2950
Wire Wire Line
	8700 3950 5700 3950
Wire Wire Line
	5700 6200 5850 6200
Wire Wire Line
	5700 6300 5850 6300
Text Label 5850 6200 0    50   ~ 0
UC_TX_FPGA_RX
Text Label 5850 6300 0    50   ~ 0
UC_RX_FPGA_TX
$Comp
L power:+5V #PWR0113
U 1 1 5E2D79BC
P 1650 3550
F 0 "#PWR0113" H 1650 3400 50  0001 C CNN
F 1 "+5V" V 1550 3500 50  0000 L CNN
F 2 "" H 1650 3550 50  0001 C CNN
F 3 "" H 1650 3550 50  0001 C CNN
	1    1650 3550
	0    1    1    0   
$EndComp
Wire Wire Line
	5700 4150 5800 4150
Text Label 5950 4150 0    50   ~ 0
TARGET_FAULT
Text Label 9050 6100 0    50   ~ 0
DEBUG_SPI_MOSI
$Comp
L Device:R R26
U 1 1 5E2F303E
P 9450 4900
F 0 "R26" V 9400 5100 50  0000 C CNN
F 1 "330" V 9450 4900 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 9380 4900 50  0001 C CNN
F 3 "~" H 9450 4900 50  0001 C CNN
	1    9450 4900
	0    1    1    0   
$EndComp
Wire Wire Line
	9000 4900 9300 4900
$Comp
L Device:R R27
U 1 1 5E302750
P 9450 5000
F 0 "R27" V 9400 5200 50  0000 C CNN
F 1 "330" V 9450 5000 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 9380 5000 50  0001 C CNN
F 3 "~" H 9450 5000 50  0001 C CNN
	1    9450 5000
	0    1    1    0   
$EndComp
$Comp
L Device:R R28
U 1 1 5E30290F
P 9450 5100
F 0 "R28" V 9400 5300 50  0000 C CNN
F 1 "330" V 9450 5100 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 9380 5100 50  0001 C CNN
F 3 "~" H 9450 5100 50  0001 C CNN
	1    9450 5100
	0    1    1    0   
$EndComp
$Comp
L Device:R R29
U 1 1 5E302A11
P 9450 5200
F 0 "R29" V 9400 5400 50  0000 C CNN
F 1 "330" V 9450 5200 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 9380 5200 50  0001 C CNN
F 3 "~" H 9450 5200 50  0001 C CNN
	1    9450 5200
	0    1    1    0   
$EndComp
$Comp
L Device:R R30
U 1 1 5E302B3D
P 9450 5300
F 0 "R30" V 9400 5500 50  0000 C CNN
F 1 "330" V 9450 5300 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 9380 5300 50  0001 C CNN
F 3 "~" H 9450 5300 50  0001 C CNN
	1    9450 5300
	0    1    1    0   
$EndComp
$Comp
L Device:R R31
U 1 1 5E302CFC
P 9450 5400
F 0 "R31" V 9400 5600 50  0000 C CNN
F 1 "330" V 9450 5400 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 9380 5400 50  0001 C CNN
F 3 "~" H 9450 5400 50  0001 C CNN
	1    9450 5400
	0    1    1    0   
$EndComp
Wire Wire Line
	9000 5000 9300 5000
Wire Wire Line
	9000 5100 9300 5100
Wire Wire Line
	9000 5200 9300 5200
Wire Wire Line
	9000 5300 9300 5300
Wire Wire Line
	9000 5400 9300 5400
Wire Wire Line
	9600 5000 9800 5000
Wire Wire Line
	9600 5100 9800 5100
Wire Wire Line
	9600 5200 9800 5200
Wire Wire Line
	9600 5300 9800 5300
Wire Wire Line
	9600 5400 9800 5400
Wire Wire Line
	9600 4900 9800 4900
Wire Wire Line
	10100 4900 10500 4900
Wire Wire Line
	10500 4900 10500 5000
Wire Wire Line
	10500 5400 10100 5400
Wire Wire Line
	10100 5300 10500 5300
Connection ~ 10500 5300
Wire Wire Line
	10500 5300 10500 5400
Wire Wire Line
	10500 5200 10500 5300
Wire Wire Line
	10100 5200 10500 5200
Connection ~ 10500 5200
Wire Wire Line
	10500 5100 10500 5200
Wire Wire Line
	10100 5100 10500 5100
Connection ~ 10500 5100
Wire Wire Line
	10500 5000 10500 5100
Wire Wire Line
	10100 5000 10500 5000
Connection ~ 10500 5000
$Comp
L Device:LED D?
U 1 1 5DF2A471
P 9950 4900
AR Path="/5DEF5588/5DF2A471" Ref="D?"  Part="1" 
AR Path="/5DF2A471" Ref="D2"  Part="1" 
F 0 "D2" H 10050 4850 50  0000 C CNN
F 1 "RED" H 10300 4850 50  0000 C CNN
F 2 "LED_SMD:LED_0603_1608Metric_Pad1.05x0.95mm_HandSolder" H 9950 4900 50  0001 C CNN
F 3 "~" H 9950 4900 50  0001 C CNN
	1    9950 4900
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D?
U 1 1 5DF2A465
P 9950 5100
AR Path="/5DEF5588/5DF2A465" Ref="D?"  Part="1" 
AR Path="/5DF2A465" Ref="D4"  Part="1" 
F 0 "D4" H 10050 5050 50  0000 C CNN
F 1 "YELLOW" H 10300 5050 50  0000 C CNN
F 2 "LED_SMD:LED_0603_1608Metric_Pad1.05x0.95mm_HandSolder" H 9950 5100 50  0001 C CNN
F 3 "~" H 9950 5100 50  0001 C CNN
	1    9950 5100
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D?
U 1 1 5DF2A45F
P 9950 5200
AR Path="/5DEF5588/5DF2A45F" Ref="D?"  Part="1" 
AR Path="/5DF2A45F" Ref="D5"  Part="1" 
F 0 "D5" H 10050 5150 50  0000 C CNN
F 1 "GREEN" H 10300 5150 50  0000 C CNN
F 2 "LED_SMD:LED_0603_1608Metric_Pad1.05x0.95mm_HandSolder" H 9950 5200 50  0001 C CNN
F 3 "~" H 9950 5200 50  0001 C CNN
	1    9950 5200
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D?
U 1 1 5DF2A459
P 9950 5300
AR Path="/5DEF5588/5DF2A459" Ref="D?"  Part="1" 
AR Path="/5DF2A459" Ref="D6"  Part="1" 
F 0 "D6" H 10050 5250 50  0000 C CNN
F 1 "BLUE" H 10300 5250 50  0000 C CNN
F 2 "LED_SMD:LED_0603_1608Metric_Pad1.05x0.95mm_HandSolder" H 9950 5300 50  0001 C CNN
F 3 "~" H 9950 5300 50  0001 C CNN
	1    9950 5300
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D?
U 1 1 5DF2A453
P 9950 5400
AR Path="/5DEF5588/5DF2A453" Ref="D?"  Part="1" 
AR Path="/5DF2A453" Ref="D7"  Part="1" 
F 0 "D7" H 10050 5350 50  0000 C CNN
F 1 "PURPLE" H 10300 5350 50  0000 C CNN
F 2 "LED_SMD:LED_0603_1608Metric_Pad1.05x0.95mm_HandSolder" H 9950 5400 50  0001 C CNN
F 3 "~" H 9950 5400 50  0001 C CNN
	1    9950 5400
	1    0    0    -1  
$EndComp
$Comp
L power:+3V3 #PWR?
U 1 1 5DF2A44D
P 10700 5100
AR Path="/5DEF5588/5DF2A44D" Ref="#PWR?"  Part="1" 
AR Path="/5DF2A44D" Ref="#PWR04"  Part="1" 
F 0 "#PWR04" H 10700 4950 50  0001 C CNN
F 1 "+3V3" H 10714 5273 50  0000 C CNN
F 2 "" H 10700 5100 50  0001 C CNN
F 3 "" H 10700 5100 50  0001 C CNN
	1    10700 5100
	0    1    1    0   
$EndComp
Wire Wire Line
	10500 5100 10700 5100
$Comp
L power:GND #PWR0111
U 1 1 5E2A5843
P 2850 2100
F 0 "#PWR0111" H 2850 1850 50  0001 C CNN
F 1 "GND" H 2850 1950 50  0000 C CNN
F 2 "" H 2850 2100 50  0001 C CNN
F 3 "" H 2850 2100 50  0001 C CNN
	1    2850 2100
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0110
U 1 1 5E2A54E0
P 2850 1600
F 0 "#PWR0110" H 2850 1350 50  0001 C CNN
F 1 "GND" H 2850 1450 50  0000 C CNN
F 2 "" H 2850 1600 50  0001 C CNN
F 3 "" H 2850 1600 50  0001 C CNN
	1    2850 1600
	-1   0    0    1   
$EndComp
Wire Wire Line
	3100 1000 3150 1000
Connection ~ 3100 1000
Wire Wire Line
	3100 2150 3100 1000
Wire Wire Line
	2950 2150 3100 2150
Wire Wire Line
	2950 2100 2950 2150
Wire Wire Line
	2950 1400 3150 1400
Wire Wire Line
	1800 1000 3100 1000
$Comp
L Connector:Conn_Coaxial J8
U 1 1 5E41D377
P 3350 1000
F 0 "J8" H 3450 974 50  0000 L CNN
F 1 "Conn_Coaxial" H 3450 884 50  0001 L CNN
F 2 "amalthea:SMA-EDGE" H 3350 1000 50  0001 C CNN
F 3 " ~" H 3350 1000 50  0001 C CNN
	1    3350 1000
	1    0    0    -1  
$EndComp
Wire Wire Line
	3500 1200 3350 1200
Connection ~ 2950 1400
Wire Wire Line
	2950 1400 2950 1600
Wire Wire Line
	2850 1400 2950 1400
Wire Wire Line
	2850 1100 1800 1100
Wire Wire Line
	2850 1400 2850 1100
Wire Wire Line
	1800 1200 2750 1200
Wire Wire Line
	2750 1200 2750 1600
Wire Wire Line
	1800 1300 2600 1300
Wire Wire Line
	2600 2100 2750 2100
Wire Wire Line
	2600 1300 2600 2100
Text Notes 2700 900  2    50   ~ 0
Trigger I/O
$Comp
L Connector_Generic:Conn_02x03_Odd_Even J7
U 1 1 5E44B790
P 2850 1800
F 0 "J7" V 2900 1750 50  0000 L CNN
F 1 "Conn_02x02_Counter_Clockwise" V 2945 1879 50  0001 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Horizontal" H 2850 1800 50  0001 C CNN
F 3 "~" H 2850 1800 50  0001 C CNN
	1    2850 1800
	0    1    1    0   
$EndComp
Wire Wire Line
	3500 1600 3350 1600
$Comp
L power:GND #PWR0107
U 1 1 5E440A75
P 3500 1600
F 0 "#PWR0107" H 3500 1350 50  0001 C CNN
F 1 "GND" H 3600 1450 50  0000 R CNN
F 2 "" H 3500 1600 50  0001 C CNN
F 3 "" H 3500 1600 50  0001 C CNN
	1    3500 1600
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR0106
U 1 1 5E43820F
P 3500 1200
F 0 "#PWR0106" H 3500 950 50  0001 C CNN
F 1 "GND" H 3600 1050 50  0000 R CNN
F 2 "" H 3500 1200 50  0001 C CNN
F 3 "" H 3500 1200 50  0001 C CNN
	1    3500 1200
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_Coaxial J9
U 1 1 5E41DB94
P 3350 1400
F 0 "J9" H 3449 1329 50  0000 L CNN
F 1 "Conn_Coaxial" H 3450 1284 50  0001 L CNN
F 2 "amalthea:SMA-EDGE" H 3350 1400 50  0001 C CNN
F 3 " ~" H 3350 1400 50  0001 C CNN
	1    3350 1400
	1    0    0    -1  
$EndComp
Wire Wire Line
	800  2200 1300 2200
Connection ~ 1300 2200
Wire Wire Line
	3500 4800 3500 5300
Wire Wire Line
	1800 1700 2150 1700
Wire Wire Line
	2150 1700 2150 2600
NoConn ~ 1800 1400
$Sheet
S 600  800  1200 1050
U 5DF88884
F0 "Debug & Control Connections" 50
F1 "debug_control_connections.sch" 50
F2 "CLKIN_60MHZ" I R 1800 1700 50 
F3 "USER_IO0" B R 1800 1000 50 
F4 "USER_IO1" B R 1800 1100 50 
F5 "USER_IO2" B R 1800 1200 50 
F6 "USER_IO3" B R 1800 1300 50 
F7 "USER_IO4" B R 1800 1400 50 
F8 "USER_IO5" B R 1800 1500 50 
$EndSheet
NoConn ~ 1800 1500
$Sheet
S 8200 4800 800  1450
U 5DEF5588
F0 "Right side indicators" 50
F1 "right_side_indicators.sch" 50
F2 "D5" O R 9000 4900 50 
F3 "D4" O R 9000 5000 50 
F4 "D3" O R 9000 5100 50 
F5 "D2" O R 9000 5200 50 
F6 "D1" O R 9000 5300 50 
F7 "D0" O R 9000 5400 50 
F8 "UC_RX_FPGA_TX" O R 9000 5650 50 
F9 "UC_TX_FPGA_RX" I R 9000 5750 50 
F10 "DEBUG_SPI_MISO" O R 9000 5900 50 
F11 "DEBUG_SPI_CLK" I R 9000 6000 50 
F12 "DEBUG_SPI_MOSI" I R 9000 6100 50 
F13 "DEBUG_SPI_CS" I R 9000 6200 50 
$EndSheet
Text Label 9050 5750 0    50   ~ 0
UC_TX_FPGA_RX
Text Label 9050 5650 0    50   ~ 0
UC_RX_FPGA_TX
Wire Wire Line
	9050 5650 9000 5650
Wire Wire Line
	9000 5750 9050 5750
Wire Wire Line
	9050 5900 9000 5900
Wire Wire Line
	9000 6000 9050 6000
Wire Wire Line
	9050 6100 9000 6100
Wire Notes Line
	7850 6550 7850 4600
Wire Notes Line
	7850 4600 11200 4600
Wire Notes Line
	3900 500  3900 3200
Wire Notes Line
	3900 3200 500  3200
Wire Wire Line
	5950 4350 5700 4350
Wire Wire Line
	5950 4450 5700 4450
$Comp
L support_hardware:AP22804-SOT U12
U 1 1 5DDCF875
P 8800 1450
F 0 "U12" H 9050 1622 50  0000 C CNN
F 1 "AP22814-SOT" H 9050 1532 50  0000 C CNN
F 2 "gsg-modules:SOT25" H 8800 1450 50  0001 C CNN
F 3 "" H 8800 1450 50  0001 C CNN
	1    8800 1450
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0114
U 1 1 5DDE27E4
P 8550 1600
F 0 "#PWR0114" H 8550 1350 50  0001 C CNN
F 1 "GND" V 8554 1472 50  0000 R CNN
F 2 "" H 8550 1600 50  0001 C CNN
F 3 "" H 8550 1600 50  0001 C CNN
	1    8550 1600
	0    1    1    0   
$EndComp
Wire Wire Line
	9400 1600 10700 1600
Wire Wire Line
	10700 1600 10700 2050
Wire Wire Line
	8700 1700 8250 1700
Connection ~ 8250 1700
Wire Wire Line
	8250 1700 8100 1700
Wire Wire Line
	8250 1850 8100 1850
Wire Wire Line
	8250 1700 8250 1850
Wire Wire Line
	7800 1700 7650 1700
Wire Wire Line
	7650 1700 7650 1500
Connection ~ 7650 1500
Wire Wire Line
	7650 1500 8700 1500
$Comp
L Device:R R1
U 1 1 5DFB954D
P 7950 1050
F 0 "R1" V 7900 850 50  0000 C CNN
F 1 "10K" V 7950 1050 50  0000 C CNN
F 2 "Resistor_SMD:R_0402_1005Metric" V 7880 1050 50  0001 C CNN
F 3 "~" H 7950 1050 50  0001 C CNN
	1    7950 1050
	0    -1   1    0   
$EndComp
Wire Wire Line
	6200 1500 6650 1500
$Comp
L support_hardware:AP22804-SOT U1
U 1 1 5DE0E59A
P 8800 800
F 0 "U1" H 9050 972 50  0000 C CNN
F 1 "AP22814-SOT" H 9050 882 50  0000 C CNN
F 2 "gsg-modules:SOT25" H 8800 800 50  0001 C CNN
F 3 "" H 8800 800 50  0001 C CNN
	1    8800 800 
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR0115
U 1 1 5DE172C2
P 8350 850
F 0 "#PWR0115" H 8350 700 50  0001 C CNN
F 1 "+5V" H 8364 1023 50  0000 C CNN
F 2 "" H 8350 850 50  0001 C CNN
F 3 "" H 8350 850 50  0001 C CNN
	1    8350 850 
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0116
U 1 1 5DE20196
P 7800 950
F 0 "#PWR0116" H 7800 700 50  0001 C CNN
F 1 "GND" V 7804 822 50  0000 R CNN
F 2 "" H 7800 950 50  0001 C CNN
F 3 "" H 7800 950 50  0001 C CNN
	1    7800 950 
	0    1    1    0   
$EndComp
Wire Wire Line
	8100 1050 8250 1050
Wire Wire Line
	9400 950  10700 950 
Wire Wire Line
	10700 950  10700 1600
Connection ~ 10700 1600
Wire Wire Line
	8250 1050 8250 1200
Wire Wire Line
	8250 1200 8100 1200
Connection ~ 8250 1050
Wire Wire Line
	8250 1050 8700 1050
Wire Wire Line
	8350 850  8700 850 
Wire Wire Line
	7800 950  7800 1050
Wire Wire Line
	7800 950  8700 950 
Connection ~ 7800 950 
Wire Wire Line
	9650 1050 9650 1350
Wire Wire Line
	9400 1050 9650 1050
Wire Wire Line
	9400 1700 9650 1700
Wire Wire Line
	9650 1700 9650 1350
Connection ~ 9650 1350
Wire Wire Line
	9650 1350 10000 1350
$Comp
L Device:R R3
U 1 1 5DEBAF7B
P 6800 4050
F 0 "R3" V 6900 4050 50  0000 C CNN
F 1 "10K" V 6800 4050 50  0000 C CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" V 6730 4050 50  0001 C CNN
F 3 "~" H 6800 4050 50  0001 C CNN
	1    6800 4050
	0    1    1    0   
$EndComp
Wire Wire Line
	5800 4150 5800 4050
Wire Wire Line
	5800 4050 6650 4050
Connection ~ 5800 4150
Wire Wire Line
	5800 4150 5950 4150
$Comp
L power:+3V3 #PWR0117
U 1 1 5DEC924F
P 7000 4050
F 0 "#PWR0117" H 7000 3900 50  0001 C CNN
F 1 "+3V3" V 7014 4178 50  0000 L CNN
F 2 "" H 7000 4050 50  0001 C CNN
F 3 "" H 7000 4050 50  0001 C CNN
	1    7000 4050
	0    1    1    0   
$EndComp
Wire Wire Line
	7000 4050 6950 4050
$Comp
L Device:C C53
U 1 1 5DED4B80
P 10850 950
F 0 "C53" V 10600 950 50  0000 C CNN
F 1 "10uF" V 10690 950 50  0000 C CNN
F 2 "Capacitor_SMD:C_0805_2012Metric" H 10888 800 50  0001 C CNN
F 3 "~" H 10850 950 50  0001 C CNN
	1    10850 950 
	0    1    1    0   
$EndComp
Connection ~ 10700 950 
$Comp
L power:GND #PWR0118
U 1 1 5DED5921
P 11000 950
F 0 "#PWR0118" H 11000 700 50  0001 C CNN
F 1 "GND" H 11100 800 50  0000 R CNN
F 2 "" H 11000 950 50  0001 C CNN
F 3 "" H 11000 950 50  0001 C CNN
	1    11000 950 
	0    -1   -1   0   
$EndComp
$Comp
L Device:C C54
U 1 1 5DF2ADB4
P 6650 950
F 0 "C54" H 6765 995 50  0000 L CNN
F 1 "0.1uF" H 6765 905 50  0000 L CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 6688 800 50  0001 C CNN
F 3 "~" H 6650 950 50  0001 C CNN
	1    6650 950 
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0119
U 1 1 5DF2CA53
P 6650 1200
F 0 "#PWR0119" H 6650 950 50  0001 C CNN
F 1 "GND" H 6654 1028 50  0000 C CNN
F 2 "" H 6650 1200 50  0001 C CNN
F 3 "" H 6650 1200 50  0001 C CNN
	1    6650 1200
	1    0    0    -1  
$EndComp
Wire Wire Line
	6650 1200 6650 1100
$Comp
L power:+5V #PWR0120
U 1 1 5DF36D7D
P 6650 700
F 0 "#PWR0120" H 6650 550 50  0001 C CNN
F 1 "+5V" H 6664 873 50  0000 C CNN
F 2 "" H 6650 700 50  0001 C CNN
F 3 "" H 6650 700 50  0001 C CNN
	1    6650 700 
	1    0    0    -1  
$EndComp
Wire Wire Line
	6650 700  6650 800 
$Comp
L Device:C C55
U 1 1 5DF41314
P 6650 1650
F 0 "C55" H 6765 1695 50  0000 L CNN
F 1 "0.1uF" H 6765 1605 50  0000 L CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 6688 1500 50  0001 C CNN
F 3 "~" H 6650 1650 50  0001 C CNN
	1    6650 1650
	1    0    0    -1  
$EndComp
Connection ~ 6650 1500
Wire Wire Line
	6650 1500 7650 1500
$Comp
L power:GND #PWR0121
U 1 1 5DF42827
P 6650 1900
F 0 "#PWR0121" H 6650 1650 50  0001 C CNN
F 1 "GND" H 6654 1728 50  0000 C CNN
F 2 "" H 6650 1900 50  0001 C CNN
F 3 "" H 6650 1900 50  0001 C CNN
	1    6650 1900
	1    0    0    -1  
$EndComp
Wire Wire Line
	6650 1900 6650 1800
$Comp
L Device:LED D?
U 1 1 5DF2A46B
P 9950 5000
AR Path="/5DEF5588/5DF2A46B" Ref="D?"  Part="1" 
AR Path="/5DF2A46B" Ref="D3"  Part="1" 
F 0 "D3" H 10050 4950 50  0000 C CNN
F 1 "ORANGE" H 10300 4950 50  0000 C CNN
F 2 "LED_SMD:LED_0603_1608Metric_Pad1.05x0.95mm_HandSolder" H 9950 5000 50  0001 C CNN
F 3 "~" H 9950 5000 50  0001 C CNN
	1    9950 5000
	1    0    0    -1  
$EndComp
$Comp
L Connector:TestPoint TP1
U 1 1 5E216C1B
P 2150 1700
F 0 "TP1" H 2208 1818 50  0000 L CNN
F 1 "TestPoint" H 2208 1728 50  0000 L CNN
F 2 "TestPoint:TestPoint_Pad_D1.0mm" H 2350 1700 50  0001 C CNN
F 3 "~" H 2350 1700 50  0001 C CNN
	1    2150 1700
	1    0    0    -1  
$EndComp
Connection ~ 2150 1700
Text Label 9050 6000 0    50   ~ 0
DEBUG_SPI_CLK
Text Label 9050 5900 0    50   ~ 0
DEBUG_SPI_MISO
Text Label 9050 6200 0    50   ~ 0
DEBUG_SPI_CS
Wire Wire Line
	9000 6200 9050 6200
Text Label 5850 6050 0    50   ~ 0
DEBUG_SPI_CS
Wire Wire Line
	5850 6050 5700 6050
$EndSCHEMATC
