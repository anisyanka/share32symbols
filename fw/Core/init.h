
#ifndef __INIT_H
#define __INIT_H

#ifdef __cplusplus
extern "C" {
#endif

void SystemClock_Config(void);
void GPIO_Init(void);
void USART1_UART_Init(void);

#ifdef __cplusplus
}
#endif

#endif /* __INIT_H */
