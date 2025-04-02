/*
	Neurobit device API.
	Simple example of console application using Neurobit driver.

	The application automatically configures the device (without use of 
	device settings window of the driver) for EEG measurement in all 
	versatile channels, starts the session and dumps physiological signal 
	samples on the screen (Tab Separated Values format).
	
	By default Neurobit Optima+ 4 USB device is expected. It can be changed 
	below or in the command line.

	Copyright (c) by Neurobit Systems, 2010-2022

	ANSI C source code. System-dependent parts written for Microsoft Windows.

--------------------------------------------------------------------------*/

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <conio.h>

#include <windows.h>

#include "api.h"
#include "param.h"

// Ethan: Include the app_fun.c file, not the header file
#include "app_fun.c"

/* Directory of Neurobit Driver runtime files */
#define NEUROBIT_RUNTIME_DIR ""

/* Name of driver library file */
// Ethan: The 64-bit version of the driver is required
#define DRV_LIB_NAME NEUROBIT_RUNTIME_DIR"NeurobitDrv64.dll"


/* Device info */
struct DevContextInfo DevInfo = {
	-1, "Neurobit Optima+ 4 USB"
};

/* Pointers to driver library functions.
	(Not all of them will be used.) */

TStartMeasurement NdStartMeasurement;
TStopMeasurement NdStopMeasurement;
TProtocolEngine NdProtocolEngine;
TGetDevSN NdGetDevSN;
TGetUserInd NdGetUserInd;

TGetDevName NdGetDevName;
TEnumDevices NdEnumDevices;
TOpenDevContext NdOpenDevContext;
TSelectDevContext NdSelectDevContext;
TCloseDevContext NdCloseDevContext;
TGetDevConfig NdGetDevConfig;
TSetDevConfig NdSetDevConfig;

TEnumParams NdEnumParams;
TParamInfo NdParamInfo;
TGetParam NdGetParam;
TSetParam NdSetParam;
TGetOptNum NdGetOptNum;
TParam2Str NdParam2Str;
TParamList2Str NdParamList2Str;
TStr2Param NdStr2Param;
TSetDefaults NdSetDefaults;
TDevServices NdDevServices;
TCreateDevWindow NdCreateDevWindow;

/* Print error message (adding new line chars) and return 1. */
#define Error(msg) printf("!%s\nPress Enter...\n", msg), getchar(), 1

/* Esc key code */
#define KB_ESC 27

/*--------------------------------------------------------------------------*/

/* Init Neurobit driver library use.
	System specific function. It returns handle to the library of given filename;
	on error it returns NULL. */
