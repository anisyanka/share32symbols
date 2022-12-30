#ifndef __USBD_CDC_IF_H__
#define __USBD_CDC_IF_H__

#ifdef __cplusplus
 extern "C" {
#endif

#include "usbd_cdc.h"

#define APP_OLED_LINE_DELIMITER '\n'
#define APP_USER_RX_BUFFER_SIZE 128

/* Define size for the receive and transmit buffer over CDC */
#define APP_RX_DATA_SIZE  256
#define APP_TX_DATA_SIZE  256

/** CDC Interface callback. */
extern USBD_CDC_ItfTypeDef USBD_Interface_fops_FS;

uint8_t CDC_Transmit_FS(uint8_t* Buf, uint16_t Len);

#ifdef __cplusplus
}
#endif

#endif /* __USBD_CDC_IF_H__ */

