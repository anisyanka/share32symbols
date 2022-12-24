
#include "main.h"
#include "init.h"
#include "usb_device.h"
#include "usbd_cdc_if.h"

#include <stdbool.h>

uint8_t ok_ans[] = { 'O', 'K', APP_END_OF_MESSAGE_SYMBOL };
uint8_t err_ans[] = { 'N', 'O', APP_END_OF_MESSAGE_SYMBOL };
char oled_line1[16] = { 0 };
char oled_line2[16] = { 0 };
bool is_package_received = false;
uint8_t user_rx_buffer[APP_USER_RX_BUFFER_SIZE] = { 0 };

int main(void)
{
	HAL_Init();
	SystemClock_Config();
	GPIO_Init();
	USB_DEVICE_Init();
	USART1_UART_Init();

	while (1)
	{
		if (is_package_received)
		{
			is_package_received = false;

			// update OLED text
			CDC_Transmit_FS(ok_ans, sizeof(ok_ans));
		}
	}
}

void Error_Handler(void)
{
	/* User can add his own implementation to report the HAL error return state */
	__disable_irq();
	while (1)
	{
	}
}

#ifdef  USE_FULL_ASSERT
/**
	* @brief  Reports the name of the source file and the source line number
	*         where the assert_param error has occurred.
	* @param  file: pointer to the source file name
	* @param  line: assert_param error line source number
	* @retval None
	*/
void assert_failed(uint8_t *file, uint32_t line)
{
	/* User can add his own implementation to report the file name and line number,
		 ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
}
#endif /* USE_FULL_ASSERT */