static HMODULE InitNeurobitDrvLib(const char * drvLibName)
{
	HMODULE drv_lib;

	/* Pointers to pointers to callback functions */
	TUserMsg *pUserMsg;
	TUserInd *pUserInd;
	TProcSamples *pProcSamples;

	/* Load Neurobit driver library */
	drv_lib = LoadLibrary(drvLibName);
	if (!drv_lib) {
		//printf("!Cannot load library %s\n", drvLibName);
		return NULL;
	}
	if (!(NdStartMeasurement = (TStartMeasurement) GetProcAddress(drv_lib, "NdStartMeasurement")) ||
		!(NdStopMeasurement = (TStopMeasurement) GetProcAddress(drv_lib, "NdStopMeasurement")) ||
		!(NdProtocolEngine = (TProtocolEngine) GetProcAddress(drv_lib, "NdProtocolEngine")) ||
		!(NdGetDevSN = (TGetDevSN) GetProcAddress(drv_lib, "NdGetDevSN")) ||
		!(NdGetUserInd = (TGetUserInd) GetProcAddress(drv_lib, "NdGetUserInd")) ||

		!(NdEnumDevices = (TEnumDevices) GetProcAddress(drv_lib, "NdEnumDevices")) ||
		!(NdOpenDevContext = (TOpenDevContext) GetProcAddress(drv_lib, "NdOpenDevContext")) ||
		!(NdSelectDevContext = (TSelectDevContext) GetProcAddress(drv_lib, "NdSelectDevContext")) ||
		!(NdCloseDevContext = (TCloseDevContext) GetProcAddress(drv_lib, "NdCloseDevContext")) ||
		!(NdGetDevConfig = (TGetDevConfig) GetProcAddress(drv_lib, "NdGetDevConfig")) ||
		!(NdSetDevConfig = (TSetDevConfig) GetProcAddress(drv_lib, "NdSetDevConfig")) ||

		!(NdGetDevName = (TGetDevName) GetProcAddress(drv_lib, "NdGetDevName")) ||
		!(NdEnumParams = (TEnumParams) GetProcAddress(drv_lib, "NdEnumParams")) ||
		!(NdParamInfo = (TParamInfo) GetProcAddress(drv_lib, "NdParamInfo")) ||
		!(NdGetParam = (TGetParam) GetProcAddress(drv_lib, "NdGetParam")) ||
		!(NdSetParam = (TSetParam) GetProcAddress(drv_lib, "NdSetParam")) ||
		!(NdGetOptNum = (TGetOptNum) GetProcAddress(drv_lib, "NdGetOptNum")) ||
		!(NdParam2Str = (TParam2Str) GetProcAddress(drv_lib, "NdParam2Str")) ||
		!(NdParamList2Str = (TParamList2Str) GetProcAddress(drv_lib, "NdParamList2Str")) ||
		!(NdStr2Param = (TStr2Param) GetProcAddress(drv_lib, "NdStr2Param")) ||
		!(NdSetDefaults = (TSetDefaults) GetProcAddress(drv_lib, "NdSetDefaults")) ||
		!(NdDevServices = (TDevServices) GetProcAddress(drv_lib, "NdDevServices")) ||
		!(NdCreateDevWindow = (TCreateDevWindow) GetProcAddress(drv_lib, "NdCreateDevWindow")) ||

		!(pUserMsg = (TUserMsg*) GetProcAddress(drv_lib, "NdUserMsg")) ||
		!(pUserInd = (TUserInd*) GetProcAddress(drv_lib, "NdUserInd")) ||
		!(pProcSamples = (TProcSamples*) GetProcAddress(drv_lib, "NdProcSamples")))
	{
		//printf("!Cannot find library function\n");
		FreeLibrary(drv_lib);
		return NULL;
	}
	*pUserMsg = NdUserMsg;
	*pUserInd = NdUserInd;
	*pProcSamples = NdProcSamples;
	
	return drv_lib;
}

/* Write dump header. The function sets sample coefficients (int to real)
	and names for individual channels in the *dev structure for further use.
	Consecutive header columns are connected with consecutive signals.
	It returns number of channels for success, or zero for error. */
static int AsciiWriteHeader(struct DevContextInfo* dev)
{
#define SIG_HEADER_LINES 7
	const char* const SigHeaderNames[SIG_HEADER_LINES] = {
		"Channel", "Min", "Max", "Unit", "SR", "Label", "Sensor"
	};
	byte chan_en[MAX_SIGNALS];
	word i, l;
	word chans; /* Number of channels */
	word sig_num; /* Number of signals */
	NDGETVAL v;

	/* Set channel enable array and number of signals */
	if (NdGetParam(ND_PAR_CHAN_NUM, 0, &v) || !((v.type & ~ND_T_LIST) == ND_T_INT))
		return 0;
	chans = v.val.i;
	for (i = sig_num = 0; i < chans; i++) {
		if (chans > 1) {
			if (NdGetParam(ND_PAR_CH_EN, i, &v) || !((v.type & ~ND_T_LIST) == ND_T_BOOL))
				return 0;
			chan_en[i] = v.val.b;
		}
		else
			chan_en[i] = true;
		if (chan_en[i])
			sig_num++;
	}

	/* Print sample array header */
	for (l = 0; l < SIG_HEADER_LINES; l++) {
		//printf(SigHeaderNames[l]);
		for (i = 0; i < chans; i++) {
			const NDPARAM* p;

			if (!chan_en[i])
				continue;
			//printf("\t");
			switch (l) {
			case 0:
				if (NdGetParam(ND_PAR_CH_NAME, i, &v) || !((v.type & ~ND_T_LIST) == ND_T_TEXT))
					return 0;
				//printf(v.val.t);
				memset(dev->names[i], 0, sizeof(dev->names[i]));
				strncpy(dev->names[i], v.val.t, sizeof(dev->names[i]) - 1);
				break;
			case 1:
				if (NdGetParam(ND_PAR_CH_RANGE_MIN, i, &v) || !((v.type & ~ND_T_LIST) == ND_T_FLOAT))
					return 0;
				//printf("%-g", v.val.f);
				break;
			case 2:
				if (NdGetParam(ND_PAR_CH_RANGE_MAX, i, &v) || !((v.type & ~ND_T_LIST) == ND_T_FLOAT))
					return 0;
				//printf("%-g", v.val.f);
				dev->coeff[i] = v.val.f / 0x80000000ul;
				break;
			case 3:
				p = NdParamInfo(ND_PAR_CH_RANGE_MAX, i);
				//printf("%s", p->unit);
				break;
			case 4:
				if (NdGetParam(ND_PAR_CH_SR, i, &v) || !((v.type & ~ND_T_LIST) == ND_T_FLOAT))
					return 0;
				//printf("%-g", v.val.f);
				break;
			case 5:
				if (NdGetParam(ND_PAR_CH_LABEL, i, &v) || !((v.type & ~ND_T_LIST) == ND_T_TEXT))
					return 0;
				//printf("%s", v.val.t);
				break;
			case 6:
				if (NdGetParam(ND_PAR_CH_TRANSDUCER, i, &v) || !((v.type & ~ND_T_LIST) == ND_T_TEXT))
					return 0;
				//printf("%s", v.val.t);
				break;
			}
		}
		//printf("\n");
	}
	dev->dev_chans = chans;
	return chans;
}

