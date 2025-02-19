/*
	Sample application interoperating with Neurobit device.

	Application & platform specific functions
	called back by protocol state machine.
	
	Source code for Microsoft Windows, as an example.

	Copyright (c) by Neurobit Systems, 2010-2022

--------------------------------------------------------------------------*/

#include "common.h"
#include "api.h"
#include "app_fun.h"

#include <stdio.h>

/* Number of a sample value characters in output file */
#define FLOAT_WIDTH 9

/* Display message for an user */
void NdUserMsg(word dc, const char *msg)
{
	//printf("U(%i) %s", dc, msg);
	//printf("\n");
}

/* Update specified indicator of measurement state at the level of user interface.
	data argument pass additional information specific to a given indicator. */
void NdUserInd(word dc, int ind, word data)
{
	/* Artifact info */
	const char* const art_msgs[ND_SIG_LOSS+1] = {
		"Signal OK",
		"No signal",
		"Signal OVERRANGE",
		"Processor OVERLOAD. Sample loss might occur."
	};

	//printf("I(%i) ", dc);
	switch (ind) {
	case ND_IND_LINK:
		switch (data) {
		case ND_LINK_CON:
			//printf("LINK: Link CONNECTED\n");
			break;
		case ND_LINK_DISC:
			//printf("LINK: Link DISCONNECTED\n");
			break;
		case ND_LINK_ERR:
			//printf("LINK: Communication ERROR\n");
			break;
		}
		break;

	case ND_IND_BAT:
		switch (data) {
		case ND_BAT_FRESH:
		case ND_BAT_OK:
			//printf("BAT: Battery OK\n");
			break;
		case ND_BAT_WEAK:
			//printf("BAT: Battery weak\n");
			break;
		case ND_BAT_FLAT:
			//printf("BAT: Battery FLAT\n");
			break;
		}
		break;

	case ND_IND_SIGNAL:
		// if (data & 0xff00)
		// 	/* Signal state in normal channel */
		// 	printf("SIG(%s): %s\n", DevInfo.names[(data >> 8) - 1], art_msgs[data & 0x00ff]);
		// else
		// 	/* Sum signal state */
		// 	printf("SIG(SUM): %s\n", art_msgs[data]);
		break;

	case ND_IND_PAUSE:
		// printf("PAUSE: %s\n", data ? "on" : "off");
		break;
	}
}

// #ifndef SYNC_SAMPLES_INLINE
// /*** Easier version: 
// 	samples received in each data packet are listed channel by channel 
// 	(on line per channel). ***/

// /* Process received samples */
// void NdProcSamples(word dc, word phase, word sum_st, const NdPackChan* chans)
// {
// 	int i, j;
// 	const NdPackChan* ch;

// #ifdef STATUS_INFO
// 	/* Print common voltage state in the 1st line */
// 	printf("[%i]\n", sum_st);
// #endif
// 	/* Loop by channels */
// 	for (i = 0, ch=chans; i < DevInfo.dev_chans; i++, ch++) {
// 		if (ch->num == 0)
// 			/* No samples in the channel at the moment */
// 			continue;
// 		const NdPackSample *s;
// 		printf("%s", DevInfo.names[i]);
// 		/* Loop by samples */
// 		for (j = 0, s = ch->samps; j < ch->num; j++, s++) {
// 			printf("\t%-*g", FLOAT_WIDTH, *s * DevInfo.coeff[i]);
// 		}
// #ifdef STATUS_INFO
// 		/* Print channel signal status */
// 		printf("\t[%i]", ch->sig_st);
// #endif
// 		printf("\n");
// 	}
// }

// #else /* defined(SYNC_SAMPLES_INLINE) */
/*** More complex version: 
	samples taken simultaneously in several channels are shown in the same 
	line, even if sample rates in individual channels are different
	(one line per the shortest sampling period).	***/

/* Process received samples */
void NdProcSamples(word dc, word phase, word sum_st, const NdPackChan *chans)
{
	/* Example: Print received samples on console screen. */
	/* REMARK! Fast console output may significantly burden processor and
		limit effective data link throughput. In order to avoid link failure
		states use this example only with low sample rates, with small console
		window or with stdout redirected to disk file. */

	/* For simplification:
		* Continuous time is assumed (phase is not checked).
	*/

	// Disable buffering of stdout to get a real-time output in the python script
	setbuf(stdout, NULL);
	char s[(MAX_SIGNALS * (FLOAT_WIDTH+1) + 2) + 1];
	char *p = s;
	word endphase = 0;  /* Flag of the last phase in input sample packet */
	word snum[MAX_SIGNALS]; /* Array of indexes of current samples from individual channels */
#ifdef STATUS_INFO
	short statuses[MAX_SIGNALS]; /* Vector of current signal statuses for individual channels */
#endif

	memset(snum, 0, sizeof(snum));
	/* Loop by sampling phases */
	do {
		word i, *n;
		const NdPackChan *ch;
		
		/* Loop by channels */
		for (i=0, ch=chans, n=snum; i<DevInfo.dev_chans; i++, ch++, n++) {
			if (!ch->samps)
				/* Channel disabled */
				continue;
			if ((phase+1)&ch->mask) {
				/* Channel was not sampled at current phase */
				p += sprintf(p, "\t");
				continue;
			}
			/* There is a sample from this channel in current phase. */
			p += sprintf(p, "\t%-*g", FLOAT_WIDTH, ch->samps[*n] * DevInfo.coeff[i]);
#ifdef STATUS_INFO
			statuses[i] = ch->sig_st;  /* Update status for channel "i" */
#endif

			(*n)++;
			if (*n==ch->num)
				endphase = 1;
		}
		/* Output sample values for given sampling phase */
		printf("%s\n", s);
		p = s;

#ifdef STATUS_INFO
		//printf("\t[%i", sum_st);
		for (i=0, ch=chans; i<DevInfo.dev_chans; i++, ch++) {
			if (!ch->samps)
				/* Channel disabled */
				continue;
			//printf("%i", statuses[i]);
		}
		//printf("]");
#endif /* STATUS_INFO */
		//printf("\n");

		phase++;
	} while (!endphase);
}
// #endif /* defined(SYNC_SAMPLES_INLINE) */
