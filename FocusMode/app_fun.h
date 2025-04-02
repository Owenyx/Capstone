/*
	Sample application interoperating with Neurobit device.

	Application & platform specific functions
	called back by protocol state machine.

	Copyright (c) by Neurobit Systems, 2010-2022

--------------------------------------------------------------------------*/

#ifndef __APP_FUN_H__
#define __APP_FUN_H__

#include "api.h"

/* Max. number of output measured signals handled in the application */
#define MAX_SIGNALS 16

/* Option (#ifdef) of more complex version of NdProcSamples callback function.
	If defined, samples taken simultaneously in several channels are
	shown in the same line, even if sample rates in individual channels
	are different (one line per the shortest sampling period). */
//#define SYNC_SAMPLES_INLINE

/* Option (#ifdef) of signal statuses output (in NdProcSamples) */
#define STATUS_INFO

/* Auxiliary structure of info associated with device context */
struct DevContextInfo {
	/* Device context */
	int dc;
	/* Device model name */
	const char *model;
	/* Number of channels */
	int dev_chans;
	/* Array of sample scaling factors */
	float coeff[MAX_SIGNALS];
	/* Channel names to print */
	char names[MAX_SIGNALS][5];
};

/* Device info */
extern struct DevContextInfo DevInfo;

/* Display message for an user */
void NdUserMsg(word dc, const char *msg);

/* Update specified indicator of measurement state at the level of user interface.
	data argument pass additional information specific to a given indicator. */
void NdUserInd(word dc, int ind, word data);

/* Process received signal samples */
void NdProcSamples(word dc, word phase, word sum_st, const NdPackChan *chans);

#endif /* __APP_FUN_H__ */