/*--------------------------------------------------------------------------*/

/* Main application function */
int main(int argc, char *argv[])
{
	HMODULE drv_lib;  /* Handle to driver library */
	int c;            /* Pressed key code */
	int wait_end = 0; /* Flag of awaiting for communication end */
	int r;            /* Start measurement result */
	NDGETVAL gv;      /* Read value of a device parameter */
	NDSETVAL sv;      /* Set value of a device parameter */
	int chans;     /* Number of channels */
	int ch;

	if (argc>1) {
		/* Device model given in program call.
			Overwrite the default. */
		DevInfo.model = argv[1];
	}
	/* Init protocol driver library */
	drv_lib = InitNeurobitDrvLib(DRV_LIB_NAME);
	if (!drv_lib)
		return Error("Cannot get driver library handle");

	/* Open device context */
	DevInfo.dc = NdOpenDevContext(DevInfo.model);
	if (DevInfo.dc < 0) {
		//printf("Selected device model: %s\n", DevInfo.model);
		return Error("Cannot open the device");
	}

	/* Get number of channels */	
	if (NdGetParam(ND_PAR_CHAN_NUM, 0, &gv)) {
			return Error("Cannot get number of channels");
	}
	chans = gv.val.i;
	
	/* Example of automatic device configuration:
		Enable all versatile channels and set "EEG" profile for them. */
	sv.val.b = true;
		if (NdSetParam(ND_PAR_CH_EN, 0, &sv)) { /* Device parameter can be set with NdSetParam... */
			return Error("Cannot enable channel");
		}
		if (NdStr2Param("nIR HEG", ND_PAR_CH_PROF, 0)) { /* ...or with NdStr2Param function */
			return Error("Cannot set \"EEG\" profile");
		}
	
	
	/* Write data header for the device and prepare info for sample processing */
	AsciiWriteHeader(&DevInfo);
#ifdef STATUS_VEC
	memset(DevInfo.status_vec, 0, sizeof(DevInfo.status_vec));  /* Initialize status vector */
#endif /* STATUS_VEC */

	/* Start measurement in the device (using default device address for
		connection) */
	//printf("Connecting to %s device. Please wait...\n", DevInfo.model);
	r = NdStartMeasurement(DevInfo.dc, ND_MEASURE_NORMAL);
	if (r > 0)
		return Error("Cannot connect to the device");
	else if (r < 0)
		return Error("Cannot start measurement in the device");
	//printf("Measurement started.\n");
	//printf("Pressing Esc ends session.\n");

	/* Main loop */
	while (1) {
		/* Call communication protocol engine periodically */
		if (!NdProtocolEngine())
			/* Communication finished. Break loop. */
			break;

		/* Keyboard hit processing */
		if (kbhit()) {
			c = getch();
			if (!c)
				/* Extended code */
				c = 0x100 + getch();

			if (c == KB_ESC && !wait_end) {
				/* Esc key pressed. Stop measurement (and wait for communication end). */
				NdStopMeasurement(DevInfo.dc);
				wait_end = 1;
			}
		}
	}
	//printf("\n\n");

	/* Close device context */
	NdCloseDevContext(DevInfo.dc);
	/* Free library handle */
	FreeLibrary(drv_lib);
	//system("PAUSE");
	return 0;
}
