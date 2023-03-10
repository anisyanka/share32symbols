#ifndef __USB_DEVICE__H__
#define __USB_DEVICE__H__

#ifdef __cplusplus
 extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx.h"
#include "stm32f1xx_hal.h"
#include "usbd_def.h"

void USB_DEVICE_Init(void);

#ifdef __cplusplus
}
#endif

#endif /* __USB_DEVICE__H__ */
