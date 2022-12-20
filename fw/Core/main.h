
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

#include "stm32f1xx_hal.h"

void Error_Handler(void);

#define SIGNAL_LED_Pin			GPIO_PIN_13
#define SIGNAL_LED_GPIO_Port	GPIOC
#define OLED_BIT_0_Pin			GPIO_PIN_0
#define	OLED_BIT_0_GPIO_Port	GPIOA
#define	OLED_BIT_1_Pin			GPIO_PIN_1
#define	OLED_BIT_1_GPIO_Port	GPIOA
#define	OLED_BIT_2_Pin			GPIO_PIN_2
#define	OLED_BIT_2_GPIO_Port	GPIOA
#define	OLED_BIT_3_Pin			GPIO_PIN_3
#define	OLED_BIT_3_GPIO_Port	GPIOA
#define	OLED_BIT_4_Pin			GPIO_PIN_4
#define	OLED_BIT_4_GPIO_Port	GPIOA
#define	OLED_BIT_5_Pin			GPIO_PIN_5
#define	OLED_BIT_5_GPIO_Port	GPIOA
#define	OLED_BIT_6_Pin			GPIO_PIN_6
#define	OLED_BIT_6_GPIO_Port	GPIOA
#define	OLED_BIT_7_Pin			GPIO_PIN_7
#define	OLED_BIT_7_GPIO_Port	GPIOA
#define	OLED_RS_Pin				GPIO_PIN_7
#define	OLED_RS_GPIO_Port		GPIOB
#define	OLED_RW_Pin				GPIO_PIN_8
#define	OLED_RW_GPIO_Port		GPIOB
#define	OLED_E_Pin				GPIO_PIN_9
#define	OLED_E_GPIO_Port		GPIOB

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
