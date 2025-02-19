/*
	Neurobit device Application Programming Interface (API).

	General definitions.

	ANSI C system independent source.

	Copyright (c) by Neurobit Systems, 2010

--------------------------------------------------------------------------*/

#ifndef __COMMON_H__
#define __COMMON_H__

typedef unsigned int dword;
typedef unsigned short word;
typedef unsigned char byte;

typedef enum {
	false,
	true
} bool;

#ifdef _MSC_VER
#define PACK( __Declaration__ ) __pragma(pack(1)) __Declaration__ __pragma( pack())
#else

#ifdef __GNUC__
#define PACK( __Declaration__ ) __Declaration__ __attribute__((__packed__))
#else

#define PACK( __Declaration__ ) __Declaration__
#endif
#endif

#ifdef __cplusplus
#define EXPORT extern "C" __declspec (dllexport)
#else
#define EXPORT __declspec (dllexport)
#endif

#endif /* __COMMON_H__ */

